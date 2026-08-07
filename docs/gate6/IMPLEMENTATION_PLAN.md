# Gate 6 — LeanEcon Core implementation plan

> Status: **P1–P5 executed; Gate 6 CLOSED (2026-08-06)** — P1 schema
> freeze (PR #7), P2 first Core batch (PR #8), P3 glossary registry v1
> (PR #9), P4 A3 contract deltas D1/D2/D4 (PR #10; 156 tests green),
> P5 clean-clone + exit package (DECISION_LOG item 25). **Gate 7
> (equilibrium-family declarations) is the next slice.** Every phase
> stopped for CTO review; execution records: DECISION_LOG items 20–25 and
> the per-phase review packages (`P2_REVIEW_BATCH.md`,
> `P4_REVIEW_BATCH.md`, `P5_EXIT_PACKAGE.md`).
>
> Originally: plan only — no implementation authorized by this document
> until CTO approval of the design, the open-question resolutions, and
> this plan.

## 0. Scope and boundaries

**In scope:** (P1) the EI schema-freeze commit (docs/contract, no code);
(P2) the first Core promotion batch (6 declarations + 2 theorem
boundaries) with per-declaration ontology records; (P3) glossary registry
versioning; (P4) the A3 contract deltas D1/D2/D4 (mapping-kind `core`,
fully-qualified `core` rows, Core pin in the bundle, namespace-scoped
scaffolding); (P5) clean-clone + evidence.

**Out of scope (later gates):** B2 proof loop, corpus expansion,
production `VERIFIED` claims, equilibrium-family DECLARATIONS (Gate 7
slice — glossary-only now), retrieval, release.

**Exit evidence (migration plan Gate 6):** approved design ✓ (this
package); first reviewed Core sample builds from a clean clone; no v3
custom Lean copied; ontology and Lean declarations agree; migration
ledger records every v3 relationship as rebuild/inspiration/historical.

## 1. Phase map

| Phase | Deliverable | CTO gate | Evidence |
|---|---|---|---|
| P1 | Schema freeze commit (docs only) | approve commit | `$comment` freeze note in `ei_schema_draft.json` + `DECISION_LOG.md` entry; CI green |
| P2 | First Core promotion batch | approve per-declaration records | `lake build LeanEcon.Core.*` green; 6 ontology records + 2 theorem boundaries reviewed |
| P3 | Glossary registry v1 | approve registry | `references/core-glossary-detail.md` versioned; fwt1 entries present (21–28) |
| P4 | A3 contract deltas D1/D2/D4 | approve code+tests | formalization/bundle/verifier updates + regression tests; 137 existing tests stay green |
| P5 | Clean-clone + Gate 6 exit package | approve exit | clean-checkout build, pytest, ledger update, evidence packet |

## 2. P1 — schema freeze (docs-only commit)

1. Add the `$comment` freeze note to
   `references/gate3/ei_schema_draft.json` (freeze date 2026-08-06,
   exercised fields: `none_noted`, nullable `review.reviewer`/`event_ref`,
   `acknowledges_none_noted`; approval ref = Gate 6 decision).
2. Add the freeze entry to `docs/gate3/DECISION_LOG.md` (status: FROZEN
   1.0.0; versioning rules: additive-optional = minor, semantic/required
   changes = major).
3. Docs-only PR → CTO approve → merge (standard protected-main flow).
4. No code changes; `interpretation.py` already validates against this
   file.

## 3. P2 — first Core promotion batch (the declarations)

Module tree (new, under `lean_workspace/LeanEcon/Core/`):

```text
LeanEcon/Core/
├── Primitives.lean      — bundle, goods index
├── Preferences.lean     — weakPreference
├── Utility.lean         — utility, strictlyIncreasing
├── Constraints.lean     — budgetSet
├── Choice.lean          — attainableSet
└── Theorems.lean        — c1-family theorem boundary (+ c3-family later)
```

Batch (6 declarations + 2 theorem boundaries), each with an ontology
record per the template (`references/core-glossary-detail.md`), the 7
promotion criteria (`a3-core-design.md` §7), and the D3 collision check:

| # | Declaration (camelCase) | Area | Seeded by | Notes |
|---|---|---|---|---|
| 1 | `weakPreference (α : Type) := α → α → Prop` | Preferences | c2 | alias; no structure |
| 2 | `bundle (Goods : Type) [Fintype Goods] := Goods → ℝ` | Primitives | c1/c3/fwt1 | **explicit param** — the fwt1 abbrev pitfall; no implicit capture |
| 3 | `budgetSet (p : Goods → ℝ) (m : ℝ) : Set (Goods → ℝ)` | Constraints | c1/fwt1 | `{x \| ∑ i, p i * x i ≤ m}` |
| 4 | `attainableSet (B : Set (Goods → ℝ)) : Set (Goods → ℝ) := B` | Choice | c1 | carries the reviewed budget-set reading |
| 5 | `utility (X : Type) := X → ℝ` | Utility | c3/fwt1 | alias |
| 6 | `strictlyIncreasing (u : bundle Goods → ℝ) : Prop` | Utility | c3 | componentwise reading (recorded decision) |
| T1 | `theorem budgetExpansion_nonShrinking` (c1 family) | Theorems | c1 | `Bold ⊆ Bnew → attainableSet Bold ⊆ attainableSet Bnew` |
| T2 | `theorem strictlyIncreasing_strictPref` (c3 family) | Theorems | c3 | direction-flip convention per c3 fixture |

Workflow per declaration: draft Lean (Hermes) → ontology record drafted →
**CTO semantic review** (meaning + signature + assumptions + axioms +
examples) → approval record → commit. No batch approval; no model-only
promotion.

**c2/c4 families need NO Core declarations** — transitivity/completeness/
reflexivity are Mathlib (`IsTrans`/`IsTotal`/`IsRefl`), monotonicity is
`Monotone`; the glossary records them as mathlib references.

## 4. P3 — glossary registry v1

- Version the registry (`references/core-glossary-detail.md` → v1) with
  the 28 entries; add a change log (entry additions = minor; meaning
  changes = major, requiring downstream re-review).
- The registry remains the single source of truth; EI
  `context.definitions` stay per-claim copies (source anchors).
- Equilibrium-family entries (21–28) stay glossary-only/core-candidate —
  **no declarations** (Gate 7 slice).

## 5. P4 — A3 contract deltas (code + tests)

| Delta | Change | Where | Tests |
|---|---|---|---|
| D1 | `core` rows carry fully-qualified `lean_identifier`; mapping-kind enum gains `core` | `formalization.py` (validation/classification), mapping-report contract doc | mapping-report tests: valid `core` row (FQ), invalid bare id flagged |
| D2 | Bundle: `workspace_identity.core_revision` + Core imports in `dependency_audit` | `bundle.py` + manifest schema | bundle validator test: missing Core pin ⇒ check fails |
| D4 | A3-local scaffolding must be namespace-scoped (lint-style check on candidate scaffolding) | `formalization.py`/verifier input validation | static check test: root-namespace scaffolding flagged |
| D3 | (review-time) collision check in the promotion checklist | docs/ontology-record template | manual review item; optional CI grep against Mathlib names |

All deltas are additive to the existing contracts; the 137 existing tests
stay green; new tests extend the A3 suites (mocked-provider pattern).

## 6. P5 — clean-clone evidence and exit package

1. Clean-checkout reproduction: fresh clone → `lake build LeanEcon.Core.*`
   → pytest green.
2. Migration ledger update: record the Core-specific v3 dispositions
   (Preamble rebuild/inspiration, preamble_library rebuild, tier1 claim
   sets historical-discard) in `docs/gate3/01` ledger.
3. Ontology-declaration agreement check: every §2 core-candidate with a
   declaration has an approved ontology record; every promoted
   declaration has a glossary entry.
4. Gate 6 exit evidence packet: design ✓, batch builds, ledger, no v3
   copy, CTO approval records — presented for Gate 7 authorization.

## 7. Risk register (informed by the fwt1 test)

| Risk | Mitigation | Evidence |
|---|---|---|
| Formalizer still fails structurally (inverted theorems, non-compiling) | Reviewer-authored statements+proofs remain load-bearing; compile probe + gap classification + gap-ack; NO change to this posture in Gate 6 | fwt1, c1–c4, walkthrough record |
| `abbrev` implicit-param capture breaks signatures | Use explicit params (`bundle (Goods : Type)`) — the fwt1 lesson; add a declaration-style checklist item | fwt1 proof iteration 1 |
| Finset sum lemmas: wrong variant (`sum_lt_sum` vs `sum_lt_sum_of_nonempty`) | Recorded in the plan; reviewer-authored proofs iterate against the kernel | fwt1 proof iteration 2 |
| Core pin drift (D2) not yet implemented ⇒ reproducibility gap for Core-using claims | D2 lands in P4 BEFORE any claim imports Core in a bundle; until then Core is not used by claims | data-flow-model §5 |
| Workspace rebuild cost after module additions | `.lake` cached; incremental builds are seconds (fwt1 demo: 13s full 2997-job build, single-file compiles fast) | toy walkthrough |
| Accidental shadowing of Mathlib names | D3 collision check at promotion; D1 FQ ids in rows; D4 namespaced scaffolding | naming-overlap review |

## 8. What this plan deliberately does NOT do

- No equilibrium-family declarations (Gate 7), no demand/choice
  correspondences, no representation theorems.
- No B2 proof loop, no corpus work, no release artifacts.
- No change to the verifier's kernel-check semantics; no new reason codes
  (A3 Open Q9 held).
- No v3 material copied; no import/adapt exceptions.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This plan
authorizes nothing; each phase begins only after its CTO gate.
