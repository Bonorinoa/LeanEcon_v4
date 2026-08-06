"""Bundle validator tests (docs/gate5/a3-design.md §6, gate3/05)."""

from leanecon.bundle import build_bundle, bundle_result, validate_bundle
from leanecon.claim_store import ArtifactStore, ClaimRecord
from tests.conftest import WORKSPACE

STD_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]


def _verified_verification() -> dict:
    return {
        "claim_id": "c1", "run_id": "run-1", "theorem_name": "leanecon_c4_monotone_order",
        "compile_ok": True, "exit_code": 0, "timed_out": False, "stderr_tail": "",
        "axiom_list": list(STD_AXIOMS), "static_sorry_ok": True, "workspace_pinned": True,
        "candidate_path": "/tmp/Candidate.lean", "elapsed_ms": 100, "outcome": "VERIFIED",
        "reason_code": None, "detail": {},
    }


def _build_happy(tmp_path) -> tuple[ArtifactStore, ClaimRecord, str]:
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    ei = store.write_ei("c1", {"claim": {"canonical_text": "x"}, "review": {"decision": "APPROVED"}}, status="accepted")
    formal = store.write_formal("c1", {"statement_text": "theorem t : True", "target_theorem": "t",
                                       "imports": ["Mathlib.Data.Real.Basic"], "gaps": []}, status="current")
    proof = "theorem t : True := by trivial"
    verification = _verified_verification()
    bundle_id, _ = build_bundle(
        store=store, claim=claim, ei_artifact=ei, formal_artifact=formal, proof_source=proof,
        verification=verification,
        approval_record={"decision": "APPROVED", "event_ref": "evt-approve"},
        axiom_record={"approved_axioms": STD_AXIOMS},
        trace_refs=["claim:c1", "run:1"], capability_snapshots={"lean_workspace": "HEALTHY"},
        workspace_root=WORKSPACE, commands=["a3 verify --claim-id c1 --proof f"],
    )
    return store, claim, bundle_id


