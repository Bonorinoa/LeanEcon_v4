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

## Tooling that remains load-bearing

`validate_statement_text`, `validate_scaffolding_namespace`, D1 FQ check,
compile probe, vacuity warning, gap classification, **`formalize --from-file`**.

**Attribution:** Hermes under CTO; not a claim of model quality parity with any public bench.
