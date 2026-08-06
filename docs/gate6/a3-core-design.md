# Gate 6 — LeanEcon Core Design (A3-facing)

**Status:** design review — **final polish incorporated 2026-08-06** after
the live First Welfare Theorem test (`fwt1`, VERIFIED end-to-end), the
data-flow deltas D1–D4, and the FWT vocabulary extension. No
implementation, no LeanEcon Core declarations, no commit. Prepared per the
Gate 5→Gate 6 handoff (`docs/gate6/INIT_GATE6.md`); the design package
authorizes nothing until the CTO signs it. The implementation roadmap is
`docs/gate6/IMPLEMENTATION_PLAN.md`.

**Authority:** Gate 6 of the approved migration plan (frozen v3 evidence),
the EI design approval of 2026-08-05 (Option B, four locked decisions),
Gate 3 contracts (`docs/gate3/02–07`, `DECISION_LOG.md`), and the Gate 5 A3
design (`docs/gate5/a3-design.md`, §4 mapping report + §5 verifier).

**Reader:** no Lean knowledge required. Lean appears only as the kernel
language and through plain-language names.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.

---

## 0. Scope

**In scope (Gate 6 exit evidence, design part):** Core vocabulary scope,
the reviewed glossary seeded from the four canonical claims (c1–c4) that
were CTO-approved and walkthrough-VERIFIED at Gate 5 — **extended with the
FWT test vocabulary (fwt1, VERIFIED 2026-08-06)** — the canonical
element-id scheme the mapping report must use, the mapping-report target
contract once Core exists, the EI schema-freeze proposal (the draft schema
exercised by A3), the Core-era data flow (see
`references/data-flow-model.md`), and explicit
`import/adapt/rebuild/inspiration/historical` dispositions for v3-era Core
material. Open questions with proposed resolutions. **The live-test record
(`references/fwt1-test-record.md`) is part of the package evidence.**

**Explicitly out of scope:** implementing any Core declaration, writing
Lean, promoting declarations, modifying the A3 workflow code, corpus
expansion, retrieval, commits. Per the migration plan: no custom Core
declaration is implemented before this design is reviewed and approved.

**What Core is (for this gate):** the controlled formal vocabulary —
definitions, ontology references, theorem namespaces — that the EI's
`context.definitions` / `context.ontology_refs` and the A3 mapping report's
`lean_identifier` / `mapping_kind` fields point AT. A3 works without it
today (Mathlib + A3-local scaffolding); Core is the target of the mapping
report. Core is not an ontology authority, a theorem prover, a benchmark
answer key, or a copy of v3's preamble.

---

## 1. Core vocabulary scope

### 1.1 Categories (from the migration plan Gate 6 list)

Core declarations are organized by the economic categories the plan names,
mapped to a namespace skeleton. Each category has a formal view and an
economic view (see §1.5).

| Category | Economic view (what it means) | Formal view (what it is in Lean) | Initial slice? |
|---|---|---|---|
| Object / agent | who decides, what is chosen | type variables, roles recorded in EI | yes (roles only) |
| Domain | the space of alternatives/bundles | types (`ℝ`, `Goods → ℝ`) | yes |
| Preference | ranking over alternatives | relations `α → α → Prop` | yes |
| Utility | numerical representation of preference | functions `X → ℝ` + representation predicates | yes |
| Constraint | what is feasible | sets (`BudgetSet`) | yes |
| Choice | what is selected from the feasible set | choice correspondences, attainable sets | yes (attainable only) |
| Demand | choice as a function of prices/income | demand correspondence (later) | **deferred** |
| Equilibrium | solution concepts (GE, Nash, …) | fixed-point/best-response structures | **deferred** (glossary entries now; declarations at Gate 7) |
| Theorem boundary | reviewed results worth stating as Core theorems | theorem declarations with proofs | yes (one per claim family, minimal) |

