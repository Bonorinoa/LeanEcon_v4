# Lean proof-authoring patterns — reviewer-authored inputs (fwt1, 2026-08-06)

When to use: authoring the load-bearing reviewer statement + proof for an
A3 claim (the formalizer is a drafting aid; the reviewer-authored input is
what gets VERIFIED). Everything below was compiled against the pinned
workspace (Lean v4.32.2, Mathlib v4.32.2) and the Mathlib signatures were
confirmed with `#check`.

## 1. The fwt1 flow (worked end-to-end pipeline test)

First Welfare Theorem claim → the exact recovery sequence:

1. `interpret` → schema-valid EI (solution_concept NON-null for the first
   time: "Pareto efficiency of Walrasian equilibrium").
2. `review --decision approve` → ACCEPTED (EI rev 2).
3. `formalize` → claim reached FORMALIZED but **compile probe FAILED
   (exit 1, empty stderr_tail)** + 8 `genuinely_missing` gaps (definition
   rows used TITLES, not `definition:<i>`); Pareto content inverted into
   hypotheses. Formalizer output preserved as evaluation evidence.
4. `gap-ack` (records the probe failure + id non-compliance + inversion as
   evaluation signals) → PROVING allowed.
5. `verify --proof <reviewer file>` → first run `PROVING → FAILED
   (AXIOM_VIOLATION)` surfacing `Classical.choice, Quot.sound, propext`
   (the designed first-run loop).
6. `axiom-approve --axioms "Classical.choice,Quot.sound,propext"` →
   re-verify → **all 11 bundle checks green** → `status` = VERIFIED,
   `replay` = replay_ok (12 events, 0 problems).

## 2. FWT formalization skeleton (reuse for welfare/exchange claims)

```lean
variable {Agent Goods : Type} [Fintype Agent] [Fintype Goods]

def FwtFeasible (e : Agent → Goods → ℝ) (y : Agent → Goods → ℝ) : Prop :=
  ∀ g : Goods, (∑ i : Agent, y i g) = (∑ i : Agent, e i g)

def FwtBudget (p : Goods → ℝ) (ei : Goods → ℝ) : Set (Goods → ℝ) :=
  {x | (∑ g : Goods, p g * x g) ≤ (∑ g : Goods, p g * ei g)}

structure FwtWalrasian (e : Agent → Goods → ℝ) (u : Agent → (Goods → ℝ) → ℝ)
    (x : Agent → Goods → ℝ) (p : Goods → ℝ) : Prop where
  feasible : FwtFeasible e x
  maximizes : ∀ i : Agent, x i ∈ FwtBudget p (e i) ∧
    ∀ y : Goods → ℝ, y ∈ FwtBudget p (e i) → u i y ≤ u i (x i)

def FwtParetoOptimal (e : Agent → Goods → ℝ) (u : Agent → (Goods → ℝ) → ℝ)
    (x : Agent → Goods → ℝ) : Prop :=
  ¬ ∃ y : Agent → Goods → ℝ, FwtFeasible e y ∧ ∀ i : Agent, u i (x i) < u i (y i)
```

Proof skeleton (the summation/contradiction argument):
1. `rintro ⟨y, hy_feas, hy_better⟩` (goal is `¬ ∃ …`).
2. Each `y i ∉ FwtBudget p (e i)` — else maximization gives `u i (y i) ≤
   u i (x i)`, contradicting `hy_better i` via `lt_of_lt_of_le` +
   `lt_irrefl`.
3. Per-agent strict values: `exact lt_of_not_ge (hy_out i)` (budget
   non-membership ⇒ endowment value < allocation value).
4. Sum over agents: `Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty
   (fun i _ => hstrict i)`.
5. Feasibility ⇒ totals equal: reorder with `Finset.sum_comm` (simpa +
   explicit `s`/`t`/`f`), pull prices out with `Finset.mul_sum`, rewrite
   `hy_feas g`, reorder back.
6. Contradiction: `simpa [hsum_eq] using hsum_lt` then `lt_irrefl`.

**`[Nonempty Agent]` is REQUIRED** — with zero agents the strong Pareto
definition is `¬ ∃ y, True ∧ True` = False, so the theorem would be false
without it. This was a real semantic gap the interpreter did not surface;
the reviewer adds it and records the decision.

**Core names (Gate 7):** prefer `marketClearing`, `budgetSetEndowment`,
`competitiveEquilibrium`, `paretoEfficiency`, theorem
`competitiveEquilibrium_paretoEfficient` over the local `Fwt*` scaffolding
above when writing new Core-importing proofs (oos1 IR-at-CE used Core).

## 2b. Strict budget expansion (oos2, 2026-08-08)

Claim: `m1 < m2` + strictly positive prices ⇒ `budgetSet p m1 ⊂ budgetSet p m2`.

