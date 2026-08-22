# v4h1 sealed holdout — predictions BEFORE live run

**Date:** 2026-08-17 · **Branch:** `v4/intelligence-sprint`
**Change under test (frozen):** `sanitize_signature_draft` +
`sanitize_core_mapping_rows` before audit; format exemplar in prompt.
Suite 224 green. Smoke: v4smk-A/B both FORMALIZED within budget
(baseline on these texts was 0/2).

**Set:** v4h1-A..E, sealed (`docs/eval/v4h1-manifest.json`,
protocol `formalizer-v4h1`). Texts NOT in the repo. One pass.

## Predictions

| # | Step | Expected | Conf |
|---|---|---|---|
| 1 | preflight | HTTP 200 | high |
| 2 | ingest ×5 DRAFT PROJECT | ✅ | high |
| 3 | interpret ×5 REVIEW_REQUIRED | ✅ | high |
| 4 | review approve (hermes/ai) ×5 ACCEPTED | ✅ | high |
| 5 | formalize audit-clean within budget | **≥3 of 5** (60%) | medium |
| 6 | identical-reject repeats across attempts | zero | high (mechanical repair) |
| 7 | probe compiles ≥1 | possible (B/D simplest) | low-med |
| 8 | draft_complete (audit-clean ∧ probe ∧ non-vacuous) ≥3/5 = +50% vs 2/13 | **uncertain** — probe is the wildcard | low |
| 9 | sole-author verified | 0 (no verify stage this sprint) | certain |

**Honest framing:** the lever targets audit-clean rate (prediction 5).
Draft_complete additionally needs the compile probe to pass, which no
repair addresses. If audit-clean hits ≥3/5 but draft-complete misses,
that is a PARTIAL result recorded honestly — the probe/elaboration
class becomes the next lever, not a hidden failure.

## Actuals (fill after)

| # | Actual | Match? |
|---|---|---|
| 1 | preflight HTTP 200 (ran earlier this session) | ✅ |
| 2 | ingest ×5 DRAFT, class PROJECT | ✅ |
| 3 | interpret ×5 REVIEW_REQUIRED | ✅ |
| 4 | review ACCEPTED ×5 (hermes/ai; B none-noted acked) | ✅ |
| 5 | audit-clean within budget **5/5** (all attempts_to_valid=1) | ✅ EXCEEDED (≥3) |
| 6 | zero identical-reject repeats; repair notes recorded each attempt | ✅ |
| 7 | probe compiles **0/5** (all elaboration failures) | ❌ (predicted low-med) |
| 8 | draft_complete **0/5** | ❌ MISS |
| 9 | sole-author verified 0 (no verify stage run) | ✅ |

## Verdict

- **Audit-clean: 2/13 (15%) → 5/5 (100%) on the new sealed set.** The
  lever fully closed its target classes (`:=` bodies, sorry, D4 root
  scaffolding, D1 core rows). Prediction 5 exceeded.
- **draft_complete 0/5 = the ≥50% intelligence target is NOT met** as
  measured by the v3 definition, because draft_complete requires the
  compile probe, and all five probes failed with elaboration errors —
  a failure class outside this lever's surface.
- Set is SPENT. One pass. No re-runs.

Attribution: Hermes Agent (Nous Research) under CTO direction.
