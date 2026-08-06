import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- c2 corrected statement (reviewer revision of formalizer output)
-- English: weak preference is transitive.
-- Substantive content: the property claim, expressed with Mathlib's IsTrans
-- (dropped the invalid `[Set α]` binder and the unused refl/completeness
-- scaffolding from the formalizer's candidate).
theorem weak_preference_transitive {α : Type} (weak_pref : α → α → Prop)
    (h_trans : IsTrans α weak_pref) :
    ∀ a b c, weak_pref a b → weak_pref b c → weak_pref a c :=
  fun a b c hab hbc => h_trans.trans a b c hab hbc

