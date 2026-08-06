# P2 — First Core promotion batch: CTO review package

> Status: **APPROVED 2026-08-06 by the CTO (verdicts D1–D6: "approve as
> proposed")** — promotion records below (§6). The six module files are
> compiled in the pinned workspace (all evidence verbatim). Committed as
> part of the P2 PR after these gates passed.
>
> Authority: design + plan approved 2026-08-06 (DECISION_LOG items 15–18);
> P1 merged (main @ 541018f); P2 batch approval = DECISION_LOG item 20.

## 0. Batch at a glance

| # | Declaration | Area | Seeded by | Kind | Compiles | Axioms |
|---|---|---|---|---|---|---|
| 1 | `bundle (Goods : Type) := Goods → ℝ` | Primitives | c1, c3, fwt1 | abbrev | ✅ | none |
| 2 | `weakPreference (α : Type) := α → α → Prop` | Preferences | c2 | abbrev | ✅ | none |
| 3 | `budgetSet {Goods} [Fintype Goods] (p : Goods → ℝ) (m : ℝ) : Set (bundle Goods)` | Constraints | c1, fwt1 | def | ✅ | none |
| 4 | `attainableSet {Goods} (B : Set (bundle Goods)) : Set (bundle Goods) := B` | Choice | c1 | def (decision-carrying) | ✅ | none |
| 5 | `utility (X : Type) := X → ℝ` | Utility | c3, fwt1 | abbrev | ✅ | none |
| 6 | `strictlyIncreasing {Goods} (u : bundle Goods → ℝ) : Prop` | Utility | c3 | def | ✅ | none |
| T1 | `budgetExpansion_nonShrinking` | Theorems | c1 (VERIFIED) | theorem | ✅ | baseline |
| T2 | `strictlyIncreasing_strictPref` | Theorems | c3 (VERIFIED) | theorem | ✅ | baseline |

Real build + audit output (pinned workspace, `leanprover/lean4:v4.32.2`,
Mathlib `v4.32.2`):

```
$ lake build LeanEcon.Core.Theorems   (builds the batch chain)
✔ [3000/3000] Built LeanEcon.Core.Theorems (1.6s)
Build completed successfully (3000 jobs).

$ lake env lean .a3-candidates/p2-check/Check.lean
LeanEcon.Core.Constraints.budgetSet {Goods : Type} [Fintype Goods] (p : Goods → ℝ) (m : ℝ) :
  Set (Primitives.bundle Goods)
LeanEcon.Core.Utility.strictlyIncreasing {Goods : Type} (u : Primitives.bundle Goods → ℝ) : Prop
LeanEcon.Core.Theorems.budgetExpansion_nonShrinking {Goods : Type} {Bold Bnew : Set (Primitives.bundle Goods)}
  (h : Bold ⊆ Bnew) : Choice.attainableSet Bold ⊆ Choice.attainableSet Bnew
LeanEcon.Core.Theorems.strictlyIncreasing_strictPref {Goods : Type} {u : Primitives.bundle Goods → ℝ}
  (hu : Utility.strictlyIncreasing u) {x y : Primitives.bundle Goods} (hxy : y ≤ x) (hne : y ≠ x) : u y < u x
'LeanEcon.Core.Theorems.budgetExpansion_nonShrinking' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Theorems.strictlyIncreasing_strictPref' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## 1. Ontology records (per declaration)

### 1. `bundle` — Primitives
- **Economic view:** a consumption vector over goods; one real quantity per
  good. Single-good claims may use `ℝ` directly (c1 fixture).
- **Formal view:** `abbrev bundle (Goods : Type) := Goods → ℝ`. Explicit
  type parameter — the fwt1 lesson (an implicit capture in the abbrev
  broke signature inference).
- **Assumptions:** none (abbrev). `[Fintype Goods]` is required only where
  sums are used (e.g. `budgetSet`), not on the abbrev itself.
- **Variants:** `Goods → ℝ` (chosen) vs `Fin n → ℝ` (indexed) vs per-claim
  `ℝ` — design Open Q1 resolved to the general family; claims pick instances.
- **Axiom audit:** none. **Collision check (D3):** no Mathlib root name
  `bundle`. ✅
- **Examples:** c1 single-good; c3/fwt1 `n → ℝ` with `Fintype`.
- **Source:** c1/c3/fwt1 objects (`bundle`/`consumption_bundle` roles).

### 2. `weakPreference` — Preferences
- **Economic view:** binary relation "A is at least as preferred as B"
  (preferred or indifferent); the c2 vocabulary.
- **Formal view:** `abbrev weakPreference (α : Type) := α → α → Prop`.
- **Assumptions:** none (alias). The rationality axioms are Mathlib
  (`IsTrans`, `IsTotal`, `IsRefl`) — referenced, never duplicated.
- **Axiom audit:** none. **D3:** no collision with Mathlib. ✅
- **Note:** c2's VERIFIED fixture used a raw relation with `IsTrans`; this
  alias is the reviewed *named home* for the vocabulary — the anchor that
  `rationalityAxiom` and future preference claims (and the Gate 7 slice)
  will build on. Smallest possible declaration.
- **Source:** c2 definition `weak_preference`; ontology ref
  `preference_relation`.

### 3. `budgetSet` — Constraints
- **Economic view:** the set of bundles affordable at prices p with income
  m: {x | Σᵢ pᵢ·xᵢ ≤ m}. The c1 "feasible budget set".
- **Formal view:** `def budgetSet {Goods : Type} [Fintype Goods]
  (p : Goods → ℝ) (m : ℝ) : Set (bundle Goods) := {x | ∑ g, p g * x g ≤ m}`.
- **Assumptions:** `[Fintype Goods]` for the finite sum. Variants: income
  form (chosen) vs endowment-relative form (`budgetSet p (∑ g, p g * e i g)`
  — recoverable; a dedicated endowment-relative definition is deferred to
  the equilibrium slice, Gate 7, where `competitiveEquilibrium` lives).
- **Axiom audit:** none. **D3:** no collision. ✅
- **Examples:** c1 budget expansion (`Bold ⊆ Bnew`); fwt1 budget sets.
- **Source:** c1 definition `feasible_budget_set`; ontology ref
  `budget_constraint`.

### 4. `attainableSet` — Choice
- **Economic view:** bundles that are affordable AND preference-satisfying;
  the c1 ambiguity ("feasible / chosen / utility-attaining") was resolved
  at review to the **budget-set reading**.
- **Formal view:** `def attainableSet {Goods : Type} (B : Set (bundle
  Goods)) : Set (bundle Goods) := B` — deliberately thin: the *decision*
  is the content (the glossary entry records the meaning; the declaration
  encodes the chosen reading). If a later claim needs the
  preference-filtered reading, that is a NEW declaration, not a mutation.
- **Assumptions:** chosen reading recorded. 
- **Axiom audit:** none. **D3:** no collision. ✅
- **Source:** c1 definition `attainable_set`; ambiguity "Definition of
  'attainable set'".

### 5. `utility` — Utility
- **Economic view:** real-valued ranking of alternatives; higher = weakly
  preferred. The c3/fwt1 `utility_function` vocabulary.
- **Formal view:** `abbrev utility (X : Type) := X → ℝ`.
- **Assumptions:** none (alias). Representation properties ("u represents
  ≽") are a later slice.
- **Axiom audit:** none. **D3:** no collision. ✅
- **Source:** c3 definition `utility_function`; fwt1 object `u`.

### 6. `strictlyIncreasing` — Utility
- **Economic view:** strictly increasing utility, componentwise reading
  (the c3 review decision): `y ≤ x` componentwise and `y ≠ x` ⇒
  `u y < u x`. Direction-flip convention from the c3 fixture: Lean `y ≤ x`
  states English "x ≥ y".
- **Formal view:** `def strictlyIncreasing {Goods : Type} (u : bundle Goods
  → ℝ) : Prop := ∀ x y, y ≤ x → y ≠ x → u y < u x`. The order on
  `bundle Goods` is Mathlib's pointwise order (componentwiseComparison).
- **Assumptions:** strong componentwise reading. Variants (weaker):
  monotone (`u y ≤ u x`); strictly increasing in each component.
- **Axiom audit:** none. **D3:** no collision with `StrictMono`. ✅
- **Source:** c3 definition `strictly_increasing_utility`; ambiguity
  "Scope of 'strictly increasing'".

### T1. `budgetExpansion_nonShrinking` — Theorems (c1 family)
- **Economic view:** c1's claim: budget expansion ⇒ attainable set does
  not shrink. Theorem boundary for the VERIFIED claim c1.
- **Formal view:** `theorem budgetExpansion_nonShrinking {Goods} {Bold Bnew
  : Set (bundle Goods)} (h : Bold ⊆ Bnew) : attainableSet Bold ⊆
  attainableSet Bnew`.
- **Assumptions:** `Bold ⊆ Bnew` stated, not hidden (the exact thing the
  c1 formalizer got wrong — vacuous/inverted).
- **Axiom audit:** `[propext, Classical.choice, Quot.sound]` (baseline,
  real output above). ✅

### T2. `strictlyIncreasing_strictPref` — Theorems (c3 family)
- **Economic view:** c3's claim: strictly increasing utility ⇒
  componentwise dominance (with inequality) raises utility.
- **Formal view:** `theorem strictlyIncreasing_strictPref {Goods} {u :
  bundle Goods → ℝ} (hu : strictlyIncreasing u) {x y} (hxy : y ≤ x)
  (hne : y ≠ x) : u y < u x`.
- **Assumptions:** direction convention per the c3 fixture.
- **Axiom audit:** `[propext, Classical.choice, Quot.sound]` (baseline). ✅

## 2. Promotion-criteria checklist (a3-core-design.md §7) — batch-wide

| Criterion | Status |
|---|---|
| 1. Plain-language economic meaning | ✅ ontology records above (economic view) |
| 2. Lean signature explanation | ✅ ontology records (formal view) |
| 3. Assumptions + stronger/weaker variants | ✅ per record (esp. budgetSet income/endowment; strictlyIncreasing strong/weak) |
| 4. Dependency/axiom audit + D3 collision check | ✅ all baseline; no Mathlib collisions (names checked: bundle, weakPreference, budgetSet, attainableSet, utility, strictlyIncreasing, budgetExpansion_nonShrinking, strictlyIncreasing_strictPref) |
| 5. Examples/counterexamples | ✅ per record (c1/c3/fwt1 anchors) |
| 6. CTO approval record | ⬅️ **this review** (per declaration) |
| 7. Needed by a reviewed claim / planned slice | ✅ T1↔c1, T2↔c3 VERIFIED; 1–6 seeded by c1–c4/fwt1 accepted EIs + mapping reports; equilibrium-family use (budgetSet endowment form, competitiveEquilibrium) is the Gate 7 slice |

## 3. Decisions requested from the CTO

| # | Decision | Proposal | Alternatives |
|---|---|---|---|
| D1 | Approve batch declarations 1–6 as proposed? | Yes — compile-verified, baseline axioms | per-declaration changes |
| D2 | `budgetSet` income form only; endowment-relative form deferred to Gate 7? | Yes (recoverable as `budgetSet p (∑ g, p g * e i g)`) | add endowment form now (scope growth) |
| D3 | `strictlyIncreasing` strong-componentwise reading + c3 direction convention? | Yes | weak/monotone variant instead |
| D4 | Module layout: 6 area modules (Primitives, Preferences, Constraints, Choice, Utility, Theorems)? | Yes — matches design §1.3; no empty Equilibrium module (migration-plan rule: no architecture theatre) | consolidate into fewer files |
| D5 | Approve `weakPreference`/`utility` as vocabulary-anchor aliases even though c2/c3 fixtures used raw types? | Yes — smallest possible declarations; they are the named homes the glossary's `preference_relation`/`utility_function` refs point AT | defer to Gate 7 |
| D6 | Approve theorem boundaries T1/T2? | Yes — honest assumptions, baseline axioms | statement-shape tweaks |

## 4. What is deliberately NOT in this batch

- No Equilibrium module / `competitiveEquilibrium` / `marketClearing` /
  `paretoEfficiency` declarations (glossary-only until Gate 7 — the fwt1
  vocabulary stays meaning-reviewed, not encoded).
- No demand / choice-correspondence / representation theorems.
- No changes to A3 code (the D1/D2/D4 contract deltas land in P4).
- No v3 material; no model-authored declarations.

## 5. Process notes

- Module files: `lean_workspace/LeanEcon/Core/{Primitives,Preferences,
  Constraints,Choice,Utility,Theorems}.lean` — **untracked**; commit
  happens per declaration after approval (batch commit or per-file as the
  CTO prefers).
- The check file (`.a3-candidates/p2-check/Check.lean`) is gitignored
  scratch; the build evidence above is reproducible with
  `lake build LeanEcon.Core.Theorems LeanEcon.Core.Preferences
  LeanEcon.Core.Constraints`.
- After approval: per-declaration approval records (event ref, reviewer,
  date) appended to each ontology record + DECISION_LOG entry, then the
  P2 commit/PR (docs-only? no — code commit: Core modules; CI scaffold
  check + a1-tests gate it; the merge-gate quirks from P1 are documented
  in the skill).

## 6. Approval records (per declaration)

Promotion criterion 6. The CTO approved the batch as proposed on
2026-08-06 (verdicts D1–D6); each declaration is approved individually
below (reviewer: Bonorinoa; ref: DECISION_LOG item 20 + P2 commit).

| Declaration | Approved | Reviewer | Ref |
|---|---|---|---|
| 1 `bundle` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| 2 `weakPreference` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| 3 `budgetSet` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| 4 `attainableSet` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| 5 `utility` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| 6 `strictlyIncreasing` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| T1 `budgetExpansion_nonShrinking` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |
| T2 `strictlyIncreasing_strictPref` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 20, P2 PR |

All 7 promotion criteria satisfied for every declaration; the batch builds
in the pinned workspace; axiom closures are the Mathlib baseline.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This package
promotes nothing; approval records must accompany any commit.
