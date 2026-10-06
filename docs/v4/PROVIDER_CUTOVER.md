# Provider cutover — OpenRouter free router (DL 57)

**Date:** 2026-10-06 · **Branch:** `provider/openrouter-free`
**Status:** implemented on the v4 development line. Historical eval
records that name `labs-leanstral-1-5` / `mistral-medium-3-5` stay
historical; they are not the live pin.

## Why

Mistral models are deprecated from active LeanEcon projects and the
subscription is being cancelled. The live egress cannot keep
`api.mistral.ai` or `MISTRAL_API_KEY`.

## Live pin

| Item | Value |
|---|---|
| Provider | OpenRouter |
| Credential | `OPENROUTER_API_KEY` (profile `.env`; never in the repo) |
| Model slug | `openrouter/free` |
| Adapter | `leanecon.adapters.openrouter.OpenRouterAdapter` |
| Endpoint | `https://openrouter.ai/api/v1/chat/completions` |

Every capability (`interpret`, `formalize`, `prove_or_repair`,
`semantic_triage`, `diagnostic_probe`, `opinion`) maps to that slug.
FORMALIZE remains a distinct *slot* so a later Lean-specialist pin can
diverge without touching OPINION (D1 still: opinion reuses interpret).

No silent fallback. A 402 is a paid-path bug, not a cue to fund an
account. The adapter records the *routed* model from the provider
response when present (provenance), while the request body carries the
pin exactly.

## Routers considered

| Slug | Cost | Role in this sprint |
|---|---|---|
| `openrouter/free` | $0; random free model that supports the request | **Live pin** |
| `openrouter/auto` | billed at the routed model | Not pinned. Paid. |
| `typesafe/jev-router` | billed at the routed model | Not pinned. Chat-completions compatible, but not zero-cost. |
| `typesafe/jev-1.13` | input-token priced; typed decisions, not prose | Not a formalizer. Future candidate for triage / machine-block classification only. |

## HuggingFace (complementary, not this sprint)

HF is the obvious open-weight catalog, not a free 119B inference API.

- `HF_TOKEN` exists on the default Hermes profile and is **not** wired
  into LeanEcon. Adding it would be a second provider boundary.
- Leanstral 1.5 (`mistralai/Leanstral-1.5-119B-A6B`, Apache-2.0) is
  open-weight. Mistral's published vLLM example uses 4-way tensor
  parallelism and a 200k context cap. That is a hardware project, not a
  serverless swap.
- Practical HF inference later: (1) OpenRouter already proxies many
  HF-hosted `:free` / paid models — stay on the single adapter;
  (2) Hugging Face Inference Endpoints (paid GPU); (3) local
  vLLM / TGI / llama.cpp for small models. None of these is in scope
  until the CTO opts into a second adapter or a self-host budget.

Gate 3 still forbids multi-provider work in core. Do not add a
HuggingFace adapter on this cutover.

## What changed in code

- Deleted `src/leanecon/adapters/mistral.py`.
- Added `src/leanecon/adapters/openrouter.py`.
- Runners, FakeAdapter, architecture-boundary tests, and provider
  contract tests follow the new module and credential name.
- Operator wrappers `scripts_local/a3_run.py` and
  `scripts_local/a1_live_probe.py` already load `OPENROUTER_API_KEY`.

## What did not change

Historical scorecards, sealed-holdout JSON, walkthroughs, and shipped
release packets keep the model ids that actually ran. Rewriting those
would falsify evidence. Live operator surfaces (README, DEVELOPMENT,
`docs/gate3/04-provider-contracts.md`, this file, DECISION_LOG 57)
carry the current pin.

## D4 A/B

`docs/v4/experiments/D4-model-ab-card.md` is **superseded**. The
unsubscribe is the re-open trigger that card named (retirement /
unavailable incumbent). There is no Mistral PAYG fallback.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
