import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import Mathlib.Order.Bounds.Basic

-- c1 corrected statement (reviewer revision of formalizer output)
-- English: budget expansion + unchanged preferences => attainable set does not shrink
-- Reviewer-selected meaning of "attainable set" = the feasible set itself
-- (c1 EI ambiguity resolution, approved). "Preferences unchanged" is
-- expository context, not asserted (visible, reviewer-acknowledged).
theorem attainable_set_monotone_under_budget_expansion {α : Type}
    (Bold Bnew Aold Anew : Set α)
    (h_expand : Bold ⊆ Bnew)
    (h_old : Aold = Bold) (h_new : Anew = Bnew) :
    Aold ⊆ Anew := by
  rw [h_old, h_new]
  exact h_expand

