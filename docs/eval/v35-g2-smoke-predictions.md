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

---

## RESULTS (2026-08-23, run after commit `b78cf9c`)

| # | Verdict | Actual |
|---|---|---|
| P1 | ✅ HIT | DRAFT r1, PROJECT, digest `8006f99d…` |
| P2 | ✅ HIT | INTERPRETED → REVIEW_REQUIRED; objects goods, p, x, y; 2 ambiguities |
| P3 | ✅ HIT | hermes/ai APPROVED → ACCEPTED, EI rev 2 `d48399fa…`, no ack needed |
| P4 | ✅ HIT (beat) | audit-clean on **attempt 1** (predicted within-3 @ 0.85) |
| P5a | ❌ MISS | **zero** probe failures occurred (predicted ≥1 @ 0.60) |
| P5b/P5c | ⚪ N/A | conditionals never triggered — no failed probe existed |
| P6 | ✅ **HIT** | **FORMALIZED ∧ fresh probe True, attempt 1 ≤ 3** |

Artifact: `artifacts/local/a3/formal/v35smk-A/rev-1.json` — target
`cost_monotone_componentwise`; genuine `[Fintype ι]` instance binder;
D4-compliant scaffolding namespace; no sorry; vacuity None; 11 mapping
rows (CLI-reported 4 genuinely_missing gaps recorded by the runner;
PROVING correctly blocked pending gap-ack — left open, out of smoke
scope); provenance `labs-leanstral-1-5`.

**Attribution caveat (recorded deliberately):** the Phase 2 Diagnosis
path NEVER FIRED in this run — there was no probe failure to diagnose.
The first-try elaborating draft is a win for the post-v3 pipeline +
fixed verifier (+ possibly the v4 format exemplar), and a striking
single-sample contrast with the same text's pre-lever record
(v4smk-B: 3 attempts, probes False ×3, draft_complete false; now
draft_complete true) — but it is NOT attributable to the L1 lever.
Lever evidence remains the fixture suite (11 tests) until a holdout
produces actual probe-failure→recovery pairs.

Tally: 5 HIT · 1 MISS · 2 N/A.
