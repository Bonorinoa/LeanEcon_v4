"""Trace replay tests (docs/gate5/a3-design.md §7.5).

Replay is deterministic validation: envelope checks + state-chain re-walk +
bundle re-validation, with no provider calls and no Lean rebuild.
"""

import json
from pathlib import Path

from leanecon import a3_runner
from leanecon.claim_store import ArtifactStore, ClaimRecord
from leanecon.events import EVENT_CLAIM_STATE_CHANGED, Event, EventLog
from leanecon.trace_replay import replay_claim, replay_run


def _event_log(tmp_path, events: list[Event], name="run-x.jsonl") -> Path:
    log = EventLog(tmp_path / name)
    for event in events:
        log.append(event)
    return log.path


def test_replay_run_valid_chain(tmp_path):
    path = _event_log(
        tmp_path,
        [
            Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-x", claim_id="c1",
                  state_before=None, state_after="DRAFT", source_component="a3-ingest",
                  actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
            Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-x", claim_id="c1",
                  state_before="DRAFT", state_after="INTERPRETED", source_component="a3-interpret",
                  actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
            Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-x", claim_id="c1",
                  state_before="INTERPRETED", state_after="REVIEW_REQUIRED", source_component="a3-validate",
                  actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
        ],
    )
    report = replay_run(path)
    assert report["replay_ok"], report["problems"]
    assert report["claims"]["c1"]["states"][-1]["to"] == "REVIEW_REQUIRED"


def test_replay_run_rejects_illegal_transition(tmp_path):
    path = _event_log(
        tmp_path,
        [
            Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-bad", claim_id="c1",
                  state_before=None, state_after="DRAFT", source_component="a3-ingest",
                  actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
            Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-bad", claim_id="c1",
                  state_before="DRAFT", state_after="ACCEPTED", source_component="a3-interpret",
                  actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
        ],
    )
    report = replay_run(path)
    assert not report["replay_ok"]
    assert any("transition not allowed" in p for p in report["problems"])


def test_replay_run_rejects_bad_envelope(tmp_path):
    # EventLog refuses invalid events at append time, so write the bad line
    # directly to simulate a corrupted/hand-edited log.
    path = tmp_path / "run-bad.jsonl"
    path.write_text(
        '{"schema_version":"1.0.0","event_id":"evt-bad","event_type":"BOGUS_TYPE",'
        '"run_id":"run-bad","emitted_at":"2026-08-06T00:00:00Z","source_component":"x",'
        '"actor":"system","reason_codes":["NOT_A_CODE"],"payload_class":"PROJECT",'
        '"trace_ref":"t"}\n',
        encoding="utf-8",
    )
    report = replay_run(path)
    assert not report["replay_ok"]
    assert any("envelope" in p for p in report["problems"])


def test_replay_claim_spans_runs(tmp_path):
    for name, state in (("a.jsonl", "DRAFT"), ("b.jsonl", "REVIEW_REQUIRED")):
        _event_log(
            tmp_path,
            [
                Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id=f"run-{name}", claim_id="c1",
                      state_before=None if state == "DRAFT" else "INTERPRETED",
                      state_after=state, source_component="a3-ingest" if state == "DRAFT" else "a3-validate",
                      actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
            ],
            name=name,
        )
    report = replay_claim(tmp_path, "c1")
    assert report["replay_ok"], report["problems"]
    assert report["claims"]["states"][-1]["to"] == "REVIEW_REQUIRED"


def test_replay_with_store_validates_bundles(tmp_path):
    # full mocked walkthrough produces a real bundle; replay must re-validate it
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c1", revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter, valid_ei

    ei = store.write_ei("c1", valid_ei(), status="draft")
    from leanecon.interpretation import finalize_ei

    finalized = finalize_ei(ei, reviewer="cto", event_ref="evt-1", acknowledges_none_noted=False)
    accepted = store.write_ei("c1", finalized, status="accepted")
    store.supersede_formals_for("c1", accepted["digest"])
    formal = store.write_formal("c1", {"statement_text": "theorem t : True", "target_theorem": "t",
                                       "gaps": [], "interpretation_digest": accepted["digest"]}, status="current")
    proof = "theorem t : True := by trivial"
    from leanecon.bundle import build_bundle

    bundle_id, _ = build_bundle(
        store=store, claim=claim, ei_artifact=accepted, formal_artifact=formal, proof_source=proof,
        verification={"compile_ok": True, "axiom_list": ["propext"], "static_sorry_ok": True,
                      "exit_code": 0, "timed_out": False, "outcome": "VERIFIED", "elapsed_ms": 1,
                      "stderr_tail": "", "axiom_audit": {}},
        approval_record={"decision": "APPROVED", "event_ref": "evt-1"},
        axiom_record={"approved_axioms": ["propext"]},
        trace_refs=["claim:c1"], capability_snapshots={"lean_workspace": "HEALTHY"},
        workspace_root=Path(__file__).resolve().parents[1] / "lean_workspace",
        commands=["a3 verify --claim-id c1"],
    )
    _event_log(events_dir, [
        Event(event_type=EVENT_CLAIM_STATE_CHANGED, run_id="run-v", claim_id="c1",
              state_before=None, state_after="DRAFT", source_component="a3-ingest",
              actor="system", payload_class="PROJECT", trace_ref="claim:c1"),
        Event(event_type="VERIFICATION_COMPLETED", run_id="run-v", claim_id="c1",
              state_before="PROVING", state_after="VERIFIED", source_component="a3-verify",
              actor="verifier", payload_class="PROJECT", trace_ref=bundle_id, detail={}),
    ], name="run-v.jsonl")
    report = replay_claim(events_dir, "c1", store=store)
    assert report["replay_ok"], report["problems"]
    assert report["bundles"] and report["bundles"][0]["ok"]
