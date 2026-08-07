# Core glossary — full entries (seed from c1–c4)

> **Registry v1.0.0** — first versioned release (2026-08-06, Gate 6 P3).
> This registry is the **single source of truth** for reviewed glossary
> terms. The EI's `context.definitions` remain per-claim copies used as
> source anchors: immutable per EI revision, they seed entries here and
> never drift independently. The compact index in `../a3-core-design.md`
> §2 is the design-time snapshot this registry supersedes.
>
> Versioning: **entry additions = minor** (v1.x, no downstream re-review);
> **meaning changes = major** (v2.0) and require downstream re-review of
> every claim citing the changed term. Status moves (promotions up the
> ladder) are recorded in the change log, not a version bump. See the
> change log below.
>
> Entries are seeded ONLY from reviewed artifacts: accepted EIs (rev-2 of
> c1–c4), mapping reports (`artifacts/local/a3/formal/c{1..4}/rev-1.json`),
> and the CTO-approved claim texts (a3-design.md Appendix A). Detail
> backing the compact index in `../a3-core-design.md` §2.

## Change log

| Version | Date | Change | Kind |
|---|---|---|---|
| v1.1.0 | 2026-08-06 | Template addition (P4 D3): ontology-record template gains the `collision_check` review item (D3 mechanical check — a3-core-design.md §7 criterion 4). Additive; no entry meaning changed; no downstream re-review required. | minor (additive) |
| — | 2026-08-06 | Gate 7 promotions (status moves — no version bump per registry rules): entries 25, 26, 27 core-candidate → **core** (DECISION_LOG item 26; per-declaration approval records `G7_REVIEW_BATCH.md` §8; PR #11); entry 7 gains the landed endowment-relative variant note; entry 28 stays glossary-only (G7 decision D5). | status moves |
| v1.0.0 | 2026-08-06 | Initial release: 28 entries seeded from c1–c4 + fwt1. P2 promotions reflected: entries 1, 6, 7, 9, 12, 13 moved **core-candidate → core** (DECISION_LOG item 20; per-declaration approval records `P2_REVIEW_BATCH.md` §6; merged PR #8). Equilibrium family (21–28) stays glossary-only/core-candidate — declarations deferred to the Gate 7 slice. | initial |

## Ontology-record template (per promoted declaration)

```text
id:            canonical term id (kebab-case in the registry; camelCase in Lean)
economic_view: plain-language meaning, as reviewed
formal_view:   Lean type/signature sketch + Mathlib reuse
assumptions:   minimal assumptions; stronger/weaker variants
axiom_audit:   expected axioms (baseline unless noted)
collision_check: D3 review item (a3-core-design.md §7.4): the fully-qualified
               name must not collide with any imported dependency's namespace,
               and unqualified use in candidates must not shadow imported
               Mathlib identifiers. Recorded per declaration at promotion
               (mechanical aid proposal: docs/gate6/P4_REVIEW_BATCH.md §D3).
examples:      example / counterexample where useful
source:        EI definition id + claim id (anchor)
aliases:       EI definition ids / ontology_refs collapsed into this entry
status:        glossary-only | core-candidate | core | mathlib
promotion:     Gate 6 promotion criteria checklist + CTO approval ref (once promoted)
```

---

## Entries

### 1. `weak-preference` (≽)
- **Economic view:** binary relation over alternatives; "A ≽ B" = "A is at
  least as preferred as B" (preferred or indifferent).
- **Formal view:** `def weakPreference (α : Type u) := α → α → Prop`
  (alias; no structure of its own).
- **Assumptions:** none in the alias; axioms (completeness, transitivity,
  reflexivity) are separate entries.
- **Axiom audit:** none (definitional alias).
- **Example:** c2: `weak_pref a b`, `weak_pref b c` ⊢ `weak_pref a c`.
- **Source:** c2 `context.definitions[0]` ("weak_preference"); object
  `weak_preference_relation`.
- **Aliases:** `preferenceRelation` (ontology ref c1/c2).
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 2. `transitivity`
- **Economic view:** if A ≽ B and B ≽ C then A ≽ C — the rationality axiom
  the c2 claim asserts.
- **Formal view:** Mathlib `IsTrans α r` / `Transitive r`; used directly
  (`hr.trans a b c hab hbc` in the c2 fixture).
- **Assumptions:** none beyond the relation.
- **Axiom audit:** baseline (c2 verified with zero axioms).
- **Source:** c2 `context.definitions[1]` ("transitivity").
- **Status:** mathlib — referenced, never duplicated in Core.

### 3. `reflexivity`
- **Economic view:** every alternative is at least as good as itself.
- **Formal view:** Mathlib `IsRefl` / `Reflexive`.
- **Source:** c2 proposed assumption ("reflexive and complete").
- **Status:** mathlib.

### 4. `completeness`
- **Economic view:** any two alternatives are comparable: a ≽ b or b ≽ a.
- **Formal view:** Mathlib `IsTotal α r` (`∀ a b, r a b ∨ r b a`).
- **Source:** c2 proposed assumption.
- **Status:** mathlib. (Note: economics "completeness" = Mathlib
  "total"; the glossary records the alias.)

### 5. `alternative`
- **Economic view:** an element of the choice domain the preference
  relation ranks (c2's A, B, C).
- **Formal view:** type variable `α`; no declaration.
- **Source:** c2 objects (kind `alternative`, role
  `option_in_preference_relation`).
- **Status:** glossary-only (role vocabulary).

### 6. `bundle`
- **Economic view:** a consumption vector over goods (c1's single-good
  case; c3's n-good case).
- **Formal view:** `abbrev bundle (Goods : Type) [Fintype Goods] :=
  Goods → ℝ`; single-good claims may use `ℝ` directly (c1 fixture).
- **Assumptions:** `[Fintype Goods]` for sums over goods.
- **Axiom audit:** none (abbrev).
- **Examples:** c3 domain `n → ℝ` with `Fintype n`; c1 fixture `abbrev
  Bundle := ℝ`.
- **Source:** c1/c3 objects (`bundle`/`consumption_bundle` roles).
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 7. `budget-set`
- **Economic view:** the set of bundles a consumer can afford given
  income and prices: {x | p·x ≤ m}.
- **Formal view:** `def budgetSet (p : Goods → ℝ) (m : ℝ) : Set (bundle
  Goods) := {x | ∑ i, p i * x i ≤ m}` (requires `[Fintype Goods]`).
- **Assumptions:** prices nonnegative optional variant; `m ≥ 0` variant.
- **Variants:** income form (chosen); endowment-relative form now
  `budgetSetEndowment` (Constraints — promoted Gate 7, DECISION_LOG item
  26, PR #11; the P2-D2-deferred form, definitionally
  `budgetSet p (∑ g, p g * e g)`).
- **Axiom audit:** baseline (sums over Fintype are Mathlib).
- **Examples:** c1's `feasible_budget_set`; expansion `Bold ⊆ Bnew`.
- **Source:** c1 definition `feasible_budget_set`; ontology ref
  `budget_constraint`.
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 8. `budget-expansion`
- **Economic view:** the feasible set grows: `Bold ⊆ Bnew` (income rise,
  price fall, or both — c1's ambiguity alternatives).
- **Formal view:** Mathlib `⊆` on `Set`; no Core declaration.
- **Source:** c1 ambiguity "Nature of the budget set expansion" +
  assumption 0 (non-empty expansion).
- **Status:** mathlib.

### 9. `attainable-set`
- **Economic view:** bundles that are affordable AND preference-
  satisfying. c1's ambiguity ("feasible / chosen / utility-attaining")
  was resolved at review to the budget-set reading; the Core record must
  carry the chosen meaning (the c1 fixture: `def Attainable (B) := B`).
- **Formal view:** core-candidate; exact signature depends on Open Q1
  (bundle family) and the chosen reading:
  `def attainableSet (B : Set (bundle Goods)) : Set (bundle Goods) := B`
  (chosen reading) or a preference-filtered variant.
- **Assumptions:** recorded reading + filter variant.
- **Source:** c1 definition `attainable_set`; object role `solution_set`;
  c1 ambiguity "Definition of 'attainable set'".
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8) —
  **the entry that proves the glossary carries semantic decisions, not
  just names.**
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 10. `preferences-unchanged`
- **Economic view:** the preference relation is fixed over the relevant
  period (c1's "unchanged preferences").
- **Formal view:** a condition on the comparison setup, not a
  declaration; expository context in c1 (the mapping report recorded it
  as such).
- **Source:** c1 definition `preferences_unchanged`.
- **Status:** glossary-only (condition vocabulary).

### 11. `consumer`
- **Economic view:** the decision-maker whose budget/preferences are at
  issue.
- **Formal view:** type variable/role; no declaration (c1 fixture treats
  the consumer as the implicit bearer of `Bundle`).
- **Source:** c1 object `consumer` (kind `agent`, role `decision_maker`).
- **Status:** glossary-only.

### 12. `utility-function`
- **Economic view:** a function u : X → ℝ representing preferences —
  higher values = weakly preferred bundles.
- **Formal view:** `abbrev utility (X : Type u) := X → ℝ` (alias).
- **Assumptions:** none in the alias; representation properties are
  separate entries (later slice).
- **Axiom audit:** none.
- **Examples:** c3 `u : (n → ℝ) → ℝ`; c4 `f : ℝ → ℝ`.
- **Source:** c3 definition `utility_function`; object `u` (role
  `utility_function`).
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 13. `strictly-increasing-utility`
- **Economic view:** componentwise ≥ (with at least one strict
  inequality) implies u(x) > u(y). c3's ambiguity ("strict in each
  component" vs "strict in the aggregate") was resolved to the
  componentwise reading at review.
- **Formal view:** core-candidate predicate over the bundle family:
  `def strictlyIncreasing (u : bundle Goods → ℝ) : Prop := ∀ x y,
  x ≥ y → x ≠ y → u x > u y` (signature sketch; direction-flip
  convention per the c3 fixture note: Lean `y ≤ x` = English "x ≥ y").
- **Assumptions:** componentwise reading (recorded decision).
- **Source:** c3 definition `strictly_increasing_utility`; degradation
  flag `ambiguity_in_strictly_increasing_definition`.
- **Status:** **core** (promoted — P2 batch, DECISION_LOG item 20, PR #8).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record `P2_REVIEW_BATCH.md` §6).

### 14. `componentwise-comparison`
- **Economic view:** x ≥ y componentwise means x_i ≥ y_i for all i.
- **Formal view:** Mathlib pointwise order `Pi.instLE` on `Goods → ℝ`
  (in ℝ the componentwise order IS the usual order — c3 fixture note).
- **Source:** c3 definition `componentwise_comparison`.
- **Status:** mathlib.

### 15. `monotone-nondecreasing`
- **Economic view:** x ≤ y ⇒ f x ≤ f y (order-preserving).
- **Formal view:** Mathlib `Monotone`.
- **Example:** c4 fixture: `(hf : Monotone f) (hab : a ≤ b) : f a ≤ f b
  := hf hab`.
- **Source:** c4 definition `monotone_nondecreasing_function`.
- **Status:** mathlib.

### 16. `order-preservation`
- **Economic view:** synonym of monotone nondecreasing; c4's terminology
  ambiguity ("monotone" vs "strictly monotone") recorded at review.
- **Formal view:** Mathlib `Monotone` (unfolded form).
- **Source:** c4 definition `order_preservation`; ambiguity
  "Terminology consistency".
- **Status:** mathlib (alias of 15, recorded).

### 17. `preference-relation`
- **Economic view:** umbrella ontology reference for ranking relations.
- **Formal view:** glossary umbrella over `weakPreference`; no
  declaration.
- **Source:** c1/c2 `ontology_refs`.
- **Status:** glossary-only.

### 18. `rationality-axiom`
- **Economic view:** completeness + transitivity (+ reflexivity) — the
  standard rationality package.
- **Formal view:** glossary; assembled from Mathlib `IsTotal` + `IsTrans`
  (+ `IsRefl`) pieces.
- **Source:** c2 `ontology_refs`.
- **Status:** glossary-only (a later slice may define a bundled
  predicate).

### 19. `budget-constraint`
- **Economic view:** the feasibility constraint; ontology ref for the
  budget set.
- **Formal view:** maps to `budgetSet`.
- **Source:** c1 `ontology_refs`.
- **Status:** glossary-only.

### 20. `solution-concept`
- **Economic view:** the solution/equilibrium notion a claim concerns
  (Nash, competitive equilibrium, …).
- **Formal view:** meta-concept; c1–c4 carry null; **fwt1 carries a
  NON-null concept** ("Pareto efficiency of Walrasian equilibrium") —
  the first live solution-concept mapping (the model mapped it to its
  hypothesis name; acknowledged as an evaluation signal).
- **Source:** c1–c4, fwt1 `conclusion.solution_or_equilibrium_concept`.
- **Status:** glossary-only; Equilibrium namespace declarations deferred
  to the Gate 7 slice.

### 21. `exchange-economy`
- **Economic view:** an economy with no production: agents with
  endowments trade under prices. The fwt1 context.
- **Formal view:** glossary-only — realized as types (Agent, Goods) plus
  endowments/allocations; no standalone declaration proposed.
- **Source:** fwt1 EI object `exchange_economy` (kind `market`, role
  `environment`); ambiguity "Scope of 'exchange economy'".
- **Status:** glossary-only.

### 22. `price-vector`
- **Economic view:** prices p : Goods → ℝ at which trade happens; the
  equilibrium prices in fwt1.
- **Formal view:** glossary-only — realized as a function type; no
  declaration proposed (Mathlib ℝ suffices).
- **Source:** fwt1 EI object `prices_p` (kind `price_vector`, role
  `equilibrium_condition`).
- **Status:** glossary-only.

### 23. `allocation`
- **Economic view:** an assignment x : Agent → Bundle of consumption to
  each agent.
- **Formal view:** glossary-only — function type; no declaration.
- **Source:** fwt1 EI object `allocation_x` (kind `allocation`, role
  `equilibrium_outcome`).
- **Status:** glossary-only.

### 24. `endowment`
- **Economic view:** initial holdings e : Agent → Bundle before trade.
- **Formal view:** glossary-only — function type; no declaration.
- **Source:** fwt1 EI object `endowments_e` (kind `endowment_vector`,
  role `initial_conditions`).
- **Status:** glossary-only.

### 25. `market-clearing`
- **Economic view:** for every good, total consumption equals total
  endowment: Σ_i x_i g = Σ_i e_i g.
- **Formal view:** `def marketClearing {Agent Goods} [Fintype Agent]
  (e x : Agent → bundle Goods) : Prop := ∀ g, (∑ i, x i g) = (∑ i, e i g)`
  (the fwt1 `FwtFeasible`, which served double duty as feasibility;
  minimal constraint set — the sum is over agents, `∀ g` over goods).
- **Axiom audit:** baseline (Fintype sums are Mathlib; verbatim
  `G7_REVIEW_BATCH.md` §6).
- **Source:** fwt1 EI definition `feasible_allocation` + market clearing
  in `competitive_equilibrium`; ontology ref `market_clearing`.
- **Status:** **core** (promoted — Gate 7 batch, DECISION_LOG item 26, PR #11).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record
  `G7_REVIEW_BATCH.md` §8).

### 26. `competitive-equilibrium` (alias: Walrasian-equilibrium)
- **Economic view:** prices p and allocation x such that every consumer
  maximizes utility in their budget set and markets clear.
- **Formal view:** `structure competitiveEquilibrium {Agent Goods}
  [Fintype Agent] [Fintype Goods] (e : Agent → bundle Goods)
  (u : Agent → bundle Goods → ℝ) (x : Agent → bundle Goods)
  (p : Goods → ℝ) : Prop where feasible : marketClearing e x;
  maximizes : ∀ i, x i ∈ budgetSetEndowment p (e i) ∧ ∀ y,
  y ∈ budgetSetEndowment p (e i) → u i y ≤ u i (x i)`.
- **Assumptions:** direct utility maximization definition — the strong
  Pareto form then needs NO local nonsatiation (classic result; recorded
  in the fwt1 proof header).
- **Source:** fwt1 EI definitions `competitive_equilibrium`,
  `Walrasian_equilibrium`; ontology refs `general_equilibrium`,
  `consumer_optimization`; the non-null `solution_concept`.
- **Status:** **core** (promoted — Gate 7 batch, DECISION_LOG item 26, PR #11).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record
  `G7_REVIEW_BATCH.md` §8).

### 27. `pareto-efficiency`
- **Economic view:** no feasible allocation makes every consumer strictly
  better off (strong form; the fwt1 claim's reading — the EI ambiguity
  "weak vs strong Pareto" resolved at review).
- **Formal view:** `def paretoEfficiency {Agent Goods} [Fintype Agent]
  (e : Agent → bundle Goods) (u : Agent → bundle Goods → ℝ)
  (x : Agent → bundle Goods) : Prop := ¬ ∃ y, marketClearing e y ∧
  ∀ i, u i (x i) < u i (y i)`.
- **Assumptions:** strong form. `[Nonempty Agent]` lives on the THEOREM
  boundary, not this definition (Gate 7 decision D4) — the empty-economy
  case makes the claim false; the fwt1 proof added `[Nonempty Agent]`, a
  real semantic gap the interpreter did not surface (recorded in the
  proof notes).
- **Source:** fwt1 EI definition `Pareto_efficient`; ambiguity "Strength
  of Pareto efficiency"; ontology ref `Pareto_optimality`.
- **Status:** **core** (promoted — Gate 7 batch, DECISION_LOG item 26, PR #11).
- **Promotion:** approved 2026-08-06 (all 7 criteria; approval record
  `G7_REVIEW_BATCH.md` §8).

### 28. `utility-maximization`
- **Economic view:** the agent's chosen bundle is utility-maximal within
  its budget set.
- **Formal view:** glossary-only — a property folded into
  `competitiveEquilibrium.maximizes`; no standalone declaration (Gate 7
  decision D5 kept this reading).
- **Source:** fwt1 EI definition `competitive_equilibrium`; ontology ref
  `consumer_optimization`.
- **Status:** glossary-only.

---

## Cross-claim coverage check

| Claim family | Glossary terms it exercises | Missing from seed? |
|---|---|---|
| c1 budget expansion | 6, 7, 8, 9, 10, 11 (+17, 19, 20) | none |
| c2 transitivity | 1, 2, 3, 4, 5 (+17, 18, 20) | none |
| c3 strict monotonicity | 6, 12, 13, 14 (+20) | none |
| c4 order preservation | 15, 16 (+20) | none |
| fwt1 first welfare theorem | 6, 7, 11, 12, 20, 21–28 (equilibrium family) | none |

The five VERIFIED claim families exercise 28 distinct vocabulary items:
9 are **promoted to core** — 6 in the first batch (1, 6, 7, 9, 12, 13 —
P2, DECISION_LOG item 20, PR #8) and 3 in the Gate 7 equilibrium batch
(25, 26, 27 — DECISION_LOG item 26, PR #11); 7 are mathlib references;
the remaining 12 are glossary-only conditions/roles. This is the EI acceptance test in
operational form: the frame + glossary can carry confident review of the
canonical claims **and** a real theorem (fwt1).

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
