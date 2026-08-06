"""A3 verifier tests (docs/gate5/a3-design.md §5).

Real-workspace tests run against the pinned Lean/Mathlib workspace and skip
gracefully when the toolchain is unavailable (CI without Lean), matching the
A1 probe test convention.
"""

import shutil
from pathlib import Path

import pytest

from leanecon import verifier
from leanecon.lean_probe import check_sorry_free
from tests.conftest import FIXTURES, WORKSPACE, elan_on_path  # noqa: F401


def workspace_ready() -> bool:
    return (WORKSPACE / "lean-toolchain").exists() and (WORKSPACE / "lakefile.lean").exists()


requires_workspace = pytest.mark.skipif(
    not workspace_ready() or not (Path.home() / ".elan" / "bin" / "lake").exists(),
    reason="pinned Lean workspace/toolchain not available",
)

STD_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})


# --- pure logic ----------------------------------------------------------


def test_parse_axiom_lines():
    stdout = "'t' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
    assert verifier.parse_axiom_lines(stdout)["t"] == ["propext", "Classical.choice", "Quot.sound"]


def test_sorry_free_check_flags_admit():
    result = check_sorry_free("theorem t : 1 = 1 := by admit")
    assert result.reason_code == "SORRY_FOUND"


# --- workspace behavior ---------------------------------------------------


@requires_workspace
def test_fixture_without_axiom_record_is_axiom_violation(elan_on_path):
    """First-run honesty: no axiom approval record yet -> AXIOM_VIOLATION,
    with the surfaced axiom list in the detail (the reviewer then approves)."""
    source = (FIXTURES / "c4_monotone_order.lean").read_text(encoding="utf-8")
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_c4_monotone_order",
                                       run_id="test-run-clean", claim_id="test-c4")
    assert record.outcome == "FAILED", record.detail
    assert record.reason_code == "AXIOM_VIOLATION"
    assert set(record.axiom_list) == STD_AXIOMS
    assert record.compile_ok is True  # the kernel accepted it; policy blocked it
    assert "sorryAx" not in record.axiom_list


@requires_workspace
def test_fixture_with_approved_axioms_verifies(elan_on_path):
    source = (FIXTURES / "c4_monotone_order.lean").read_text(encoding="utf-8")
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_c4_monotone_order",
                                       run_id="test-run-ok", claim_id="test-c4-ok",
                                       approved_axioms=STD_AXIOMS)
    assert record.outcome == "VERIFIED", record.detail
    assert record.reason_code is None
    assert "sorryAx" not in record.axiom_list


@requires_workspace
def test_unapproved_axiom_fails_axiom_violation(elan_on_path):
    source = (
        "import Mathlib.Data.Real.Basic\n"
        "axiom my_test_axiom : 1 = 1\n"
        "theorem leanecon_test_uses_axiom : 1 = 1 := my_test_axiom\n"
    )
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_test_uses_axiom",
                                       run_id="test-run-ax", claim_id="test-ax")
    assert record.outcome == "FAILED"
    assert record.reason_code == "AXIOM_VIOLATION"
    assert "my_test_axiom" in record.detail.get("unapproved_axioms", [])


@requires_workspace
def test_approved_axiom_passes(elan_on_path):
    source = (
        "import Mathlib.Data.Real.Basic\n"
        "axiom my_approved_axiom : 1 = 1\n"
        "theorem leanecon_test_approved_axiom : 1 = 1 := my_approved_axiom\n"
    )
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_test_approved_axiom",
                                       run_id="test-run-axok", claim_id="test-axok",
                                       approved_axioms=frozenset({"my_approved_axiom", "propext",
                                                                  "Classical.choice", "Quot.sound"}))
    assert record.outcome == "VERIFIED", record.detail


@requires_workspace
def test_syntax_error_is_failed(elan_on_path):
    record = verifier.verify_candidate(WORKSPACE, "def broken : Nat :=", "broken",
                                       run_id="test-run-syn", claim_id="test-syn")
    assert record.outcome == "FAILED"
    assert record.reason_code == "LEAN_SYNTAX_ERROR"


