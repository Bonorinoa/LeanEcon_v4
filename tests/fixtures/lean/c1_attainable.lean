/-
A3 canonical claim C1 fixture (docs/gate5/a3-design.md Appendix A).

English claim:
  "If a consumer's feasible budget set expands while preferences remain
   unchanged, the consumer's attainable set does not shrink."

Formal statement (target theorem): leanecon_c1_attainable_monotone

Reviewer notes:
  - "Attainable set" is ambiguous (feasible / chosen / utility-attaining);
    the accepted interpretation selects the budget-set reading, and the
    mapping report records that choice. The conclusion formalizes the
    set-inclusion core; "preferences unchanged" is recorded as expository
    context, not asserted here (visible gap, reviewer-acknowledged).
  - Definitions below are A3-local scaffolding, NOT LeanEcon Core. Core
    promotion requires the Gate 6 process.

Fixture provenance: authored by Hermes Agent (Nous Research) under CTO
direction; CTO semantic review is part of the Gate 5 walkthrough.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- A3-local scaffolding definitions (not LeanEcon Core; Gate 6 review required).
abbrev Bundle := ℝ
abbrev BudgetSet := Set Bundle

/-- Attainable set: the bundles affordable under a budget set (reviewer-selected meaning). -/
def Attainable (B : BudgetSet) : Set Bundle := B

theorem leanecon_c1_attainable_monotone {Bold Bnew : BudgetSet} (hexpand : Bold ⊆ Bnew) :
    Attainable Bold ⊆ Attainable Bnew := by
  exact hexpand