```lean
theorem budget_set_strictly_expands {Goods : Type} [Fintype Goods] [Nonempty Goods]
    [DecidableEq Goods]
    (p : Goods → ℝ) (m1 m2 : ℝ) (hp : ∀ g, 0 < p g) (hm : m1 < m2) :
    budgetSet p m1 ⊂ budgetSet p m2 := by
  refine ssubset_iff_subset_not_subset.mpr ⟨?subset, ?nsuperset⟩
  · intro x hx
    simp only [budgetSet, Set.mem_setOf_eq] at hx ⊢
    exact le_trans hx (le_of_lt hm)
  · -- point-mass witness costing exactly m2 on default good
    inhabit Goods
    set g0 : Goods := default
    -- x g = if g = g0 then m2 / p g0 else 0
    -- ∑ p*x = m2 via sum_congr + split_ifs + field_simp
    ...
```

Semantic edges (interpreter did not surface):
- **`[Nonempty Goods]`** — empty goods ⇒ every budget set is a singleton ⇒
  strict expansion is false (same class as fwt1 `[Nonempty Agent]`).
- **`[DecidableEq Goods]`** — needed for the `if g = g0` point-mass witness.
- Subset half is `le_trans` + `le_of_lt`; strict half is witness ∉ B(m1).

## 3. Mathlib gotchas (verified signatures, v4.32.2)

- **`abbrev X := Goods → ℝ` captures `Goods` as an IMPLICIT parameter** →
  "don't know how to synthesize implicit argument `Goods`" at declaration
  headers (parameter types are resolved before the body). Fix: inline
  `Goods → ℝ` in signatures (fwt1 iteration 1).
- `Finset.sum_lt_sum : (hle : ∀ i ∈ s, f i ≤ g i) (hlt : ∃ i ∈ s, f i <
  g i) : ∑ f < ∑ g` — all-≤ + ONE strict. The all-strict form is
  **`Finset.sum_lt_sum_of_nonempty : (hs : s.Nonempty) (hlt : ∀ i ∈ s,
  f i < g i) : ∑ f < ∑ g`** (fwt1 iteration 2; `[AddCommMonoid] [Preorder]
  [IsOrderedCancelAddMonoid]` — fine for ℝ).
- `Finset.mul_sum (s : Finset ι) (f : ι → R) (a : R) : a * ∑ i ∈ s, f i =
  ∑ i ∈ s, a * f i` — explicit args in (s, f, a) order; use
  `simpa using (Finset.mul_sum (Finset.univ : Finset Agent) (fun i => y i
  g) (p g)).symm` for the direction `∑ a*f = a * ∑ f`.
- `Finset.sum_comm {s} {t} {f} : ∑ x ∈ s, ∑ y ∈ t, f x y = ∑ y ∈ t,
  ∑ x ∈ s, f x y` — implicit args; `simpa using (Finset.sum_comm (s :=
  (Finset.univ : Finset Agent)) (t := (Finset.univ : Finset Goods)) (f :=
  fun i g => p g * y i g))` closes binder-form gaps (Fintype `∑ i, x` is
  defeq to `∑ i ∈ univ, x`).
- `lt_of_not_ge : ¬ a ≥ b → a < b` — the bridge from budget
  non-membership to strict value inequality.
- `Finset.univ_nonempty : (Finset.univ : Finset α).Nonempty` — needs
  `[Fintype α] [Nonempty α]`.
- **`simp [h] at h'` deriving `False` auto-closes the goal** (Gate 7,
  2026-08-06): when a hypothesis simplifies to `False` (e.g. rewriting
  `∑e < ∑y` with `h_eq : ∑y = ∑e` gives `a < a` → `False`), `simp at h'`
  solves the goal outright — a trailing `exact h'` errors with "No goals
  to be solved". Apply the linter's `unnecessarySimpa` suggestions
  literally: `simpa [h_eq] using h_lt` → `simp [h_eq] at h_lt` (no exact
  line). This is a compile-failure-class difference between `simpa
  using` and `simp at`, not a semantic one.
- `sorryAx` in `#print axioms` while the file has compile errors is
  error residue, not a real sorry — fix the error and it disappears
  (fwt1 iteration 1 showed `[propext, sorryAx, Classical.choice,
  Quot.sound]`; after the fix: `[propext, Classical.choice,
  Quot.sound]`).
- Specific imports `Mathlib.Data.Real.Basic` + `Mathlib.Tactic` suffice
  for ℝ, `Set`, `Fintype`, and `∑` (see `sandbox-toy-demo.md`).

## 4. Axiom expectations for economic proofs

The FWT proof (classical reasoning via `lt_of_not_ge`) closed with exactly
the Mathlib baseline: `[propext, Classical.choice, Quot.sound]`. Any proof
using `by_contra`/`lt_of_not_ge`/`classical` will likely pull
`Classical.choice`; that is expected and covered by the per-run axiom
record once per claim (baseline approval). Zero-axiom theorems need no
record (bundle check 6 vacuous).

## 5. Evaluation-signal record (fwt1)

- Formalizer: structural inversion (conclusion content in hypotheses) —
  new failure class beyond vacuity; see SKILL.md §4.
- Mapping report: definition TITLES instead of `definition:<i>` → 8
  `genuinely_missing` gaps; solution_concept mapped (non-null) to the
  hypothesis name.
- Core equilibrium family later **promoted Gate 7** (PR #11); OOS oos1/oos2
  first live claim-level `12_core_pin`. See `references/oos-batch-complete.md`.
- Expectations-first run record: `artifacts/local/fwt1-expectations.md`
  (predicted 7/7 vs actual; belief-vs-working comparison table).
