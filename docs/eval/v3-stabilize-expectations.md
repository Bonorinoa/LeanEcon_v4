# Predictions — v3 stabilize (Codex recovery)

**Written before** pytest / ruff / release-state / fixture scorers
were re-run after the recovery edits. Do not edit the Expected column
after the fact. Fill Actuals only.

**Scope of this run:** no live provider, no new held-out ingest, no
tag, no push. Spent splits `v3h` / `v3h2` stay frozen.

| # | Step | Expected | Confidence | Rationale |
|---|---|---|---:|---|
| 1 | `.venv/bin/python -m pytest -q` | all green; n ≥ 210 | 0.85 | 207 already green on the Codex tree; this slice adds release-state + sealed-protocol tests |
| 2 | `scripts/check_release_state.py` | exit 0, `release-state OK` | 0.95 | package is `3.0.0.dev0`; builder matches; `DEVELOPMENT.md` names both |
| 3 | `ruff check src tests scripts` | exit 0 | 0.80 | Codex applied format/lint; select is `E4,E9,F,I` |
| 4 | `ruff format --check src tests scripts` | exit 0 | 0.75 | mechanical wrap of the pre-existing 31-file backlog |
| 5 | `scripts/eval_formalizer.py --fixtures tests/fixtures/eval/formalizer` | `provider_calls == 0`, n=7 | 0.95 | existing Phase 2 contract; not touched semantically |
| 6 | `scripts/eval_semantic_reviews.py` on committed sealed fixtures | deterministic JSON; `case_count == 1`; `cases_with_two_reviews == 1` | 0.90 | fixtures authored in this slice; no live claims |
| 7 | gold-isolation scan | no new `FORBIDDEN_PATHS` | 0.95 | sealed fixtures live under `tests/fixtures/eval/semantic/`, not `gold/` |
| 8 | live `a3_run.py` formalize / new holdout | **not run** | 1.00 | v3h/v3h2 spent; no CTO-approved fresh texts; 60–70% stays MISSED |

## Actuals (fill after)

| # | Actual | Match? |
|---|---|---|
| 1 | 212 passed in 90.08s | ✅ (n=212 ≥ 210) |
| 2 | `release-state OK` exit 0 | ✅ |
| 3 | `ruff check` All checks passed | ✅ |
| 4 | `ruff format --check` 54 files already formatted (after one local wrap) | ✅ |
| 5 | `n=7`, `provider_calls=0` | ✅ |
| 6 | 11 protocol/release-state tests green; CLI tmp-fixture scored two faithful reviews, `cases_with_two_reviews=1` | ✅ |
| 7 | no new `FORBIDDEN_PATHS`; sealed fixtures are in-memory / tmp | ✅ |
| 8 | not run (as predicted) | ✅ |

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
