/-
A3 canonical claim C3 fixture (docs/gate5/a3-design.md Appendix A).

English claim:
  "If a utility function is strictly increasing, then x >= y componentwise
   and x != y implies u(x) > u(y)."

Formal statement (target theorem): leanecon_c3_strict_mono

Reviewer notes:
  - In ℝ the componentwise order IS the usual order, so the claim reduces
    to strict monotonicity; the mapping report records the direction-flip
    convention (Lean's y ≤ x states the English "x ≥ y").
  - Pure Mathlib: StrictMono + lt_of_le_of_ne, no scaffolding needed.

Fixture provenance: authored by Hermes Agent (Nous Research) under CTO
direction; CTO semantic review is part of the Gate 5 walkthrough.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem leanecon_c3_strict_mono (u : ℝ → ℝ) (hu : StrictMono u) {x y : ℝ}
    (hxy : y ≤ x) (hne : y ≠ x) : u y < u x := by
  exact hu (lt_of_le_of_ne hxy hne)
