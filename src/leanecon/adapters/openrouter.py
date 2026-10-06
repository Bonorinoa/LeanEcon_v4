"""Provider adapter — the single egress boundary to the model API.

This is the only module that may construct the provider HTTP request or
read the provider credential. Every capability is pinned to OpenRouter's
free router (`openrouter/free`), which only selects zero-price models.
A failed call is a typed failure, never an implicit switch to a paid
model. A 402 is a paid-path bug, not a cue to fund an account.

Jev Router (`typesafe/jev-router`) and `openrouter/auto` bill at the
routed model's price and are not the live pin. HuggingFace inference
is a complementary future path, not a second live adapter.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable

import httpx

from leanecon.events import (
    EVENT_PROVIDER_REQUEST_BLOCKED,
    CapabilityStatus,
    Event,
)
from leanecon.providers import (
    Capability,
    CapabilityMapping,
    ProviderAdapter,
    ProviderFailure,
    ProviderFailureKind,
    ProviderMetadata,
    ProviderResponse,
)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
CREDENTIAL_ENV_NAME = "OPENROUTER_API_KEY"
# OpenRouter free router: routes only among models priced at $0.
FREE_MODEL = "openrouter/free"
PROVIDER = "openrouter"
APP_REFERER = "https://github.com/Bonorinoa/LeanEcon_v4"
APP_TITLE = "LeanEcon"

#: Capability -> model mapping. Lives here as adapter configuration;
#: core code never references model identifiers directly.
MVP_MODEL_MAP: dict[Capability, CapabilityMapping] = {
    capability: CapabilityMapping(capability=capability, model=FREE_MODEL, provider=PROVIDER)
    for capability in (
        Capability.INTERPRET,
        Capability.FORMALIZE,
        Capability.PROVE_OR_REPAIR,
        Capability.SEMANTIC_TRIAGE,
        Capability.DIAGNOSTIC_PROBE,
        Capability.OPINION,
    )
}


def failure_for_http_status(status_code: int) -> ProviderFailure | None:
    """Map an HTTP status to a typed failure, or None on 2xx/3xx."""
    if status_code < 400:
        return None
    if status_code == 401:
        return ProviderFailure(
            ProviderFailureKind.UNAVAILABLE,
            "credential rejected by provider (401)",
            provider=PROVIDER,
        )
    if status_code == 402:
        return ProviderFailure(
            ProviderFailureKind.INVALID_OUTPUT,
            "paid-path (HTTP 402); live pin is the free router only",
            provider=PROVIDER,
        )
    if status_code >= 500 or status_code == 429:
        return ProviderFailure(
            ProviderFailureKind.UNAVAILABLE,
            f"provider outage/rate-limit (HTTP {status_code})",
            provider=PROVIDER,
        )
    return ProviderFailure(
        ProviderFailureKind.INVALID_OUTPUT,
        f"provider request error (HTTP {status_code})",
        provider=PROVIDER,
    )


def default_transport(request: dict, api_key: str, timeout_s: float) -> dict:
    """Real HTTP transport. Injectable for deterministic tests."""
    response = httpx.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": APP_REFERER,
            "X-Title": APP_TITLE,
        },
        json=request,
        timeout=timeout_s,
    )
    failure = failure_for_http_status(response.status_code)
    if failure is not None:
        raise failure
    return response.json()


class OpenRouterAdapter(ProviderAdapter):
    """Single provider egress boundary. Owns credentials, retries,
    normalization, and provider metadata."""

    provider_name = PROVIDER
    credential_env_name = CREDENTIAL_ENV_NAME

    def __init__(
        self,
        policy_evaluate: Callable | None = None,
        emit_event: Callable | None = None,
        transport: Callable | None = None,
        api_key_env: str = CREDENTIAL_ENV_NAME,
        max_attempts: int = 2,
        timeout_s: float = 60.0,
    ):
        super().__init__(
            policy_evaluate=policy_evaluate,
            emit_event=emit_event,
            transport=transport or default_transport,
            max_attempts=max_attempts,
            timeout_s=timeout_s,
        )
        self._api_key_env = api_key_env

    # -- adapter internals ------------------------------------------------
    def _load_credential(self) -> str:
        key = os.environ.get(self._api_key_env)
        if not key:
            raise ProviderFailure(
                ProviderFailureKind.UNAVAILABLE,
                f"credential {self._api_key_env} not configured",
                attempts=0,
                provider=self.provider_name,
            )
        return key

    def _invoke(self, capability, model, payload, decision, run_id) -> ProviderResponse:
        api_key = self._load_credential()
        request = self._build_request(capability, model, payload)
        raw: dict | None = None
        started = time.monotonic()
        for attempt in range(1, self.max_attempts + 1):
            try:
                raw = self._transport(request, api_key, self.timeout_s)
                break
            except ProviderFailure as failure:
                if (
                    failure.kind is ProviderFailureKind.INVALID_OUTPUT
                    or attempt >= self.max_attempts
                ):
                    raise ProviderFailure(
                        failure.kind,
                        failure.message,
                        attempts=attempt,
                        provider=self.provider_name,
                    ) from failure
                time.sleep(min(2.0**attempt, 8.0))
        if raw is None:
            raise ProviderFailure(
                ProviderFailureKind.UNAVAILABLE,
                "provider request failed on all safe retries",
                attempts=self.max_attempts,
                provider=self.provider_name,
            )
        latency_ms = int((time.monotonic() - started) * 1000)
        return self._normalize(capability, model, raw, latency_ms, decision)

    def _build_request(self, capability: Capability, model: str, payload: dict) -> dict:
        prompt = payload.get("prompt") or json.dumps(payload, sort_keys=True)
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

    def _normalize(self, capability, model, raw, latency_ms, decision) -> ProviderResponse:
        if not isinstance(raw, dict):
            raise ProviderFailure(
                ProviderFailureKind.INVALID_OUTPUT,
                "provider returned non-object response",
                provider=self.provider_name,
            )
        choices = raw.get("choices")
        if not choices or not isinstance(choices, list) or "message" not in choices[0]:
            raise ProviderFailure(
                ProviderFailureKind.INVALID_OUTPUT,
                "provider response missing choices/message",
                provider=self.provider_name,
            )
        content = choices[0]["message"].get("content")
        if not content:
            raise ProviderFailure(
                ProviderFailureKind.INVALID_OUTPUT,
                "provider message missing content",
                provider=self.provider_name,
            )
        usage = raw.get("usage")
        routed = raw.get("model")
        recorded_model = routed if isinstance(routed, str) and routed else model
        metadata = ProviderMetadata(
            provider=self.provider_name,
            model=recorded_model,
            request_id=raw.get("id"),
            latency_ms=latency_ms,
            token_metadata=(
                {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                }
                if isinstance(usage, dict)
                else None
            ),
        )
        status = CapabilityStatus.HEALTHY
        note = None
        if decision.redaction_report:
            status = CapabilityStatus.DEGRADED
            note = (
                f"payload redacted before transmission: {len(decision.redaction_report)} field(s)"
            )
        return ProviderResponse(
            capability=capability,
            status=status,
            output={"content": content},
            metadata=metadata,
            degradation_note=note,
        )

    # -- event emission on denial ------------------------------------------
    def emit_blocked_event(self, decision, capability, run_id, claim_id) -> Event:
        """Builds the PROVIDER_REQUEST_BLOCKED event for a denied request
        (trace completeness). Suitable as the boundary emit_event callback."""
        return Event(
            event_type=EVENT_PROVIDER_REQUEST_BLOCKED,
            run_id=run_id,
            claim_id=claim_id,
            source_component="provider-boundary",
            actor="policy-boundary",
            reason_codes=(decision.reason_code,) if decision.reason_code else (),
            payload_class=decision.payload_class.value,
            trace_ref=f"deny-{run_id}",
            detail={"capability": capability.value},
        )
