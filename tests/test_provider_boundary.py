"""Provider contract and Mistral adapter tests (docs/gate3/04).

All provider calls use mocked transports — deterministic failures, no
network. A single controlled live probe exists separately in the A1
runner (never in this suite).
"""

import pytest

from leanecon import data_policy
from leanecon.adapters.mistral import (
    MVP_MODEL_MAP,
    MistralAdapter,
)
from leanecon.events import CapabilityStatus, EVENT_PROVIDER_REQUEST_BLOCKED
from leanecon.providers import (
    Capability,
    ProviderFailure,
    ProviderFailureKind,
)


def _ok_transport(request, api_key, timeout_s):
    return {
        "id": "req-mock-1",
        "choices": [{"message": {"content": '{"ok": true}'}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }


def _adapter(transport=_ok_transport, **kwargs):
    adapter = MistralAdapter(transport=transport, **kwargs)
    adapter._api_key_env = "MISTRAL_TEST_KEY"
    return adapter


# --- capability mapping (configuration, not core contracts) ----------------


def test_mvp_mapping_matches_gate3_decision():
    assert MVP_MODEL_MAP[Capability.INTERPRET].model == "mistral-medium-3-5"
    assert MVP_MODEL_MAP[Capability.FORMALIZE].model == "labs-leanstral-1-5"
    assert MVP_MODEL_MAP[Capability.PROVE_OR_REPAIR].model == "labs-leanstral-1-5"
    assert MVP_MODEL_MAP[Capability.SEMANTIC_TRIAGE].model == "mistral-medium-3-5"
    assert all(m.provider == "mistral" for m in MVP_MODEL_MAP.values())


# --- success path -----------------------------------------------------------


def test_request_round_trip_records_provider_metadata(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    adapter = _adapter()
    response = adapter.request(
        capability=Capability.INTERPRET,
        model="mistral-medium-3-5",
        typed_payload={"prompt": "interpret this micro claim"},
        declared_class="PROJECT",
        run_id="run-10",
    )
    assert response.status is CapabilityStatus.HEALTHY
    assert response.metadata.model == "mistral-medium-3-5"
    assert response.metadata.provider == "mistral"
    assert response.metadata.request_id == "req-mock-1"
    assert response.metadata.latency_ms is not None
    assert response.metadata.token_metadata == {"prompt_tokens": 10, "completion_tokens": 5}


def test_no_silent_fallback_model_is_exactly_the_requested_one(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    seen = {}

    def capture(request, api_key, timeout_s):
        seen["model"] = request["model"]
        return _ok_transport(request, api_key, timeout_s)

    adapter = _adapter(transport=capture)
    adapter.request(
        capability=Capability.FORMALIZE,
        model="labs-leanstral-1-5",
        typed_payload={"prompt": "formalize accepted interpretation"},
        declared_class="PROJECT",
        run_id="run-11",
    )
    assert seen["model"] == "labs-leanstral-1-5"


# --- failure semantics --------------------------------------------------------


def test_outage_produces_typed_provider_unavailable(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")

    def outage(request, api_key, timeout_s):
        raise ProviderFailure(ProviderFailureKind.UNAVAILABLE, "HTTP 503", provider="mistral")

    adapter = _adapter(transport=outage, max_attempts=1)
    with pytest.raises(ProviderFailure) as exc_info:
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "x"},
            declared_class="PROJECT",
            run_id="run-12",
        )
    assert exc_info.value.kind is ProviderFailureKind.UNAVAILABLE
    assert exc_info.value.reason_code == "PROVIDER_UNAVAILABLE"


def test_malformed_output_produces_typed_invalid_output(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")

    def malformed(request, api_key, timeout_s):
        return {"unexpected": "shape"}

    adapter = _adapter(transport=malformed)
    with pytest.raises(ProviderFailure) as exc_info:
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "x"},
            declared_class="PROJECT",
            run_id="run-13",
        )
    assert exc_info.value.kind is ProviderFailureKind.INVALID_OUTPUT
    assert exc_info.value.reason_code == "PROVIDER_INVALID_OUTPUT"


def test_missing_credential_is_typed_unavailable(monkeypatch):
    monkeypatch.delenv("MISTRAL_TEST_KEY", raising=False)
    adapter = _adapter()
    with pytest.raises(ProviderFailure) as exc_info:
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "x"},
            declared_class="PROJECT",
            run_id="run-14",
        )
    assert exc_info.value.kind is ProviderFailureKind.UNAVAILABLE


