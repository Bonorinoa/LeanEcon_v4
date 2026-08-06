/-
LeanEcon.Core.Primitives — the goods/bundle substrate.

First Core promotion batch (P2, per docs/gate6/IMPLEMENTATION_PLAN.md).
Each declaration carries an ontology record in docs/gate6/P2_REVIEW_BATCH.md.
Policy: specific Mathlib imports only (never `import Mathlib`); no new
axioms; no Mathlib root-namespace name collisions (D3).
-/
import Mathlib.Data.Real.Basic

namespace LeanEcon.Core

namespace Primitives

/-- A consumption bundle over a goods type: one real value per good.
    Glossary: `bundle` (seeded by c1, c3, fwt1). Explicit type parameter
    (the fwt1 abbrev-implicit-capture lesson: never capture a type variable
    implicitly in an abbrev). Single-good claims may use `ℝ` directly. -/
abbrev bundle (Goods : Type) := Goods → ℝ

end Primitives

end LeanEcon.Core
