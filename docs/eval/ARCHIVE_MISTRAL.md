# Archive — Mistral-era live results

**Status:** historical. Mistral is unsubscribed (DECISION_LOG 57,
2026-10-06). These files record what actually ran under
`mistral-medium-3-5` / `labs-leanstral-1-5`. Do not treat them as
the live pin. Do not rewrite the model ids.

Live pin: `openrouter/free` via `leanecon.adapters.openrouter`.
Packet: `docs/v4/PROVIDER_CUTOVER.md`.

## Scorecards and holdouts (committed)

| Path | What it is |
|---|---|
| `docs/eval/interpreter-scorecard.md` | interpret on `mistral-medium-3-5` |
| `docs/eval/formalizer-scorecard.md` | formalize on `labs-leanstral-1-5` |
| `docs/eval/v35h1-score.json` | sealed holdout draft_complete 2/3 (leanstral) |
| `docs/eval/v35-baseline-reprobe.json` | leanstral reprobe |
| `docs/eval/v4h1-*.json` | prior sealed set (leanstral, 0/5 elaborates) |
| `docs/eval/v3h3-*.json` | spent v3 holdout |
| `artifacts/a1/evidence-20260805/` | A1 live C4–C6 under Mistral |

## Local walkthrough artifacts (gitignored)

`artifacts/local/a3/claims/*.json` and matching `eis/`, `formal/`,
`bundles/` were produced under the Mistral pin unless the claim id
starts with `orfree-`. Leave them on disk as evidence; do not delete.

## What was deleted (do not restore)

- `src/leanecon/adapters/mistral.py`
- `MISTRAL_API_KEY` / `api.mistral.ai` live wiring
- `scripts/mistral_preflight.py`

**Attribution:** Hermes Agent under CTO direction.
