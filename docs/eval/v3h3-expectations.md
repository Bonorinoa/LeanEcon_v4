# v3h3 sealed holdout — predictions BEFORE live run

**Date:** 2026-08-16
**Branch:** `v3/phase1-wire-loop` @ `e1f84e7`
**Set:** v3h3-A/B/C/D/E (CTO approved as proposed 2026-08-16)
**Protocol:** `formalizer-sealed-1` — claim text is not committed.
**Purpose:** beliefs vs pipeline. Do not edit the Expected column after
the fact. One live pass only. This set becomes spent after scoring.

Threshold: 60% of n=5 is **3/5**. 2/5 = 40% = missed.

## Predictions

| # | Step | Expected | Confidence | Rationale |
|---|---|---|---|---|
| 1 | preflight ping | HTTP 200 | 0.6 | PAYG key worked 2026-08-13; 3 days stale |
| 2 | ingest v3h3-A..E | DRAFT ×5, new ids, no gold reject | 0.95 | fresh texts; no gold markers |
| 3 | interpret live | REVIEW_REQUIRED ×5 | 0.7 | interpreter 3/3 schema-valid on v3p1 |
| 4 | review (AI hermes) | ACCEPTED ×5 (none_noted ack if needed) | 0.7 | simple-class; AI reviewer exercised |
| 5 | formalize v3h3-A | audit-clean ≤3; probe mixed; draft_complete **no** | 0.35 | homogeneity needs λ>0 algebra; D1/`:=` likely |
| 6 | formalize v3h3-B | audit-clean ≤3; probe TRUE possible; draft_complete **maybe** | 0.45 | le_refl membership; easiest of the five |
| 7 | formalize v3h3-C | audit-clean ≤3; draft_complete **no** | 0.30 | close to v2p1-B which never live-drafted clean |
| 8 | formalize v3h3-D | audit-clean ≤3; probe mixed; draft_complete **maybe** | 0.40 | definitional clearing; Fintype/import risk |
| 9 | formalize v3h3-E | audit-clean ≤3; draft_complete **no** | 0.25 | inversion class (IR as hyp); D1 on budgetSetEndowment |
| 10 | first_try_valid | **0/5** | 0.80 | 0/8 on spent splits |
| 11 | draft_complete | **1/5 or 2/5** (B and/or D) | 0.55 | historical 25%; B/D are the only plausible hits |
| 12 | 60–70% (need 3/5) | **MISSED** | 0.80 | would need a step-change the loop has not shown |
| 13 | sole_author_verified | 0 | 0.99 | no model proof |
| 14 | spent v3h/v3h2/v2p1 untouched | unchanged | 0.95 | new ids only |
| 15 | provider BLOCKED | possible; record honestly | 0.25 | 402 maps to INVALID_OUTPUT; a3_run may trip approval |

## Actuals (fill after)

| # | Actual | Match? |
|---|---|---|
| 1 | HTTP 200, ping OK | ✅ |
| 2 | DRAFT ×5, distinct events, class=PROJECT | ✅ |
| 3 | REVIEW_REQUIRED ×5 | ✅ |
| 4 | ACCEPTED ×5 (hermes/ai); A/C none_noted ack | ✅ |
| 5 | A FAILED attempts=3; t1 sorry+`:=`; t2–3 `:=`; no artifact | ✅ (predicted no draft_complete) |
| 6 | B FORMALIZED attempts=3; first_try no; probe FALSE (syntax); 6 gaps | ❌ (predicted maybe draft_complete) |
| 7 | C FORMALIZED attempts=3; **first_try_valid yes**; probe FALSE; 2 gaps | ✅ (predicted no draft_complete) |
| 8 | D FAILED attempts=3; t1 `:=`+D4; t2–3 D4 (redefined marketClearing at root) | ❌ (predicted maybe draft_complete) |
| 9 | E FORMALIZED attempts=3; audit-clean at t2; probe FALSE; 3 gaps | ✅ (predicted no draft_complete) |
| 10 | first_try_valid **1/5** (C only) | ❌ (predicted 0/5) |
| 11 | draft_complete **0/5** | ❌ (predicted 1–2/5) |
| 12 | **60–70% MISSED** (need 3/5; got 0/5) | ✅ |
| 13 | sole_author_verified **0** | ✅ |
| 14 | v2p1-A still VERIFIED; v3h-A still FORMALIZED; v3h2-A still FAILED | ✅ |
| 15 | no BLOCKED; no 402 | ✅ (better than the 0.25 risk) |

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
