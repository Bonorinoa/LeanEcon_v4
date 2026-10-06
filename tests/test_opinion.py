"""v4 slice 1 — consultative opinion side-door (DL 51/D3; DECISION_LOG 55).

Deterministic tests only (provider_calls=0): the provider adapter is the
conftest FakeAdapter with ``_make_adapter`` monkeypatched at module scope,
mirroring the ``_fast_probe`` pattern in test_a3_runner.py. Assertions
cover the DoD: consultative-only powers (no lifecycle transition), schema
+ provenance, machine-block determinism, P1-P6 labels, pedagogical mode
(D5), and the failure paths (UNAVAILABLE / PROVIDER_INVALID_OUTPUT).
"""

from __future__ import annotations

import json

import pytest

from leanecon import a3_runner
from leanecon.adapters.openrouter import MVP_MODEL_MAP
from leanecon.claim_store import ArtifactStore, ClaimRecord
from leanecon.events import EVENT_OPINION_EMITTED, EVENT_OPINION_FAILED, EVENT_OPINION_REQUESTED
from leanecon.opinion import (
    MODE_CONSULTATIVE,
    MODE_PEDAGOGICAL,
    machine_block,
    parse_opinion_response,
    validate_opinion_artifact,
)
from leanecon.providers import Capability, ProviderFailureKind
from tests.conftest import FakeAdapter, complete_mapping_report, formalize_output, valid_ei

C1_THEOREM = "budgetExpansionPreservesAttainable"


@pytest.fixture(autouse=True)
def _fast_probe(monkeypatch):
    """Deterministic compile probe: always compiles (fixture scoring)."""

    def fake_probe(*args, **kwargs):
        return {"compiles": True, "exit_code": 0, "stderr_tail": ""}

    monkeypatch.setattr(a3_runner, "probe_statement_compiles", fake_probe)
    return fake_probe


@pytest.fixture
def fake_adapter(monkeypatch):
    """Route cmd_opinion's provider construction to a FakeAdapter."""

    def _install(**kwargs):
        adapter = FakeAdapter(**kwargs)
        monkeypatch.setattr(a3_runner, "_make_adapter", lambda run_id, log: adapter)
        return adapter

    return _install


