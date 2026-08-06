/-
LeanEcon.Core.Utility — numerical representation of preferences.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md.
-/
import LeanEcon.Core.Primitives
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core

namespace Utility

open Primitives

/-- A utility function: real-valued ranking over X. Glossary: `utility`
    (seeded by c3, fwt1). Representation properties (e.g. "u represents
    ≽") are a later slice; this is the named formal home for the
    utility_function vocabulary. -/
abbrev utility (X : Type) := X → ℝ

/-- Strictly increasing utility over bundles, componentwise reading (the c3
    review decision): `y ≤ x` componentwise and `y ≠ x` implies `u y < u x`.
    Note the direction-flip convention from the c3 fixture: Lean `y ≤ x`
    states the English "x ≥ y". On `bundle Goods` the order is Mathlib's
    pointwise order (componentwiseComparison, mathlib). Glossary:
    `strictlyIncreasing` (seeded by c3). -/
def strictlyIncreasing {Goods : Type} (u : bundle Goods → ℝ) : Prop :=
  ∀ x y : bundle Goods, y ≤ x → y ≠ x → u y < u x

end Utility

end LeanEcon.Core
