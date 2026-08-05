"""Event envelope contract tests (docs/gate3/02)."""

import json

import pytest

from leanecon.events import (
    EVENT_CLAIM_STATE_CHANGED,
    EVENT_HEALTH_CHECK,
    Event,
    EventLog,
    REASON_CODES,
    CapabilityStatus,
    validate_event,
)


def test_envelope_has_all_required_fields():
    event = Event(
        event_type=EVENT_CLAIM_STATE_CHANGED,
        run_id="run-1",
        claim_id="claim-1",
        source_component="interpreter",
        actor="system",
        state_before="INTERPRETED",
        state_after="REVIEW_REQUIRED",
        payload_class="PROJECT",
        trace_ref="trace-1",
    )
    record = event.to_dict()
    for field in (
        "schema_version",
        "event_id",
        "event_type",
        "run_id",
        "claim_id",
        "emitted_at",
        "source_component",
        "actor",
        "state_before",
        "state_after",
        "reason_codes",
        "payload_class",
        "trace_ref",
    ):
        assert field in record, field


def test_claim_id_nullable_only_for_health_checks():
    health = Event(
        event_type=EVENT_HEALTH_CHECK,
        run_id="run-2",
        source_component="a1-runner",
        actor="system",
        payload_class="PROJECT",
        trace_ref="trace-2",
    )
    assert validate_event(health.to_dict()) == []
    claim_event = Event(
        event_type=EVENT_CLAIM_STATE_CHANGED,
        run_id="run-3",
        claim_id=None,
        source_component="interpreter",
        actor="system",
        payload_class="PROJECT",
        trace_ref="trace-3",
    )
    problems = validate_event(claim_event.to_dict())
    assert any("claim_id" in p for p in problems)


def test_unknown_reason_code_rejected():
    event = Event(
        event_type=EVENT_HEALTH_CHECK,
        run_id="run-4",
        source_component="a1-runner",
        actor="system",
        payload_class="PROJECT",
        trace_ref="trace-4",
        reason_codes=("NOT_A_REAL_CODE",),
    )
    problems = validate_event(event.to_dict())
    assert any("unknown reason code" in p for p in problems)


def test_registered_reason_codes_match_gate3_registry():
    expected = {
        "SEMANTIC_AMBIGUITY",
        "USER_REJECTED",
        "LEAN_SYNTAX_ERROR",
        "SORRY_FOUND",
        "AXIOM_VIOLATION",
        "PROOF_TIMEOUT",
        "PROVIDER_UNAVAILABLE",
        "PROVIDER_INVALID_OUTPUT",
        "INPUT_REJECTED",
        "WORKSPACE_UNPINNED",
        "LSP_UNAVAILABLE",
        "RESTRICTED_BLOCKED",
    }
    assert set(REASON_CODES) == expected


def test_event_log_is_append_only_and_validating(tmp_path):
    log = EventLog(tmp_path / "trace.jsonl")
    event = Event(
        event_type=EVENT_HEALTH_CHECK,
        run_id="run-5",
        source_component="a1-runner",
        actor="system",
        payload_class="PROJECT",
        trace_ref="trace-5",
    )
    log.append(event)
    log.append(event)
    records = log.read_all()
    assert len(records) == 2
    assert all(json.loads(json.dumps(r)) == r for r in records)
    bad = Event(
        event_type=EVENT_HEALTH_CHECK,
        run_id="run-6",
        source_component="a1-runner",
        actor="system",
        payload_class="PROJECT",
        trace_ref="trace-6",
        reason_codes=("BOGUS",),
    )
    with pytest.raises(ValueError):
        log.append(bad)
    assert len(log.read_all()) == 2  # invalid event never appended


def test_capability_status_vocabulary_is_s3a():
    assert {s.value for s in CapabilityStatus} == {"HEALTHY", "DEGRADED", "UNAVAILABLE"}
