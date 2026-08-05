"""Mistral adapter — the single egress boundary to the Mistral API.

This is the only module that may construct a Mistral HTTP request or read
the Mistral credential. MVP mapping (configuration, Gate 3 decision 6):
- interpretation/explanation -> mistral-medium-3-5
- Lean formalization/proof/repair -> labs-leanstral-1-5
- semantic triage -> Mistral, explicitly non-authoritative

No silent fallback: a failed model is a typed failure, never an implicit
switch to another model.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable, Optional

import httpx

from leanecon.events import (
    CapabilityStatus,
    EVENT_PROVIDER_REQUEST_BLOCKED,
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

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
CREDENTIAL_ENV_NAME = "MISTRAL_API_KEY"

#: MVP capability -> model mapping. Lives here as adapter configuration;
#: core code never references model identifiers directly.
MVP_MODEL_MAP: dict[Capability, CapabilityMapping] = {
    Capability.INTERPRET: CapabilityMapping(
        capability=Capability.INTERPRET, model="mistral-medium-3-5", provider="mistral"
    ),
    Capability.FORMALIZE: CapabilityMapping(
        capability=Capability.FORMALIZE, model="labs-leanstral-1-5", provider="mistral"
    ),
    Capability.PROVE_OR_REPAIR: CapabilityMapping(
        capability=Capability.PROVE_OR_REPAIR, model="labs-leanstral-1-5", provider="mistral"
    ),
    Capability.SEMANTIC_TRIAGE: CapabilityMapping(
        capability=Capability.SEMANTIC_TRIAGE, model="mistral-medium-3-5", provider="mistral"
    ),
    Capability.DIAGNOSTIC_PROBE: CapabilityMapping(
        capability=Capability.DIAGNOSTIC_PROBE, model="mistral-medium-3-5", provider="mistral"
    ),
}


def default_transport(request: dict, api_key: str, timeout_s: float) -> dict:
    """Real HTTP transport. Injectable for deterministic tests."""
    response = httpx.post(
        MISTRAL_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=request,
        timeout=timeout_s,
    )
    if response.status_code == 401:
        raise ProviderFailure(
            ProviderFailureKind.UNAVAILABLE,
            "credential rejected by provider (401)",
            provider="mistral",
        )
    if response.status_code >= 500 or response.status_code == 429:
        raise ProviderFailure(
            ProviderFailureKind.UNAVAILABLE,
            f"provider outage/rate-limit (HTTP {response.status_code})",
            provider="mistral",
        )
    if response.status_code >= 400:
        raise ProviderFailure(
            ProviderFailureKind.INVALID_OUTPUT,
            f"provider request error (HTTP {response.status_code})",
            provider="mistral",
        )
    return response.json()


class MistralAdapter(ProviderAdapter):
    """Single Mistral egress boundary. Owns credentials, retries,
    normalization, and provider metadata."""

    provider_name = "mistral"
    credential_env_name = CREDENTIAL_ENV_NAME

    def __init__(
        self,
        policy_evaluate: Optional[Callable] = None,
        emit_event: Optional[Callable] = None,
        transport: Optional[Callable] = None,
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
        raw: Optional[dict] = None
        started = time.monotonic()
        for attempt in range(1, self.max_attempts + 1):
            try:
                raw = self._transport(request, api_key, self.timeout_s)
                break
            except ProviderFailure as failure:
                if failure.kind is ProviderFailureKind.INVALID_OUTPUT or attempt >= self.max_attempts:
                    raise ProviderFailure(
                        failure.kind,
                        failure.message,
                        attempts=attempt,
                        provider=self.provider_name,
                    ) from failure
                time.sleep(min(2.0 ** attempt, 8.0))
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
        metadata = ProviderMetadata(
            provider=self.provider_name,
            model=model,
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
            note = f"payload redacted before transmission: {len(decision.redaction_report)} field(s)"
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
