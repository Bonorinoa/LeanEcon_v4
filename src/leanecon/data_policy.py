"""MVP-thin outbound data policy (docs/gate3/06-outbound-data-enforcement.md).

Locked at Gate 3 (CTO decisions 9–11):
- one provider boundary; PUBLIC and PROJECT are sendable classes;
- RESTRICTED is hard-denied in MVP (no opt-in mechanism);
- unknown/mixed classification fails closed to RESTRICTED;
- sealed gold / hidden labels / hidden v3 evaluation material are denied
  always, even inside PROJECT-classified payloads;
- redaction is limited to secrets/credentials; broad PII classification,
  retention controls, and per-run restricted opt-in are future work.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

SECRET_FIELD_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|password|passwd|secret|credential|authorization|private[_-]?key)"
)
# Built from fragments so no credential-shaped literal appears in tracked
# source (keeps CI credential-pattern scans clean).
_GH_CLASSIC = "gh" + "p_[A-Za-z0-9]{20,}"
_GH_FINE = "github" + "_pat_[A-Za-z0-9_]{20,}"
SECRET_VALUE_PATTERN = re.compile(
    rf"({_GH_CLASSIC}|{_GH_FINE}|sk-[A-Za-z0-9_-]{{16,}}|xox[baprs]-[A-Za-z0-9-]{{10,}})"
)

#: Marker keys that identify evaluator-only material. These must never
#: reach a provider, regardless of declared class (evaluation integrity).
GOLD_MARKERS = frozenset(
    {
        "sealed_gold",
        "gold_statement",
        "gold_answer",
        "hidden_label",
        "hidden_labels",
        "answer_key",
        "v3_hidden_eval",
        "evaluator_only",
    }
)

REASON_RESTRICTED_BLOCKED = "RESTRICTED_BLOCKED"
REASON_GOLD_BLOCKED = "INPUT_REJECTED"


class PayloadClass(str, Enum):
    PUBLIC = "PUBLIC"
    PROJECT = "PROJECT"
    RESTRICTED = "RESTRICTED"


def classify(declared: Any) -> PayloadClass:
    """Fail-closed classification: anything not explicitly PUBLIC/PROJECT
    becomes RESTRICTED (unknown, missing, mixed, wrong type)."""
    if isinstance(declared, PayloadClass):
        return declared
    if isinstance(declared, str):
        try:
            return PayloadClass(declared.strip().upper())
        except ValueError:
            return PayloadClass.RESTRICTED
    return PayloadClass.RESTRICTED


def contains_gold(payload: Any) -> list:
    """Recursively find gold/hidden-evaluation markers. Returns found keys."""
    found: list = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if str(key).lower() in GOLD_MARKERS:
                    found.append(str(key))
                walk(value)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)

    walk(payload)
    return found


def redact(payload: Any) -> tuple:
    """Remove secret/credential fields and scrub secret-looking values.
    Returns (redacted_payload, redaction_report). No broad PII pipeline
    in MVP (deferred before external users)."""
    report: list = []

    def walk(node: Any, path: str) -> Any:
        if isinstance(node, dict):
            out = {}
            for key, value in node.items():
                here = f"{path}.{key}" if path else str(key)
                if SECRET_FIELD_PATTERN.search(str(key)):
                    report.append({"path": here, "action": "field_removed"})
                    continue
                out[key] = walk(value, here)
            return out
        if isinstance(node, list):
            return [walk(item, f"{path}[{i}]") for i, item in enumerate(node)]
        if isinstance(node, str) and SECRET_VALUE_PATTERN.search(node):
            report.append({"path": path, "action": "value_scrubbed"})
            return "[REDACTED]"
        return node

    return walk(payload, ""), report


def canonical_digest(payload: Any) -> str:
    """SHA-256 over canonical JSON (Gate 3 ambiguity A4: SHA-256 for
    trust-relevant artifacts; applied here to post-redaction payloads)."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    payload_class: PayloadClass
    reason_code: Optional[str] = None
    redaction_report: list = field(default_factory=list)
    content_digest: Optional[str] = None
    detail: str = ""


def evaluate(payload: Any, declared_class: Any) -> PolicyDecision:
    """Single policy decision for one typed outbound request.

    Order matters: classify fail-closed → deny RESTRICTED → deny gold →
    redact → allow with digest. Denied requests never carry a digest of
    the raw payload.
    """
    payload_class = classify(declared_class)
    if payload_class is PayloadClass.RESTRICTED:
        return PolicyDecision(
            allowed=False,
            payload_class=payload_class,
            reason_code=REASON_RESTRICTED_BLOCKED,
            detail="RESTRICTED is hard-denied in MVP; no opt-in mechanism",
        )
    gold_hits = contains_gold(payload)
    if gold_hits:
        return PolicyDecision(
            allowed=False,
            payload_class=payload_class,
            reason_code=REASON_GOLD_BLOCKED,
            detail=f"sealed gold/hidden evaluation markers present: {sorted(set(gold_hits))}",
        )
    redacted, report = redact(payload)
    return PolicyDecision(
        allowed=True,
        payload_class=payload_class,
        redaction_report=report,
        content_digest=canonical_digest(redacted),
    )
