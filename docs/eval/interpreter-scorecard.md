# Interpreter scorecard (v0.3 / v1 baseline)

**Model:** mistral-medium-3-5  
**Role:** meaning hypothesis for review (never self-certifies)

## Observations (walkthrough + OOS)

| Claim | Schema-valid EI? | `none_noted` discipline | Solution concept | Missed semantic edges |
|---|---|---|---|---|
| c1–c4 | yes (after validation) | exercised | mostly null / local | attainable reading ambiguity |
| fwt1 | yes | ok | CE present | `[Nonempty Agent]` empty-economy |
| oos1 | yes | ok | Walrasian EQ | — |
| oos2 | yes | ok | null | `[Nonempty Goods]`, `DecidableEq` |
| oos3 | yes | ok | mixed Nash | domain outside Core |

## Rates (qualitative)

| Metric | Observation |
|---|---|
| Schema-valid after parse | high (invalid → FAILED) |
| Empty ambiguities without `none_noted` | blocked by business rules |
| Reviewer revision churn | common (rev-1 draft → rev-2 accepted) |
| Suitable as unreviewed truth | **never** |

**Attribution:** Hermes under CTO.
