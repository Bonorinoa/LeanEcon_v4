# orfree E2E — predictions (committed before live calls)

**Date:** 2026-10-06
**Pin:** `openrouter/free` / `OPENROUTER_API_KEY`
**Protocol:** same-text/new-id for A/B; one fresh adversarial simple-class
claim for C. Not a sealed holdout. Not a tag. n=3 smoke.
**Baselines (Mistral-era, archived):** interpret schema-valid high on
medium-3.5; formalize first-try-valid ~0–1/8 leanstral; v35h1
draft_complete **2/3**; sole-author VERIFIED **0%**.

Frozen METRICS (`docs/v3.5/METRICS.md`): `draft_complete` = audit-clean
∧ probe compiles ∧ non-vacuous ∧ non-inverted.

## Claims

| Id | Text source | Why adversarial |
|---|---|---|
| `orfree-A` | same-text as `c1` (budget expand ⇒ attainable does not shrink) | historically vacuous formalize; tests JSON EI + P4 |
| `orfree-B` | same-text as `c2` (weak preference transitive) | historically bad binder; tests Lean surface P1 |
| `orfree-C` | fresh: "If all prices are zero and income is nonnegative, every nonnegative bundle is affordable." | degenerate budget; invites vacuity / ill-typed ℝ sums; not in stored `source_text` |

## Numbered predictions (before any live call)

| # | Step | Expected | Conf. | Rationale |
|---|---|---|---|---|
| 1 | ingest A/B/C | DRAFT, exit 0 | 0.95 | no gold/RESTRICTED markers |
| 2 | interpret A | schema-valid EI, REVIEW_REQUIRED | 0.45 | free router is random; JSON discipline is luck vs medium-3.5 |
| 3 | interpret B | schema-valid EI | 0.45 | same |
| 4 | interpret C | schema-valid **or** FAILED INVALID_OUTPUT | 0.50 | degenerate claim may still parse; model may ramble |
| 5 | interpret observability | provenance.model is a concrete routed slug ≠ only `openrouter/free` **or** equals `openrouter/free` if router omits `model` | 0.70 | adapter records `raw.model` |
| 6 | review A/B/C (AI, none_noted ack if needed) | ACCEPTED | 0.80 | we approve drafts that validate; meaning is not earned |
| 7 | formalize A | not draft_complete; likely static reject or non-compiling | 0.75 | leanstral already vacuous here; generalist free model worse |
| 8 | formalize B | not draft_complete; P1 reject (sorry/`:=`/binder) | 0.70 | historical c2 class |
| 9 | formalize C | not draft_complete; vacuity **or** type_mismatch | 0.65 | zero prices |
| 10 | formalize first_try_valid | 0/3 | 0.70 | historical ~0; free router not Lean-trained |
| 11 | draft_complete | 0/3 | 0.60 | vs v35h1 2/3 this is the accuracy-hurt test |
| 12 | runtime interpret | 5–90 s each; ≥1 call >30 s | 0.55 | reasoning free models |
| 13 | runtime formalize | 30–240 s each (≤3 attempts + probe) | 0.60 | probe is 10–20 s per attempt when Lean is warm |
| 14 | BLOCKED / 402 | 0 | 0.75 | pin is free router; 402 would be a bug |
| 15 | opinion after formalize (if FORMALIZED) | consultative artifact, state unchanged | 0.70 | DL 55 |

**Hurt threshold (pre-committed):** accuracy hurt if interpret
schema-valid < 2/3 **or** draft_complete < 1/3 (drop vs v35h1 2/3).
Observability hurt if routed model / latency missing on a HEALTHY
response. Runtime hurt if a single interpret or formalize exceeds 4
minutes or the batch cannot finish from provider timeouts.

If hurt: browse OpenRouter free-variant catalogue and propose pins.
If not: keep `openrouter/free`.

**Attribution:** Hermes Agent under CTO direction. Predictions locked
before live calls.
