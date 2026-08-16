# v4 sprint — wire intelligence into the state machine

**Status:** proposed 2026-08-16. Parent: `docs/v4/INIT_V4.md`.
Does **not** authorize implementation until the CTO says go.
v3 must be on `main` first.

**Goal:** one frozen change to the formalize draft transition, then
one new sealed holdout. Success = draft-complete ≥ 3/5 on that set,
or a written miss. Spent sets (v3h / v3h2 / v3h3) stay spent.

## Out

Agents, UI, API, B2 proving, Nash Core, embeddings, retuning spent
holdouts, new lifecycle states.

## Five working days

| Day | Work | Exit |
|---|---|---|
| 1 | Failure-class inventory from v3h/v3h2/v3h3 (sorry / `:=` / D4 / probe syntax). Pick **one** lever: prompt, repair wrapper, or model pin. Write the experiment card + predictions. **Stop for approve.** | one lever named |
| 2 | Implement the lever on **dev fixtures only**. Fixture scorer stays `provider_calls=0`. Red tests for the failure class you chose. | pytest green |
| 3 | Live smoke on 2 **new-id same-text** claims (not holdout). Predictions first. Keep or revert. | go / revert |
| 4 | If go: freeze the change. Author 5 fresh sealed texts. CTO approves texts. Predictions file. | texts locked |
| 5 | One live pass. Score. Stop. Record met / missed. | `docs/eval/v4h1-*` |

## Default lever (if the CTO does not pick)

**Repair wrapper, not a model swap.** The v3h3 failures were
signature-body (`:=` / `sorry`) and D4 (redefining Core at root) and
probe syntax. A deterministic pre-submit sanitizer (strip theorem
`:=` / `sorry`, refuse root-level Core redefs, feed the reject back
as Feedback) is cheaper than changing labs-leanstral and is testable
without a provider.

Model pin is the fallback if Day 3 smoke is still 0/2 audit-clean.

## Definition of done

- One change, one new sealed set, one score.
- State machine invariants untouched (reviewer, kernel, F1).
- No v4.0.0 tag from this sprint unless draft-complete ≥ 60% **or**
  the CTO narrows again in writing.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
