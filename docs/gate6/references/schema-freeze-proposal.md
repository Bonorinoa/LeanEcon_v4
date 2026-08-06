# Schema-freeze proposal — EconomicInterpretation 1.0.0

> Records the exact diff between the pre-A3 draft and the freeze target,
> the evidence that exercised each change, and the normative enforcement
> notes. Backs `../a3-core-design.md` §5. The freeze takes effect only on
> CTO approval of the Gate 6 package.

## 1. Baseline and freeze target

- Baseline (pre-A3 draft): `references/gate3/ei_schema_draft.json` as
  approved for exercise by the Gate 5 A3 design (2026-08-06).
- Freeze target: the **same file, as it now stands** — the three
  exercised changes below are already in the file (they were added as
  draft-schema exercises during Gate 5). Freezing = approving the
  exercised draft as the normative contract; no field changes are
  proposed.

| Property | Value |
|---|---|
| `schema_version` | `1.0.0` (const) |
| `$id` | `https://leanecon.org/schemas/economic-interpretation/1.0.0` |
| Required root fields | unchanged: `schema_version`, `claim`, `context`, `objects`, `assumptions`, `conclusion`, `ambiguities`, `provenance`, `confidence`, `review`, `data_classification` |
| Freeze mechanics | CTO approval recorded in the Gate 6 decision entry + `DECISION_LOG.md`; `$comment` added to the file recording freeze date, exercised fields, approval ref |

## 2. The three exercised changes (draft → freeze)

### 2.1 `none_noted` (root-level boolean)

- **Draft addition (Gate 5):** `"none_noted": {"type": "boolean",
  "description": "…true when no ambiguity was identified; requires
  reviewer acknowledgement in review before APPROVED."}`
- **Exercise evidence:** enforcement path built and tested in the review
  command (`--acknowledge-none-noted` required; refusal keeps the claim
  at `REVIEW_REQUIRED` and emits no state-change event). None of the
  four live EIs hit `none_noted: true` (all had real ambiguities) — the
  flag itself is live-validated by the schema; the enforcement gate is
  test-verified.
- **Freeze:** normative. `none_noted: true` ⇒ `APPROVED` requires
  `review.acknowledges_none_noted: true`.

### 2.2 Nullable `review.reviewer` / `review.event_ref` while `PENDING`

- **Draft addition (Gate 5):** `"reviewer": {"type": ["string", "null"],
  …}` and `"event_ref": {"type": ["string", "null"], …}` with
  descriptions: null while `PENDING`, set by the reviewer approval event.
- **Exercise evidence:** all four walkthroughs (and the c1r2 comparison
  run) produced PENDING candidates with null reviewer/event_ref, then
  populated them at approval — exercised live end-to-end.
- **Freeze:** normative. Only the reviewer approval event may populate
  them; automated triage can never set `review.decision = APPROVED`
  (const + command path).

### 2.3 `review.acknowledges_none_noted` (boolean)

- **Draft addition (Gate 5):** acknowledgement flag in the review record.
- **Exercise evidence:** review-command enforcement tests; no live claim
  needed it (no `none_noted` hit).
- **Freeze:** normative. Meaningful only when `none_noted` is true;
  otherwise ignored.

## 3. Normative enforcement notes (already implemented; now contract)

1. `none_noted` ⇒ mandatory acknowledgement before `APPROVED`.
2. `reviewer`/`event_ref` null while `PENDING`, populated only by the
   reviewer approval event.
3. Automated triage sets `confidence`/flags only — never `APPROVED`.
4. `assumptions.accepted` is empty at production time; only the reviewer
   moves assumptions (an event, recorded in provenance/review notes).
5. Classification fail-closed: unknown/mixed sensitivity →
   `RESTRICTED` (ingest-time denial; A3 §2.4).
6. Accepted EI immutable by digest; any semantic change = new revision
   (Gate 3 rule, unchanged).

## 4. Versioning rules (normative)

- **Minor** (additive optional fields): allowed with a decision-log entry.
- **Major** (removing/renaming fields, changing meaning or requiredness):
  new `$id` (e.g. `…/1.1.0`), schema bump, downstream invalidation of
  artifacts built on the old version per the digest chain.

## 5. Rationale for freezing at `1.0.0` (not `1.1.0`)

The additions happened during the draft period of an **unreleased**
schema: there is no frozen 1.0.0 release to be incompatible with, no
external consumer, and the A3 code already validates against this exact
file. Folding the exercised fields into the initial frozen `1.0.0` avoids
churn and keeps `$id` stable. `1.1.0` was considered and rejected; it
would record a compatibility transition that never happened. (Open Q4 in
the design.)

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
