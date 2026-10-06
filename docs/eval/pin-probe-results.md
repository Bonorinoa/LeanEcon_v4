# Pin probe — candidate free slugs (results)

**Date:** 2026-10-06 · **Predictions:** written before the run
(`artifacts/local/orfree-e2e/pin-probe-predictions.md`)
**Prompts:** the real `interpret_prompt` / `formalize_prompt`
**Method:** direct OpenRouter chat-completions calls, n=2 per slug,
no `max_tokens`, 300s per-call timeout. Zero $ (free tier).

## Results

| Capability | Slug | n | JSON ok | Required shape | Latency (s) | Median |
|---|---|---|---|---|---|---|
| interpret | `openrouter/free` | 2 | 2/2 | 2/2 | 88.1, 14.1 | 51.1 |
| interpret | `nvidia/nemotron-3.5-lightning:free` | 2 | 0/2 | 0/2 | 0.09, 0.11 | **404** |
| formalize | `openrouter/free` | 2 | 2/2 | 2/2 | 206.9, 315.3 | 261.1 |
| interpret | `cohere/north-mini-code:free` | 3 | 3/3 | 3/3 | 52.2, 36.2, 24.0 | **36.2** |
| formalize | `cohere/north-mini-code:free` | 3 | **2/3** | 2/3 | 172.0, 295.5, 160.5 | 172.0 |
| formalize | `poolside/laguna-s-2.1:free` | — | not run | — | — | — |

`north-mini-code` was run on the real prompts n=3 (see
`artifacts/local/orfree-e2e/candidate-*.json`). The `laguna` leg was
not run: after the first three slugs the evidence was already
inconclusive, and the marginal cost is ~5 min per draw.

## The finding that matters: account guardrails silently remove endpoints

`nvidia/nemotron-3.5-lightning:free` — the **#3 free model on
OpenRouter by 7-day usage** — returns **HTTP 404**:

```
0 endpoints out of 1 requested are available matching your guardrail
restrictions and data policy. ...
Free model training violation (account settings): 1 endpoint excluded;
configurable at https://openrouter.ai/s...
```

So the account's OpenRouter data-policy setting excludes free
endpoints that train on submitted data. Consequences:

1. **The eligible free pool is smaller than the catalogue.** A slug can
   be listed, popular, and still unusable from this account.
2. **`openrouter/free` routes only among *eligible* free models**, so
   its latency/variance reflects a shrunken pool — plausibly the
   direct cause of the orfree E2E timeouts (600s formalize, 217s
   empty-content interpret).
3. Any future pin choice must be validated against the account
   guardrails, not just the catalogue page.

Changing the OpenRouter privacy/data setting is a **user-account
decision**, not a repo change. Do not flip it from an agent session.

## Prediction vs actual

| # | Predicted | Actual |
|---|---|---|
| 1 | free-router interpret median 10–60s | 51.1s ✅ |
| 2 | ≥1 empty/timeout draw in 2 | 0 in 2 (both shaped) ❌ |
| 3 | nemotron faster than free-router | technically 0.1s but **404**, not speed ❌ |
| 4 | nemotron shape ≥1/2 | 0/2, policy-excluded ❌ |
| 5 | free-router formalize ≥1 draw >120s | 206.9s and 315.3s ✅ |
| 8 | no 402 anywhere | 402 none; **404 policy exclusion** found ⚠️ |

## Conclusion

**No pin swap is justified on this evidence.**

| | `openrouter/free` | `cohere/north-mini-code:free` |
|---|---|---|
| interpret | 2/2 shape, 14–88s (median 51s) | 3/3 shape, 24–52s (median **36s**) |
| formalize | 2/2 shape, 207–315s (median 261s) | **2/3** shape, 160–296s (median **172s**) |
| reproducibility | **random model per call** | named, deterministic slug |

The candidate is faster on both capabilities and much faster on
interpret, but it produced **one malformed (non-JSON) formalize draw in
three**. The router was shape-valid on both of its draws, but slower,
and — more importantly for an auditable system — it routes to a
**random model per call**, so a provenance record cannot be
reproduced.

n is tiny (2–3 per cell). Neither slug wins decisively.

**Recommendation:** keep `openrouter/free` as the live pin. If runtime
or reproducibility is to be bought down, run a *powered* dev-fixture
A/B (n≥8, predictions first) between the router, `north-mini-code`, and
`laguna-s-2.1` before any `MVP_MODEL_MAP` edit. Do not swap on n=3.

**Attribution:** Hermes Agent under CTO direction. Not a sealed
holdout. Not a tag.
