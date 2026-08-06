"""A3 verifier (docs/gate5/a3-design.md §5).

Builds the candidate in the pinned workspace, detects sorry/admit twice
(static scan + kernel-level axiom audit), and produces the axiom/
dependency audit compared against the per-run reviewer record
(``axiom_approval_ref``). Outcome semantics:

- VERIFIED: compile ok, no sorry, every used axiom approved;
- FAILED: compile error (LEAN_SYNTAX_ERROR), sorry (SORRY_FOUND),
  unapproved axiom (AXIOM_VIOLATION), or timeout (PROOF_TIMEOUT);
- BLOCKED: could not safely run (unpinned workspace, lake missing).

The verifier never mutates anything outside its per-run candidate
directory. Kernel authority: ``lake env lean`` runs inside the pinned
workspace so Mathlib resolution matches the recorded identity.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from leanecon.claim_store import sanitize_module_part
from leanecon.events import CapabilityStatus
from leanecon.lean_probe import check_sorry_free, read_workspace_identity

REASON_LEAN_SYNTAX_ERROR = "LEAN_SYNTAX_ERROR"
REASON_SORRY_FOUND = "SORRY_FOUND"
REASON_AXIOM_VIOLATION = "AXIOM_VIOLATION"
REASON_PROOF_TIMEOUT = "PROOF_TIMEOUT"
REASON_WORKSPACE_UNPINNED = "WORKSPACE_UNPINNED"

_AXIOM_LINE = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]")


@dataclass(frozen=True)
class VerificationRecord:
    claim_id: str
    run_id: str
    theorem_name: str
    compile_ok: bool
    exit_code: Optional[int]
    timed_out: bool
    stderr_tail: str
    axiom_list: list[str]
    static_sorry_ok: bool
    workspace_pinned: bool
    candidate_path: str
    elapsed_ms: int
    outcome: str  # VERIFIED | FAILED | BLOCKED
    reason_code: Optional[str] = None
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "run_id": self.run_id,
            "theorem_name": self.theorem_name,
            "compile_ok": self.compile_ok,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "stderr_tail": self.stderr_tail,
            "axiom_list": self.axiom_list,
            "static_sorry_ok": self.static_sorry_ok,
            "workspace_pinned": self.workspace_pinned,
            "candidate_path": self.candidate_path,
            "elapsed_ms": self.elapsed_ms,
            "outcome": self.outcome,
            "reason_code": self.reason_code,
            "detail": self.detail,
        }


def parse_axiom_lines(stdout: str) -> dict[str, list[str]]:
    """Parse '#print axioms' output: {theorem_name: [axiom, ...]}."""
    found: dict[str, list[str]] = {}
    for match in _AXIOM_LINE.finditer(stdout):
        name = match.group(1).strip()
        axioms = [a.strip() for a in match.group(2).split(",") if a.strip()]
        found[name] = axioms
    return found


def run_lake_env_lean(workspace_root: Path, source_path: Path, timeout_s: int) -> tuple:
    """Run ``lake env lean <file>`` in the pinned workspace.

    Returns (exit_code | None, stdout, stderr, timed_out). None exit code
    means the process could not start (toolchain missing).
    """
    lake = shutil.which("lake")
    if lake is None:
        return None, "", "lake executable not found on PATH", False
    try:
        proc = subprocess.run(
            [lake, "env", "lean", str(source_path)],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        return None, "", f"lake env lean timed out after {timeout_s}s", True


def verify_candidate(
    workspace_root: Path,
    candidate_source: str,
    theorem_name: str,
    run_id: str,
    claim_id: str,
    approved_axioms: Optional[frozenset] = None,
    timeout_s: int = 600,
) -> VerificationRecord:
    """Compile and audit one candidate in the pinned workspace."""
    started = time.monotonic()

    identity = read_workspace_identity(workspace_root)
    if not identity.pinned:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=False, exit_code=None, timed_out=False, stderr_tail="workspace unpinned",
            axiom_list=[], static_sorry_ok=False, workspace_pinned=False,
            candidate_path="", elapsed_ms=0, outcome="BLOCKED", reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"workspace_root": str(workspace_root)},
        )

    # per-run candidate directory OUTSIDE the LeanEcon lib tree: files inside
    # a lean_lib dir get a module name inferred from their path, which must
    # match — per-run candidates would collide. .a3-candidates/ is never
    # committed and never mutates the tracked library. claim_id and run_id
    # are CLI-supplied strings, so both are sanitized before use in paths.
    safe_claim = sanitize_module_part(claim_id)
    safe_run = sanitize_module_part(run_id)
    run_dir = workspace_root / ".a3-candidates" / safe_claim / safe_run
    run_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = run_dir / "Candidate.lean"
    # The kernel-level axiom audit needs the compiler to report the theorem's
    # axiom closure: append a #print axioms query to the COMPILED file. The
    # query is a compiler directive, not part of the statement/proof artifact
    # (digests and the bundle use candidate_source without it).
    compile_source = candidate_source + f"\n#print axioms {theorem_name}\n"
    candidate_path.write_text(compile_source, encoding="utf-8")

    static = check_sorry_free(candidate_source)
    static_sorry_ok = static.status is CapabilityStatus.HEALTHY
    if not static_sorry_ok:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=False, exit_code=None, timed_out=False,
            stderr_tail="static sorry scan", axiom_list=[], static_sorry_ok=False,
            workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=0,
            outcome="FAILED", reason_code=REASON_SORRY_FOUND,
            detail={"marker": static.detail.get("marker")},
        )

    exit_code, stdout, stderr, timed_out = run_lake_env_lean(workspace_root, candidate_path, timeout_s)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    if timed_out:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=False, exit_code=None, timed_out=True, stderr_tail=stderr[-500:],
            axiom_list=[], static_sorry_ok=True, workspace_pinned=True,
            candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="FAILED", reason_code=REASON_PROOF_TIMEOUT,
            detail={"timeout_s": timeout_s},
        )
    if exit_code is None:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=False, exit_code=None, timed_out=False, stderr_tail=stderr[-500:],
            axiom_list=[], static_sorry_ok=True, workspace_pinned=True,
            candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="BLOCKED", reason_code=REASON_WORKSPACE_UNPINNED,
            detail={"error": stderr[-300:]},
        )

    axioms_by_name = parse_axiom_lines(stdout)
    axiom_list = sorted(axioms_by_name.get(theorem_name, []))

    if exit_code != 0:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=False, exit_code=exit_code, timed_out=False,
            stderr_tail=stderr[-800:], axiom_list=axiom_list, static_sorry_ok=True,
            workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="FAILED", reason_code=REASON_LEAN_SYNTAX_ERROR,
            detail={"exit_code": exit_code},
        )
    if theorem_name not in axioms_by_name:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=True, exit_code=0, timed_out=False,
            stderr_tail=stderr[-300:], axiom_list=[], static_sorry_ok=True,
            workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="FAILED", reason_code=REASON_LEAN_SYNTAX_ERROR,
            detail={"error": f"#print axioms did not report theorem '{theorem_name}'"},
        )
    if "sorryAx" in axiom_list:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=True, exit_code=0, timed_out=False,
            stderr_tail=stderr[-300:], axiom_list=axiom_list, static_sorry_ok=True,
            workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="FAILED", reason_code=REASON_SORRY_FOUND,
            detail={"marker": "sorryAx (kernel-level audit)"},
        )

    if approved_axioms is None:
        unapproved = axiom_list
    else:
        unapproved = sorted(a for a in axiom_list if a not in approved_axioms)

    if unapproved:
        return VerificationRecord(
            claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
            compile_ok=True, exit_code=0, timed_out=False,
            stderr_tail=stderr[-300:], axiom_list=axiom_list, static_sorry_ok=True,
            workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
            outcome="FAILED", reason_code=REASON_AXIOM_VIOLATION,
            detail={"unapproved_axioms": unapproved},
        )

    return VerificationRecord(
        claim_id=claim_id, run_id=run_id, theorem_name=theorem_name,
        compile_ok=True, exit_code=0, timed_out=False,
        stderr_tail=stderr[-300:], axiom_list=axiom_list, static_sorry_ok=True,
        workspace_pinned=True, candidate_path=str(candidate_path), elapsed_ms=elapsed_ms,
        outcome="VERIFIED", reason_code=None, detail={},
    )
