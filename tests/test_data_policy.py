"""Outbound data policy tests (docs/gate3/06 and references test matrix).

MVP-thin posture locked at Gate 3: PUBLIC/PROJECT sendable, RESTRICTED
hard-denied, unknown/mixed fail closed, gold/hidden material denied even
inside PROJECT payloads, secrets redacted, denials never contact the
provider and always emit RESTRICTED_BLOCKED.
"""

from leanecon import data_policy
from leanecon.data_policy import (
    PayloadClass,
    classify,
    contains_gold,
    evaluate,
    redact,
)


# --- classification -------------------------------------------------------


def test_explicit_classes_round_trip():
    assert classify("PUBLIC") is PayloadClass.PUBLIC
    assert classify("PROJECT") is PayloadClass.PROJECT
    assert classify("RESTRICTED") is PayloadClass.RESTRICTED
    assert classify("public") is PayloadClass.PUBLIC  # case-insensitive


def test_unknown_and_missing_classes_fail_closed():
    assert classify("TOP_SECRET") is PayloadClass.RESTRICTED
    assert classify(None) is PayloadClass.RESTRICTED
    assert classify("") is PayloadClass.RESTRICTED
    assert classify(42) is PayloadClass.RESTRICTED
    assert classify({"mixed": ["PUBLIC", "RESTRICTED"]}) is PayloadClass.RESTRICTED


# --- authorization --------------------------------------------------------


def test_restricted_denied_without_any_outbound_contact():
    calls = []

    decision = evaluate({"prompt": "sensitive"}, "RESTRICTED")
    assert decision.allowed is False
    assert decision.reason_code == "RESTRICTED_BLOCKED"
    assert decision.content_digest is None  # no digest of raw payload
    assert calls == []


def test_restricted_denied_even_with_fake_approval_metadata():
    # MVP has no opt-in mechanism: approval-looking fields change nothing.
    decision = evaluate(
        {"prompt": "sensitive", "run_approval": {"approver": "someone", "run_id": "run-9"}},
        "RESTRICTED",
    )
    assert decision.allowed is False
    assert decision.reason_code == "RESTRICTED_BLOCKED"


def test_unknown_class_denied_before_provider_contact():
    decision = evaluate({"prompt": "x"}, "WHATEVER")
    assert decision.allowed is False
    assert decision.reason_code == "RESTRICTED_BLOCKED"


# --- evaluation integrity -------------------------------------------------


def test_sealed_gold_denied_even_when_classified_project():
    payload = {"prompt": "interpret this", "sealed_gold": "theorem stub answer"}
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is False
    assert decision.reason_code == "INPUT_REJECTED"
    assert "sealed_gold" in decision.detail


def test_gold_marker_inside_string_value_is_denied():
    """Evaluation integrity: a pasted gold statement in claim TEXT (not a
    structured key) must be denied too (Gate 5 hardening)."""
    payload = {"prompt": "interpret: the sealed_gold theorem stub answer is x"}
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is False
    assert decision.reason_code == "INPUT_REJECTED"
    assert "sealed_gold" in decision.detail


def test_ordinary_prose_does_not_false_positive():
    payload = {"prompt": "the answer is clearly visible to the reviewer"}
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is True


def test_hidden_labels_and_v3_hidden_material_denied():
    for marker in ("hidden_label", "gold_answer", "v3_hidden_eval", "answer_key"):
        decision = evaluate({"prompt": "x", marker: "secret-stuff"}, "PROJECT")
        assert decision.allowed is False, marker
        assert decision.reason_code == "INPUT_REJECTED", marker


def test_nested_gold_marker_found():
    payload = {"prompt": "x", "context": {"deep": {"gold_statement": "..."}}}
    assert contains_gold(payload) == ["gold_statement"]
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is False


# --- redaction --------------------------------------------------------------


def test_secret_fields_removed_before_transmission():
    fake_key = "sk-" + "abcdefghijklmnop" + "1234"
    payload = {
        "prompt": "interpret this claim",
        "api_key": fake_key,
        "Authorization": "Bearer something",
        "nested": {"db_password": "hunter2", "safe": "value"},
    }
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is True
    report_paths = {r["path"] for r in decision.redaction_report}
    assert "api_key" in report_paths
    assert "Authorization" in report_paths
    assert "nested.db_password" in report_paths
    # Redacted content digest must exist and be stable
    assert decision.content_digest is not None
    redacted, _ = redact(payload)
    assert "api_key" not in redacted
    assert "db_password" not in redacted["nested"]
    assert decision.content_digest == data_policy.canonical_digest(redacted)


def test_secret_looking_values_scrubbed_in_strings():
    # Build the fake token dynamically so no credential-shaped literal
    # ever appears in tracked source (keeps CI credential scans clean).
    fake_token = "ghp_" + "A" * 30
    payload = {"prompt": f"use {fake_token} to call"}
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is True
    redacted, report = redact(payload)
    assert redacted["prompt"] == "[REDACTED]"
    assert fake_token not in str(redacted)
    assert any(r["action"] == "value_scrubbed" for r in report)


def test_clean_project_payload_passes_with_digest():
    payload = {"prompt": "If preferences are complete and transitive..."}
    decision = evaluate(payload, "PROJECT")
    assert decision.allowed is True
    assert decision.payload_class is PayloadClass.PROJECT
    assert decision.reason_code is None
    assert decision.content_digest is not None
    assert len(decision.content_digest) == 64  # sha256 hex


def test_public_payload_sendable():
    decision = evaluate({"prompt": "public question"}, "PUBLIC")
    assert decision.allowed is True
    assert decision.payload_class is PayloadClass.PUBLIC
