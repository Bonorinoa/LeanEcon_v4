# 3.3 EconomicInterpretation — Design Discussion Draft

**Status:** open design discussion; the JSON Schema is a draft and is not an approved schema freeze.

`EconomicInterpretation` is the human-reviewable semantic bridge between an English claim and a later formal statement. It is not a proof, does not certify truth, and must not contain hidden benchmark answers.

## v1 contract

The normative draft is [`references/gate3/ei_schema_draft.json`](../../references/gate3/ei_schema_draft.json). It uses `schema_version: "1.0.0"`; fields are explicit rather than an unrestricted metadata bag.

Required concepts: canonical claim, context, objects/agents/markets, roles, domains, definitions and ontology references, assumptions separated into proposed and accepted, variables and quantifier order, conclusion, solution/equilibrium concept when applicable, ambiguity list and alternatives, provenance, confidence, degradation flags, reviewer decision, approval event reference, and data classification.

A reviewer should be able to answer: “What does this claim mean, under which assumptions, and what remains ambiguous?” without reading Lean.

## Illustrative example (not a proof)

> “If a consumer’s feasible budget set expands while preferences remain unchanged, the consumer’s attainable set does not shrink.”

An interpretation would identify a consumer, feasible set, budget expansion relation, unchanged preference relation, and a set-inclusion conclusion. It would state missing assumptions and mark the reviewer decision `PENDING`. It would not claim that a theorem has been proven.

## Review and compatibility rules

- `DRAFT` interpretations may be edited; `ACCEPTED` interpretations are immutable by content digest.
- Any semantic change to an accepted interpretation invalidates formalization and proof artifacts until a new approval event.
- Additive optional fields are minor-compatible. Removing/renaming fields, changing meaning, or changing requiredness is a major version change.
- Confidence and degradation flags describe the interpretation process; they are not semantic approval.
- `review.decision` must be `PENDING`, `APPROVED`, or `REJECTED`; automated triage cannot set `APPROVED`.
- Classification is fail-closed: unknown or mixed-sensitivity content is `RESTRICTED` until reviewed.

**CTO boundary:** This draft does not choose the v4 economics ontology, promote Core declarations, or decide which formal statement is correct. Those remain later CTO-controlled decisions. See [`07-ei-core-design-proposal.md`](07-ei-core-design-proposal.md) for the design discussion.
