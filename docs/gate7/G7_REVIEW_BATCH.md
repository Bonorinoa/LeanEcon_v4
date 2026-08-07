# Gate 7 — Equilibrium-family Core promotion batch: CTO review package

> Status: **APPROVED 2026-08-06 by the CTO** — the batch was promoted
> (verdict: "approve as proposed"; per-declaration approval records §8).
> The slice (declarations + theorem boundary, decisions D1–D9) was
> approved in-session; all Lean compiled BEFORE this review (verbatim
> kernel evidence §6). The modules + this package are committed as the
> Gate 7 PR (PR #11); merge per the established flow.
>
> Authority: Gate 6 CLOSED (DECISION_LOG item 25; P5 exit packet §5.1
> carried-forward item 1); design + plan approved (items 15–18); glossary
> registry v1 locked (item 17); slice approved as proposed (D1–D9, this
> session).

## 0. Batch at a glance

| # | Declaration | Area | Seeded by | Kind | Compiles | Axioms |
|---|---|---|---|---|---|---|
| 1 | `budgetSetEndowment {Goods} [Fintype Goods] (p e : Goods → ℝ) : Set (bundle Goods)` | Constraints | fwt1 `FwtBudget`; P2 D2 | def | ✅ | baseline |
| 2 | `marketClearing {Agent Goods} [Fintype Agent] (e x : Agent → bundle Goods) : Prop` | Equilibrium | fwt1 `FwtFeasible` | def | ✅ | baseline |
| 3 | `competitiveEquilibrium {Agent Goods} [Fintype Agent] [Fintype Goods] (e) (u) (x) (p) : Prop` | Equilibrium | fwt1 `FwtWalrasian` | structure | ✅ | baseline |
| 4 | `paretoEfficiency {Agent Goods} [Fintype Agent] (e u x) : Prop` | Equilibrium | fwt1 `FwtParetoOptimal` | def | ✅ | baseline |
| T3 | `competitiveEquilibrium_paretoEfficient` (FWT boundary) | Theorems | claim fwt1 (VERIFIED) | theorem | ✅ | baseline |

Source anchors (all reviewed artifacts): fwt1 accepted EI
`artifacts/local/a3/eis/fwt1/rev-2.json`, mapping report
`artifacts/local/a3/formal/fwt1/rev-1.json`, gap-ack
`artifacts/local/a3/reviews/fwt1/gap-1.json`, reviewer proof input
`artifacts/local/fwt1/proof_input.lean`, VERIFIED bundle
`bundle-fwt1-r1-35615e`. Glossary entries promoted: **25, 26, 27 →
core**; entry 7 (budget-set) gains the landed variant note; entry 28
stays glossary-only (decision D5).

## 1. Ontology records (per declaration)

### 1. `budgetSetEndowment` — Constraints
- **Economic view:** bundles an agent can afford at prices p when its
  wealth is the market value of its endowment e: {x | Σ_g p_g·x_g ≤
  Σ_g p_g·e_g}. P2 decision D2 explicitly deferred the dedicated form to the
  equilibrium slice; this is that landing.
- **Formal view:** `def budgetSetEndowment {Goods} [Fintype Goods]
  (p : Goods → ℝ) (e : Goods → ℝ) : Set (bundle Goods) := budgetSet p
  (∑ g, p g * e g)` — definitionally the P2-documented recovery
  (`budgetSet p (∑ g, p g * e i g)`), given a name so the glossary's
  two-argument budget (entry 26 sketch: `budget p (e i)`) has a named home.
- **Assumptions:** `[Fintype Goods]` for the sum. Variants: income form
  (`budgetSet`, P2); no nonnegativity/positivity assumptions — matching
  fwt1, where the EI's proposed assumptions were shown unnecessary.
- **Axiom audit:** `[propext, Classical.choice, Quot.sound]` (verbatim §6).
  **D3:** no Mathlib root name (probe + 2 greps, §6). ✅
- **Examples:** fwt1 `FwtBudget p (e i)` — the exact shape in the VERIFIED
  proof; `competitiveEquilibrium.maximizes` (this batch) uses it.
- **Source:** fwt1 proof input (`FwtBudget`); glossary entry 7 variant;
  P2 D2 decision.

### 2. `marketClearing` — Equilibrium
- **Economic view:** markets clear when for every good, total consumption
  equals total endowment: Σ_i x_i,g = Σ_i e_i,g. Entry 25's "componentwise
  sum equality".
- **Formal view:** `def marketClearing {Agent Goods} [Fintype Agent]
  (e x : Agent → bundle Goods) : Prop := ∀ g : Goods, (∑ i, x i g) =
  (∑ i, e i g)`. Minimal constraint set: the sum is over agents, so only
  `[Fintype Agent]`; `∀ g` over goods needs no Fintype. `[Fintype Goods]`
  enters where budget sets do (structure/theorem level).
- **Assumptions:** none beyond `[Fintype Agent]`. Variants: adding
  `[Fintype Goods]` for uniformity (rejected — minimality); weak (≤) form
  (no recorded claim uses it — equality is the fwt1 reading).
- **Axiom audit:** baseline (verbatim §6). **D3:** clean. ✅
- **Examples:** fwt1 `FwtFeasible` (served double duty as feasibility in
  the claim).
- **Source:** fwt1 EI definition `feasible_allocation` + market clearing
  inside `competitive_equilibrium`; ontology ref `market_clearing`; entry 25.

### 3. `competitiveEquilibrium` — Equilibrium
- **Economic view:** prices p and allocation x such that every consumer
  maximizes utility in their endowment-relative budget set and markets
  clear. Entry 26 (alias: Walrasian-equilibrium). **Direct
  utility-maximization reading** — the strong Pareto theorem then needs no
  local nonsatiation (classic result; recorded in the fwt1 proof header).
- **Formal view:** `structure competitiveEquilibrium {Agent Goods}
  [Fintype Agent] [Fintype Goods] (e) (u : Agent → bundle Goods → ℝ) (x)
  (p : Goods → ℝ) : Prop where feasible : marketClearing e x; maximizes :
  ∀ i, x i ∈ budgetSetEndowment p (e i) ∧ ∀ y, y ∈ budgetSetEndowment
  p (e i) → u i y ≤ u i (x i)`. Field-based (`h.maximizes i` is how the
  FWT proof accesses it).
- **Assumptions:** `[Fintype Agent] [Fintype Goods]`; direct reading
  (recorded decision D2). Variants: weak form requiring local nonsatiation
  (rejected — changes the reviewed meaning); fwt1's `FwtWalrasian` local
  scaffolding is superseded by this declaration for Core-importing claims.
- **Axiom audit:** baseline (verbatim §6). **D3:** clean. ✅
- **Examples:** fwt1 `FwtWalrasian`; the canonical exchange-economy GE
  concept.
- **Source:** fwt1 EI definitions `competitive_equilibrium`,
  `Walrasian_equilibrium`; ontology refs `general_equilibrium`,
  `consumer_optimization`; the non-null `solution_concept` row.

### 4. `paretoEfficiency` — Equilibrium
- **Economic view:** no feasible allocation makes every consumer strictly
  better off — **strong form** (the fwt1 EI ambiguity "weak vs strong
  Pareto" resolved at review to this reading). Entry 27.
- **Formal view:** `def paretoEfficiency {Agent Goods} [Fintype Agent]
  (e) (u : Agent → bundle Goods → ℝ) (x : Agent → bundle Goods) : Prop :=
  ¬ ∃ y, marketClearing e y ∧ ∀ i, u i (x i) < u i (y i)`.
- **Assumptions:** strong form. `[Nonempty Agent]` deliberately NOT on the
  definition (decision D4) — the definition is total and the empty economy
  is simply not Pareto efficient under this reading; the implication
  claim needs Nonempty, and it lives on the theorem (matching the fwt1
  proof header). Variants: weak form (∃ strict with all weak) — rejected,
  not the reviewed meaning.
- **Axiom audit:** baseline (verbatim §6). **D3:** clean. ✅
- **Example / counterexample:** the empty-economy degeneracy (definition
  yields `False`) — the real semantic edge the interpreter did not
  surface, now documented at the theorem boundary instead of hidden.
- **Source:** fwt1 EI definition `Pareto_efficient`; ambiguity "Strength of
  Pareto efficiency"; ontology ref `Pareto_optimality`.

### T3. `competitiveEquilibrium_paretoEfficient` — Theorems (fwt1 family)
- **Economic view:** the First Welfare Theorem for the exchange economy —
  every competitive equilibrium allocation is Pareto efficient (strong
  form). The fwt1 VERIFIED claim, now a Core theorem boundary (P2 T1/T2
  pattern).
- **Formal view:** `theorem ... {Agent Goods} [Fintype Agent] [Fintype
  Goods] [Nonempty Agent] {e} {u} {x} {p} (h : competitiveEquilibrium e u
  x p) : paretoEfficiency e u x`. Proof (ported verbatim from the VERIFIED
  fwt1 input): strict domination ⇒ each y_i outside its budget set
  (maximization contradicts) ⇒ per-agent value e < value y
  (`lt_of_not_ge`) ⇒ sum over agents (`sum_lt_sum_of_nonempty`) ⇒
  feasibility equates totals (double-sum reorder, `sum_comm` + `mul_sum`)
  ⇒ contradiction.
- **Assumptions:** `[Nonempty Agent]` explicit — the empty-economy
  semantic gap carried into Core as a documented hypothesis, not hidden.
- **Axiom audit:** `[propext, Classical.choice, Quot.sound]` (verbatim
  §6). **D3:** clean. ✅
- **Source:** claim fwt1 (VERIFIED); bundle `bundle-fwt1-r1-35615e`;
  reviewer proof input.

## 2. Promotion-criteria checklist (a3-core-design.md §7)

| Criterion | Status |
|---|---|
| 1. Plain-language economic meaning | ✅ ontology records (economic views, all from reviewed registry entries) |
| 2. Lean signature explanation | ✅ formal views per record |
| 3. Assumptions + stronger/weaker variants | ✅ per record (D2 direct reading; D4 Nonempty placement; income vs endowment forms) |
| 4. Dependency/axiom audit + D3 collision | ✅ all five baseline (verbatim); probe = 5 unknown identifiers; root-decl grep exit 1; any-occurrence grep exit 1 |
| 5. Examples/counterexamples | ✅ fwt1 anchors + empty-economy counterexample |
| 6. CTO approval record | ⬅️ **this review** (per-declaration records §6 after approval) |
| 7. Needed by a reviewed claim / planned slice | ✅ every declaration traces to the fwt1 accepted EI / mapping report / VERIFIED bundle — no orphans; T3 ↔ fwt1 family |

## 3. Decisions (D1–D9, approved as tabled 2026-08-06)

| # | Decision | Proposal (chosen) | Alternatives |
|---|---|---|---|
| D1 | `marketClearing` signature | `[Fintype Agent]` only (sum over agents; ∀ over goods) | +`[Fintype Goods]` for uniformity; raw `Agent → Goods → ℝ` |
| D2 | `competitiveEquilibrium` shape | `structure … : Prop where feasible; maximizes` — direct maximization reading | weak form + nonsatiation (meaning change) |
| D3 | Endowment-relative budget set | dedicated `budgetSetEndowment` in Constraints | inline recovery, zero new declarations |
| D4 | `[Nonempty Agent]` placement | on the theorem, not the definition | on `paretoEfficiency` (changes reviewed meaning) |
| D5 | `utilityMaximization` (entry 28) | stays glossary-only, folded into `maximizes` | standalone predicate (scope growth) |
| D6 | FWT theorem boundary | in-batch `competitiveEquilibrium_paretoEfficient` | declarations-only; name `firstWelfareTheorem` |
| D7/D8 | Module layout / home | `Equilibrium.lean` new; `budgetSetEndowment` in Constraints; theorem in Theorems | budgetSetEndowment inside Equilibrium |
| D9 | Scope | no tooling deltas (D3 CI grep, verify-side signal, `none`-kind removal) | CTO opt-in |

## 4. What is deliberately NOT in this batch

- **No declarations for entries 21–24** (`exchangeEconomy`, `priceVector`,
  `allocation`, `endowment`) — glossary-only; realized as types/roles in
  the batch's signatures, exactly as in fwt1.
- **No standalone `utilityMaximization`** (entry 28 — D5).
- No demand/choice correspondences, no representation theorems, no
  production `VERIFIED` claims importing Core (P5.2 flow remains the
  template).
- No tooling deltas: D3 CI grep, verify-side scaffolding signal,
  `mapping_kind: none` removal (P4 D7/D8 deferred items — recorded in
  `P4_REVIEW_BATCH.md`).
- No B2 proof loop, corpus, retrieval, release; no A3 code changes; no
  registry **meaning** changes (status moves only, per registry v1 rules).
- No v3 material (rebuild/inspiration dispositions unchanged, ledger K1–K6).

## 5. Expectations vs actuals (prediction-first, recorded pre-run)

Full record: `artifacts/local/gate7-expectations.md` (gitignored).

| # | Predicted | Actual | Verdict |
|---|---|---|---|
| 1 | build PASS, incremental | PASS, 3002 jobs, exit 0 | ✅ |
| 2 | budgetSetEndowment Set-valued | `Set (bundle Goods)` | ✅ |
| 3 | marketClearing ∀ g sums | `(e x : Agent → bundle Goods) : Prop` | ✅ |
| 4 | competitiveEquilibrium structure Prop | `: Prop`, feasible/maximizes | ✅ |
| 5 | paretoEfficiency ¬ ∃ y | `(e u x) : Prop` | ✅ |
| 6 | theorem compiles 1st try | **semantic port compiled first build**; linter-compliance pass had 1 dead-tactic on the linter's own `simp at` suggestion (fixed; no semantic iterations) | ✅ (nuance) |
| 7 | baseline axioms | `[propext, Classical.choice, Quot.sound]` on theorem + all 4 defs | ✅ |
| 8 | D3 unknown identifiers | 5 × unknownIdentifier; greps exit 1 | ✅ |
| 9 | pytest 156 | 156 passed in 33.95s | ✅ |

**9/9 confirmed** — including the two predictions that mattered (first-try
theorem port, baseline axiom closure on a real theorem).

## 6. Verbatim kernel evidence (pinned workspace, leanprover/lean4:v4.32.2, Mathlib v4.32.2)

```
$ lake build LeanEcon.Core.Equilibrium LeanEcon.Core.Constraints LeanEcon.Core.Theorems
✔ [3002/3002] Built LeanEcon.Core.Theorems (1.5s)
Build completed successfully (3002 jobs).
BUILD_EXIT=0

$ lake env lean .a3-candidates/gate7-check/Check.lean ; echo "CHECK_EXIT=$?"
LeanEcon.Core.Constraints.budgetSetEndowment {Goods : Type} [Fintype Goods] (p e : Goods → ℝ) :
  Set (LeanEcon.Core.Primitives.bundle Goods)
LeanEcon.Core.Equilibrium.marketClearing {Agent Goods : Type} [Fintype Agent]
  (e x : Agent → LeanEcon.Core.Primitives.bundle Goods) : Prop
LeanEcon.Core.Equilibrium.competitiveEquilibrium {Agent Goods : Type} [Fintype Agent] [Fintype Goods]
  (e : Agent → LeanEcon.Core.Primitives.bundle Goods) (u : Agent → LeanEcon.Core.Primitives.bundle Goods → ℝ)
  (x : Agent → LeanEcon.Core.Primitives.bundle Goods) (p : Goods → ℝ) : Prop
LeanEcon.Core.Equilibrium.paretoEfficiency {Agent Goods : Type} [Fintype Agent]
  (e : Agent → LeanEcon.Core.Primitives.bundle Goods) (u : Agent → LeanEcon.Core.Primitives.bundle Goods → ℝ)
  (x : Agent → LeanEcon.Core.Primitives.bundle Goods) : Prop
LeanEcon.Core.Theorems.competitiveEquilibrium_paretoEfficient {Agent Goods : Type} [Fintype Agent] [Fintype Goods]
  [Nonempty Agent] {e : Agent → LeanEcon.Core.Primitives.bundle Goods}
  {u : Agent → LeanEcon.Core.Primitives.bundle Goods → ℝ} {x : Agent → LeanEcon.Core.Primitives.bundle Goods}
  {p : Goods → ℝ} (h : LeanEcon.Core.Equilibrium.competitiveEquilibrium e u x p) :
  LeanEcon.Core.Equilibrium.paretoEfficiency e u x
'LeanEcon.Core.Constraints.budgetSetEndowment' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Equilibrium.marketClearing' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Equilibrium.competitiveEquilibrium' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Equilibrium.paretoEfficiency' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Theorems.competitiveEquilibrium_paretoEfficient' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
CHECK_EXIT=0

$ lake env lean .a3-candidates/gate7-check/MathlibProbe.lean ; echo "PROBE_EXIT=$?"
.a3-candidates/gate7-check/MathlibProbe.lean:9:7: error(lean.unknownIdentifier): Unknown identifier `marketClearing`
.a3-candidates/gate7-check/MathlibProbe.lean:10:7: error(lean.unknownIdentifier): Unknown identifier `competitiveEquilibrium`
.a3-candidates/gate7-check/MathlibProbe.lean:11:7: error(lean.unknownIdentifier): Unknown identifier `paretoEfficiency`
.a3-candidates/gate7-check/MathlibProbe.lean:12:7: error(lean.unknownIdentifier): Unknown identifier `budgetSetEndowment`
.a3-candidates/gate7-check/MathlibProbe.lean:13:7: error(lean.unknownIdentifier): Unknown identifier `competitiveEquilibrium_paretoEfficient`
PROBE_EXIT=1

$ grep -rnE '^\s*(protected\s+)?(def|abbrev|structure|class|inductive|theorem|lemma|instance)\s+(marketClearing|competitiveEquilibrium|paretoEfficiency|budgetSetEndowment|competitiveEquilibrium_paretoEfficient)\b' .lake/packages/mathlib/Mathlib/
grep_root_exit=1   # no root-level declarations carry any of the five names
$ grep -rlE '\b(marketClearing|competitiveEquilibrium|paretoEfficiency|budgetSetEndowment|competitiveEquilibrium_paretoEfficient)\b' .lake/packages/mathlib/Mathlib/
grep_any_exit=1    # no occurrence anywhere in Mathlib source
```

The probe's non-zero exit is the evidence (unknown identifier = no Mathlib
root name); grep exits 1 = no matches. D3 is triple-verified.

## 7. Process notes

- Files: `lean_workspace/LeanEcon/Core/{Constraints,Equilibrium,Theorems}.lean`
  (modified/new — Equilibrium is the module created by this batch, no empty
  modules rule honored). Check files under `lean_workspace/.a3-candidates/
  gate7-check/` (gitignored). Docs: this package (new `docs/gate7/`).
- Reproducible: `lake build LeanEcon.Core.Equilibrium LeanEcon.Core.
  Constraints LeanEcon.Core.Theorems` + `lake env lean .a3-candidates/
  gate7-check/Check.lean`.
- After approval (per P2 pattern): per-declaration approval records (§8 of
  this package), registry change-log rows (entries 25/26/27 → core; entry 7
  variant note; entry 28 unchanged), DECISION_LOG items 26+ (batch approved;
  commit pending), then the commit/PR — dispatch scaffold+a1, verify checks
  green via check-runs API (latest run per name), `merge_pr.py <PR>
  clear-checks`, confirm protection restore with `verify_protection.py`.

## 8. Approval records (per declaration)

Promotion criterion 6. The CTO approved the batch as proposed on
2026-08-06 (slice D1–D9 tabled in-session; batch verdict: "approve as
proposed"); each declaration is approved individually below (reviewer:
Bonorinoa; ref: DECISION_LOG item 26 + Gate 7 PR #11).

| Declaration | Approved | Reviewer | Ref |
|---|---|---|---|
| 1 `budgetSetEndowment` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 26, PR #11 |
| 2 `marketClearing` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 26, PR #11 |
| 3 `competitiveEquilibrium` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 26, PR #11 |
| 4 `paretoEfficiency` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 26, PR #11 |
| T3 `competitiveEquilibrium_paretoEfficient` | ✅ 2026-08-06 | Bonorinoa | DECISION_LOG 26, PR #11 |

All 7 promotion criteria satisfied for every declaration; the batch builds
in the pinned workspace; axiom closures are the Mathlib baseline (verbatim
§6).

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This package
promotes nothing; per-declaration approval records must accompany any
commit.