def test_happy_bundle_passes_all_eleven(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    checks = validate_bundle(store, bundle_id, claim)
    assert bundle_result(checks) == "VERIFIED"
    assert all(ok for _, ok, _ in checks), [c for c in checks if not c[1]]


def test_sorry_in_axiom_audit_fails_check_5(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    manifest = store.read_bundle_manifest(bundle_id)
    # a verification whose axiom audit includes sorryAx must fail the no-sorry check
    import json

    verification = _verified_verification()
    verification["axiom_list"] = STD_AXIOMS + ["sorryAx"]
    (bundle_dir / "verification.json").write_text(json.dumps(verification), encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    assert not dict((c[0], c[1]) for c in checks)["5_no_sorry"]


def test_missing_axiom_record_fails_check_6(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    bundle_dir.joinpath("axiom_record.json").write_text("{}", encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    assert not dict((c[0], c[1]) for c in checks)["6_axiom_audit"]


def test_unapproved_axiom_fails_check_6(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    bundle_dir.joinpath("axiom_record.json").write_text(
        '{"approved_axioms": ["propext"]}', encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    assert not dict((c[0], c[1]) for c in checks)["6_axiom_audit"]


def test_corrupt_claim_digest_fails_check_1(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    bundle_dir.joinpath("claim.json").write_text('{"claim_id": "other"}', encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    assert not dict((c[0], c[1]) for c in checks)["1_exact_claim"]


def test_unpinned_workspace_identity_fails_check_7(tmp_path):
    store, claim, bundle_id = _build_happy(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    import json

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["workspace_identity"]["pinned"] = False
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    assert not dict((c[0], c[1]) for c in checks)["7_pinned_workspace"]


def test_zero_axiom_bundle_passes_without_axiom_record(tmp_path):
    """Live-walkthrough finding: a theorem using no axioms needs no approval
    record — check 6 passes vacuously."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    ei = store.write_ei("c1", {"claim": {"canonical_text": "x"}, "review": {"decision": "APPROVED"}}, status="accepted")
    formal = store.write_formal("c1", {"statement_text": "theorem t : True", "target_theorem": "t",
                                       "imports": [], "gaps": []}, status="current")
    verification = _verified_verification()
    verification["axiom_list"] = []  # zero axioms
    bundle_id, _ = build_bundle(
        store=store, claim=claim, ei_artifact=ei, formal_artifact=formal, proof_source="theorem t : True := by trivial",
        verification=verification,
        approval_record={"decision": "APPROVED", "event_ref": "evt-approve"},
        axiom_record=None,  # no approval needed
        trace_refs=["claim:c1"], capability_snapshots={"lean_workspace": "HEALTHY"},
        workspace_root=WORKSPACE, commands=["a3 verify --claim-id c1"],
    )
    checks = validate_bundle(store, bundle_id, claim)
    assert dict((c[0], c[1]) for c in checks)["6_axiom_audit"] is True
    assert bundle_result(checks) == "VERIFIED"


# ---------------------------------------------------------------------------
# P4 D2: Core pin (workspace_identity.core_revision + dependency_audit.core_imports)
# (a3-core-design.md §1.4; data-flow-model.md §5; IMPLEMENTATION_PLAN.md §5)
# ---------------------------------------------------------------------------


def _build_with_core(tmp_path) -> tuple[ArtifactStore, ClaimRecord, str]:
    """Happy-path bundle whose formal statement AND proof import Core."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    ei = store.write_ei("c1", {"claim": {"canonical_text": "x"}, "review": {"decision": "APPROVED"}}, status="accepted")
    formal = store.write_formal("c1", {"statement_text": "theorem t : True", "target_theorem": "t",
                                       "imports": ["LeanEcon.Core.Constraints"], "gaps": []}, status="current")
    proof = "import LeanEcon.Core.Constraints\n\ntheorem t : True := by trivial"
    verification = _verified_verification()
    bundle_id, _ = build_bundle(
        store=store, claim=claim, ei_artifact=ei, formal_artifact=formal, proof_source=proof,
        verification=verification,
        approval_record={"decision": "APPROVED", "event_ref": "evt-approve"},
        axiom_record={"approved_axioms": STD_AXIOMS},
        trace_refs=["claim:c1", "run:1"], capability_snapshots={"lean_workspace": "HEALTHY"},
        workspace_root=WORKSPACE, commands=["a3 verify --claim-id c1 --proof f"],
    )
    return store, claim, bundle_id


def test_manifest_records_core_revision_and_imports(tmp_path):
    """D2: dependency_audit.core_imports present; workspace_identity.core_revision
    is the digest of the merged Core tree (real workspace, P2 batch)."""
    store, _, bundle_id = _build_with_core(tmp_path)
    manifest = store.read_bundle_manifest(bundle_id)
    assert manifest["dependency_audit"]["core_imports"] == ["LeanEcon.Core.Constraints"]
    core_rev = manifest["workspace_identity"]["core_revision"]
    assert core_rev, "Core tree exists in the pinned workspace; the pin must be recorded"
    assert len(core_rev) == 64  # sha256


def test_core_imports_with_pin_pass_check_12(tmp_path):
    store, claim, bundle_id = _build_with_core(tmp_path)
    checks = validate_bundle(store, bundle_id, claim)
    by_name = dict((c[0], c[1]) for c in checks)
    assert by_name["12_core_pin"] is True
    assert bundle_result(checks) == "VERIFIED"


def test_core_imports_without_pin_fail_check_12(tmp_path):
    store, claim, bundle_id = _build_with_core(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    import json

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    del manifest["workspace_identity"]["core_revision"]
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    by_name = dict((c[0], c[1]) for c in checks)
    assert by_name["12_core_pin"] is False
    assert bundle_result(checks) == "INVALID"


def test_stale_core_pin_fails_check_12(tmp_path):
    """data-flow-model.md §8: a recorded pin that no longer matches the
    workspace tree digest rejects the bundle (stale-pin detection)."""
    store, claim, bundle_id = _build_with_core(tmp_path)
    bundle_dir = store.bundle_path(bundle_id)
    import json

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["workspace_identity"]["core_revision"] = "deadbeef" * 8
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    checks = validate_bundle(store, bundle_id, claim)
    by_name = dict((c[0], c[1]) for c in checks)
    assert by_name["12_core_pin"] is False
    detail = dict((c[0], c[2]) for c in checks)["12_core_pin"]
    assert "stale" in detail


def test_no_core_imports_needs_no_pin(tmp_path):
    """Pre-Core claims (c1–c4, fwt1 shape): no Core imports -> check 12 vacuous."""
    store, claim, bundle_id = _build_happy(tmp_path)
    manifest = store.read_bundle_manifest(bundle_id)
    assert manifest["dependency_audit"]["core_imports"] == []
    checks = validate_bundle(store, bundle_id, claim)
    by_name = dict((c[0], c[1]) for c in checks)
    assert by_name["12_core_pin"] is True
    assert bundle_result(checks) == "VERIFIED"


def test_core_import_from_proof_only_is_recorded(tmp_path):
    """The kernel compiles the PROOF input; a Core import there must be
    recorded even when the formal statement imports none."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    ei = store.write_ei("c1", {"claim": {"canonical_text": "x"}, "review": {"decision": "APPROVED"}}, status="accepted")
    formal = store.write_formal("c1", {"statement_text": "theorem t : True", "target_theorem": "t",
                                       "imports": ["Mathlib.Data.Real.Basic"], "gaps": []}, status="current")
    proof = "import LeanEcon.Core.Primitives\n\ntheorem t : True := by trivial"
    bundle_id, _ = build_bundle(
        store=store, claim=claim, ei_artifact=ei, formal_artifact=formal, proof_source=proof,
        verification=_verified_verification(),
        approval_record={"decision": "APPROVED", "event_ref": "evt-approve"},
        axiom_record={"approved_axioms": STD_AXIOMS},
        trace_refs=["claim:c1"], capability_snapshots={"lean_workspace": "HEALTHY"},
        workspace_root=WORKSPACE, commands=["a3 verify --claim-id c1"],
    )
    manifest = store.read_bundle_manifest(bundle_id)
    assert manifest["dependency_audit"]["core_imports"] == ["LeanEcon.Core.Primitives"]
    checks = validate_bundle(store, bundle_id, claim)
    assert dict((c[0], c[1]) for c in checks)["12_core_pin"] is True
