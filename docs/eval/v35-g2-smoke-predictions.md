# G2 smoke predictions — v35smk-A (committed BEFORE any live call)

**Date:** 2026-08-23 · **Success definition (G2):** FORMALIZED ∧
`statement_probe.compiles=true` within ≤3 attempts, zero weakened checks.
Same-text technique: source text identical to canonical `v4smk-B`
(dev fixture text; no new semantic approval needed), fresh claim id.
Prior on THIS text: v4smk-B ran 3 audit-clean attempts, probes False×3
(pre-diagnosis era).

| # | Step | Prediction | Conf | Rationale |
|---|---|---|---|---|
| P1 | ingest v35smk-A | DRAFT created, no INPUT_REJECTED | 0.99 | plain PROJECT-class text |
| P2 | interpret | INTERPRETED → REVIEW_REQUIRED; EI carries ≥3 definitions incl. goods/prices/bundles | 0.90 | simple-class envelope |
| P3 | review (hermes, ai) | APPROVE → ACCEPTED, no none_noted ack needed | 0.95 | mirrors v4smk-B approval-1 |
| P4 | formalize reaches FORMALIZED (audit-clean within 3) | yes | 0.85 | v4h1 went 5/5 audit-clean |
| P5a | ≥1 in-loop probe failure occurs (some attempt probe_compiles=false) | yes | 0.60 | ∑-notation + binder choices are exactly where drafts slip |
| P5b | if attempt k failed probe and attempt k+1 ran: recomputed `_revision_feedback_block(history[:k])` contains a `Diagnosis` line | yes | 0.97 | pure function, unit-tested; recomputed post-hoc from stored artifact |
| P5c | attempt-1 failure class (if any) ∈ {syntax, binder_annotation, type_mismatch} | yes | 0.75 | these dominate the model-draft surface on dev texts |
| P6 | **SUCCESS: FORMALIZED ∧ fresh probe True ≤3 attempts** | **yes** | **0.50** | honest coin-flip: text went 0/3 pre-lever; the Diagnosis targets exactly binder/syntax shapes; one smoke ≠ evidence, it's a canary |

Honesty notes: P6 at 0.50 is a genuine 50/50 — recorded as such. A miss
does NOT fail Phase 2 (fixture gates already green); it downweights the
lever and feeds the next card. A hit is one data point, not a rate.
