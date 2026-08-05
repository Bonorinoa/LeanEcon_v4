# 3.3/3.7 EconomicInterpretation and LeanEcon Core Design Discussion

**Status:** discussion proposal, not an approved schema freeze and not an implementation plan. This document answers the CTO's question: how can the system make “what does this claim mean, under which assumptions, and what remains ambiguous?” credible without requiring the reviewer to read Lean?

## Recommendation in one sentence

Use a structured, human-readable **meaning frame** plus a small controlled glossary now; let the reviewed LeanEcon Core become the eventual formal ontology; derive a graph view when useful, but do not make a graph database or OWL-style ontology a v1 dependency.

## Separate the two layers

### EconomicInterpretation: review artifact

`EconomicInterpretation` is a versioned meaning hypothesis. It is designed for a CTO to inspect and accept/reject before formalization. It should contain:

- canonical and source claim text;
- explicit objects/agents/markets and their roles;
- domain and context;
- definitions and source anchors;
- assumptions separated into source-stated, interpreter-proposed, and reviewer-accepted;
- variables and quantifier/scope statements in controlled English;
- conclusion and solution/equilibrium concept when relevant;
- concrete ambiguities with alternatives, or explicit `none_noted` plus reviewer acknowledgement;
- provenance for each material mapping or interpreter decision;
- confidence/degradation indicators that describe the process, not semantic truth;
- reviewer decision and approval event;
- data classification.

It is not a theorem, proof, ontology authority, or hidden answer key.

### LeanEcon Core: formal substrate

The Core is a small, first-principles Lean library whose declarations are promoted one at a time after semantic review. A Core definition is not automatically accepted because a model proposed it or because Lean compiles it. Each promoted concept needs a plain-language meaning, assumptions, signature explanation, dependency/axiom audit, examples/counterexamples where useful, and CTO approval.

The Core should eventually ground EI references, but Gate 3 does not choose its ontology or implement declarations.

## Options

| Option | Description | Strength | Risk | Recommendation |
|---|---|---|---|---|
| A. Free-form frame | Mostly prose and loosely structured fields | Fastest | Hard to compare/review consistently | Reject as v1 |
| B. Controlled frame + glossary | Explicit EI fields, stable concept IDs, small reviewed vocabulary, source anchors | Reviewable without Lean and evolvable | Requires disciplined vocabulary stewardship | **Recommended** |
| C. Graph-first representation | Nodes/edges or graph database as primary model | Makes relations explicit | Complexity, premature ontology, v3-shaped architecture risk | Reject as v1 storage |

A graph can still be a **derived validation view**: nodes are EI elements/concept references; edges are `assumes`, `quantifies`, `concludes`, `refines`, and `contrasts_with`. Store the EI as versioned JSON; render or validate a graph only when it answers a concrete review question.

## How credibility is established

Credibility comes from process and traceability, not from claiming that a schema is complete:

1. Every material EI element has a source anchor or an explicit interpreter decision.
2. Assumptions are visibly separated into proposed versus accepted.
3. Ambiguities contain concrete alternatives; “none noted” requires reviewer acknowledgement.
4. The reviewer can inspect the claim, frame, assumptions, and conclusion without Lean.
5. Accepted EI is immutable by digest; changes invalidate formalization and proof artifacts.
6. The formalizer receives only accepted EI and later-approved Core references—not hidden gold or benchmark answer text.
7. Once Core exists, formalization emits a mapping report from EI elements to approved Core identifiers. Missing mappings are visible gaps, not silently invented definitions.
8. Three to five canonical claims are reviewed by the CTO as the EI acceptance test before A3. If the frame cannot support confident review, revise it.

## Worked example 1: budget-set expansion

**Claim:** “If a consumer's feasible budget set expands while preferences remain unchanged, the consumer's attainable set does not shrink.”

**Meaning frame:**

- Object: consumer `c`; role: decision-maker.
- Object: feasible set `B_old`; role: original budget/choice set.
- Object: feasible set `B_new`; role: expanded budget/choice set.
- Proposed relation: `B_old ⊆ B_new`.
- Context: preference relation unchanged between the two comparisons.
- Scope: for the same consumer and preference relation; the conclusion concerns attainable choices, not utility ranking alone.
- Ambiguity: “attainable set” could mean feasible set, chosen set, or utility-attaining set. Reviewer must select one.
- Missing assumption candidate: the definition of “attainable set” and whether choices are compared directly or through a choice correspondence.
- Conclusion: under the accepted definition, the new attainable set contains the old one.
- Review state: `PENDING`; no formal statement implied.

The frame is useful because it exposes the exact semantic fork before Lean formalization.

## Worked example 2: equilibrium claim

**Claim:** “A finite strategic game has a mixed-strategy Nash equilibrium.”

**Meaning frame:**

- Objects: finite player set, finite action sets, payoff functions, mixed-strategy profile.
- Roles: players choose; payoff functions evaluate outcomes; profile is the candidate equilibrium.
- Definitions: “finite,” “mixed strategy,” and “Nash equilibrium” require glossary references.
- Scope: existence, not uniqueness; quantifier order is “for every finite game, there exists a mixed-strategy profile…”
- Assumptions: finiteness is source-stated; payoff codomain and mixed-strategy construction may be interpreter-proposed until reviewed.
- Ambiguity: whether the claim means normal-form finite game and which equilibrium definition is intended.
- Conclusion: existence of at least one profile satisfying the accepted best-response condition.
- Review state: `PENDING`; no Core theorem or proof implied.

This example shows why solution concept, quantifier order, and definition references are essential.

## MVP versus later

**MVP / before A3:** structured EI review artifact, controlled English, stable IDs, source anchors, proposed/accepted assumptions, ambiguity alternatives, reviewer event, digest immutability, and a small glossary authored during review.

**Later / Gate 5–6:** EI-to-Core mapping reports, promoted Lean concepts, declaration-level semantic review, derived relation graphs, richer ontology governance, and any retrieval/indexing over the Core.

**Explicitly out of scope:** OWL/RDF ontology engineering, general economics knowledge graph, automatic Core promotion, graph database dependency, textbook-scale ontology, and using v3 declarations as the v4 ontology.

## CTO decisions before A3

1. Approve Option B as the design direction: controlled EI frame plus small reviewed glossary.
2. Require `none_noted` plus reviewer acknowledgement when no ambiguity is identified?
3. Require a formalization mapping report before a candidate can enter `PROVING`?
4. Confirm the first 3–5 canonical claims are the acceptance test for EI credibility.

**Attribution:** Prepared by Hermes Agent (Nous Research) under direction of the CTO. The CTO remains the sole semantic approver.
