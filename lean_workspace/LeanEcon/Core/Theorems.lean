/-
LeanEcon.Core.Theorems — reviewed theorem boundaries.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md. Each theorem boundary supports a VERIFIED
canonical claim family; statements are honest about their assumptions.
-/
import LeanEcon.Core.Choice
import LeanEcon.Core.Equilibrium
import LeanEcon.Core.Utility
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core

namespace Theorems

open Choice
open Constraints
open Equilibrium
open Primitives
open Utility

/-- c1 family (VERIFIED claim c1): expanding the feasible set does not
    shrink the attainable set. The assumption `Bold ⊆ Bnew` is stated, not
    hidden. -/
theorem budgetExpansion_nonShrinking {Goods : Type} {Bold Bnew : Set (bundle Goods)}
    (h : Bold ⊆ Bnew) : attainableSet Bold ⊆ attainableSet Bnew := by
  simpa [attainableSet] using h

/-- c3 family (VERIFIED claim c3): a strictly increasing utility is
    strictly increasing in the componentwise order. Direction convention as
    in the c3 fixture: `hxy : y ≤ x` states the English "x ≥ y". -/
theorem strictlyIncreasing_strictPref {Goods : Type} {u : bundle Goods → ℝ}
    (hu : strictlyIncreasing u) {x y : bundle Goods} (hxy : y ≤ x) (hne : y ≠ x) :
    u y < u x := by
  exact hu x y hxy hne

/-- First Welfare Theorem (fwt1 family, VERIFIED claim fwt1): every
    competitive equilibrium allocation is Pareto efficient (strong form,
    exchange economy). Reviewer-authored proof ported from
    artifacts/local/fwt1/proof_input.lean. `[Nonempty Agent]` is required —
    the empty-economy case makes the strong Pareto claim false (a real
    semantic gap the interpreter did not surface; recorded in the fwt1
    proof header). -/
theorem competitiveEquilibrium_paretoEfficient {Agent Goods : Type} [Fintype Agent]
    [Fintype Goods] [Nonempty Agent] {e : Agent → bundle Goods}
    {u : Agent → bundle Goods → ℝ} {x : Agent → bundle Goods} {p : Goods → ℝ}
    (h : competitiveEquilibrium e u x p) : paretoEfficiency e u x := by
  rintro ⟨y, hy_feas, hy_better⟩
  -- 1. each agent's y_i is outside its budget set
  have hy_out : ∀ i : Agent, y i ∉ budgetSetEndowment p (e i) := by
    intro i hyi
    have hle : u i (y i) ≤ u i (x i) := (h.maximizes i).2 (y i) hyi
    have hlt : u i (x i) < u i (x i) := lt_of_lt_of_le (hy_better i) hle
    exact (lt_irrefl (u i (x i))) hlt
  -- 2. hence each agent's endowment value is strictly below its allocation value
  have hstrict : ∀ i : Agent, (∑ g : Goods, p g * e i g) < (∑ g : Goods, p g * y i g) := by
    intro i
    exact lt_of_not_ge (hy_out i)
  -- 3. summing over agents: total value of e < total value of y
  have hsum_lt : (∑ i : Agent, ∑ g : Goods, p g * e i g) <
      (∑ i : Agent, ∑ g : Goods, p g * y i g) := by
    exact Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty (fun i _ => hstrict i)
  -- 4. but feasibility gives total value of e = total value of y
  have hsum_eq : (∑ i : Agent, ∑ g : Goods, p g * y i g) =
      (∑ i : Agent, ∑ g : Goods, p g * e i g) := by
    calc
      (∑ i : Agent, ∑ g : Goods, p g * y i g) =
          ∑ g : Goods, ∑ i : Agent, p g * y i g := by
        simpa using (Finset.sum_comm (s := (Finset.univ : Finset Agent))
          (t := (Finset.univ : Finset Goods)) (f := fun i g => p g * y i g))
      _ = ∑ g : Goods, p g * (∑ i : Agent, y i g) := by
        apply Finset.sum_congr rfl
        intro g _
        rw [← Finset.mul_sum]
      _ = ∑ g : Goods, p g * (∑ i : Agent, e i g) := by
        apply Finset.sum_congr rfl
        intro g _
        rw [hy_feas g]
      _ = ∑ g : Goods, ∑ i : Agent, p g * e i g := by
        apply Finset.sum_congr rfl
        intro g _
        rw [Finset.mul_sum]
      _ = ∑ i : Agent, ∑ g : Goods, p g * e i g := by
        simpa using (Finset.sum_comm (s := (Finset.univ : Finset Goods))
          (t := (Finset.univ : Finset Agent)) (f := fun g i => p g * e i g))
  -- 5. contradiction
  have hcontra : (∑ i : Agent, ∑ g : Goods, p g * e i g) <
      (∑ i : Agent, ∑ g : Goods, p g * e i g) := by
    simp [hsum_eq] at hsum_lt
  exact (lt_irrefl _) hcontra

end Theorems

end LeanEcon.Core
