"""A3 claim lifecycle state machine (docs/gate5/a3-design.md §1, gate3/02).

The transition table is the single source of truth for allowed claim-state
moves. Enforced by the a3_runner before any state-changing command persists.

Actor rules (enforced in the runner, not here):
- only a human reviewer may move REVIEW_REQUIRED -> ACCEPTED | REJECTED;
- the system may emit processing states and FAILED/BLOCKED;
- VERIFIED is emitted only by the bundle validator path.
"""

from __future__ import annotations

CLAIM_STATES = (
    "DRAFT",
    "INTERPRETED",
    "REVIEW_REQUIRED",
    "ACCEPTED",
    "REJECTED",
    "FORMALIZED",
    "PROVING",
    "VERIFIED",
    "FAILED",
    "BLOCKED",
)

#: Allowed (from, to) edges. ``None`` means "new revision at DRAFT".
#: Retry edges (FAILED -> PROVING, BLOCKED -> PROVING, BLOCKED -> INTERPRETED,
#: BLOCKED -> FORMALIZED, FAILED -> INTERPRETED) implement the gate3/02
#: semantics "retryable through a new attempt/revision" and
#: "retryable when blocker clears".
TRANSITIONS: frozenset[tuple[str | None, str]] = frozenset(
    {
        (None, "DRAFT"),
        # interpretation
        ("DRAFT", "INTERPRETED"),
        ("DRAFT", "BLOCKED"),
        # gate3/02 failure-exit rule: work ran and produced a negative result
        ("DRAFT", "FAILED"),
        # re-formalization attempt (formalize --force): new formal revision,
        # same claim; supersedes the previous candidate
        ("FORMALIZED", "FORMALIZED"),
        # retry formalization after a rejected candidate (FAILED by
        # PROVIDER_INVALID_OUTPUT etc.) — same claim, fresh attempt
        ("FAILED", "FORMALIZED"),
        ("INTERPRETED", "REVIEW_REQUIRED"),
        ("INTERPRETED", "FAILED"),
        # semantic review gate (reviewer only)
        ("REVIEW_REQUIRED", "ACCEPTED"),
        ("REVIEW_REQUIRED", "REJECTED"),
        # formalization
        ("ACCEPTED", "FORMALIZED"),
        ("ACCEPTED", "BLOCKED"),
        ("FORMALIZED", "FAILED"),
        # verification
        ("FORMALIZED", "PROVING"),
        ("PROVING", "VERIFIED"),
        ("PROVING", "FAILED"),
        ("PROVING", "BLOCKED"),
        # retries
        ("FAILED", "PROVING"),
        ("FAILED", "INTERPRETED"),
        ("BLOCKED", "INTERPRETED"),
        ("BLOCKED", "FORMALIZED"),
        ("BLOCKED", "PROVING"),
    }
)

#: Terminal states for a given claim revision.
TERMINAL_STATES = frozenset({"REJECTED", "VERIFIED"})


def validate_transition(state_before: str | None, state_after: str) -> str | None:
    """Return an error message when the transition is not allowed, else None."""
    if state_after not in CLAIM_STATES:
        return f"unknown target state: {state_after}"
    if state_before is not None and state_before not in CLAIM_STATES:
        return f"unknown source state: {state_before}"
    if (state_before, state_after) not in TRANSITIONS:
        return f"transition not allowed: {state_before} -> {state_after}"
    return None