MVP slice = exactly the vocabulary the four canonical claims exercise (§2)
plus the **glossary-only extension from the fwt1 test** (equilibrium-family
*meanings* reviewed; their *declarations* deferred to the Gate 7 slice).
Demand, equilibrium declarations, representation theorems, game theory and
general equilibrium are **later slices**, per the migration plan: "do not
begin by attempting to formalize entire textbooks or deep
general-equilibrium results."

### 1.2 Microeconomics-first, shallow cross-domain policy

Deep coverage starts in consumer theory (the four claims' domain). Other
domains (macro, econometrics, static game theory) enter only through the
Gate 7 shallow slice claims — one or two shallow claims each — and only
with declarations that earn their place via the promotion criteria (§5).
No declaration enters Core because a corpus row mentions it.

### 1.3 Namespace skeleton and naming conventions

```text
LeanEcon.Core
├── Primitives     — bundle, goods index, sums over goods
├── Preferences    — weakPreference, completeness / transitivity / reflexivity
├── Utility        — utility, strictlyIncreasing (representation: later)
├── Constraints    — budgetSet
├── Choice         — attainableSet (choice correspondence, demand: later)
├── Equilibrium    — (glossary-only now; declarations at Gate 7)
└── Theorems       — reviewed theorem boundaries per claim family
```

- Namespace `LeanEcon.Core.<Area>`; definitions in `camelCase` (Mathlib
  style), types in `PascalCase`; theorem names descriptive, e.g.
  `budgetExpansion_nonShrinking`.
- **Collision rule (D3):** Core names must not reuse Mathlib root-namespace
  identifiers (`Set`, `Monotone`, `IsTrans`, `Function`, …). The
  promotion checklist includes a mechanical collision check; candidates
  must not shadow imported Mathlib identifiers (see §4, D4).
- Candidate file locations for A3 keep their current per-run paths
  (`lean_workspace/LeanEcon/A3/<claim>/<run>/`); Core lives in its own
  module tree, committed only after per-declaration approval.
- Every declaration carries an **ontology record** (see `references/
  core-glossary-detail.md` for the record template) — plain-language
  meaning, signature explanation, assumptions + stronger/weaker variants,
  dependency/axiom audit, examples/counterexamples, CTO approval ref.

### 1.4 Mathlib dependency and import policy

- Core modules import **specific** Mathlib files (orders, `ℝ`, `Set`,
  `Finset`/`Fintype` sums) — never `import Mathlib` wholesale.
- No new axioms in Core. The axiom baseline is the Mathlib one already
  reviewed at Gate 5 (`propext`, `Classical.choice`, `Quot.sound`);
  anything beyond it triggers the per-run axiom review record (A3 §5.3).
  **The fwt1 test confirmed this holds on a real theorem**: the reviewer-
  authored FWT proof (utility maximization + market clearing + Pareto
  contradiction) verified with exactly the baseline closure.
- Workspace pinning is inherited from the existing A3 pinned workspace
  (`lean-toolchain` + Mathlib revision in the lakefile). **Core adds its
  own pin (D2):** the bundle's `workspace_identity` gains
  `core_revision` (commit sha or manifest digest of the Core module tree)
  and `dependency_audit` records Core imports — a `VERIFIED` claim must be
  reproducible against the exact Core revision (see
  `references/data-flow-model.md` §5).

### 1.5 Formal view versus economic view

Every Core concept has two recorded faces:

- **Economic view** — the plain-language meaning and its source anchor
  (EI definition text, claim). This is what the CTO reviews and approves.
- **Formal view** — the Lean type/signature and what structure it reuses.

The mapping report's `note` column carries the economic reading of a row;
the Core ontology record carries the formal one. A declaration is
approved only when both faces are approved together; either face changing
is a new Core revision (never an in-place mutation).

### 1.6 Non-goals (explicit)

- No textbook-scale ontology; no OWL/RDF; no graph database dependency
  (locked at Gate 3, Option B).
- No automatic Core promotion; no declaration accepted because a model
  proposed it or because Lean compiles it.
- No v3 declarations as the v4 ontology (locked); no benchmark gold or
  intended-statements entering Core (§6).
- No provider logic, prompts, or adapter code inside Core.
- No theorem statements whose only support is an A3-local scaffolding
  file — promotion is a separate, reviewed act.

---

## 2. Reviewed glossary — seed from the four canonical claims (+ fwt1)

The glossary registry (full entries with Lean signature sketches, anchors,
variants, examples) is `references/core-glossary-detail.md`. The seed
below is the compact index: every term is a term a reviewed, VERIFIED
artifact actually used — the four canonical claims (c1–c4) **and the fwt1
First Welfare Theorem test (2026-08-06)**. **A term is in this glossary
because a reviewed artifact used it — not because a textbook listed it.**

| Term | Plain meaning | Seeded by | Lean anchor | Status |
|---|---|---|---|---|
| `weakPreference` (≽) | binary relation "at least as preferred as" | c2 (def) | Core candidate: `def weakPreference (α) := α → α → Prop` | core-candidate |
| `transitivity` | ∀a b c, aRb → bRc → aRc | c2 (def) | Mathlib `IsTrans` | mathlib |
| `reflexivity` | ∀a, aRa | c2 (proposed assumption) | Mathlib `IsRefl` | mathlib |
| `completeness` | ∀a b, aRb ∨ bRa | c2 (proposed assumption) | Mathlib `IsTotal` | mathlib |
| `alternative` | element of the choice domain | c2 (objects A/B/C) | type variable; role recorded in EI | glossary-only |
| `bundle` | consumption vector over goods | c1, c3, **fwt1** | Core candidate: `abbrev bundle (Goods : Type) [Fintype Goods] := Goods → ℝ` | core-candidate |
| `budgetSet` | affordable bundles {x \| p·x ≤ m} | c1 (def, obj), **fwt1** | Core candidate (see detail file) | core-candidate |
| `budgetExpansion` | `B_old ⊆ B_new` | c1 (assumption) | Mathlib `⊆` on `Set` | mathlib |
| `attainableSet` | affordable ∧ preference-satisfying (reviewer-selected reading) | c1 (def, obj, ambiguity) | Core candidate; record carries chosen meaning | core-candidate |
| `preferencesUnchanged` | expository condition, not a declaration | c1 (def) | no declaration; glossary-only condition | glossary-only |
| `consumer` | decision-maker role | c1 (obj), **fwt1** | type variable/role | glossary-only |
| `utilityFunction` | u : X → ℝ representing preferences | c3 (def), **fwt1** | Core candidate: `abbrev utility (X : Type) := X → ℝ` | core-candidate |
| `strictlyIncreasingUtility` | componentwise ≥ (one strict) ⇒ u(x) > u(y) | c3 (def, ambiguity) | Core candidate predicate | core-candidate |
| `componentwiseComparison` | pointwise vector order | c3 (def) | Mathlib `Pi.instLE` on `Goods → ℝ` | mathlib |
| `monotoneNondecreasing` | order-preserving f | c4 (def) | Mathlib `Monotone` | mathlib |
| `orderPreservation` | synonym of monotone (terminology ambiguity recorded) | c4 (def, ambiguity) | Mathlib `Monotone` | mathlib |
| `preferenceRelation` | umbrella ontology ref | c1, c2 (`ontology_refs`) | glossary umbrella over `weakPreference` | glossary-only |
| `rationalityAxiom` | completeness + transitivity (+ reflexivity) | c2 (`ontology_refs`) | glossary; Mathlib pieces | glossary-only |
| `budgetConstraint` | ontology ref → `budgetSet` | c1 (`ontology_refs`) | glossary | glossary-only |
| `solutionConcept` | meta-concept (equilibrium family) | c1–c4 (null); **fwt1 (non-null)** | no declaration in the initial slice | glossary-only |
| `exchangeEconomy` | no-production economy (agents, goods, endowments) | **fwt1** (EI) | glossary-only; context for equilibrium | glossary-only |
| `priceVector` | p : Goods → ℝ, equilibrium prices | **fwt1** (obj) | glossary-only (ℝ-valued function) | glossary-only |
| `allocation` | x : Agent → Bundle, who gets what | **fwt1** (obj) | glossary-only (function type) | glossary-only |
| `endowment` | e : Agent → Bundle, initial holdings | **fwt1** (obj) | glossary-only (function type) | glossary-only |
| `marketClearing` | per-good Σ allocations = Σ endowments | **fwt1** (def) | Core candidate (componentwise sum equality) | core-candidate |
| `competitiveEquilibrium` (Walrasian) | utility maximization in budget set + market clearing | **fwt1** (EI def, solution_concept) | Core candidate structure (feasible + maximizes) | core-candidate |
| `paretoEfficiency` | no feasible allocation makes every consumer strictly better off (strong form) | **fwt1** (EI def, ambiguity) | Core candidate predicate | core-candidate |
| `utilityMaximization` | chosen bundle is u-maximal in the budget set | **fwt1** (EI def) | glossary-only (property, folded into `competitiveEquilibrium`) | glossary-only |

Rules for the registry:

1. **Seeding rule.** New entries enter only from reviewed artifacts (an
   accepted EI definition, a mapping-report identifier, a CTO-approved
   claim term, or a VERIFIED claim family) — never from a model's prose.
2. **One canonical entry per concept.** The claims produced near-synonyms
   (`monotone_nondecreasing_function`, `order_preservation`; `weak_preference`,
   `preference_relation`; `competitive_equilibrium`, `Walrasian_equilibrium`);
   the glossary collapses them to one canonical entry each and records the
   aliases.
3. **Status ladder.** `glossary-only` (meaning reviewed, no Lean
   declaration) → `core-candidate` (a declaration is proposed, promotion
   criteria in §5) → `core` (promoted). `mathlib` terms are referenced,
   never duplicated.
4. **Aliases are recorded, not multiplied.** Each entry lists the EI
   definition ids that seeded it.
5. **The fwt1 extension is meaning-review only.** The equilibrium-family
   entries (21–28) are glossary-only/core-candidate *meanings*; their
   declarations are deferred to the Gate 7 slice per the migration plan's
   "start small" rule (§1.1). The fwt1 theorem itself remains an A3 test
   record, not a Core declaration.

---

## 3. Canonical element-id scheme (the mapping report's addressing)

The Gate 5 walkthrough found the formalizer does not reliably use the
canonical ids (`object:u`, definition titles instead of `definition:<i>`);
the strict completeness check surfaced them as gaps, and reviewer gap-acks
recorded the non-compliance as an evaluation signal. **The fwt1 test
repeated the definition-titles failure (8 gaps, all `definition:<i>` ids
missing)** — confirming the mechanism, not the model. **Core makes the
scheme normative** — it is the addressing contract the mapping report must
use, independent of what any model emits.

| EI element | Canonical id | Notes |
|---|---|---|
| claim record | `claim` | kind `claim` (c3's `"c3"` was non-canonical) |
| object | `objects[].id` verbatim | e.g. `consumer`, `u`, `x`, `feasible_budget_set` — **no `object:` prefix** |
| assumption | `assumption:<i>` | i = stable index over `assumptions` (proposed ∪ accepted, authored order) |
| definition | `definition:<i>` | i = index over `context.definitions` |
| quantifier | `quantifier:<i>` | i = index over `quantifiers` |
| conclusion | `conclusion` | singleton |
| solution/equilibrium concept | `solution_concept` | maps to `conclusion.solution_or_equilibrium_concept` |

Rules:

1. **Exactness.** Ids are authored in the accepted EI and must be used
   verbatim in mapping reports — no prefixes (`object:`), no titles, no
   paraphrases. A row whose id deviates is an **id-scheme deviation**
   (covered by an existing gap class, Gate 5 hardening), not a missing row.
2. **Stability.** Assumption/definition/quantifier indices are fixed at EI
   creation for the life of the revision. A reviewer move
   (proposed → accepted) preserves the id; the move is an event, not a
   renumbering.
3. **Completeness.** Every material element (objects with roles,
   assumptions, quantifiers, conclusion, solution concept, definitions
   that materially affect meaning) gets exactly one row. Unmapped material
   rows are visible gaps that block `PROVING` until a reviewer gap
   acknowledgement exists (A3 §4.4) — unchanged.
4. **Missing-element safety.** An id that has no EI element to anchor to
   (e.g. c1's report citing a hypothesis absent from the statement) is a
   report defect — the report must not invent elements. The reviewer
   catches this at mapping-report review; the id scheme makes it visible.
5. **fwt1 confirmation.** The solution_concept got a row (first non-null
   mapping) but mapped to the model's hypothesis name rather than a
   definition — the reviewer acknowledged it as an evaluation signal. The
   scheme's job is to make such rows *visible*, which it did.

---

## 4. Mapping-report target contract (once Core exists)

The A3 §4.2 table stays; Core adds the `core` mapping kind and tightens
the vocabulary. Target state of a row:

| Column | Value | Constraint |
|---|---|---|
| `ei_element_id` | canonical id (§3) | must exist in the accepted EI; used verbatim |
| `ei_element_kind` | object / assumption / quantifier / conclusion / solution / definition | from the EI element |
| `lean_identifier` | Mathlib id, **Core id (fully qualified, D1)**, glossary term, or A3-local scaffolding name | empty iff `status = unmapped` |
| `mapping_kind` | `mathlib` \| `core` \| `glossary_term` \| `local_definition` | `none` is **dropped** (see Open Q2) |
| `status` | `mapped` \| `unmapped` \| `deferred` | `deferred` only for expository context items |
| `provenance` | how the mapping was chosen | required |
| `note` | free-text justification, visible to the reviewer | required |

Mapping-kind semantics:

- `mathlib` — Mathlib structure reused as-is (`Set`, `Monotone`,
  `IsTrans`, pointwise order). No Core involvement.
- `core` — a **promoted** Core declaration (`LeanEcon.Core.…`). This is
  the new kind; it is what the EI's `ontology_refs` point AT. A `core`
  row is the strongest evidence a reviewer can get: the identifier was
  itself semantically reviewed. **D1: `core` rows carry the fully
  qualified identifier** (e.g. `LeanEcon.Core.Choice.attainableSet`,
  never bare `attainableSet`) — eliminating any `open`-based shadowing
  ambiguity; the row must resolve as written.
- `glossary_term` — a reviewed glossary term with **no** Lean declaration
  yet (interim). Always carries a promotion plan or an explicit deferral
  in the note. This is the honest middle state between "scaffolding" and
  "Core". The fwt1 equilibrium-family vocabulary (21–28) is
  `glossary_term` material today.
- `local_definition` — A3-local scaffolding inside the candidate file
  (MVP only; explicitly labeled; never promoted without the Gate 6
  process). **D4: scaffolding must be namespace-scoped**
  (`namespace A3Scaffolding.<claim>`), never root-namespace — the fwt1
  reviewer-authored proof and the c1–c4 fixtures all put scaffolding at
  root, which *can* shadow Mathlib within the file; namespacing removes
  the confound. Gate 5's `"A3-local scaffolding, not LeanEcon Core"`
  comment convention stays.

Completeness rule (unchanged from A3 §4.4, now anchored): material
elements must be `mapped` with kind `mathlib`, `core`, or `glossary_term`
— a `local_definition` for a material economic element is legal for MVP
but is itself a promotion candidate the reviewer sees. Unmapped material
elements block `PROVING` until gap acknowledgement.

**Where Core plugs into the verifier (A3 §5):** nothing changes in the
verifier itself. Core identifiers enter the candidate's imports; the
kernel checks them against the pinned workspace exactly as it checks
Mathlib. The axiom audit runs unchanged — a Core declaration carrying a
non-baseline axiom would surface there and fail until approved. **D2: the
bundle records the Core revision** (`workspace_identity.core_revision` +
Core imports in `dependency_audit`) so a `VERIFIED` result is
reproducible against the exact Core commit — see
`references/data-flow-model.md` §5.

---

## 5. Schema-freeze proposal (exercised draft → frozen)

The EI draft schema (`references/gate3/ei_schema_draft.json`) was
exercised live by Gate 5 A3 on the four canonical claims (plus the c1r2
pipeline-comparison run) **and by the fwt1 test** — its PENDING→APPROVED
flow, nullable review fields, ambiguity list, and `none_noted` handling
all validated again on a non-trivial claim. Three draft-schema changes are
now live-tested and are part of the freeze proposal:

1. **`none_noted`** (boolean) — set when the interpreter found no
   ambiguity; enforcement: the review command **requires**
   `acknowledges_none_noted: true` before `APPROVED` (tested in the review
   path; no live claim hit it — all live EIs had real ambiguities).
2. **Nullable `review.reviewer` / `review.event_ref` while `PENDING`** —
   null at interpretation time, set only by the reviewer approval event
   (exercised by all five live walkthroughs: c1–c4 and fwt1).
3. **`review.acknowledges_none_noted`** — the acknowledgement flag
   (enforcement path tested).

Freeze terms:

- Approve the **current file as-is** as the normative
  `EconomicInterpretation` contract, version `1.0.0`, `$id`
  `https://leanecon.org/schemas/economic-interpretation/1.0.0` — the
  exercised additions are part of the initial frozen version (no released
  consumers exist; there is no earlier 1.0.0 to be incompatible with).
  Alternative (freeze as `1.1.0` to flag the additions) was considered
  and rejected as churn.
- The file stays at `references/gate3/ei_schema_draft.json` (the code
  loads it from there; no churn); it gains a `$comment` (allowed by
  draft 2020-12) recording the freeze date, the exercised fields, and the
  approval ref. A freeze entry is added to `DECISION_LOG.md`.
- Versioning rules (unchanged from Gate 3, now normative): additive
  optional fields = minor; removing/renaming fields, changing meaning, or
  changing requiredness = major.
- Normative enforcement notes (already implemented in `interpretation.py`
  + the review command): `none_noted` ⇒ acknowledgement required;
  `reviewer`/`event_ref` null while `PENDING`; automated triage never
  sets `APPROVED`; `assumptions.accepted` empty at production (only the
  reviewer moves assumptions); classification fail-closed to
  `RESTRICTED`.

Exact diff record: `references/schema-freeze-proposal.md`.

---

## 6. v3 disposition register (Core material)

v3 is frozen evidence (tag `v3-freeze-20260804`). Per the migration plan,
custom v3 implementation defaults to `rebuild`/`inspiration`/
`historical-discard`; `import` and `adapt` require explicit exception
approval. **No exception is proposed here.**

| v3 artifact | Class | Disposition | Rationale |
|---|---|---|---|
| `lean_workspace/LeanEcon/Preamble/**` (Foundations, Preferences, Optimization, GameTheory, GeneralEquilibrium, Macroeconomics) | custom Lean | **rebuild** (scope taxonomy: **inspiration**) | Custom v3 Lean, never copied. The *categories* (preferences, utility, choice, optimization, GE, GT) inspire the v4 namespace skeleton (§1.3); every v4 declaration is authored first-principles and reviewed per §5 promotion criteria |
| `lean_workspace/LeanEcon/<uuid>.lean`, `local_gate_*.lean` | generated scratch | **historical-discard** | Ad-hoc candidate files, no curated value |
| `src/preamble_library.py` | Python orchestration | **rebuild** (concept: **inspiration**) | The "curated preamble" idea (declarations with meaning records) inspires Core's ontology record; v3 implementation is v3-specific |
| `benchmark_baselines/v3_alpha/tier1_core.json` | benchmark results | **historical-discard** | v3 benchmark evidence; never v4 release evidence (locked: no v3 score is comparable) |
| `evals/claim_sets/tier1_core_preamble_definable.jsonl` | claim set + **theorem stubs** | **historical-discard** (statement-shape: **inspiration**) | Contains intended formal statements — gold-shaped; kept out of v4 runtime, Core, and corpus. The `theorem_stub` *shape* (imports + named target theorem) informs the reviewed-fixture format, already independently re-authored at Gate 5 |
| v3 `docs/*` (evidence register, inventory, strategy) | evidence | **historical** | Retained as frozen evidence; referenced for provenance only |

The authoritative disposition register remains the Gate 3 migration
ledger (`docs/gate3/01`); this table is the Core-specific slice and feeds
a ledger update at implementation time.

**Contamination rules (mirror Gate 3/5, now Core-specific):**

- No benchmark gold, intended statement, or v3 stub enters Core as a
  declaration or theorem.
- No provider logic, prompt text, or adapter code enters Core.
- Promotion is per-declaration with a recorded CTO approval — never batch,
  never model-suggested without review.

---

## 7. Declaration promotion criteria (Gate 6 → implementation)

A declaration enters Core only when **all** of these hold (from the
migration plan's per-declaration list, made operational):

1. Plain-language economic meaning (economic view) — reviewed.
2. Lean type/signature explanation (formal view) — reviewed.
3. Assumptions and stronger/weaker variants listed.
4. Dependency/axiom audit (baseline axioms only unless separately
   approved per-run) **+ namespace collision check (D3): the
   fully-qualified name must not collide with any imported dependency's
   namespace, and unqualified use in candidates must not shadow imported
   Mathlib identifiers**.
5. Examples and counterexamples where useful.
6. A CTO approval record (event ref, reviewer, date) in the ontology
   record and the decision log.
7. It is **needed by a reviewed claim or a planned slice** — no orphan
   declarations.

The first promotion batch is bounded: the core-candidate terms of §2
(`weakPreference`, `bundle`, `budgetSet`, `attainableSet`,
`utilityFunction`, `strictlyIncreasingUtility`) + the two minimal theorem
boundaries supporting the c1/c3 families. The fwt1 equilibrium-family
terms (21–28) are **glossary-only today**; their declarations are the
Gate 7 slice. That batch is **implementation work after this design is
approved** — see `IMPLEMENTATION_PLAN.md`.

---

## 7.5 Live-test evidence (fwt1) — what the system proved

On 2026-08-06, after the design was first drafted, the A3 pipeline was
exercised end-to-end on the First Welfare Theorem (claim `fwt1`): a real
theorem with a real summation/contradiction proof. Result: **VERIFIED**
with a valid bundle and green trace replay. The record
(`references/fwt1-test-record.md`) documents expectations-before-run vs
actual, including:

- The formalizer failed **structurally** (Pareto content inverted into
  hypotheses; compile probe FAILED; 8 gaps) — the strongest live evidence
  yet that reviewer-in-the-loop is load-bearing.
- Every designed honest-failure mechanism fired (probe, gap classification
  + gap-ack, first-run axiom loop, reviewer-authored input, replay).
- The reviewer-authored FWT proof verified with the baseline axiom
  closure — "Core adds no axioms" holds on a real theorem.
- Eight new vocabulary items + the first non-null `solution_concept`
  mapping → the §2 glossary extension (entries 21–28).
- Two Lean lessons for implementation: `abbrev` capturing type params as
  implicit args breaks signature inference (use explicit `Goods → ℝ`
  shapes or explicit params), and `Finset.sum_lt_sum` needs the
  all-≤/one-strict form (`sum_lt_sum_of_nonempty` is the all-strict
  variant) — recorded in the implementation plan's risk register.

---

## 8. Open questions and proposed resolutions

| # | Question | Proposed resolution | Evidence / status |
|---|---|---|---|
| 1 | Bundle type family: `Goods → ℝ` with `[Fintype Goods]` vs `Fin n → ℝ` vs per-claim `ℝ`? | `abbrev bundle (Goods : Type) [Fintype Goods] := Goods → ℝ`; single-good claims may use `ℝ` directly (as c1's fixture does). Core defines the general family; claims choose the instance | **fwt1 confirmed** — the test formalization used `Goods → ℝ` with `[Fintype Goods]` + `[Fintype Agent]` and verified cleanly; the implicit-param pitfall (abbrev capturing `Goods`) is a documented Lean lesson |
| 2 | `mapping_kind: none` (seen on `solution_concept` rows): keep or drop? | **Drop.** An unmapped row is `status: unmapped` with empty `lean_identifier`; `solution_concept` with a null concept maps as `deferred`-style expository or stays unmapped+acknowledged | fwt1's solution_concept row was `mapped` (to the model's hypothesis name, acknowledged as an evaluation signal) — the `none`-kind question stands; proposal unchanged |
| 3 | Assumption id stability across proposed→accepted moves | Preserve the original index; the move is an event, not a renumbering | no new evidence; proposal stands |
| 4 | Schema freeze version: `1.0.0` (additions folded in) vs `1.1.0` (additions flagged) | `1.0.0` — no released consumers, no prior frozen version | fwt1 exercised the draft schema again (PENDING→APPROVED, nullable fields) — freeze proposal stands |
| 5 | Initial slice strictly the four claims' vocabulary, or add demand/choice correspondences now? | Strictly the four claims' vocabulary as declarations; the fwt1 equilibrium-family vocabulary joins as **glossary-only meanings** now, with declarations deferred to the Gate 7 slice | fwt1 provided the vocabulary; the migration plan's "start small" rule governs declarations |
| 6 | Where the glossary registry lives | `references/core-glossary-detail.md` (this package) becomes the registry; EI `context.definitions` keep per-claim copies as source anchors | **resolved** — registry in place, extended with fwt1 entries |
| 7 | Schema file location on freeze | Keep `references/gate3/ei_schema_draft.json` + `$comment` freeze note; no relocation churn | proposal stands |
| 8 | D1–D4 contract deltas (FQ core ids, Core pin in bundle, collision check, namespace-scoped scaffolding) | All four adopted as part of this design (§1.3, §1.4, §4, §7); implementation per the plan | D1/D4 directly motivated by the fwt1 test and the naming-overlap review; D2 by reproducibility; D3 by the Mathlib-collision analysis |

---

## 9. Process notes

- Current `main`: `7921e7b` (Gate 5 A3 + formalizer hardening merged). Test
  baseline verified: **137 passed** (Gate 6 design sessions added no code).
- Evidence used: the four VERIFIED bundles + mapping reports + accepted
  EIs under `artifacts/local/a3/`; the **fwt1 VERIFIED bundle +
  expectations-vs-actual record** (`artifacts/local/fwt1-expectations.md`,
  gitignored); `references/walkthrough-2026-08-06.md`; v3 frozen repo
  (read-only) for the disposition register.
- The Gate 6 package: this design + `references/` (glossary detail, schema
  freeze, toy walkthrough, data-flow model, fwt1 test record) +
  `IMPLEMENTATION_PLAN.md`.
- Workspace hygiene: the sandbox toy module and test scratch were removed
  after their demos; `LeanEcon.A1` rebuilds clean; the tree carries only
  the untracked Gate 6 package (no commits).
- Next step after approval: implementation **per the plan's phases**, each
  with CTO review — schema freeze commit first, then Core module
  scaffolding and the first promotion batch, then the A3 contract deltas
  (D1/D2/D4) and evidence.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This document
authorizes nothing; Core implementation proceeds only after CTO approval
of this design, the flagged open questions (resolutions above), and the
implementation plan.