def test_retry_exhaustion_is_unavailable_not_invalid(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    attempts = {"n": 0}

    def flaky(request, api_key, timeout_s):
        attempts["n"] += 1
        raise ProviderFailure(ProviderFailureKind.UNAVAILABLE, "HTTP 500", provider="mistral")

    adapter = _adapter(transport=flaky, max_attempts=2)
    import leanecon.adapters.mistral as mistral_mod

    monkeypatch.setattr(mistral_mod.time, "sleep", lambda _s: None)
    with pytest.raises(ProviderFailure) as exc_info:
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "x"},
            declared_class="PROJECT",
            run_id="run-15",
        )
    assert exc_info.value.kind is ProviderFailureKind.UNAVAILABLE
    assert attempts["n"] == 2  # bounded retries


# --- boundary enforcement ------------------------------------------------------


def test_denied_request_never_reaches_transport(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    contacted = []

    def spy(request, api_key, timeout_s):
        contacted.append(request)
        return _ok_transport(request, api_key, timeout_s)

    events = []
    adapter = _adapter(transport=spy, emit_event=lambda decision, cap, run_id, claim_id: events.append(
        adapter.emit_blocked_event(decision, cap, run_id, claim_id)
    ))
    with pytest.raises(ProviderFailure):
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "restricted content"},
            declared_class="RESTRICTED",
            run_id="run-16",
        )
    assert contacted == []  # no outbound call on denial
    assert len(events) == 1
    event = events[0]
    assert event.event_type == EVENT_PROVIDER_REQUEST_BLOCKED
    assert event.reason_codes == ("RESTRICTED_BLOCKED",)
    assert event.payload_class == "RESTRICTED"


def test_gold_payload_denied_at_boundary(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    contacted = []

    def spy(request, api_key, timeout_s):
        contacted.append(request)
        return _ok_transport(request, api_key, timeout_s)

    adapter = _adapter(transport=spy)
    with pytest.raises(ProviderFailure):
        adapter.request(
            capability=Capability.INTERPRET,
            model="mistral-medium-3-5",
            typed_payload={"prompt": "x", "gold_answer": "hidden"},
            declared_class="PROJECT",
            run_id="run-17",
        )
    assert contacted == []


def test_redaction_applies_to_transmitted_payload(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    seen = {}

    def capture(request, api_key, timeout_s):
        seen["request"] = request
        return _ok_transport(request, api_key, timeout_s)

    adapter = _adapter(transport=capture)
    fake_key = "sk-" + "abcdefghijklmnop"
    adapter.request(
        capability=Capability.INTERPRET,
        model="mistral-medium-3-5",
        typed_payload={"prompt": "clean claim", "api_key": fake_key},
        declared_class="PROJECT",
        run_id="run-18",
    )
    transmitted = seen["request"]
    serialized = str(transmitted)
    assert fake_key not in serialized
    assert "api_key" not in serialized


def test_degraded_status_recorded_when_redaction_occurred(monkeypatch):
    monkeypatch.setenv("MISTRAL_TEST_KEY", "test-key-not-real")
    adapter = _adapter()
    response = adapter.request(
        capability=Capability.INTERPRET,
        model="mistral-medium-3-5",
        typed_payload={"prompt": "clean claim", "secret": "value"},
        declared_class="PROJECT",
        run_id="run-19",
    )
    assert response.status is CapabilityStatus.DEGRADED
    assert response.degradation_note is not None
