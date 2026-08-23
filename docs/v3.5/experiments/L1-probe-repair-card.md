# Experiment card — L1 probe-in-loop repair (Phase 2)

**Date:** 2026-08-23 · **Branch:** `v35/intelligence-sprint`
**Gate:** G2 (go / revert). Budget policy: DECISION_LOG 51/D2 — inside
`MAX_REVISION_ATTEMPTS=3`; no silent expansion.

## Correction of record (found during recon)

`formalize_claim`'s docstring claims the loop probe is a dummy and the
harness exits on first audit-clean draft. The code wires the REAL
`probe_statement_compiles` into the loop. Artifact forensics:
v4smk/v4h1 artifacts show `revision_attempts=3`, every attempt
audit-clean, every in-loop probe False (real probe consumed the
budget; the runner formalizes from the last audit-clean draft anyway).
The docstring is stale INIT_V3 prose. This card treats the code, not
the docstring, as ground truth; the docstring is corrected in this
phase.

## Hypothesis

On dev fixtures whose model drafts fail elaboration, directing the
repair attempt by the *classified* probe-failure class (P2 taxonomy,
`docs/v3.5/METRICS.md`) raises the elaborates_rate versus raw-stderr
feedback, without regressing audit-clean rate or burning extra budget.

Baseline (dev, measured Phase 1): model_draft elaborates 4/8;
failures exclusively `binder_annotation` (×2) and `syntax` (×2).

## Mechanism split (principled vs heuristic, named)

| Part | Kind | Content |
|---|---|---|
| Classification | **principled** | deterministic subclassing of probe stderr (already shipped, tested against real shapes) |
| Directive table | **principled** | static mapping class → Lean fact (e.g. `[Set α]` is invalid because `Set` is not a typeclass; genuine classes: `Fintype`, `LinearOrder`, …). Table is total over the classifier's outputs; no free-form invention |
| Prompt assembly | **heuristic** | wording/order of the repair block appended to the next attempt's prompt |
| Binder rewriting | **rejected** | mechanical `[Set α] → …` transforms change binder semantics; NOT safe, stays out. Sanitizer scope remains P1/mechanical-P3 |

## Change under test

1. New module `leanecon/probe_repair.py`: `diagnose(feedback_dict) ->
   str | None` producing a short directive line for probe-failed
   feedback; `None` for audit-failed / clean feedback (unchanged
   behavior there).
2. `a3_runner._revision_feedback_block` appends the directive line
   when the last feedback carries a failed probe. One code path; no
   second loop; budget untouched.
3. Stale docstring corrected to describe actual behavior.

## Metrics & gates

- Fixture scorer stays green (deterministic, no provider).
- New unit tests: directive-table totality over classifier outputs;
  diagnosis appears iff last feedback has a failed probe; clean
  single-attempt path produces no diagnosis section; budget constants
  untouched.
- Optional live smoke (only on explicit CTO go; spends Labs quota):
  1 claim, v4smk-B text (dev fixture), predictions written first;
  success = FORMALIZED ∧ fresh probe True within ≤3 attempts.
- Rollback trigger: any audit-clean regression on fixtures, or any
  test weakening.

## Non-goals

No tactic search, no LSP session, no proof generation, no sanitizer
scope growth, no budget change, no MVP_MODEL_MAP edit.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
