# Core toy walkthrough — sandboxed demo for the Gate 6 design review

> Purpose: make the LeanEcon Core design concrete for a reader who does not
> read Lean. Everything here was **actually compiled** in the pinned v4
> workspace (`leanprover/lean4:v4.32.2`, Mathlib `v4.32.2`) on 2026-08-06;
> the outputs below are verbatim. The toy module is a sandbox sketch, NOT
> the approved Core, and was removed after the demo (see §8).
>
> Companion: `../a3-core-design.md` (the design this demo illustrates).

## 0. The three layers, in one picture

```
                    ┌────────────────────────────────────────────────┐
                    │  Mathlib  (the trusted general library)        │
                    │  sets, orders, ℝ, sums — reviewed by the       │
                    │  Mathlib community, pinned by the workspace    │
                    └────────────────────────────────────────────────┘
                                    ▲ referenced (`mathlib` rows)
                    ┌────────────────────────────────────────────────┐
                    │  LeanEcon Core  (the economics vocabulary)     │
                    │  weakPreference, budgetSet, attainableSet      │
                    │  — each declaration reviewed by the CTO once,  │
                    │  then reused everywhere (`core` rows)          │
                    └────────────────────────────────────────────────┘
                                    ▲ imported by
                    ┌────────────────────────────────────────────────┐
                    │  A3 candidate files (per claim, per run)       │
                    │  theorem statement + proof + mapping report    │
                    │  — what the kernel actually checks             │
                    └────────────────────────────────────────────────┘
```

- **Mathlib** is the load-bearing general library: it supplies `Set`,
  `Monotone`, `IsTrans`, the real numbers, and sums. LeanEcon Core never
  re-defines what Mathlib already provides.
- **LeanEcon Core** is the *economics* vocabulary — the concepts a claim
  means, not how they are encoded in general math. Its entire value is
  that every declaration was reviewed once, semantically, by the CTO, and
  then every later claim reuses the reviewed meaning instead of inventing
  a fresh definition per candidate file.
- **A3 candidate files** are the per-run artifacts: the formal statement,
  the proof, and the mapping report. They are generated per claim, never
  promoted; Core is the only vocabulary they borrow that persists.

---

## 1. The toy

Claim c1 (CTO-approved, VERIFIED at Gate 5):

> "If a consumer's feasible budget set expands while preferences remain
> unchanged, the consumer's attainable set does not shrink."

The toy Core module (`LeanEcon.Core.Sandbox`) contains three declarations
and one theorem boundary, mirroring the vocabulary c1 uses. Full source:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace LeanEcon.Core.Sandbox

/-- Weak preference: "A is at least as preferred as B". Toy of `weak-preference` (c2). -/
abbrev WeakPreference (α : Type) := α → α → Prop

/-- Budget set: affordable bundles {x | Σᵢ pᵢ·xᵢ ≤ m}. Toy of `budget-set` (c1). -/
def budgetSet {Goods : Type} [Fintype Goods] (p : Goods → ℝ) (m : ℝ) :
    Set (Goods → ℝ) :=
  {x | ∑ i, p i * x i ≤ m}

/-- Attainable set: reviewer-selected c1 reading (budget-set reading). -/
def attainableSet {Goods : Type} (B : Set (Goods → ℝ)) : Set (Goods → ℝ) :=
  B

/-- Theorem boundary, c1 family: expansion does not shrink the attainable set. -/
theorem attainableSet_monotone {Goods : Type} {Bold Bnew : Set (Goods → ℝ)}
    (h : Bold ⊆ Bnew) : attainableSet Bold ⊆ attainableSet Bnew := by
  exact h