def _args(tmp_path, **kwargs) -> object:
    from types import SimpleNamespace

    base = {
        "store": str(tmp_path),
        "events_dir": str(tmp_path / "events"),
        "claim_id": "c1",
        "surface": "formal",
        "pedagogical": False,
        "reviewer": "student-alice",
        "notes": "",
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def _seed_formalized(
    tmp_path,
    claim_id: str = "c1",
    statement: str = "theorem budgetExpansionPreservesAttainable : True",
) -> tuple[ArtifactStore, ClaimRecord]:
    """Drive a claim through interpret-free ACCEPTED + live formalize."""
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(
        claim_id=claim_id,
        revision=1,
        source_text=(
            "If a consumer's feasible budget set expands while preferences "
            "remain unchanged, the consumer's attainable set does not shrink."
        ),
        data_class="PROJECT",
    )
    store.save_claim(claim)
    ei = valid_ei(claim_text=claim.source_text)
    store.write_ei(claim_id, ei, status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs(claim_id)[-1]
    store.save_claim(claim)

    run_id, log = a3_runner._new_run(tmp_path / "events")
    adapter = FakeAdapter(formalize_factory=lambda: formalize_output(statement, C1_THEOREM))
    state, _ = a3_runner.formalize_claim(claim, store, log, run_id, adapter, a3_runner.WORKSPACE)
    assert state == "FORMALIZED"
    claim.state = state
    claim.formal_rev = store.formal_revs(claim_id)[-1]
    store.save_claim(claim)
    return store, claim


def _read_events(tmp_path) -> list[dict]:
    records = []
    for p in (tmp_path / "events").glob("*.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def _snapshot_counts(store: ArtifactStore, claim_id: str) -> tuple[int, int, int]:
    return (
        len(store.ei_revs(claim_id)),
        len(store.formal_revs(claim_id)),
        len(store.list_review_records(claim_id)),
    )


# -- refusal and no-state-transition guarantees ----------------------------


def test_opinion_refuses_without_formalization(tmp_path):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id="c-nf", revision=1, source_text="x", data_class="PROJECT")
    store.save_claim(claim)
    with pytest.raises(SystemExit, match="no formalization"):
        a3_runner.cmd_opinion(_args(tmp_path, claim_id="c-nf"), store)


def test_opinion_never_transitions_lifecycle(tmp_path, fake_adapter):
    fake_adapter()
    store, claim = _seed_formalized(tmp_path)
    before = (claim.state,) + _snapshot_counts(store, "c1")
    assert a3_runner.cmd_opinion(_args(tmp_path), store) == 0
    claim_after = store.load_claim("c1")
    after = (claim_after.state,) + _snapshot_counts(store, "c1")
    assert after == before, "opinion must not change state or write EI/formal/review records"
    assert store.opinion_revs("c1") == [1]


# -- happy path: artifact shape + events + anchors --------------------------


def test_opinion_consultative_artifact_shape(tmp_path, fake_adapter):
    fake_adapter()
    store, _ = _seed_formalized(tmp_path)
    assert a3_runner.cmd_opinion(_args(tmp_path, reviewer="student-alice", notes="q1"), store) == 0

    artifact = store.read_opinion("c1", 1)
    assert validate_opinion_artifact(artifact) == []
    assert artifact["mode"] == MODE_CONSULTATIVE
    assert artifact["surface"] == "formal"
    assert artifact["actor"] == "student-alice"
    assert artifact["notes"] == "q1"
    assert artifact["pedagogical"] is None
    prov = artifact["provenance"]
    assert prov["kind"] == "consultative_opinion"
    assert prov["capability"] == "opinion"
    assert prov["model"] == MVP_MODEL_MAP[Capability.OPINION].model
    anchor = artifact["artifact_anchor"]
    formal = store.read_formal("c1", 1)
    ei = store.read_ei("c1", 1)
    assert anchor["formal_digest"] == formal["digest"]
    assert anchor["ei_digest"] == ei["digest"]
    assert artifact["assessment"]["summary"]
    assert isinstance(artifact["assessment"]["strengths"], list)

    events = _read_events(tmp_path)
    kinds = [e["event_type"] for e in events]
    assert EVENT_OPINION_REQUESTED in kinds
    assert EVENT_OPINION_EMITTED in kinds
    emitted = next(e for e in events if e["event_type"] == EVENT_OPINION_EMITTED)
    assert emitted["detail"]["opinion_id"] == artifact["opinion_id"]
    # opinion events are audit events: they must never carry state fields
    for e in events:
        if e["event_type"] in (EVENT_OPINION_REQUESTED, EVENT_OPINION_EMITTED):
            assert e.get("state_before") is None and e.get("state_after") is None


def test_opinion_pedagogical_mode(tmp_path, fake_adapter):
    fake_adapter()
    store, _ = _seed_formalized(tmp_path)
    args = _args(tmp_path, pedagogical=True)
    assert a3_runner.cmd_opinion(args, store) == 0
    artifact = store.read_opinion("c1", 1)
    assert artifact["mode"] == MODE_PEDAGOGICAL
    assert validate_opinion_artifact(artifact) == []
    ped = artifact["pedagogical"]
    assert isinstance(ped, dict)
    assert ped["learner_explanation"]
    assert isinstance(ped["what_to_try_next"], list) and ped["what_to_try_next"]


def test_opinion_records_model_capability_request(tmp_path, fake_adapter):
    adapter = fake_adapter()
    store, _ = _seed_formalized(tmp_path)
    a3_runner.cmd_opinion(_args(tmp_path), store)
    seen = [r for r in adapter.requests_seen if r["capability"] is Capability.OPINION]
    assert len(seen) == 1
    assert seen[0]["model"] == MVP_MODEL_MAP[Capability.OPINION].model
    # D1: opinion rides the interpret/triage pin. After DL 57 the
    # FORMALIZE *slot* remains distinct even though the live slug is
    # currently the same free router.
    assert MVP_MODEL_MAP[Capability.OPINION].model == MVP_MODEL_MAP[Capability.INTERPRET].model
    assert Capability.FORMALIZE in MVP_MODEL_MAP


# -- machine block: determinism + P1-P6 labeling ---------------------------


def test_opinion_machine_block_deterministic_across_runs(tmp_path, fake_adapter):
    fake_adapter()
    store, _ = _seed_formalized(tmp_path)
    a3_runner.cmd_opinion(_args(tmp_path), store)
    a3_runner.cmd_opinion(_args(tmp_path), store)
    first = store.read_opinion("c1", 1)["machine_block"]
    second = store.read_opinion("c1", 2)["machine_block"]
    assert first == second, "machine block must be identical for the same artifact revision"
    assert first["deterministic"] is True


def test_opinion_machine_block_probe_failure_labels(tmp_path):
    """Direct-seed a formal artifact whose probe failed (P2 violation)."""
    store = ArtifactStore(tmp_path)
    claim_id = "c-p2"
    claim = ClaimRecord(claim_id=claim_id, revision=1, source_text="x", data_class="PROJECT")
    store.save_claim(claim)
    ei = valid_ei()
    store.write_ei(claim_id, ei, status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs(claim_id)[-1]
    store.save_claim(claim)

    report = complete_mapping_report()
    gaps = [
        {"ei_element_id": "consumer", "ei_element_kind": "object", "reason": "missing mapping row"}
    ]
    from leanecon.formalization import classify_gaps

    classified = classify_gaps(gaps, report)
    stored_ei = store.read_ei(claim_id, 1)
    candidate = {
        "statement_text": "theorem bad_binder [Set Alpha] : True",
        "target_theorem": "bad_binder",
        "mapping_report": report,
        "imports": [],
        "interpretation_digest": stored_ei["digest"],
        "gaps": classified,
        "statement_probe": {
            "compiles": False,
            "exit_code": 1,
            "stderr_tail": "invalid binder annotation [Set Alpha] (unexpected token at line 3)",
        },
        "vacuity_warning": None,
        "revision_attempts": 3,
        "revision_history": [
            {
                "draft": "theorem x : False",
                "static_problems": ["sorry not allowed"],
                "probe_compiles": None,
                "probe_stderr": "",
            },
            {
                "draft": "theorem bad_binder [Set Alpha] : True",
                "static_problems": [],
                "probe_compiles": False,
                "probe_stderr": "invalid binder annotation [Set Alpha]",
            },
        ],
        "provenance": {"capability": "formalize", "model": "test", "request_id": "r"},
    }
    formal = store.write_formal(claim_id, candidate, status="current")
    claim.formal_rev = formal["revision"]
    store.save_claim(claim)

    block = machine_block(formal, ei)
    props = block["properties"]
    assert props["P2_elaboration"]["compiles"] is False
    assert props["P2_elaboration"]["probe_failure_class"] == "binder_annotation"
    assert block["repair_diagnosis"] is not None
    assert "binder" in block["repair_diagnosis"]
    assert props["P1_surface_legality"]["clean"] is True
    assert props["P1_surface_legality"]["earlier_violations"] == ["sorry not allowed"]
    assert props["P3_contract"]["genuinely_missing"] == ["consumer"]
    assert props["P4_substance"]["vacuity_or_inversion"] is False
    assert block["attempts"]["attempts_to_valid"] == 2
    assert block["attempts"]["probe_failed_attempts"] == 1
    assert props["P5_semantic_fidelity"].startswith("reviewer-owned")
    assert props["P6_proof_adequacy"].startswith("verify-stage")

    # machine-block identity is deterministic on the artifact alone
    again = machine_block(store.read_formal(claim_id, 1), ei)
    assert block == again


# -- failure paths ----------------------------------------------------------


def test_opinion_provider_unavailable(tmp_path, fake_adapter):
    fake_adapter(opinion_failure=ProviderFailureKind.UNAVAILABLE)
    store, _ = _seed_formalized(tmp_path)
    assert a3_runner.cmd_opinion(_args(tmp_path), store) == 1
    assert store.opinion_revs("c1") == []
    events = _read_events(tmp_path)
    failed = [e for e in events if e["event_type"] == EVENT_OPINION_FAILED]
    assert len(failed) == 1
    assert failed[0]["reason_codes"] == ["PROVIDER_UNAVAILABLE"]
    assert store.load_claim("c1").state == "FORMALIZED"


def test_opinion_invalid_model_output(tmp_path, fake_adapter):
    fake_adapter(opinion_factory=lambda mode: {"bogus": True})
    store, _ = _seed_formalized(tmp_path)
    assert a3_runner.cmd_opinion(_args(tmp_path), store) == 1
    assert store.opinion_revs("c1") == []
    events = _read_events(tmp_path)
    failed = [e for e in events if e["event_type"] == EVENT_OPINION_FAILED]
    assert failed and failed[-1]["reason_codes"] == ["PROVIDER_INVALID_OUTPUT"]


# -- parse + schema guards --------------------------------------------------


def test_parse_opinion_rejects_reserved_verdict_keys():
    payload = {
        "assessment": {
            "summary": "s",
            "strengths": [],
            "concerns": [],
            "suggestions": [],
        },
        "pedagogical": None,
        "decision": "ACCEPTED",
    }
    with pytest.raises(ValueError, match="reserved outcome key"):
        parse_opinion_response(json.dumps(payload), MODE_CONSULTATIVE)


def test_parse_opinion_mode_mismatch_rejected():
    consultative = {
        "assessment": {"summary": "s", "strengths": [], "concerns": [], "suggestions": []},
        "pedagogical": None,
    }
    with pytest.raises(ValueError, match="pedagogical object"):
        parse_opinion_response(json.dumps(consultative), MODE_PEDAGOGICAL)
    ped = dict(consultative)
    ped["pedagogical"] = {"learner_explanation": "e", "what_to_try_next": []}
    with pytest.raises(ValueError, match="pedagogical object"):
        parse_opinion_response(json.dumps(ped), MODE_CONSULTATIVE)


def test_validate_opinion_artifact_guards(tmp_path, fake_adapter):
    fake_adapter()
    store, _ = _seed_formalized(tmp_path)
    a3_runner.cmd_opinion(_args(tmp_path), store)
    artifact = store.read_opinion("c1", 1)
    assert validate_opinion_artifact(artifact) == []

    tainted = dict(artifact)
    tainted["decision"] = "ACCEPTED"
    assert any("reserved outcome key" in p for p in validate_opinion_artifact(tainted))

    tainted = dict(artifact)
    tainted["provenance"] = dict(artifact["provenance"])
    tainted["provenance"]["kind"] = "approval"
    assert any("consultative_opinion" in p for p in validate_opinion_artifact(tainted))

    tainted = dict(artifact)
    tainted["machine_block"] = dict(artifact["machine_block"])
    tainted["machine_block"]["deterministic"] = False
    assert any("deterministic" in p for p in validate_opinion_artifact(tainted))

    tainted = dict(artifact)
    tainted["artifact_anchor"] = dict(artifact["artifact_anchor"])
    del tainted["artifact_anchor"]["formal_digest"]
    assert any("formal_digest" in p for p in validate_opinion_artifact(tainted))
