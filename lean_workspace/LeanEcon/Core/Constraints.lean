/-
LeanEcon.Core.Constraints — feasibility vocabulary.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md.
-/
import LeanEcon.Core.Primitives
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core

namespace Constraints

open Primitives

/-- Budget set: bundles affordable at prices p with income m, i.e.
    {x | Σᵢ pᵢ·xᵢ ≤ m}. Glossary: `budgetSet` (seeded by c1, fwt1).
    The endowment-relative form used by fwt1 is recoverable as
    `budgetSet p (∑ g, p g * e i g)`; a dedicated endowment-relative
    definition is deferred to the equilibrium slice (Gate 7). -/
def budgetSet {Goods : Type} [Fintype Goods] (p : Goods → ℝ) (m : ℝ) :
    Set (bundle Goods) :=
  {x | (∑ g : Goods, p g * x g) ≤ m}

end Constraints

end LeanEcon.Core
