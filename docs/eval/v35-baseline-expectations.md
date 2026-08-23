# v3.5 Phase 1 — P2 baseline expectations (BEFORE the re-probe run)

**Date:** 2026-08-23 · **Branch:** `v35/intelligence-sprint`
**Instrument:** `verifier.probe_statement_compiles` (wrap bug FIXED
2026-08-17) + `eval_formalizer.classify_probe_failure`.
**Method:** re-compile already-stored `statement_text` from formal
artifacts. Zero provider calls. **Dev diagnostic only** — sealed sets
(v3h*, v3h2, v3h3, v4h1) are excluded entirely; nothing here unspends
them and none of these numbers is the earn number (that is `v35h1`,
fresh, one pass).
**Population:** every non-sealed formal artifact with `statement_text`,
partitioned by provenance:

- `model_draft` — `provenance.capability == "formalize"` without
  `source == "from_file"` / reviewer-authored markers.
- `reviewer_authored` — everything else (recovery path); reported
  separately, never pooled into a model rate.

## Predictions (written before any compile ran)

| # | Prediction | Conf |
|---|---|---|
| B1 | Model-draft population is small (< 10 unique statements) — most surviving artifacts came from reviewer recovery | high |
| B2 | Model-draft elaborates_rate < 0.5 (v4h1 saw 0/5; no lever since targets P2) | high |
| B3 | Dominant failure class on model drafts: `unknown_identifier` (bare Core names / missing imports), then `type_mismatch` | medium |
| B4 | Reviewer-authored statements elaborate ≥ 0.7 (they reached VERIFIED paths) | medium-high |
| B5 | At least one probe result differs from its stored `statement_probe.compiles`, exposing exactly how much the wrap bug distorted v3-era numbers | medium |

## Actuals (2026-08-23, post-run — see v35-baseline-reprobe.json)

| # | Actual | Match? |
|---|---|---|
| B1 | model_draft population **n=8** unique statements (< 10) | ✅ |
| B2 | model_draft elaborates_rate **0.500** (4/8). Prediction was strictly `< 0.5` — landed **on the boundary**: ❌ MISS by tie, direction correct | ❌ (boundary) |
| B3 | Dominant failure classes: `binder_annotation` ×2, `syntax` ×2 — **no `unknown_identifier` at all** (D1/FQ promotion appears to have eliminated that class on these texts) | ❌ MISS |
| B4 | reviewer_authored elaborates_rate **0.800** (4/5) ≥ 0.7 | ✅ |
| B5 | **11/13** stored-vs-fresh probe mismatches (mostly `False→True`: v2p1-A/B/C, v3p1-A recorded non-compiling under the buggy axiom-wrap but elaborate cleanly) | ✅ EXCEEDED |

## Findings that shape Phase 2

1. **The v3-era probe numbers were wrong, now measured:** the buggy
   wrap flipped clean statements to FAIL. Historical `probe FALSE`
   scorecard rows predating 2026-08-17 are unreliable as P2 evidence.
2. **P2 failure surface on dev texts is narrow:** `binder_annotation`
   and `syntax` account for all four model-draft failures. Both are
   mechanical/prompt-addressable shapes — this is the Phase 2 lever
   target list, grounded in class data rather than stderr anecdotes.
3. **Compile≠pass caveat preserved:** one "elaborates" row (c3)
   carries `declaration uses 'sorry'` — counted as a P2 *signal* pass,
   never as quality. The scorer keeps sorry out of `draft_complete`.
4. Classifier hardened with two real-world shapes found by this run
   (RED-first: `test_classify_probe_failure_shapes_seen_in_reprobe`).

Attribution: Hermes Agent (Nous Research) under CTO direction.
