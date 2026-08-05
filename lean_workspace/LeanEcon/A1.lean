/-
A1 workspace probe.

This module exists only to prove that the pinned Lean/Mathlib workspace
builds and that the kernel checks declarations against it (Gate 4, A1
criteria 1 and 2). It carries no economics content: LeanEcon Core
declarations are Gate 6 work and require separate design review.
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-- A1 compiler probe: a kernel-checked declaration in the pinned workspace. -/
theorem leanecon_a1_probe (x : ℝ) : x + 0 = x := by
  simp

/-- A1 typed-failure fixture target: intentionally valid Lean used to
confirm the probe compiles; the invalid-input counterpart lives in the
Python probe tests, not here. -/
def leaneconA1Marker : Nat :=
  4
