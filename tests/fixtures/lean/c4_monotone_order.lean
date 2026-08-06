/-
A3 canonical claim C4 fixture (docs/gate5/a3-design.md Appendix A).

English claim:
  "A monotone nondecreasing function f : R -> R preserves order: a <= b
   implies f a <= f b."

Formal statement (target theorem): leanecon_c4_monotone_order

Reviewer notes:
  - Pure Mathlib anchor: the statement is exactly Mathlib's Monotone
    unfolded for ℝ; used to calibrate the verification machinery with
    zero scaffolding.
  - Axiom baseline expected: propext, Classical.choice, Quot.sound.

Fixture provenance: authored by Hermes Agent (Nous Research) under CTO
direction; CTO semantic review is part of the Gate 5 walkthrough.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem leanecon_c4_monotone_order (f : ℝ → ℝ) (hf : Monotone f) (a b : ℝ) (hab : a ≤ b) : f a ≤ f b := by
  exact hf hab
