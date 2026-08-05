"""Minimal append-only event envelope (docs/gate3/02-lifecycle-events.md).

Design decisions locked at Gate 3:
- minimal stable envelope; digests live on artifacts/bundles, not events;
- capability snapshots only for diagnostics and bundle metadata;
- ``HEALTH_CHECK`` is an event type, never a claim lifecycle state;
- events are append-only: corrections append, never mutate.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = "1.0.0"

#: Event types used by A1 diagnostics and the Gate 3 examples.
EVENT_HEALTH_CHECK = "HEALTH_CHECK"
EVENT_DIAGNOSTIC_RESULT = "DIAGNOSTIC_RESULT"
EVENT_CLAIM_STATE_CHANGED = "CLAIM_STATE_CHANGED"
EVENT_PROVIDER_REQUEST_BLOCKED = "PROVIDER_REQUEST_BLOCKED"
EVENT_VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"

#: Reason-code registry locked at Gate 3 (docs/gate3/02, minimal A1/A3 set),
#: plus PROVIDER_INVALID_OUTPUT (plan minimum list; A1 criterion 10) and
#: RESTRICTED_BLOCKED (docs/gate3/06 outbound contract). Codes are added
#: only when a real failure cannot be represented clearly.
REASON_CODES = (
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
)


class CapabilityStatus(str, Enum):
    """S3a diagnostic vocabulary (Gate 3 decision 3). Diagnostics and
    verification-bundle metadata only — no health matrix, SLOs, or
    sampling windows."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Event:
    """One append-only audit event.

    ``claim_id`` is nullable only for standalone health checks/diagnostics.
    ``state_before``/``state_after`` are nullable when no claim transition
    occurred (e.g. capability probes).
    """

    event_type: str
    run_id: str
    source_component: str
    actor: str
    payload_class: str
    trace_ref: str
    claim_id: Optional[str] = None
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    reason_codes: tuple = ()
    detail: dict = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4()}")
    emitted_at: str = field(default_factory=_utc_now_iso)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "run_id": self.run_id,
            "claim_id": self.claim_id,
            "emitted_at": self.emitted_at,
            "source_component": self.source_component,
            "actor": self.actor,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "reason_codes": list(self.reason_codes),
            "payload_class": self.payload_class,
            "trace_ref": self.trace_ref,
            "detail": self.detail,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=False, separators=(",", ":"))


REQUIRED_EVENT_FIELDS = (
    "schema_version",
    "event_id",
    "event_type",
    "run_id",
    "emitted_at",
    "source_component",
    "actor",
    "reason_codes",
    "payload_class",
    "trace_ref",
)


def validate_event(record: dict) -> list:
    """Return a list of problems (empty when valid). claim_id may be null
    only for standalone diagnostics/health checks."""
    problems = [f"missing field: {f}" for f in REQUIRED_EVENT_FIELDS if f not in record]
    for code in record.get("reason_codes", []):
        if code not in REASON_CODES:
            problems.append(f"unknown reason code: {code}")
    if record.get("claim_id") is None and record.get("event_type") in (
        EVENT_CLAIM_STATE_CHANGED,
        EVENT_VERIFICATION_COMPLETED,
    ):
        problems.append("claim_id required for claim lifecycle events")
    return problems


class EventLog:
    """Append-only JSONL event log. No mutation API by design."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> Event:
        problems = validate_event(event.to_dict())
        if problems:
            raise ValueError(f"refusing to append invalid event: {problems}")
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.to_json() + "\n")
        return event

    def read_all(self) -> list:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
