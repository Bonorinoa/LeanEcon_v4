import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- c4 statement: the formalizer's own statement, reviewed and kept as-is
-- (correct monotonicity statement with a valid inline proof).
theorem monotone_nondecreasing_preserves_order (f : ℝ → ℝ)
    (hf : ∀ x y, x ≤ y → f x ≤ f y) (a b : ℝ) (hle : a ≤ b) : f a ≤ f b :=
  hf a b hle

