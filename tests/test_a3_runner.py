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
    WORKSPACE,
    complete_mapping_report,
    elan_on_path,  # noqa: F401
    formalize_output,
    valid_ei,
)
from tests.test_verifier import requires_workspace

C1_THEOREM = "leanecon_c1_attainable_monotone"


@pytest.fixture(autouse=True)
def _fast_probe(monkeypatch):
    """Keep mocked formalize runs fast and CI-deterministic: the statement
    compile probe is a real `lake env lean` call; unit tests don't need it.
    The probe itself has a dedicated real-workspace test in test_verifier.py."""
    monkeypatch.setattr(
        a3_runner, "probe_statement_compiles",
        lambda *a, **k: {"compiles": True, "exit_code": 0, "stderr_tail": ""},
    )
    yield


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
    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-gap")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate is not None and candidate["gaps"]
    assert candidate["gaps"][0]["classification"] == "unmapped_with_note"

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
    state, candidate = a3_runner.formalize_claim(claim, store, log2, run_id2, adapter2, WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c1")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate is not None and not candidate["gaps"]

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


def test_formalize_rejects_statement_with_sorry(tmp_path):
    """Walkthrough hardening: a formalizer statement carrying sorry/admit or
    an attached proof body is a hard contract violation — FAILED with
    PROVIDER_INVALID_OUTPUT, and NO formal artifact is written."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-sorry", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-sorry", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-sorry")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    def factory():
        return formalize_output(f"theorem {C1_THEOREM} : True := by sorry", C1_THEOREM)

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id,
                                                 FakeAdapter(formalize_factory=factory), WORKSPACE)
    assert state == "FAILED"
    assert candidate is None
    assert store.formal_revs("c-sorry") == []
    records = [json.loads(l) for p in (tmp_path / "events").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("reason_codes") == ["PROVIDER_INVALID_OUTPUT"] and
               "statement_problems" in r.get("detail", {}) for r in records)


def test_formalize_requires_force_for_reformulation(tmp_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-f", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-f", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-f")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    adapter = FakeAdapter(formalize_factory=lambda: formalize_output(f"theorem t1 : True", "t1"))
    state, _ = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-f")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    revs_before = len(store.formal_revs("c-f"))

    # without --force the CLI refuses
    with pytest.raises(SystemExit, match="use --force"):
        a3_runner.cmd_formalize(_args(tmp_path, claim_id="c-f", force=False), store)

    # with --force a NEW formal revision supersedes (FORMALIZED -> FORMALIZED)
    run_id2, log2 = a3_runner._new_run(events_dir)
    state2, candidate2 = a3_runner.formalize_claim(claim, store, log2, run_id2,
                                                   FakeAdapter(formalize_factory=lambda: formalize_output("theorem t2 : True", "t2")),
                                                   WORKSPACE)
    claim.state = state2
    claim.formal_rev = store.formal_revs("c-f")[-1]
    store.save_claim(claim)
    assert state2 == "FORMALIZED"
    assert len(store.formal_revs("c-f")) == revs_before + 1
    assert candidate2 is not None and candidate2["target_theorem"] == "t2"
    formal = store.read_formal("c-f", store.formal_revs("c-f")[-1])
    assert formal["target_theorem"] == "t2"


def test_formalize_rejection_keeps_previous_rev(tmp_path):
    """Walkthrough finding: a rejected candidate (PROVIDER_INVALID_OUTPUT)
    writes NO artifact — the claim goes FAILED, cmd_formalize must not crash
    on the empty revision list, and the previous formal_rev is preserved."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-keep", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-keep", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-keep")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    # a first successful formalization establishes a formal_rev
    state, _ = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output("theorem t1 : True", "t1")), WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-keep")[-1]
    store.save_claim(claim)
    assert claim.formal_rev is not None

    # the second attempt is rejected -> FAILED, previous rev kept
    state, candidate = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output("theorem t2 : True := by sorry", "t2")),
        WORKSPACE)
    claim.state = state
    store.save_claim(claim)
    assert state == "FAILED"
    assert candidate is None
    assert claim.formal_rev is not None  # previous reference intact
    assert len(store.formal_revs("c-keep")) == 1  # no new artifact


def test_formalize_retry_from_failed(tmp_path):
    """A claim FAILED by a rejected candidate can retry formalization
    (FAILED -> FORMALIZED lifecycle edge)."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-retry", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-retry", valid_ei(), status="accepted")
    claim.state = "FAILED"
    claim.accepted_ei_rev = store.ei_revs("c-retry")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    state, candidate = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output("theorem t3 : True", "t3")), WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-retry")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate is not None and candidate["target_theorem"] == "t3"


def test_formalize_probe_and_vacuity_recorded(tmp_path, monkeypatch):
    """The compile probe and vacuity warning are evaluation signals recorded
    in the formal artifact (and surfaced by cmd_formalize)."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-pv", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-pv", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-pv")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    # vacuous statement: conclusion restates a hypothesis
    statement = f"theorem {C1_THEOREM} (h : P) : P"
    monkeypatch.setattr(a3_runner, "probe_statement_compiles",
                        lambda *a, **k: {"compiles": False, "exit_code": 1, "stderr_tail": "boom"})
    state, candidate = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output(statement, C1_THEOREM)), WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-pv")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate is not None
    assert candidate["statement_probe"]["compiles"] is False
    assert "vacuity" in (candidate["vacuity_warning"] or "").lower()
    formal = store.read_formal("c-pv", store.formal_revs("c-pv")[-1])
    assert formal["statement_probe"]["compiles"] is False
    assert formal["vacuity_warning"]


# ---------------------------------------------------------------------------
# P4 D4: namespace-scoped A3-local scaffolding (end-to-end, mocked provider)
# ---------------------------------------------------------------------------


def test_formalize_rejects_root_namespace_scaffolding(tmp_path):
    """A candidate whose A3-local scaffolding sits at the root namespace is
    rejected pre-store (PROVIDER_INVALID_OUTPUT) — the fwt1 'abbrev Bundle'
    confound removed EARLIER (D4)."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-d4", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-d4", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-d4")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    statement = "abbrev Bundle := ℝ\n\ntheorem t : True"
    state, candidate = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output(statement, "t")), WORKSPACE)
    claim.state = state
    store.save_claim(claim)
    assert state == "FAILED"
    assert candidate is None
    assert len(store.formal_revs("c-d4")) == 0  # no artifact pollution
    records = [json.loads(l) for p in (tmp_path / "events").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("reason_codes") == ["PROVIDER_INVALID_OUTPUT"] for r in records)


def test_formalize_accepts_namespaced_scaffolding(tmp_path):
    """Scaffolding inside 'namespace A3Scaffolding.<claim>' passes D4 and the
    candidate reaches the store as FORMALIZED."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-d4ok", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei("c-d4ok", valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs("c-d4ok")[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    statement = (
        "namespace A3Scaffolding.c1\n"
        "abbrev Bundle := ℝ\n"
        "end A3Scaffolding.c1\n"
        "\n"
        "theorem t : True"
    )
    state, candidate = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output(statement, "t")), WORKSPACE)
    claim.state = state
    claim.formal_rev = store.formal_revs("c-d4ok")[-1]
    store.save_claim(claim)
    assert state == "FORMALIZED"
    assert candidate is not None and candidate["target_theorem"] == "t"
    assert len(store.formal_revs("c-d4ok")) == 1