end LeanEcon.Core.Sandbox
```

What each piece is:

| Piece | Kind | Why this shape |
|---|---|---|
| `WeakPreference` | `abbrev` (alias) | A preference relation IS just a binary predicate — no structure of its own. The name is the review surface: "this is what 'at least as preferred as' means here". |
| `budgetSet` | `def` (definition) | A definition with real content: the set of bundles whose cost `Σ pᵢ·xᵢ` fits income `m`. It depends on Mathlib (`Set`, `ℝ`, `Fintype` sums) and records the *economic meaning* in its doc comment. |
| `attainableSet` | `def` | Deliberately thin: the c1 review selected the budget-set reading of the ambiguous "attainable set". The definition encodes that decision. If the review had chosen the "utility-attaining" reading, this would filter by preference instead. |
| `attainableSet_monotone` | `theorem` | A *theorem boundary*: a reviewed result other claims can import instead of re-proving. It is honest about its assumption (`Bold ⊆ Bnew` is stated, not hidden). |

The `[Fintype Goods]` on `budgetSet` says "finitely many goods" — it is
the mechanism that lets `Σᵢ` (a finite sum) make sense. This is exactly
the Open Question 1 (bundle family) made concrete.

---

## 2. The same claim at three maturity stages

The point of Core is visible by comparing the *mapping report* — the
reviewer-facing table that says where every EI element went — across
stages. The claim is the same; the vocabulary's home changes.

### Stage A — today (Gate 5): everything is A3-local scaffolding

Statement (abridged, matches the real c1 fixture):

```lean
abbrev Bundle := ℝ
abbrev BudgetSet := Set Bundle
def Attainable (B : BudgetSet) : Set Bundle := B

theorem stageA_attainable_monotone {Bold Bnew : BudgetSet} (hexpand : Bold ⊆ Bnew) :
    Attainable Bold ⊆ Attainable Bnew := by exact hexpand
```

Mapping report (real shape observed in `formal/c1/rev-1.json`):

| ei_element_id | kind | lean_identifier | mapping_kind |
|---|---|---|---|
| consumer | agent | `consumer` | `local_definition` |
| feasible_budget_set | set | `budget_set` | `local_definition` |
| attainable_set | set | `attainable_set` | `local_definition` |
| preferences | relation | `preferences` | `local_definition` |
| assumption:0 | assumption | `h_budget_expands` | `local_definition` |
| conclusion | conclusion | `budget_set ⊆ attainable_set` | `local_definition` |
| solution_concept | solution | (null) | `none` (unmapped) |
| definition:0 | definition | `feasible_budget_set` | `glossary_term` |

**What this means:** the economics vocabulary was invented inside this one
candidate file. It works (the kernel accepted it), but every future claim
re-invents "budget set" from scratch, and the reviewer must re-check the
meaning each time. This is the status quo that made the four claims
VERIFIED — and the status quo Core exists to replace.

### Stage B — interim: glossary rows, no declarations yet

Same statement as Stage A, but the mapping report cites the *reviewed
glossary* instead of fresh names:

| ei_element_id | kind | lean_identifier | mapping_kind |
|---|---|---|---|
| attainable_set | set | `attainable-set` (glossary) | `glossary_term` |
| feasible_budget_set | set | `budget-set` (glossary) | `glossary_term` |

The statement still carries scaffolding (no Lean declaration exists yet),
but the report now says "this means the reviewed glossary term
`attainable-set`, pending promotion". A `glossary_term` row always names
its promotion plan in the note — the honest middle state.

### Stage C — target: Core rows

Statement (compiled for real, see §3):

```lean
import LeanEcon.Core.Sandbox
open LeanEcon.Core.Sandbox

theorem stageC_attainable_monotone {Goods : Type} {Bold Bnew : Set (Goods → ℝ)}
    (h : Bold ⊆ Bnew) : attainableSet Bold ⊆ attainableSet Bnew :=
  attainableSet_monotone h
