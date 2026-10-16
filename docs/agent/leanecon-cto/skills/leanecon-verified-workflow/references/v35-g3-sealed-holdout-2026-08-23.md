# v3.5 G3 — sealed holdout v35h1 execution record (2026-08-23)

Session detail for `leanecon-verified-workflow` §4 "Sealed-holdout
mechanics". Branch `v35/intelligence-sprint` @ `99455fe`; predictions
committed pre-run @ `5f60ee2`; DECISION_LOG 54.

## Result

`formalizer-v35h1`, n=3, ONE pass, SPENT:

| Case | Claim | Attempts | Probe | draft_complete |
|---|---|---|---|---|
| A | strict monotonicity ⇒ strict preference | 2 | ✓ after repair | ✓ |
| B | CE bundle ∈ endowment budget set | 3 | ✗ | ✗ |
| C | expenditure ≥ 0 under nonnegativity | 1 | ✓ first try | ✓ |

audit_clean 3/3 · elaborates 2/3 · **draft_complete 2/3 = 0.667 ≥ 0.60
— earn target MET** (prior sealed v4h1 was 0/5 under the same frozen
strict conjunction).

## What actually happened per case

- **A — the recovery pair.** Attempt 1 invented `Bundle goods`; probe
  failed with `instance_synthesis` (`Preorder (Bundle goods)` not
  synthesizable). The Diagnosis directive went into attempt 2's prompt;
  attempt 2 compiled. First live probe-failure→recovery under the L1
  lever. Temporal association confirmed; causality NOT claimed at n=1.
- **B — honest non-repair + infra confound.** Attempt 1 failed on a
  STALE `LeanEcon.Core.Constraints.budgetSet.olean` (workspace build
  hygiene, not model signal; classified honestly as `unclassified`,
  directive correctly refused to guess). Attempts 2–3 repeated the
  IDENTICAL self-inflicted type error (`e i : ι` where `ι → ℝ`
  expected, same position) despite the `type_mismatch` directive.
  Lesson recorded both ways: the directive points, it cannot force.
- **C — clean single-attempt pass**, including the `none_noted`
  reviewer ack path firing exactly as designed.

## Prediction ledger

9 HIT (incl. 1 EXCEEDED) · 1 SPLIT (recorded both ways) · 1 N/A
(preflight script no longer exists). Headline draft_complete≥2/3 was
predicted at 0.40 confidence — genuine uncertainty stated BEFORE the
run, hit anyway. Case-level calls were 3/3 (B called as the failure).

## Mechanics that mattered (now §4 pitfalls)

1. Near-verbatim collision: original C draft ≈ spent v3h3-C; redesigned
   to nonneg-expenditure BEFORE freezing. Deconflict against ALL claim
   texts, not just verbatim.
2. Digest integrity: manifest pins raw-text sha256; the CLI `digest=`
   display hashes a different input — verify at the record level before
   concluding drift (A checked out exact).
3. Stale olean burned an attempt: `lake build` freshness check belongs
   BEFORE the pass, not after the first weird failure.
4. Scoring: ONE pass from artifacts, recomputing
   `_revision_feedback_block(history[:k])` to prove what the model
   actually saw (P8a-style verification).

Repo evidence: `docs/eval/v35h1-manifest.json`,
`docs/eval/v35h1-expectations.md` (predictions + actuals),
`docs/eval/v35h1-score.json` (payload),
`docs/gate3/DECISION_LOG.md` #54.

Attribution: Hermes Agent (Nous Research) under CTO direction.
