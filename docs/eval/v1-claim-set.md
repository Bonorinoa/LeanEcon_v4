# v1 candidate claim set (frozen)

Frozen for eval regression and release evidence. Local artifacts under
`artifacts/local/a3/` (gitignored) are operational records; this table is
the **normative** endpoint list.

| Claim id | Domain | Expected endpoint | Notes |
|---|---|---|---|
| c1 | consumer / attainable | **VERIFIED** | walkthrough; Core later optional |
| c2 | preferences / transitive | **VERIFIED** | walkthrough |
| c3 | utility / strict mono | **VERIFIED** | walkthrough |
| c4 | monotone order | **VERIFIED** | walkthrough; Mathlib-heavy |
| fwt1 | FWT / CE → PE | **VERIFIED** | Gate 6–7 seed; Core theorem exists |
| oos1 | IR at CE | **VERIFIED** + `12_core_pin` | OOS 2026-08-08 |
| oos2 | budget expansion | **VERIFIED** + `12_core_pin` | recovery path case |
| oos3 | mixed Nash | **FORMALIZED** (boundary) | no Core game theory; not v1 VERIFIED target |
| c1r2 | same-text re-run | FAILED / experimental | not a release gate |

## Fixtures

Reviewed Lean proofs: `tests/fixtures/lean/` and `tests/fixtures/lean/walkthrough/`.

## Scoring

See `formalizer-scorecard.md` and `interpreter-scorecard.md`. Do not treat
model draft success as VERIFIED success.
