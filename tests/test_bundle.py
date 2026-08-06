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
