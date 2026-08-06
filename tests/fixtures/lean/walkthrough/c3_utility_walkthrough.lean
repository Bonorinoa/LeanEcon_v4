import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- c3 corrected statement (reviewer revision of formalizer output)
-- English: strictly increasing utility => componentwise x >= y, x != y => u(x) > u(y).
-- Domain ambiguity (flagged in the approved EI) resolved to R: in R the
-- componentwise order IS the usual order, so the claim reduces to strict
-- monotonicity (direction-flip convention: Lean's y <= x states English x >= y).
-- The formalizer's candidate lacked the strict-monotonicity hypothesis and
-- used an incomplete-proof placeholder; both fixed here.
theorem strictly_increasing_utility_implies_strict_preference (u : ℝ → ℝ)
    (h_mono : StrictMono u) {x y : ℝ}
    (h_ge : y ≤ x) (h_ne : y ≠ x) : u y < u x := by
  exact h_mono (lt_of_le_of_ne h_ge h_ne)

