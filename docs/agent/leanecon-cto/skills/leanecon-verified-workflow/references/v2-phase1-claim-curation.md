# v2 Phase 1 — Fresh OOS claim curation (2026-08-08)

Use when drafting new out-of-sample claims (v2 Phase 1 AI-reviewer exercise,
or any future claim-set expansion). Design authority: `docs/v2/INIT_V2.md`
(CTO-approved 2026-08-08). Pre-run predictions were written to
`artifacts/local/v2-p1-expectations.md` BEFORE any ingest; the set is held
at the claim-text gate awaiting CTO semantic approval (empty clarify ≠
consent — §4).

## Freshness guarantee

- Read the EXACT `source_text` from `artifacts/local/a3/claims/<id>.json`
  for EVERY canonical claim (c1–c4, fwt1, oos1–3, c1r2) before drafting.
  Never draft from `docs/eval/v1-claim-set.md` table prose (it summarizes)
  or from memory of prior sessions.
- Fresh = no verbatim overlap with any canonical text. Same-text re-runs
  under a new claim id (c1r2 pattern) are for isolating a pipeline
  question, not for "fresh OOS" sets.

## Simple-class envelope (selection criteria)

- Single-claim sequential; provable with EXISTING v1 proof patterns
  (`tests/fixtures/lean/` + `Theorems.lean` calc/sum_comm patterns).
- Maps ONLY to existing Core declarations (bundle, weakPreference, utility,
  strictlyIncreasing, budgetSet, budgetSetEndowment, attainableSet,
  marketClearing, competitiveEquilibrium, paretoEfficiency) — NO new Core
  declarations, no game theory, no Nash.
- Excluded classes (rejected during curation, with reasons):
  - **Optimization/calculus derivations** (e.g. Cobb–Douglas demand
    `x1* = M/(2p1)`): no such proof pattern exists in the v1 fixture
    library; it buries the walkthrough in proof burden instead of
    exercising the reviewer.
  - **Existence theorems** (e.g. 2-agent CE existence, Arrow–Debreu
    class): oos3 (Nash existence) already stalled at FORMALIZED — existence
    proofs are research-grade, not the simple-class target.
- Give each claim a DIFFERENT AI-reviewer decision surface (A: assumption/
  gap framing; B: stated-assumption recording; C: assumption-vs-derived
  honesty + aggregate pattern) so the exercise measures agreement across
  surfaces rather than the same surface N times.

## Worked set (v2p1-A/B/C — texts approved by CTO gate #1 pending)

- **v2p1-A** budget binds at an optimum (single agent): finitely many
  goods (≥1), strictly positive prices, strictly increasing utility, x
  maximizes u over the endowment-relative budget set ⇒ value(x) =
  value(e). Core: `budgetSetEndowment`, `strictlyIncreasing`, `bundle`.
  Expected gap: `[Nonempty Goods]` + strictly positive prices (fwt1
  `[Nonempty Agent]` precedent).
- **v2p1-B** spending is monotone in consumption: nonnegative prices p,
  x ≤ y componentwise ⇒ (∑ g, p g * x g) ≤ (∑ g, p g * y g). Core:
  `bundle` + budgetSet value expression. Pure Mathlib
  (`Finset.sum_le_sum` + `mul_le_mul`). Expected gap: price nonnegativity
  is a stated assumption, not derived.
- **v2p1-C** Walras' law (aggregate): markets clear AND every budget binds
  ⇒ aggregate expenditure = aggregate endowment value. Core:
  `marketClearing`, `budgetSetEndowment`, `bundle`. Proof follows the fwt1
  summation pattern (sum_comm + mul_sum + hy_feas). Expected gap: "budget
  binds" is an assumption, not derived from monotonicity.

## Method notes

- Predictions BEFORE ingest: numbered rows with step, expected, confidence,
  rationale (expectations-first methodology, §6). 8 rows for the worked set.
- Claim texts need CTO semantic approval BEFORE `ingest`; an empty clarify
  response = hold, restate options as plain text.
- Zero source changes in Phase 1; `artifacts/` is the gitignored
  operational record.

**Attribution:** Hermes Agent under CTO direction; the CTO remains the
accountable semantic authority and sole semantic approver of claim texts.
