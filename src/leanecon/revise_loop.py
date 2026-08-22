"""Bounded kernel-feedback revision loop (v2 Phase 2).

Per INIT_V2.md Phase 2: the model's formal-statement draft is revised
against kernel feedback in a bounded (2-3 attempt) loop, with the kernel
axiom audit as the success gate. This module is the loop HARNESS only —
provider and kernel boundaries are injected by the caller.

The three non-negotiables (encoded in tests/test_revise_loop.py):

1. CONTAMINATION GATE (B2 spike, 2026-08-08): a draft that fails the
   static/audit contract is rejected even when a naive compile probe
   would report "compiles". Bare compile exit 0 is NEVER a pass; the
   audit gate decides.
2. BUDGET: at most MAX_REVISION_ATTEMPTS attempts; the loop never
   silently attempts more.
3. Every attempt's feedback is recorded (draft, static problems, probe
   outcome) so the reviewer packet carries the full revision history.

The audit callable is expected to run the v1 static contracts
(validate_statement_text, D4 scaffolding, D1 mapping) and, at the kernel
boundary, the sorryAx audit — the same gate the verifier enforces.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

#: Bounded revision budget (INIT_V2.md Phase 2: 2-3 attempts).
MAX_REVISION_ATTEMPTS = 3


@dataclass
class Feedback:
    """Per-attempt record: the draft offered and the kernel/static feedback."""

    draft: str
    static_problems: list[str] = field(default_factory=list)
    probe_compiles: bool | None = None
    probe_stderr: str = ""


@dataclass
class ReviseOutcome:
    """Final loop result: acceptance plus the full revision history."""

    accepted: bool
    attempts_used: int
    revision_history: list[Feedback] = field(default_factory=list)


def revise_statement_draft(
    draft_fn: Callable[[list[Feedback]], str],
    audit: Callable[[str], list[str]],
    probe: Callable[[str], tuple[bool, str]],
) -> ReviseOutcome:
    """Run the bounded revision loop.

    Args:
        draft_fn: ``draft_fn(history) -> next draft text`` — may use the
            revision history to revise (kernel feedback surfaced verbatim
            in ``Feedback``).
        audit: ``audit(stmt) -> static contract problems`` (empty list =
            clean). Authoritative: a draft failing audit is rejected even
            if the probe would naively report compiles.
        probe: ``probe(stmt) -> (compiles, stderr)`` kernel probe signal.

    Returns:
        ReviseOutcome with accepted/attempts_used/revision_history.
    """
    history: list[Feedback] = []
    for _ in range(MAX_REVISION_ATTEMPTS):
        draft = draft_fn(history)
        problems = audit(draft)
        if problems:
            history.append(Feedback(draft=draft, static_problems=problems))
            continue
        compiles, stderr = probe(draft)
        record = Feedback(draft=draft, probe_compiles=compiles, probe_stderr=stderr)
        history.append(record)
        if compiles:
            return ReviseOutcome(
                accepted=True, attempts_used=len(history), revision_history=history
            )
    return ReviseOutcome(accepted=False, attempts_used=len(history), revision_history=history)