```

Mapping report:

| ei_element_id | kind | lean_identifier | mapping_kind |
|---|---|---|---|
| consumer | agent | (role; type variable) | `glossary_term` (role) |
| feasible_budget_set | set | `LeanEcon.Core.Sandbox.budgetSet` | `core` |
| attainable_set | set | `LeanEcon.Core.Sandbox.attainableSet` | `core` |
| preferences | relation | `LeanEcon.Core.Sandbox.WeakPreference` | `core` |
| assumption:0 | assumption | `h : Bold ⊆ Bnew` | `mathlib` |
| conclusion | conclusion | `attainableSet Bold ⊆ attainableSet Bnew` | `core` (theorem boundary) |
| solution_concept | solution | (null) | unmapped (acknowledged) |
| definition:0 | definition | `budgetSet` | `core` |

**What changed:** the economics rows point AT one reviewed place instead
of at per-candidate inventions. "Budget set" now means *the same thing* in
every claim that uses it. The `mathlib` row shows structure that Core
correctly leaves to Mathlib (`⊆`). The unmapped `solution_concept` is the
visible, reviewer-acknowledged gap it was before (c1 has no solution
concept — the null is honest).

---

## 3. Real compile output (pinned workspace, 2026-08-06)

Toy Core module build:

```
$ lake build LeanEcon.Core.Sandbox
✔ [2997/2997] Built LeanEcon.Core.Sandbox (13s)
Build completed successfully (2997 jobs).
```

Stage A (local scaffolding) — compiles, baseline axioms only:

```
$ lake env lean .a3-candidates/sandbox-local/run-1/Candidate.lean
'stageA_attainable_monotone' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Stage C (Core import) — compiles, **same** baseline axioms:

```
$ lake env lean .a3-candidates/sandbox-core/run-1/Candidate.lean
'stageC_attainable_monotone' depends on axioms: [propext, Classical.choice, Quot.sound]
'stageC_budget_grows_with_income' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The second line is the important one: `stageC_budget_grows_with_income`
proves "budget sets grow with income" using the toy Core `budgetSet` —
and the kernel reports it needs **nothing beyond the Mathlib baseline**.
Core declarations add no new axioms (design §1.4 holds in practice).

Stage C-bad (invented Core id — what the formalizer does today):

```
$ lake env lean .a3-candidates/sandbox-core/run-bad/Candidate.lean
Candidate.lean:15:4: error: Function expected at
  budgetSetX
Hint: The identifier `budgetSetX` is unknown … This is often the result of a
typo or a missing `import` or `open` statement.
```

Exit code 1 ⇒ the verifier records `LEAN_SYNTAX_ERROR`, the claim stays
`FORMALIZED`, the failure lands in the bundle and the trace. **The kernel
arbitrates invented names** — no model output, no reviewer wish, and no
unreviewed declaration can make `budgetSetX` mean something.

---

## 4. How the assets flow through the state machine (Stage C)

| # | State change | Actor | What happens to Core |
|---|---|---|---|
| 1 | – → `DRAFT` | system (ingest) | Claim text + classification. Core is not involved. |
| 2 | `DRAFT` → `INTERPRETED` | system (interpret, mistral-medium-3-5) | EI candidate produced. `context.ontology_refs` may name Core/glossary terms — but this is a *proposal*, not yet binding. |
| 3 | `INTERPRETED` → `REVIEW_REQUIRED` | system (validate) | Schema-valid candidate. |
| 4 | `REVIEW_REQUIRED` → `ACCEPTED` | **reviewer (CTO)** | The human approves the EI. Only now do its `ontology_refs` carry weight. (`none_noted` needs acknowledgement.) |
| 5 | `ACCEPTED` → `FORMALIZED` | system (formalize, labs-leanstral-1-5) | Formalizer receives **accepted EI + glossary/Core context** — never gold. Emits statement + mapping report. Economics rows must now be `core` / `glossary_term` / `local_definition`; invented ids fail at the next step. |
| 6 | `FORMALIZED` → `PROVING` | system | Blocked while any material row is unmapped (unless reviewer gap-acks). Proof input supplied by reviewer. |
| 7 | `PROVING` → `VERIFIED` | system (verifier + bundle validator) | `lake env lean` compiles against the pinned workspace **with Core imports**; `#print axioms` audit; all 11 bundle checks. `VERIFIED` = kernel-verified + complete bundle. |
| 8 | bundle + replay | system | The bundle records statement, mapping report, axiom audit — the Core identifiers appear in the trace as the vocabulary used. |

Two subtleties worth naming:

