/-
LeanEcon.Core.Choice — what is selected from the feasible set.

First Core promotion batch (P2). Ontology records in
docs/gate6/P2_REVIEW_BATCH.md.
-/
import LeanEcon.Core.Primitives

namespace LeanEcon.Core

namespace Choice

open Primitives

/-- Attainable set: the reviewer-selected c1 reading — the budget-set
    reading (the bundles in B). The c1 ambiguity "feasible / chosen /
    utility-attaining" was resolved at review to this reading; the
    definition records that decision (the glossary entry carries the
    meaning, the declaration carries the encoding). Glossary:
    `attainableSet` (seeded by c1). -/
def attainableSet {Goods : Type} (B : Set (bundle Goods)) : Set (bundle Goods) :=
  B

end Choice

end LeanEcon.Core
