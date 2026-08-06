/-
LeanEcon.Core.Preferences — the ranking-relation vocabulary.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md.
-/

namespace LeanEcon.Core

namespace Preferences

/-- Weak preference: binary ranking relation "A is at least as preferred as
    B" (preferred or indifferent). Glossary: `weakPreference` (seeded by c2).
    The rationality axioms on top (transitivity, completeness, reflexivity)
    are Mathlib (`IsTrans`, `IsTotal`, `IsRefl`) — referenced, never
    duplicated. -/
abbrev weakPreference (α : Type) := α → α → Prop

end Preferences

end LeanEcon.Core
