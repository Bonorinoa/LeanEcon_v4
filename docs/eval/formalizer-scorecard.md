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

## Tooling that remains load-bearing

`validate_statement_text`, `validate_scaffolding_namespace`, D1 FQ check,
compile probe, vacuity warning, gap classification, **`formalize --from-file`**.

**Attribution:** Hermes under CTO; not a claim of model quality parity with any public bench.
