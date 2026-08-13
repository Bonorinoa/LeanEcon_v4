# Formalizer scorecard (v0.3 / v1 baseline)

**Model:** labs-leanstral-1-5 (via adapter MVP map)  
**Role:** drafting aid only  
**Sources:** walkthrough 2026-08-06, fwt1, OOS 2026-08-08

## Live batch summary

| Claim | Statement valid? | Compiles (probe)? | Vacuity / inversion? | Core-id / D1? | Endpoint without reviewer formal? |
|---|---|---|---|---|---|
| c1 | weak (vacuous) | mixed | vacuity | id scheme issues | no — reviewer proof |
| c2 | no (bad binder) | fail | — | id issues | no |
| c3 | no (`sorry` body) | — | — | — | no |
| c4 | yes | yes | no | better | reviewer still owned proof |
| fwt1 | structural inversion | fail/probe | **inversion** | title-id gaps | no |
| oos1 | vacuous `True` hyps | fail | vacuity | **0 core rows** | no |
| oos2 | 2× `:=` reject | n/a | — | n/a | no artifact |
| oos3 | 2× D1 bare core | n/a | — | D1 caught | no |

## Rates (qualitative baseline — not a leaderboard)

| Metric | Observation |
|---|---|
| Statement-valid first try | low (~1/8 clean) |
| Static reject catch rate | high (sorry/`:=`/D4/D1) |
| Core FQ compliance when attempted | poor; D1 earned keep |
| Suitable as sole author of VERIFIED | **0%** — reviewer proof load-bearing |

## v2 record (2026-08-09 — Phase 1 claims + revision-loop evidence)

Model: labs-leanstral-1-5 (unchanged). Claims v2p1-A/B/C: fresh OOS,
simple-class, all three ended VERIFIED via the CTO-authorized reviewer
recovery path (v1 `formalize --from-file`).

| Claim | Live attempts (waves) | Attempt outcomes | Audit/contamination | Recovery → endpoint |
|---|---|---|---|---|
| v2p1-A | 2 | wave1 `:=` body (line 1); wave2 `:=` body | static reject ×2; no artifact (v1 guard) | reviewer from-file → FORMALIZED → VERIFIED |
| v2p1-B | 2 | wave1 `sorry` + `:=` (line 25) | **contamination caught pre-kernel** (B2 lesson live) | reviewer from-file → VERIFIED |
| v2p1-C | 2 | wave1 `:=` body; wave2 `:=` body | static reject ×2; mapping drift (added non-source quantifiers) flagged at EI review | reviewer from-file (D1 fixes) → VERIFIED |

Loop evidence (Phase 2, `src/leanecon/revise_loop.py` + `tests/test_revise_loop.py`):
- Contamination gate: a sorry-carrying draft is rejected by audit even when
  a naive probe reports "compiles" — test + live (v2p1-B) evidence.
- Budget: MAX_REVISION_ATTEMPTS=3 enforced; no silent 4th attempt (test).
- Attempt distribution (live): 2 waves × 3 claims, all static-rejected;
  reviewer recovery per v1 surface (unchanged).

| Metric (v2 set) | Observation |
|---|---|
| Statement-valid first try (live) | 0/3 (consistent with v1 ~1/8) |
| Static reject catch rate | 6/6 attempts caught (2 waves × 3) |
| Contamination caught before kernel | 1/1 (v2p1-B `sorry`) |
| Suitable as sole author of VERIFIED | unchanged **0%** — reviewer proof load-bearing |

Phase 3 (2026-08-09 / shipped 2026-08-12 Phoenix): skeleton contract
shipped (`src/leanecon/skeleton.py`, 5 Red-first tests green, suite 176).
Edit-distance / time-to-VERIFIED measurement on v2p1 proofs DEFERRED —
no measurement rows yet; contract only. Not a v2 claim of 60–70% draft
completion.

## v3 held-out (2026-08-13 — FINAL pipeline)

Held-out v3h-A/B/C/D (frozen split `docs/eval/v3-claim-split.md`).

| Claim | Attempts | Outcome | Probe (axiom-wrap) | draft_complete |
|---|---|---|---|---|
| v3h-A | 3 | FORMALIZED | **TRUE** | ✅ |
| v3h-B | 3 | FAILED, no artifact | n/a | ❌ |
| v3h-C | 3 | FORMALIZED | FALSE (metavars) | ❌ |
| v3h-D | 2 | FORMALIZED | **TRUE** | ✅ |

| Metric | Value |
|---|---|
| first_try_valid | **0/4** |
| attempts_to_valid | A=3, B=null, C=null, D=2 |
| draft_complete (60–70% predicate) | **2/4 = 50%** |
| static rejects | D1 (C t2–t3, A t1), `:=` (A t1) |
| sole_author_verified | **0** |
| 60–70% verdict | **MISSED** (needs 3/4) |

Probe amendment (METRICS §3.1 operationalization): bare signatures can
never compile as `theorem` (Lean requires a body); probe rewrites to
`axiom` to measure signature elaboration. Kernel audit untouched.

## v3 Phase 1 (2026-08-13 — loop wired + live same-text set)

`a3_runner.formalize_claim` calls `revise_statement_draft`
(`MAX_REVISION_ATTEMPTS=3`). Unit suite **180**. Live set: v3p1-A/B/C
(same text as v2p1-A/B/C; new ids; D4).

| Claim | Attempts | Outcome | Probe | Notes |
|---|---|---|---|---|
| v3p1-A | 1 | FORMALIZED | fail | audit-clean first try; 4 mapping gaps; `walrasian_demand_exhausts_budget` |
| v3p1-B | 3 | FAILED, no artifact | n/a | `:=` body + D1 (core rows used Lean types, not FQ Core ids) |
| v3p1-C | 2 | FORMALIZED | fail | attempt 1 `:=` caught; attempt 2 signature-only; 10 mapping gaps |

| Metric (v3p1 set) | Observation |
|---|---|
| Statement-valid first try (audit-clean) | **1/3** (A). Not 60–70%. Probe still fail on both FORMALIZED. |
| attempts_to_valid | A=1, B=`null`, C=2 |
| Budget / no 4th | held (B exhausted at 3) |
| Contamination / `:=` still fails | held (B no artifact; C attempt 1 rejected then cleaned) |
| Suitable as sole author of VERIFIED | **0%** — no model proof verified; `--from-file` still recovery |
| 60–70% draft-complete | **not claimed** |

## Tooling that remains load-bearing

`validate_statement_text`, `validate_scaffolding_namespace`, D1 FQ check,
compile probe, vacuity warning, gap classification, **`formalize --from-file`**.

**Attribution:** Hermes under CTO; not a claim of model quality parity with any public bench.
