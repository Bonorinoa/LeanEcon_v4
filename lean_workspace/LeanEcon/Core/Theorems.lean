/-
LeanEcon.Core.Theorems — reviewed theorem boundaries.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md. Each theorem boundary supports a VERIFIED
canonical claim family; statements are honest about their assumptions.
-/
import LeanEcon.Core.Choice
import LeanEcon.Core.Utility
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core

namespace Theorems

open Choice
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

end Theorems

end LeanEcon.Core
