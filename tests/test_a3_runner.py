"""A3 runner end-to-end tests (docs/gate5/a3-design.md §7, §9).

A complete walkthrough with a mocked provider and the real pinned workspace
verifier: ingest -> interpret -> review -> formalize -> verify (first
attempt FAILED/axiom, reviewer axiom record, retry -> VERIFIED) -> bundle ->
replay. Workspace-dependent steps skip gracefully without Lean.
"""

import json
from argparse import Namespace
from pathlib import Path

import pytest

from leanecon import a3_runner
from leanecon.claim_store import ArtifactStore, ClaimRecord
from leanecon.providers import ProviderFailureKind
from tests.conftest import (
    FIXTURES,
    complete_mapping_report,
    elan_on_path,  # noqa: F401
    formalize_output,
    valid_ei,
)
from tests.test_verifier import requires_workspace

C1_THEOREM = "leanecon_c1_attainable_monotone"


def _args(tmp_path, **kwargs) -> Namespace:
    base = {"events_dir": str(tmp_path / "events")}
    base.update(kwargs)
    return Namespace(**base)


def _walk_to_review(tmp_path, claim_id="c1", ei_factory=None) -> tuple[ArtifactStore, ClaimRecord, Path, dict]:
    from tests.conftest import FakeAdapter

    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id=claim_id, revision=1, source_text="claim c1", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    adapter = FakeAdapter(ei_factory=ei_factory or (lambda: valid_ei()))
    state, ei = a3_runner.interpret_claim(claim, store, log, run_id, adapter)
    claim.state = state
    store.save_claim(claim)
    return store, claim, events_dir, ei


def test_restricted_class_denied_at_ingest(tmp_path):
    store = ArtifactStore(tmp_path)
    rc = a3_runner.cmd_ingest(_args(tmp_path, claim_id="bad", claim_text="x", claim_class="RESTRICTED"), store)
    assert rc == 1
    assert store.list_claims() == []
    events = list((tmp_path / "events").glob("*.jsonl"))
    assert events, "blocked event must be logged"
    records = [json.loads(l) for p in events for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("reason_codes") == ["RESTRICTED_BLOCKED"] for r in records)


def test_gold_marker_in_claim_text_denied_at_ingest(tmp_path):
    store = ArtifactStore(tmp_path)
    rc = a3_runner.cmd_ingest(_args(tmp_path, claim_id="gold", claim_text="the sealed_gold answer is x",
                                    claim_class="PROJECT"), store)
    assert rc == 1
    assert store.list_claims() == []
    records = [json.loads(l) for p in (tmp_path / "events").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("reason_codes") == ["INPUT_REJECTED"] for r in records)


def test_gold_marker_key_in_claim_text_denied(tmp_path):
    store = ArtifactStore(tmp_path)
    rc = a3_runner.cmd_ingest(_args(tmp_path, claim_id="gold2", claim_text="payload has gold_statement field",
                                    claim_class="PROJECT"), store)
    assert rc == 1