- **Core is consulted twice, differently.** At step 4 the reviewer approves
  *meaning* (via the EI, which cites Core/glossary terms). At step 7 the
  kernel checks *syntax and derivability* (via the imports). Neither
  replaces the other: the mapping report is the bridge a reviewer reads
  between them (a3-design §8: "the reviewer owns meaning; the kernel owns
  correctness").
- **Core is never written by the pipeline.** The two agents (interpret,
  formalize) only *read* Core/glossary context and *report* identifiers.
  Declarations enter Core only through the promotion process (§7 of the
  design): authored, documented, CTO-approved — one at a time.

---

## 5. What the agents actually see (and why it stays honest)

- **Interpretation agent** sees: claim text + classification. Output: EI.
  It may *suggest* `ontology_refs` (e.g. `budget-set`) but the reviewer
  owns whether those refs are right.
- **Formalization agent** sees: the **accepted** EI + formalization
  context (glossary refs, workspace identity). Output: statement + mapping
  report. It never sees hidden gold, never sees v3 material, and its
  mapping rows are judged against the canonical element-id scheme (§3 of
  the design) — the walkthrough's `object:u`-style deviations are
  classified as `id_scheme_deviation`, recorded, and reviewed.
- **Reviewer (CTO)** sees: the EI (no Lean), the mapping report rows (no
  Lean), the statement + proof (Lean, but alongside the rows), the axiom
  audit. The design goal: every economic decision is reviewable *without*
  reading Lean, and every Lean decision is anchored by a row.

---

## 6. Failure modes the toy demonstrated

| Failure | What happens | Why it is not silent |
|---|---|---|
| Formalizer invents a Core id (`budgetSetX`) | `lake env lean` exits 1; verifier records `LEAN_SYNTAX_ERROR`; claim stays `FORMALIZED`; failure in bundle + trace | The kernel arbitrates; the trace is append-only; a failed bundle is a faithful record |
| Formalizer uses `object:u` instead of `u` | Mapping row classified `id_scheme_deviation`; material element still covered; reviewer sees the deviation | The strict completeness check + reviewer records make it visible |
| A Core declaration would need a new axiom | `#print axioms` surfaces it; `AXIOM_VIOLATION` until a reviewer approves the per-run axiom list | Axiom authority stays per-run reviewer records (Gate 3 decision 8) |
| Reviewer disagrees with a mapping | `REJECTED` or gap-ack with notes; new revision or acknowledged gap | Revision terminal; nothing downstream is reused without re-approval |

---

## 7. Why this shape (the design rationale, in one breath)

1. **One reviewed place, not per-claim invention** — the economics
   vocabulary is reviewed once per declaration and reused; the mapping
   report proves *which* reviewed place each claim used.
2. **The reviewer never has to read Lean to approve meaning** — the EI
   and the mapping rows carry it; Lean is the contract that pins it.
3. **The kernel stays the honest arbiter** — compile, axiom audit, and
   the `#print axioms` closure run on the *same* pinned workspace, so
   "it compiles" is real, and "it uses only approved axioms" is
   demonstrated, not asserted.
4. **Gaps are visible, not papered over** — `unmapped` blocks `PROVING`
   until the reviewer acknowledges; invented names fail loudly at the
   kernel. Nothing is silently defined.
5. **Core stays small and defensible** — declarations enter only via the
   promotion criteria (plain meaning, signature, variants, axiom audit,
   examples, CTO approval). The toy shows how small that can be: three
   declarations + one theorem boundary already carry the c1 family.

---

## 8. Sandbox hygiene (what was real vs what remains)

- The toy module `lean_workspace/LeanEcon/Core/Sandbox.lean` and the
  three candidates under `lean_workspace/.a3-candidates/sandbox-*` were
  **compiled and demonstrated** (all outputs in this doc are verbatim),
  then **removed after CTO approval of the cleanup**; their `.lake`
  build artifacts were pruned. The workspace is back to its tracked state
  (only `A1.lean` in the lib) and `lake build LeanEcon.A1` re-verifies
  clean.
- Nothing from this demo is a Core declaration; nothing was committed;
  nothing was promoted. The design (`../a3-core-design.md`) remains the
  only thing awaiting CTO approval.
- Re-run instructions (if the CTO wants to redo the demo): recreate the
  four files, `lake build LeanEcon.Core.Sandbox`, then `lake env lean`
  each candidate from `lean_workspace/`.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