@requires_workspace
def test_kernel_level_sorry_detection(elan_on_path, monkeypatch):
    """Static scan mocked away; the kernel axiom audit must still catch sorryAx."""
    source = "import Mathlib.Data.Real.Basic\ntheorem leanecon_test_sorry : 1 = 1 := by sorry\n"
    # force the static scan to pass so the kernel-level layer is exercised
    monkeypatch.setattr(verifier, "check_sorry_free", lambda src: _healthy())
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_test_sorry",
                                       run_id="test-run-sorry", claim_id="test-sorry")
    assert record.outcome == "FAILED"
    assert record.reason_code == "SORRY_FOUND"
    assert "sorryAx" in record.axiom_list


@requires_workspace
def test_static_sorry_scan_is_first_layer():
    source = "theorem t : 1 = 1 := by sorry\n"
    record = verifier.verify_candidate(WORKSPACE, source, "t",
                                       run_id="test-run-static", claim_id="test-static")
    assert record.outcome == "FAILED"
    assert record.reason_code == "SORRY_FOUND"


def test_timeout_is_failed_proof_timeout(monkeypatch, tmp_path):
    (tmp_path / "lean-toolchain").write_text("leanprover/lean4:v4.32.2\n")
    (tmp_path / "lakefile.lean").write_text('import Lake\nrequire "leanprover-community" / "mathlib" @ git "v4.32.2"\n')

    def fake_run(workspace, source, timeout_s):
        return None, "", "lake env lean timed out", True

    monkeypatch.setattr(verifier, "run_lake_env_lean", fake_run)
    record = verifier.verify_candidate(tmp_path, "theorem t : True := by trivial", "t",
                                       run_id="test-run-timeout", claim_id="test-timeout",
                                       timeout_s=1)
    assert record.outcome == "FAILED"
    assert record.reason_code == "PROOF_TIMEOUT"


def test_unpinned_workspace_is_blocked(tmp_path):
    record = verifier.verify_candidate(tmp_path, "theorem t : True := by trivial", "t",
                                       run_id="test-run-unpin", claim_id="test-unpin")
    assert record.outcome == "BLOCKED"
    assert record.reason_code == "WORKSPACE_UNPINNED"


def test_lake_missing_is_blocked(tmp_path, monkeypatch):
    (tmp_path / "lean-toolchain").write_text("leanprover/lean4:v4.32.2\n")
    (tmp_path / "lakefile.lean").write_text('import Lake\nrequire "leanprover-community" / "mathlib" @ git "v4.32.2"\n')
    monkeypatch.setattr(verifier.shutil, "which", lambda name: None)
    record = verifier.verify_candidate(tmp_path, "theorem t : True := by trivial", "t",
                                       run_id="test-run-nolake", claim_id="test-nolake")
    assert record.outcome == "BLOCKED"
    assert record.reason_code == "WORKSPACE_UNPINNED"


def test_claim_id_path_traversal_is_sanitized():
    """CLI-supplied claim/run ids must not escape the candidate dir."""
    record = verifier.verify_candidate(WORKSPACE, "theorem t : True := by trivial", "t",
                                       run_id="../../escape", claim_id="../evil")
    # the record carries the candidate path; it must stay inside the workspace
    candidate = Path(record.candidate_path)
    assert ".a3-candidates" in candidate.parts
    assert ".." not in candidate.parts, candidate
    # sanitized forms: '../evil' -> '___evil', '../../escape' -> '______escape'
    assert candidate.parts[-3] == "___evil", candidate
    assert candidate.parts[-2] == "______escape", candidate


@requires_workspace
def test_wrong_theorem_in_proof_is_failed_with_bundle_path(elan_on_path):
    """Proof proving a DIFFERENT theorem -> FAILED. The appended kernel
    axiom query (#print axioms <target>) fails compilation because the
    target was never declared — an honest compile-level failure that the
    bundle builder can attach to."""
    source = (
        "import Mathlib.Data.Real.Basic\n"
        "theorem some_other_theorem : 1 = 1 := by rfl\n"
    )
    record = verifier.verify_candidate(WORKSPACE, source, "leanecon_target_never_declared",
                                       run_id="test-run-wrongthm", claim_id="test-wrongthm")
    assert record.outcome == "FAILED"
    assert record.reason_code == "LEAN_SYNTAX_ERROR"
    assert record.candidate_path  # bundle-attachable failure record


def _healthy():
    from leanecon.events import CapabilityStatus

    from leanecon.lean_probe import ProbeResult

    return ProbeResult(capability="sorry_check", status=CapabilityStatus.HEALTHY, detail={})