def test_interpret_review_none_noted_requires_acknowledgement(tmp_path, elan_on_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    adapter = FakeAdapter(ei_factory=lambda: valid_ei(none_noted=True))
    state, ei = a3_runner.interpret_claim(claim, store, log, run_id, adapter)
    claim.state = state
    store.save_claim(claim)
    assert state == "REVIEW_REQUIRED"

    # approve without acknowledgement must be refused
    rc = a3_runner.cmd_review(_args(tmp_path, claim_id="c1", decision="approve", reviewer="cto",
                                    acknowledge_none_noted=False, notes="", reason=""), store)
    assert rc == 1
    assert store.load_claim("c1").state == "REVIEW_REQUIRED"

    # with acknowledgement the approval lands
    rc = a3_runner.cmd_review(_args(tmp_path, claim_id="c1", decision="approve", reviewer="cto",
                                    acknowledge_none_noted=True, notes="ok", reason=""), store)
    assert rc == 0
    assert store.load_claim("c1").state == "ACCEPTED"
    accepted_rev = store.load_claim("c1").accepted_ei_rev
    assert accepted_rev is not None
    accepted = store.read_ei("c1", accepted_rev)
    assert accepted["review"]["acknowledges_none_noted"] is True


def test_reject_path_is_terminal(tmp_path):
    store, claim, events_dir, ei = _walk_to_review(tmp_path, claim_id="c-rej")
    rc = a3_runner.cmd_review(_args(tmp_path, claim_id="c-rej", decision="reject", reviewer="cto",
                                    acknowledge_none_noted=False, notes="ambiguous",
                                    reason="SEMANTIC_AMBIGUITY"), store)
    assert rc == 0
    assert store.load_claim("c-rej").state == "REJECTED"


def test_mapping_gaps_block_proving(tmp_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-gap", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    ei_artifact = store.write_ei("c-gap", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = ei_artifact["revision"]
    store.save_claim(claim)

    def factory():
        report = complete_mapping_report()
        report[0] = {**report[0], "status": "unmapped", "note": "no identifier"}
        return formalize_output(f"theorem {C1_THEOREM} : True", C1_THEOREM, report)

    adapter = FakeAdapter(formalize_factory=factory)
    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-gap")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate["gaps"]

    # verify must be refused while gaps are unacknowledged
    with pytest.raises(SystemExit):
        a3_runner.cmd_verify(_args(tmp_path, claim_id="c-gap", proof=str(FIXTURES / "c1_attainable.lean"),
                                   timeout=120), store)

    # the FORMALIZED state event must be in the trace even with gaps
    records = [json.loads(l) for p in (tmp_path / "events").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
    formalized_events = [r for r in records if r.get("event_type") == "CLAIM_STATE_CHANGED" and r.get("state_after") == "FORMALIZED"]
    assert formalized_events, "FORMALIZED state event missing from trace when gaps present"
    assert formalized_events[-1]["detail"].get("gap_count") == 1

    # gap acknowledgement then allows verify to start
    rc = a3_runner.cmd_gap_ack(_args(tmp_path, claim_id="c-gap", reviewer="cto", notes="accepted"), store)
    assert rc == 0
    assert store.list_review_records("c-gap", "gap")


@requires_workspace
def test_full_walkthrough_verified_with_axiom_loop(tmp_path, elan_on_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim c1", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    # 1. interpret (none_noted=True to exercise the acknowledgement)
    adapter = FakeAdapter(ei_factory=lambda: valid_ei(none_noted=True))
    state, ei = a3_runner.interpret_claim(claim, store, log, run_id, adapter)
    claim.state = state
    store.save_claim(claim)
    assert state == "REVIEW_REQUIRED"

    # 2. reviewer approves with acknowledgement
    assert a3_runner.cmd_review(_args(tmp_path, claim_id="c1", decision="approve", reviewer="cto",
                                      acknowledge_none_noted=True, notes="ok", reason=""), store) == 0
    claim = store.load_claim("c1")
    assert claim.state == "ACCEPTED"

    # 3. formalize (complete mapping)
    def factory():
        return formalize_output(
            f"theorem {C1_THEOREM} : True", C1_THEOREM, complete_mapping_report()
        )

    run_id2, log2 = a3_runner._new_run(events_dir)
    adapter2 = FakeAdapter(formalize_factory=factory)
    state, candidate = a3_runner.formalize_claim(claim, store, log2, run_id2, adapter2)
    claim.state = state
    claim.formal_rev = store.formal_revs("c1")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert not candidate["gaps"]

    # 4. first verify attempt: no axiom record -> AXIOM_VIOLATION (honest loop)
    proof = str(FIXTURES / "c1_attainable.lean")
    a3_runner.cmd_verify(_args(tmp_path, claim_id="c1", proof=proof, timeout=240), store)
    claim = store.load_claim("c1")
    assert claim.state == "FAILED"
    bundle_id = claim.current_bundle
    assert bundle_id is not None
    verification = json.loads((store.bundle_path(bundle_id) / "verification.json").read_text())
    assert verification["reason_code"] == "AXIOM_VIOLATION"
    used = verification["axiom_list"]
    assert used

    # 5. reviewer approves exactly the axioms the kernel surfaced
    assert a3_runner.cmd_axiom_approve(_args(tmp_path, claim_id="c1", reviewer="cto",
                                             axioms=",".join(used), notes=""), store) == 0

    # 6. retry on the same candidate -> VERIFIED
    a3_runner.cmd_verify(_args(tmp_path, claim_id="c1", proof=proof, timeout=240), store)
    claim = store.load_claim("c1")
    assert claim.state == "VERIFIED"
    assert claim.current_bundle is not None
    assert claim.current_bundle != bundle_id
    checks = a3_runner.validate_bundle(store, claim.current_bundle, claim)
    assert all(ok for _, ok, _ in checks), [c for c in checks if not c[1]]

    # 7. trace replay over the whole walkthrough (spans runs)
    report = a3_runner.replay_claim(events_dir, "c1", store=store)
    assert report["replay_ok"], report["problems"]
    states = [s["to"] for s in report["claims"]["states"] if "to" in s]
    assert states == ["INTERPRETED", "REVIEW_REQUIRED", "ACCEPTED", "FORMALIZED",
                      "PROVING", "FAILED", "PROVING", "VERIFIED"]
    assert any(b["ok"] for b in report["bundles"])

    # 8. status command is readable
    a3_runner.cmd_status(_args(tmp_path, claim_id="c1"), store)


def test_provider_outage_is_blocked(tmp_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-out", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    adapter = FakeAdapter(interpret_failure=ProviderFailureKind.UNAVAILABLE)
    state, ei = a3_runner.interpret_claim(claim, store, log, run_id, adapter)
    claim.state = state
    store.save_claim(claim)
    assert state == "BLOCKED"
    records = [json.loads(l) for p in (tmp_path / "events").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("reason_codes") == ["PROVIDER_UNAVAILABLE"] for r in records)


def test_malformed_interpret_output_is_failed(tmp_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-bad", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    class MalformedAdapter(FakeAdapter):
        def _invoke(self, capability, model, payload, decision, run_id):
            from leanecon.events import CapabilityStatus
            from leanecon.providers import ProviderMetadata, ProviderResponse

            return ProviderResponse(capability=capability, status=CapabilityStatus.HEALTHY,
                                    output={"content": "this is not json"},
                                    metadata=ProviderMetadata(provider="mistral", model=model))

    state, ei = a3_runner.interpret_claim(claim, store, log, run_id, MalformedAdapter())
    claim.state = state
    store.save_claim(claim)
    assert state == "FAILED"
