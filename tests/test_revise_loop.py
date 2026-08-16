"""Phase 2 red tests — bounded kernel-feedback revision loop (v2).

TDD order per INIT_V2.md Phase 2: write the failure-mode fixtures FIRST,
watch them fail, then implement the minimal loop in
``src/leanecon/revise_loop.py``.

The three non-negotiable loop semantics under test:

1. CONTAMINATION GATE (B2 spike lesson, 2026-08-08): a draft carrying a
   sorry / proof body is rejected by the AUDIT contract even when the
   kernel probe would naively report it "compiles". A bare compile exit 0
   is NEVER a pass. The loop's success criterion is the audit gate.
2. BUDGET: the revision loop is bounded (2-3 attempts); it never silently
   attempts a 4th draft.
3. CLEAN-PASS: a genuinely clean draft passes within budget and the
   revision history (per-attempt feedback) is recorded for the packet.
"""

from leanecon.revise_loop import (
    MAX_REVISION_ATTEMPTS,
    revise_statement_draft,
)


def _draft_sequence(drafts):
    """draft_fn yielding ``drafts`` in order, repeating the last one."""
    it = iter(drafts)
    last = drafts[-1]

    def fn(history):
        return next(it, last)

    return fn


def test_contaminated_candidate_is_rejected_by_audit_gate_even_when_it_compiles():
    """B2 lesson at the loop level: sorry-carrying draft must be rejected
    by the audit contract even if the probe would say it compiles."""
    calls = []

    def audit(stmt):
        calls.append(stmt)
        if "sorry" in stmt:
            return ["statement contains 'sorry' (contract violation)"]
        return []

    def probe(stmt):
        # Naive signal: would "compile" anything — the audit gate must win.
        return True, ""

    outcome = revise_statement_draft(
        draft_fn=_draft_sequence(["theorem t : True := sorry", "theorem t : True"]),
        audit=audit,
        probe=probe,
    )

    assert outcome.accepted is True
    assert outcome.attempts_used == 2
    # Attempt 1 (the contaminated draft) was rejected by the audit gate,
    # never accepted despite probe()=compiles.
    assert outcome.revision_history[0].static_problems
    assert "sorry" in outcome.revision_history[0].static_problems[0]


def test_attempt_budget_is_enforced_no_silent_extra_attempts():
    """The loop is bounded; a draft that never improves gets exactly
    MAX_REVISION_ATTEMPTS attempts, not a silent 4th."""
    probe_calls = []

    def audit(stmt):
        return []

    def probe(stmt):
        probe_calls.append(stmt)
        return False, "kernel error"

    outcome = revise_statement_draft(
        draft_fn=_draft_sequence(["d1", "d2", "d3", "d4"]),
        audit=audit,
        probe=probe,
    )

    assert outcome.accepted is False
    assert outcome.attempts_used == MAX_REVISION_ATTEMPTS
    assert len(probe_calls) == MAX_REVISION_ATTEMPTS
    assert "d4" not in probe_calls  # no silent 4th attempt


def test_clean_candidate_passes_within_budget_and_records_revision_history():
    """A clean draft passes within budget; per-attempt feedback is logged."""

    def audit(stmt):
        return ["bad draft"] if "bad" in stmt else []

    def probe(stmt):
        return stmt == "good", "" if stmt == "good" else "compile err"

    outcome = revise_statement_draft(
        draft_fn=_draft_sequence(["bad", "good"]),
        audit=audit,
        probe=probe,
    )

    assert outcome.accepted is True
    assert outcome.attempts_used == 2
    assert len(outcome.revision_history) == 2
    assert outcome.revision_history[0].static_problems == ["bad draft"]
    assert outcome.revision_history[1].probe_compiles is True
