# Experiment card — D4 model-pin A/B (formalizer fallback decision)

**Date:** 2026-09-07 · **Branch:** `v4/g0-kickoff` (proposal only — no push)
**Parent:** `docs/v4/INIT_V4_AGENTIC.md` · **Gate:** DL 51/D4 (swaps need
dev-fixture A/B then sealed evidence)
**Status:** **HELD by CTO 2026-09-07** — keep `labs-leanstral-1-5` pinned
until retirement forces the decision. Supersedes the same-day earlier
direction to run the A/B now. Consequences recorded: the ~Sept 20
re-pin deadline lapses; the swap becomes a forced move at expiry
(~Sept 30) or on a 404 at run time; a mid-sprint retirement risks an
evidence discontinuity on the formalizer pin. Re-open trigger: any 404/
401/retirement notice on the pinned model, or CTO direction.

## Trigger (why now)

`labs-leanstral-1-5` (Labs tier) carries a **reported retirement date of
September 30, 2026** (Mistral Labs listing, corroborated 2026-07;
re-confirm via API before relying). CTO decision 2026-09-07: run the D4
A/B on dev fixtures now, re-pin by ~Sept 20, seal the v4 holdout
(n≥8) on the **final** pin so evidence sits on the model the product
will ship with.

## Candidate pool (honest constraints)

The adapter speaks to the Mistral API only; no local GPU for
self-hosting (leanstral is Apache-2.0 open-weight, but 119B MoE does
not run here). Candidates are therefore Mistral-hosted model ids:

| Candidate | Tier | Cost /M tok (in/out) | Notes |
|---|---|---|---|
| `labs-leanstral-1-5` (incumbent) | Labs | $0 | Lean-specialist; retirement 9/30 (reported) |
| `mistral-medium-3-5` | PAYG | $1.50 / $7.50 | Current interpret/triage pin; generalist |
| `mistral-small-4` | PAYG | $0.15 / $0.60 | 10× cheaper; fallback posture today |

Dev fixture A/B measures formalization drafting only (same pipeline,
fixed prompt + postprocess). Cost per claim is pennies; rate limits are
the binding constraint on run days.

## Hypothesis

Re-pinning the formalizer to a generalist PAYG model trades leanstral's
Lean-specialist drafting for availability stability. Measured question:
**which candidate maximizes elaborates_rate ∧ audit-clean parity on dev
fixtures, under the frozen METRICS definitions?** Expected: a regression
on elaboration versus leanstral (generalists were never Lean-trained at
leanstral's level); the A/B quantifies it so the re-pin decision is a
number, not a hope.

## Procedure (dev only — zero sealed spend)

1. Fixture set: 6–8 dev texts drawn from stored dev claims spanning the
   P2 failure classes the Diagnosis table covers (`binder_annotation`,
   `syntax`, `instance_synthesis`, `type_mismatch`) — same-text/new-id
   technique; never re-run sealed/spent sets.
2. Per candidate: run the formalize pipeline with the current pinned
   prompt + postprocess; record `audit_clean_rate` and `elaborates_rate`
   per frozen definitions (`docs/v3.5/METRICS.md`), partitioning by
   provenance (model_draft only — no reviewer-authored pooling).
3. Same day/order to keep provider nondeterminism fair; attempts within
   `MAX_REVISION_ATTEMPTS=3` (D2 untouched).
4. Predictions committed before any live call (`docs/eval/*-expectations.md`
   pattern). Sealed sets stay spent; fixtures stay fixtures.

## Decision rule (pre-committed)

| Outcome | Action |
|---|---|
| A candidate beats incumbent elaborates_rate at audit-clean parity on the fixture set | propose re-pin to that candidate (DL 51/D4 pathway) |
| No candidate beats incumbent | keep leanstral through retirement; plan = expiry fallback to the best PAYG candidate, recorded as a written regression expectation, then v4 holdout on the fallback pin |
| Incumbent already retired / 404 at run time | decision is forced: pick best PAYG candidate by the same rule |

Deadline: decision written by **~Sept 20**, leaving ≥10 days before
9/30 for the re-pin + sealed holdout prep (texts, predictions) on the
final pin.

## Sealed holdout after re-pin

n≥8 fresh sealed texts, curated to stress the covered failure classes
(INIT open question 3). One pass, predictions first, manifest locked.
`formalizer-<pin>-v4h2` naming. Spent sets stay spent.

## Non-goals

No prompt retuning as part of the A/B (prompt is the incumbent lever,
frozen). No self-host. No multi-provider adapter work. No MVP_MODEL_MAP
edit outside the DL 51/D4 pathway. No sealed spend. No change to
interpret/triage pins.

Attribution: prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
