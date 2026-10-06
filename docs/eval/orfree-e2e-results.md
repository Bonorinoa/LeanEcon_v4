# orfree E2E results (OpenRouter free router)

**Date:** 2026-10-06 · **Pin:** `openrouter/free`
**Predictions:** `docs/eval/orfree-e2e-expectations.md` (commit `fd7b737`,
before live calls)
**Store:** `artifacts/local/a3/` · **Driver logs:**
`artifacts/local/orfree-e2e/` (gitignored)
**Adversarial tester:** Bot Mode `@adversarial-tester` is not reachable
(no `message_agent`). `delegate_task` to Nous also failed (no Portal
token). Predictions were written adversarially in-session instead.

Live adapter records the *routed* model on formalize provenance.
Interpret artifacts still omit provider metadata (observability gap).

## Claims

| Id | State | Notes |
|---|---|---|
| orfree-A | FORMALIZED (gaps=5) | same-text c1 |
| orfree-B | ACCEPTED, no formal | same-text c2; formalize timed out 600s |
| orfree-C | FAILED interpret | `PROVIDER_INVALID_OUTPUT` / missing content after 217s |

## Timings (seconds)

| Step | A | B | C |
|---|---|---|---|
| ingest | 0.11 | 0.08 | 0.08 |
| interpret | 20.9 | 22.9 | 180 timeout then 217.5 FAILED |
| review (AI) | 0.08 | 0.07 | n/a |
| formalize | 216.5 FORMALIZED | 600 TIMEOUT | n/a |
| opinion | 180 TIMEOUT | n/a | n/a |

## Accuracy (frozen METRICS)

| Metric | Result | v35h1 leanstral | Hurt vs threshold? |
|---|---|---|---|
| interpret schema-valid | 2/3 | high (qualitative) | no (`< 2/3` was the bar) |
| first_try_valid | 0/1 scored (A attempt1 HTTP 404) | ~0 historical | — |
| draft_complete | **1/3** (A yes; B timeout; C no formal) | **2/3** | no (`< 1/3` was the bar) |
| sole_author VERIFIED | 0/3 | 0% | no |

orfree-A `score_case`: `draft_complete=true`, `probe_compiles=true`,
`vacuity_flag=false`, `attempts_to_valid=2`, routed model
`dots-studio/dots-3-note-preview:free`. **P5 (meaning) is not earned:**
the statement maps “attainable set” to `c.utility '' c.budgetSet`, which
is not the claim. Machine draft_complete ≠ semantic fidelity.

## Observability

| Check | Result |
|---|---|
| Formalize provenance.model | A: `dots-studio/dots-3-note-preview:free` |
| Interpret EI / events carry routed model | **no** — events have digest only |
| 402 paid-path | none |
| Empty content on 200 | C: `provider message missing content` (reasoning models) |

## Runtime / reliability — **HURT** (pre-committed: any step >4 min or timeout)

- B formalize: 600s timeout, no artifact
- C interpret: 217s then empty content
- opinion A: 180s timeout
- A formalize attempt 1: HTTP 404 inside the revision loop (router miss)

## Predictions vs actuals

| # | Predicted | Actual |
|---|---|---|
| 1 ingest | pass | pass 3/3 |
| 2–4 interpret | ~0.45 schema-valid | 2/3; C INVALID_OUTPUT |
| 5 interpret routed model | likely on provenance | **fail** on interpret artifacts |
| 6 review | ACCEPTED | A/B ACCEPTED |
| 7–9 formalize not draft_complete | 0/3 | **A draft_complete machine-true**; B timeout; C n/a |
| 10 first_try_valid 0/3 | 0/3 | A first try 404; others unscored |
| 11 draft_complete 0/3 | 0/3 | **1/3** |
| 12 interpret 5–90s | mixed | A/B ~21s; C 217s |
| 13 formalize 30–240s | mixed | A 217s; B 600s timeout |
| 14 no 402 | pass | pass |
| 15 opinion | skip | timeout |

## Catalogue (because runtime hurt)

Top free models by OpenRouter 7-day usage (2026-10): Nemotron 3 Ultra,
Laguna S 2.1, Nemotron 3.5 Lightning, Dots3-Note Preview (the one that
served A), Ling 3.0 Flash Sante, Inkling, North Mini Code.

**Recommended next pins (not applied — no second live A/B yet):**

| Capability | Candidate | Why |
|---|---|---|
| interpret / opinion / triage | `nvidia/nemotron-3.5-lightning:free` | 3B-active, high-throughput; cut 200s empty-content draws |
| formalize | `cohere/north-mini-code:free` or `poolside/laguna-s-2.1:free` | coding/JSON; Laguna is heavier |

Keep `openrouter/free` until a timed A/B on those slugs. Do not pin
`openrouter/auto` / Jev (paid).

## Event trace (claim_id, type, transition)

```
orfree-A ingest None→DRAFT
orfree-A interpret DRAFT→INTERPRETED→REVIEW_REQUIRED  (20.9s)
orfree-A review REVIEW_REQUIRED→ACCEPTED
orfree-A formalize ACCEPTED→FORMALIZED  attempts=2 probe=True gaps=5  (216.5s)
orfree-B ingest None→DRAFT
orfree-B interpret DRAFT→INTERPRETED→REVIEW_REQUIRED  (22.9s)
orfree-B review REVIEW_REQUIRED→ACCEPTED
orfree-B formalize TIMEOUT 600s (still ACCEPTED, no formal_rev)
orfree-C ingest None→DRAFT
orfree-C interpret DRAFT→FAILED PROVIDER_INVALID_OUTPUT missing content  (217.5s)
```

Raw JSONL: `artifacts/local/a3-events/a3-*.jsonl` for those run ids.
Formal artifact: `artifacts/local/a3/formal/orfree-A/rev-1.json`.

**Attribution:** Hermes Agent under CTO direction. Not a sealed holdout.
Not a tag.
