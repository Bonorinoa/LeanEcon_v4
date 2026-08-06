/-
A3 canonical claim C2 fixture (docs/gate5/a3-design.md Appendix A).

English claim:
  "Weak preference is transitive: if A is weakly preferred to B and B is
   weakly preferred to C, then A is weakly preferred to C."

Formal statement (target theorem): leanecon_c2_pref_transitive

Reviewer notes:
  - The relation r : α → α → Prop stands for weak preference; transitivity
    is taken as the defining assumption (axiom of the statement), matching
    the standard preference-theory definition in the reviewed glossary.
  - Pure Mathlib: relation + Transitive, no scaffolding needed.

Fixture provenance: authored by Hermes Agent (Nous Research) under CTO
direction; CTO semantic review is part of the Gate 5 walkthrough.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem leanecon_c2_pref_transitive {α : Type} (r : α → α → Prop) (hr : IsTrans α r)
    {a b c : α} (hab : r a b) (hbc : r b c) : r a c := by
  exact hr.trans a b c hab hbc
