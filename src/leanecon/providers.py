"""Provider-neutral capability contracts (docs/gate3/04-provider-contracts.md).

The core depends on capabilities, never on vendors. Adapters own API
calls, credentials, retries/timeouts, response normalization, and
provider metadata. No silent fallback. Credentials are referenced by
name only and never appear in core code or logs.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from leanecon.events import CapabilityStatus


class Capability(str, Enum):
    INTERPRET = "interpret"
    FORMALIZE = "formalize"
    PROVE_OR_REPAIR = "prove_or_repair"
    SEMANTIC_TRIAGE = "semantic_triage"
    #: A1 diagnostic capability: structured-output probe against a model.
    DIAGNOSTIC_PROBE = "diagnostic_probe"


class ProviderFailureKind(str, Enum):
    """Failure semantics locked at Gate 3 (docs/gate3/04):
    - malformed output from a request that ran -> FAILED / PROVIDER_INVALID_OUTPUT;
    - outage, credential failure, or exhausted safe retry -> BLOCKED /
      PROVIDER_UNAVAILABLE."""

    INVALID_OUTPUT = "PROVIDER_INVALID_OUTPUT"
    UNAVAILABLE = "PROVIDER_UNAVAILABLE"


class ProviderFailure(Exception):
    """Typed provider failure. Core code must never see vendor-specific
    exception taxonomies."""

    def __init__(self, kind: ProviderFailureKind, message: str, attempts: int = 1, provider: str = "unknown"):
        super().__init__(message)
        self.kind = kind
        self.message = message
        self.attempts = attempts
        self.provider = provider

    @property
    def reason_code(self) -> str:
        return self.kind.value


@dataclass(frozen=True)
class ProviderMetadata:
    """Per-request provider metadata (Gate 3 / A1 criterion 6): model,
    request id where available, latency, and token metadata where
    available. Absent values are None, never fabricated."""

    provider: str
    model: str
    request_id: Optional[str] = None
    latency_ms: Optional[int] = None
    token_metadata: Optional[dict] = None


@dataclass(frozen=True)
class ProviderResponse:
    capability: Capability
    status: CapabilityStatus
    output: Any
    metadata: ProviderMetadata
    degradation_note: Optional[str] = None
    trace_ref: str = field(default_factory=lambda: f"req-{uuid.uuid4()}")


@dataclass(frozen=True)
class CapabilityMapping:
    """Configuration-level capability -> model mapping. Model identifiers
    live in configuration, not in core contracts."""

    capability: Capability
    model: str
    provider: str


class ProviderAdapter(ABC):
    """The only component permitted to know a vendor API.

    Subclasses own: API calls, credential loading, retries/backoff,
    rate limits, response normalization, provider metadata, and
    provider-specific error mapping. The boundary enforces the outbound
    data policy before any transmission.
    """

    provider_name: str = "abstract"
    credential_env_name: str = ""  # reference by name only

    def __init__(
        self,
        policy_evaluate: Optional[Callable] = None,
        emit_event: Optional[Callable] = None,
        transport: Optional[Callable] = None,
        max_attempts: int = 2,
        timeout_s: float = 60.0,
    ):
        from leanecon import data_policy

        self._policy_evaluate = policy_evaluate or data_policy.evaluate
        self._emit_event = emit_event
        self._transport = transport  # injectable for deterministic tests
        self.max_attempts = max_attempts
        self.timeout_s = timeout_s

    # -- boundary -------------------------------------------------------
    def request(
        self,
        capability: Capability,
        model: str,
        typed_payload: dict,
        declared_class: Any,
        run_id: str,
        claim_id: Optional[str] = None,
    ) -> ProviderResponse:
        """Single egress path: policy decision first, then transmission.

        Denied requests never contact the provider and are recorded as
        PROVIDER_REQUEST_BLOCKED events with the policy reason code.
        """
        decision = self._policy_evaluate(typed_payload, declared_class)
        if not decision.allowed:
            emitter = self._emit_event
            if emitter is not None:
                emitter(decision, capability, run_id, claim_id)
            raise ProviderFailure(
                ProviderFailureKind.UNAVAILABLE,
                f"outbound policy denied {capability.value}: {decision.reason_code}",
                attempts=0,
                provider=self.provider_name,
            )
        payload = _redacted_payload(typed_payload, decision)
        return self._invoke(capability, model, payload, decision, run_id)

    # -- adapter hooks ---------------------------------------------------
    @abstractmethod
    def _invoke(
        self,
        capability: Capability,
        model: str,
        payload: dict,
        decision: Any,
        run_id: str,
    ) -> ProviderResponse:
        """Vendor-specific call. Implementations must map vendor errors to
        ProviderFailure kinds and never leak raw vendor exceptions."""


def _redacted_payload(payload: dict, decision: Any) -> dict:
    """Re-run redaction to obtain the transmission payload. Redaction is
    deterministic, so the digest matches the transmitted content."""
    from leanecon import data_policy

    redacted, _report = data_policy.redact(payload)
    return redacted


def payload_digest(payload: dict) -> str:
    from leanecon import data_policy

    return data_policy.canonical_digest(payload)


def request_fingerprint(metadata: ProviderMetadata, digest: str) -> str:
    return hashlib.sha256(f"{metadata.provider}:{metadata.model}:{digest}".encode()).hexdigest()
