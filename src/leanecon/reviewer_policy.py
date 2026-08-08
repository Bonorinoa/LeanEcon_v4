"""Reviewer identity policy (docs/gate3/08-reviewer-policy.md).

Gate 3 originally locked semantic approval to a human reviewer. CTO decision
2026-08-08 (DECISION_LOG item 31) authorizes AI reviewers for the supported
workflow: an authorized AI agent may emit ACCEPTED/REJECTED, gap-ack, and
axiom-approve records. The CTO remains the accountable semantic authority;
AI is an authorized agent, not an independent sovereign.

Kinds:
- ``human`` — a named human identity (default when not auto-detected as AI)
- ``ai`` — an authorized AI agent identity

Identity is always required. Kind may be passed explicitly or inferred from
the reviewer id (see ``infer_reviewer_kind``).
"""

from __future__ import annotations

import re
from typing import Literal

ReviewerKind = Literal["human", "ai"]

REVIEWER_KINDS: frozenset[str] = frozenset({"human", "ai"})

# Match common AI agent ids without requiring a fixed roster.
# Examples: ai, AI, hermes, hermes-agent, leanecon-ai, leanecon-ai:v1, ai:oos-batch
_AI_IDENTITY_RE = re.compile(
    r"^(ai|hermes|hermes-agent|leanecon-ai)([:_-].+)?$",
    re.IGNORECASE,
)


def infer_reviewer_kind(reviewer_id: str) -> ReviewerKind:
    """Infer kind from identity when --reviewer-kind is omitted."""
    rid = (reviewer_id or "").strip()
    if not rid:
        raise ValueError("reviewer identity is empty")
    if _AI_IDENTITY_RE.match(rid):
        return "ai"
    return "human"


def normalize_reviewer_kind(kind: str | None, reviewer_id: str) -> ReviewerKind:
    """Resolve explicit kind or auto-infer. Raises ValueError on bad input."""
    if kind is None or str(kind).strip() == "" or str(kind).strip().lower() == "auto":
        return infer_reviewer_kind(reviewer_id)
    k = str(kind).strip().lower()
    if k not in REVIEWER_KINDS:
        raise ValueError(f"reviewer_kind must be one of {sorted(REVIEWER_KINDS)} or auto, got {kind!r}")
    return k  # type: ignore[return-value]


def resolve_reviewer(reviewer_id: str | None, kind: str | None = None) -> tuple[str, ReviewerKind]:
    """Return (reviewer_id, reviewer_kind). Requires a non-empty identity."""
    rid = (reviewer_id or "").strip()
    if not rid:
        raise ValueError("reviewer identity required")
    return rid, normalize_reviewer_kind(kind, rid)
