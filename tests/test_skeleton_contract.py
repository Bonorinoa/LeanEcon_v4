"""Phase 3 red tests — proof-skeleton drafting contract (v2).

TDD order per INIT_V2.md Phase 3: skeleton-format contract tests first
(structure, explicit gap marking, no smuggled fabricated bodies), then
the minimal ``leanecon.skeleton`` module.

The invariants under test:

1. STRUCTURE: a skeleton parses into an explicit have-chain with marked
   gaps; ``has_unresolved_gaps`` tells the workflow the draft must NOT
   proceed to verify.
2. EXPLICIT GAPS: every placeholder step carries a ``-- GAP: <note>``
   annotation; an unannotated sorry/admit placeholder or an empty gap
   note is a contract violation (the reviewer must know what to fill).
3. NO SMUGGLED BODIES (B2 lesson at skeleton level): a step with a
   complete-looking tactic body and no gap marker is flagged — the exact
   class that fabricated ``sorry`` bodies with exit 0 in the
   bounded-search spike (2026-08-08).
4. AUDIT GATE UNCHANGED: a skeleton with unresolved gaps fails the
   contamination check (it would fail the kernel sorryAx audit if sent
   to verify); the refined proof is contamination-free. The verifier's
   kernel audit remains the only pass gate — this module adds no bypass.
"""

from leanecon.skeleton import (
    Skeleton,
    refined_proof_ok,
    skeleton_edit_distance,
    validate_skeleton,
)

SKELETON_FIXTURE = """theorem t : P → Q := by
  have h1 : P := by
    -- GAP: h1 is the hypothesis itself
    exact ?_
  have h2 : Q := by
    -- GAP: derive Q from h1
    sorry
  exact h2"""


def test_skeleton_parses_have_chain_and_gaps():
    skel = validate_skeleton(SKELETON_FIXTURE)
    assert isinstance(skel, Skeleton)
    assert [s.name for s in skel.have_steps] == ["h1", "h2"]
    assert skel.has_unresolved_gaps is True
    assert [s.name for s in skel.gaps] == ["h1", "h2"]
    assert skel.problems == []


def test_gaps_must_be_explicit_and_annotated():
    unannotated = """theorem t : P := by
  have h1 : P := by
    sorry"""
    skel = validate_skeleton(unannotated)
    assert skel.has_unresolved_gaps
    assert any("unannotated" in p and "h1" in p for p in skel.problems)

    empty_note = """theorem t : P := by
  have h1 : P := by
    -- GAP:
    sorry"""
    skel2 = validate_skeleton(empty_note)
    assert any("empty gap note" in p and "h1" in p for p in skel2.problems)


def test_complete_looking_body_without_gap_marker_is_flagged():
    smuggled = """theorem t : P := by
  have h1 : P := by
    aesop"""
    skel = validate_skeleton(smuggled)
    assert any("unmarked" in p and "B2" in p for p in skel.problems)


def test_skeleton_never_bypasses_audit_contract():
    skel = validate_skeleton(SKELETON_FIXTURE)
    assert skel.has_unresolved_gaps
    assert not refined_proof_ok(SKELETON_FIXTURE)  # sorry present

    refined = """theorem t : P → Q := by
  have h1 : P := by
    exact hp
  have h2 : Q := by
    exact hq
  exact h2"""
    assert refined_proof_ok(refined)
    assert not validate_skeleton(refined).has_unresolved_gaps


def test_edit_distance_measures_reviewer_delta():
    skeleton = SKELETON_FIXTURE
    small_delta = """theorem t : P → Q := by
  have h1 : P := by
    exact hp
  have h2 : Q := by
    -- GAP: derive Q from h1
    sorry
  exact h2"""
    big_delta = """theorem t : P → Q := by
  intro hp
  have h1 : P := hp
  have h2 : Q := by
    exact (f hp)
  exact h2"""
    assert skeleton_edit_distance(skeleton, skeleton) == 0
    assert skeleton_edit_distance(skeleton, small_delta) < skeleton_edit_distance(
        skeleton, big_delta
    )
