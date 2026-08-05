"""Lean workspace and LSP probes (Gate 4, A1 criteria 1–3, 9).

Isolated from the application service: probes only report typed results
and capability status; they never mutate the workspace. Invalid Lean
input produces a typed failure (criterion 9), never an untyped crash.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from leanecon.events import CapabilityStatus

REASON_LEAN_SYNTAX_ERROR = "LEAN_SYNTAX_ERROR"
REASON_WORKSPACE_UNPINNED = "WORKSPACE_UNPINNED"
REASON_LSP_UNAVAILABLE = "LSP_UNAVAILABLE"

def _lsp_initialize_request() -> str:
    """JSON-RPC ``initialize`` framed with the required Content-Length
    header. Without the header the Lean LSP watchdog rejects the message."""
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"processId": None, "rootUri": None, "capabilities": {}},
        }
    )
    return f"Content-Length: {len(body)}\r\n\r\n{body}"


@dataclass(frozen=True)
class ProbeResult:
    capability: str
    status: CapabilityStatus
    reason_code: Optional[str] = None
    detail: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WorkspaceIdentity:
    """Pinned workspace identity for the verification bundle: Lean toolchain
    and Mathlib revision. A missing pin is WORKSPACE_UNPINNED, never a
    silent default."""

    workspace_root: str
    lean_toolchain: Optional[str]
    mathlib_revision: Optional[str]

    @property
    def pinned(self) -> bool:
        return bool(self.lean_toolchain and self.mathlib_revision)


def read_workspace_identity(workspace_root: Path) -> WorkspaceIdentity:
    root = Path(workspace_root)
    toolchain_file = root / "lean-toolchain"
    toolchain = toolchain_file.read_text(encoding="utf-8").strip() if toolchain_file.exists() else None
    lakefile = root / "lakefile.lean"
    mathlib_rev = None
    if lakefile.exists():
        text = lakefile.read_text(encoding="utf-8")
        # The pin is the git tag declared in the mathlib require line, e.g.
        # require "leanprover-community" / "mathlib" @ git "v4.32.2"
        match = re.search(r'"mathlib"\s*@\s*git\s+"([^"]+)"', text)
        if match:
            mathlib_rev = match.group(1)
    return WorkspaceIdentity(str(root), toolchain or None, mathlib_rev)


def probe_workspace(workspace_root: Path) -> ProbeResult:
    identity = read_workspace_identity(workspace_root)
    if not identity.pinned:
        return ProbeResult(
            capability="lean_workspace",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"workspace_root": str(workspace_root)},
        )
    return ProbeResult(
        capability="lean_workspace",
        status=CapabilityStatus.HEALTHY,
        detail={
            "workspace_root": str(workspace_root),
            "lean_toolchain": identity.lean_toolchain,
            "mathlib_revision": identity.mathlib_revision,
        },
    )


def probe_lean_compile(workspace_root: Path, target: str = "LeanEcon.A1", timeout_s: int = 1800) -> ProbeResult:
    """Criterion 1: pinned Lean and Mathlib build successfully."""
    identity = read_workspace_identity(workspace_root)
    if not identity.pinned:
        return ProbeResult(
            capability="lean_compile",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"workspace_root": str(workspace_root)},
        )
    lake = shutil.which("lake")
    if lake is None:
        return ProbeResult(
            capability="lean_compile",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"error": "lake executable not found on PATH"},
        )
    try:
        proc = subprocess.run(
            [lake, "build", target],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return ProbeResult(
            capability="lean_compile",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"error": f"lake build timed out after {timeout_s}s"},
        )
    if proc.returncode == 0:
        return ProbeResult(
            capability="lean_compile",
            status=CapabilityStatus.HEALTHY,
            detail={"target": target, "exit_code": 0},
        )
    return ProbeResult(
        capability="lean_compile",
        status=CapabilityStatus.UNAVAILABLE,
        reason_code=REASON_LEAN_SYNTAX_ERROR,
        detail={"target": target, "exit_code": proc.returncode, "stderr_tail": proc.stderr[-500:]},
    )


def check_sorry_free(source: str) -> ProbeResult:
    """Typed failure for sorry/admit in candidate Lean text (supports the
    VERIFIED bar; A1 uses it as a deterministic invalid-input probe)."""
    lowered = source.lower()
    for marker in ("sorry", "admit"):
        if marker in lowered:
            return ProbeResult(
                capability="sorry_check",
                status=CapabilityStatus.UNAVAILABLE,
                reason_code="SORRY_FOUND",
                detail={"marker": marker},
            )
    return ProbeResult(capability="sorry_check", status=CapabilityStatus.HEALTHY, detail={})


def probe_invalid_lean(workspace_root: Path, snippet: str, timeout_s: int = 120) -> ProbeResult:
    """Criterion 9: invalid Lean input produces a typed failure.

    Writes the snippet to a throwaway file outside the tracked library and
    runs ``lean`` on it. A zero exit code here would itself be a defect.
    """
    lean = shutil.which("lean")
    if lean is None:
        return ProbeResult(
            capability="lean_invalid_input",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"error": "lean executable not found on PATH"},
        )
    scratch = Path(workspace_root) / ".a1-scratch"
    scratch.mkdir(exist_ok=True)
    probe_file = scratch / "invalid_probe.lean"
    probe_file.write_text(snippet, encoding="utf-8")
    try:
        proc = subprocess.run(
            [lean, str(probe_file)],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return ProbeResult(
            capability="lean_invalid_input",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_LEAN_SYNTAX_ERROR,
            detail={"error": "lean timed out on invalid input probe"},
        )
    finally:
        probe_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        return ProbeResult(
            capability="lean_invalid_input",
            status=CapabilityStatus.HEALTHY,  # the probe behaved: invalid input was rejected
            reason_code=REASON_LEAN_SYNTAX_ERROR,
            detail={"exit_code": proc.returncode, "stderr_tail": proc.stderr[-300:]},
        )
    return ProbeResult(
        capability="lean_invalid_input",
        status=CapabilityStatus.UNAVAILABLE,
        reason_code=REASON_LEAN_SYNTAX_ERROR,
        detail={"error": "invalid Lean snippet unexpectedly compiled", "exit_code": 0},
    )


def probe_lsp(workspace_root: Path, timeout_s: int = 30) -> ProbeResult:
    """Criterion 3: LSP responds, or explicitly reports UNAVAILABLE —
    no silent fallback."""
    server = shutil.which("lean")
    if server is None:
        return ProbeResult(
            capability="lsp",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_LSP_UNAVAILABLE,
            detail={"error": "lean executable not found on PATH"},
        )
    try:
        proc = subprocess.run(
            [server, "--server"],
            cwd=str(workspace_root),
            input=_lsp_initialize_request(),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return ProbeResult(
            capability="lsp",
            status=CapabilityStatus.UNAVAILABLE,
            reason_code=REASON_LSP_UNAVAILABLE,
            detail={"error": f"LSP initialize timed out after {timeout_s}s"},
        )
    if '"capabilities"' in proc.stdout:
        return ProbeResult(
            capability="lsp",
            status=CapabilityStatus.HEALTHY,
            detail={"server": "lean --server"},
        )
    return ProbeResult(
        capability="lsp",
        status=CapabilityStatus.UNAVAILABLE,
        reason_code=REASON_LSP_UNAVAILABLE,
        detail={"exit_code": proc.returncode, "stderr_tail": proc.stderr[-300:]},
    )
