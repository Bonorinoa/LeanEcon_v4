# v3 claim split (Phase 2 — HELD-OUT FROZEN 2026-08-13)

**Status:** HELD-OUT set frozen 2026-08-13 (branch `v3/phase1-wire-loop`
@ `715bb52`). Scoring = `scripts/eval_formalizer.py` + live `a3_run.py`.
60–70% may be claimed **only** from this table after a live run.

## Dev / regression (scorer fixtures; do not tune prompts only to these)

`c1–c4`, `fwt1`, `oos1–2` (v1 claim set) + synthetic cases in
`tests/fixtures/eval/formalizer/` (CI scores those; no provider).

## v2 memory (pipeline-change comparison)

`v3p1-A/B/C` — same text as VERIFIED `v2p1-A/B/C`, new ids. Live
2026-08-13: first_try_valid 1/3, A=1/C=2/B=null attempts. Do **not**
re-formalize `v2p1-*`.

## HELD-OUT v3 (the 60–70% set — frozen)

Fresh simple-class texts, no verbatim overlap with any existing
`source_text` (checked against all claim files). Existing Core only
(`budgetSet`, `budgetSetEndowment`, `attainableSet`, `marketClearing`,
`competitiveEquilibrium`, `strictlyIncreasing`); no calculus, no
existence, no game theory. Proofs follow existing fixture patterns.

| id | Text | Core anchor | Expected proof pattern |
|---|---|---|---|
| v3h-A | If every price weakly falls (p' g ≤ p g for every good g) while income m is unchanged, the budget set weakly expands: any bundle affordable at prices p remains affordable at prices p'. | `budgetSet` | `Finset.sum_le_sum` + `mul_le_mul_of_nonneg_right` + `le_trans`; stated nonnegativity of the bundle |
| v3h-B | In an exchange economy, at any competitive equilibrium the allocation is feasible: markets clear. | `competitiveEquilibrium` | structure projection `h.feasible` |
| v3h-C | The attainable set is exactly the budget set: a bundle is attainable precisely when it is affordable. | `attainableSet` | definitional (rfl / iff of membership) |
| v3h-D | In an exchange economy, if markets clear and every consumer's bundle lies in their endowment-relative budget set, then aggregate expenditure does not exceed aggregate endowment value. | `marketClearing`, `budgetSetEndowment` | per-agent `sum_le_sum` over `Finset`; inequality version of the Walras identity |

Scored: `first_try_valid`, `attempts_to_valid`, `probe_compiles`,
`draft_complete` (audit-clean ∧ probe ∧ no vacuity/inversion),
`static_reject_class`, `sole_author_verified` (expected 0).

**Boundary (not scored):** `oos3` (Nash existence).

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
