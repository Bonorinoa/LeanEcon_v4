"""A3 lifecycle state machine tests (docs/gate5/a3-design.md §1, gate3/02)."""

from leanecon.lifecycle import (
    CLAIM_STATES,
    TERMINAL_STATES,
    TRANSITIONS,
    validate_transition,
)


def test_all_states_present():
    assert set(CLAIM_STATES) == {
        "DRAFT", "INTERPRETED", "REVIEW_REQUIRED", "ACCEPTED", "REJECTED",
        "FORMALIZED", "PROVING", "VERIFIED", "FAILED", "BLOCKED",
    }


def test_happy_path_is_allowed():
    edges = [
        (None, "DRAFT"),
        ("DRAFT", "INTERPRETED"),
        ("INTERPRETED", "REVIEW_REQUIRED"),
        ("REVIEW_REQUIRED", "ACCEPTED"),
        ("ACCEPTED", "FORMALIZED"),
        ("FORMALIZED", "PROVING"),
        ("PROVING", "VERIFIED"),
    ]
    for before, after in edges:
        assert validate_transition(before, after) is None, (before, after)


def test_review_required_cannot_be_skipped():
    assert validate_transition("DRAFT", "ACCEPTED") is not None
    assert validate_transition("INTERPRETED", "FORMALIZED") is not None
    assert validate_transition("ACCEPTED", "PROVING") is not None


def test_rejected_and_verified_are_terminal():
    assert TERMINAL_STATES == {"REJECTED", "VERIFIED"}
    assert validate_transition("REJECTED", "DRAFT") is not None
    assert validate_transition("VERIFIED", "PROVING") is not None


def test_retry_edges_exist():
    # gate3/02: FAILED retryable through a new attempt; BLOCKED retryable when cleared
    for edge in [
        ("FAILED", "PROVING"),
        ("BLOCKED", "PROVING"),
        ("BLOCKED", "INTERPRETED"),
        ("BLOCKED", "FORMALIZED"),
        ("FAILED", "INTERPRETED"),
    ]:
        assert edge in TRANSITIONS, edge


def test_failure_exits_from_processing_states():
    assert validate_transition("DRAFT", "BLOCKED") is None
    # gate3/02 failure-exit rule: work ran and produced a negative result
    assert validate_transition("DRAFT", "FAILED") is None
    assert validate_transition("INTERPRETED", "FAILED") is None
    assert validate_transition("ACCEPTED", "BLOCKED") is None
    assert validate_transition("PROVING", "FAILED") is None
    assert validate_transition("PROVING", "BLOCKED") is None


def test_unknown_states_rejected():
    assert validate_transition(None, "NOPE") is not None
    assert validate_transition("NOPE", "DRAFT") is not None
