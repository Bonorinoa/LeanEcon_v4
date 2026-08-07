/-
LeanEcon.Core.Equilibrium — solution concepts for the exchange economy.

Gate 7 equilibrium-family slice (per-declaration promotion). Ontology
records in docs/gate7/G7_REVIEW_BATCH.md. Seeded by the fwt1 test (VERIFIED
2026-08-06): accepted EI rev-2, mapping report rev-1, reviewer proof input,
bundle-fwt1-r1-35615e. The module exists because these declarations were
approved — no empty modules (migration-plan rule).
-/
import LeanEcon.Core.Primitives
import LeanEcon.Core.Constraints
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core

namespace Equilibrium

open Constraints
open Primitives

/-- Market clearing: for every good, the total allocation equals the total
    endowment. Glossary: `marketClearing` (entry 25; fwt1 `FwtFeasible`,
    which served double duty as feasibility). Componentwise sum equality:
    the sum is over agents, the equality is per good. -/
def marketClearing {Agent Goods : Type} [Fintype Agent] (e x : Agent → bundle Goods) :
    Prop :=
  ∀ g : Goods, (∑ i : Agent, x i g) = (∑ i : Agent, e i g)

/-- Competitive (Walrasian) equilibrium: an allocation x and prices p such
    that every consumer maximizes utility in their endowment-relative budget
    set and markets clear. Glossary: `competitiveEquilibrium` (entry 26;
    alias Walrasian-equilibrium). Direct utility-maximization reading — the
    strong Pareto form then needs no local nonsatiation (recorded in the
    fwt1 proof header). -/
structure competitiveEquilibrium {Agent Goods : Type} [Fintype Agent] [Fintype Goods]
    (e : Agent → bundle Goods) (u : Agent → bundle Goods → ℝ)
    (x : Agent → bundle Goods) (p : Goods → ℝ) : Prop where
  feasible : marketClearing e x
  maximizes : ∀ i : Agent, x i ∈ budgetSetEndowment p (e i) ∧
    ∀ y : bundle Goods, y ∈ budgetSetEndowment p (e i) → u i y ≤ u i (x i)

/-- Pareto efficiency (strong form): no feasible allocation makes every
    consumer strictly better off. Glossary: `paretoEfficiency` (entry 27;
    the fwt1 EI ambiguity "weak vs strong Pareto" resolved at review to the
    strong reading). The empty-economy degeneracy is handled at the theorem
    boundary (`[Nonempty Agent]`), not in this definition — matching the
    fwt1 proof header. -/
def paretoEfficiency {Agent Goods : Type} [Fintype Agent] (e : Agent → bundle Goods)
    (u : Agent → bundle Goods → ℝ) (x : Agent → bundle Goods) : Prop :=
  ¬ ∃ y : Agent → bundle Goods, marketClearing e y ∧ ∀ i : Agent, u i (x i) < u i (y i)

end Equilibrium

end LeanEcon.Core
