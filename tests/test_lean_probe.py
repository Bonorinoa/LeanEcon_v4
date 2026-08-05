"""Lean workspace probe tests (Gate 4, A1 criteria 1–3, 9).

Workspace-dependent tests skip gracefully when the pinned workspace has
not been built yet (e.g. in CI without Lean); pure-logic tests always run.
"""

import shutil
from pathlib import Path

import pytest

from leanecon.events import CapabilityStatus
from leanecon.lean_probe import (
    check_sorry_free,
    probe_invalid_lean,
    probe_lsp,
    probe_workspace,
    read_workspace_identity,
)

WORKSPACE = Path(__file__).resolve().parents[1] / "lean_workspace"


def workspace_ready() -> bool:
    return (WORKSPACE / "lean-toolchain").exists() and (WORKSPACE / "lakefile.lean").exists()


requires_workspace = pytest.mark.skipif(
    not workspace_ready() or shutil.which("lake") is None,
    reason="pinned Lean workspace/toolchain not available",
)


# --- pure logic (always run) -------------------------------------------


def test_sorry_free_check_flags_sorry():
    result = check_sorry_free("theorem t : 1 = 1 := by sorry")
    assert result.status is CapabilityStatus.UNAVAILABLE
    assert result.reason_code == "SORRY_FOUND"


def test_sorry_free_check_flags_admit():
    result = check_sorry_free("theorem t : 1 = 1 := by admit")
    assert result.reason_code == "SORRY_FOUND"


def test_sorry_free_check_passes_clean_code():
    result = check_sorry_free("theorem t : 1 = 1 := by rfl")
    assert result.status is CapabilityStatus.HEALTHY


def test_unpinned_workspace_is_typed_unavailable(tmp_path):
    result = probe_workspace(tmp_path)
    assert result.status is CapabilityStatus.UNAVAILABLE
    assert result.reason_code == "WORKSPACE_UNPINNED"


def test_workspace_identity_reads_pins(tmp_path):
    (tmp_path / "lean-toolchain").write_text("leanprover/lean4:v4.32.2\n")
    (tmp_path / "lakefile.lean").write_text(
        'require "leanprover-community" / "mathlib" @ git "v4.32.2"\n'
    )
    identity = read_workspace_identity(tmp_path)
    assert identity.pinned
    assert identity.lean_toolchain == "leanprover/lean4:v4.32.2"
    assert identity.mathlib_revision == "v4.32.2"


# --- workspace probes (require pinned build) ------------------------------


@requires_workspace
def test_pinned_workspace_is_healthy():
    result = probe_workspace(WORKSPACE)
    assert result.status is CapabilityStatus.HEALTHY
    assert result.detail["lean_toolchain"] == "leanprover/lean4:v4.32.2"
    assert result.detail["mathlib_revision"] == "v4.32.2"


@requires_workspace
def test_invalid_lean_input_produces_typed_failure():
    result = probe_invalid_lean(WORKSPACE, "def broken : Nat := ", timeout_s=120)
    assert result.reason_code == "LEAN_SYNTAX_ERROR"
    # The probe is healthy iff Lean rejected the invalid input as expected.
    assert result.status is CapabilityStatus.HEALTHY
    assert result.detail["exit_code"] != 0
