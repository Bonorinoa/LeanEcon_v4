# Gate 7 slice proposal — equilibrium-family Core declarations (2026-08-06)

> Status: **PROPOSED — CTO verdict PENDING.** The slice was presented at the
> Gate 7 kickoff session (2026-08-06) with a read-back of locked decisions;
> the `clarify` approval dialog returned EMPTY, which is NOT consent (skill
> §4) — no Lean drafted, no files written, worktree untouched (main @
> 6778e98, 156 tests green). Resume only after the CTO actively
> approves/adjusts. Authority anchors: `docs/gate6/P5_EXIT_PACKAGE.md` §5
> (open item 1), `docs/gate6/a3-core-design.md` §2 (entries 21–28) + §7,
> `docs/gate6/references/core-glossary-detail.md` entries 21–28,
> DECISION_LOG items 15–25.

## 1. Scope (proposed)

Home module `LeanEcon.Core.Equilibrium` (new — created only because this
batch fills it; migration-plan rule: no empty modules), one declaration in
`Constraints.lean`, one theorem boundary in `Theorems.lean`. Draft
signatures (verified against the P2 modules as they exist; fwt1-proof-
portable):

```lean
-- Constraints.lean (new)
def budgetSetEndowment {Goods : Type} [Fintype Goods] (p : Goods → ℝ) (e : Goods → ℝ) :
    Set (bundle Goods) :=
  budgetSet p (∑ g : Goods, p g * e g)

-- Equilibrium.lean (new module)
def marketClearing {Agent Goods : Type} [Fintype Agent] (e x : Agent → bundle Goods) : Prop :=
  ∀ g : Goods, (∑ i : Agent, x i g) = (∑ i : Agent, e i g)

structure competitiveEquilibrium {Agent Goods : Type} [Fintype Agent] [Fintype Goods]
    (e : Agent → bundle Goods) (u : Agent → bundle Goods → ℝ)
    (x : Agent → bundle Goods) (p : Goods → ℝ) : Prop where
  feasible : marketClearing e x
  maximizes : ∀ i : Agent, x i ∈ budgetSetEndowment p (e i) ∧
    ∀ y : bundle Goods, y ∈ budgetSetEndowment p (e i) → u i y ≤ u i (x i)

def paretoEfficiency {Agent Goods : Type} [Fintype Agent] (e : Agent → bundle Goods)
    (u : Agent → bundle Goods → ℝ) (x : Agent → bundle Goods) : Prop :=
  ¬ ∃ y : Agent → bundle Goods, marketClearing e y ∧ ∀ i : Agent, u i (x i) < u i (y i)

-- Theorems.lean (theorem boundary; direct port of the fwt1 reviewer proof)
theorem competitiveEquilibrium_paretoEfficient {Agent Goods : Type} [Fintype Agent]
    [Fintype Goods] [Nonempty Agent] {e : Agent → bundle Goods}
    {u : Agent → bundle Goods → ℝ} {x : Agent → bundle Goods} {p : Goods → ℝ}
    (h : competitiveEquilibrium e u x p) : paretoEfficiency e u x := by ...
```

Key semantic decisions embedded in the proposal:
- **Direct utility-maximization reading** for `competitiveEquilibrium`
  (glossary entry 26): strong Pareto then needs NO local nonsatiation — the
  fwt1 finding. `maximizes` states `x i ∈ B_i ∧ ∀ y ∈ B_i, u i y ≤ u i (x i)`.
- **`[Nonempty Agent]` lives on the THEOREM, not the definition.** With zero
  agents `paretoEfficiency` = `¬ ∃ y, True ∧ True` = False, so "CE ⇒ Pareto"
  is false without it (the semantic gap the interpreter never surfaced; the
  fwt1 proof header recorded it). The definition stays total and meaningful.
- **Minimal `[Fintype]` per declaration**: `marketClearing`/`paretoEfficiency`
  need `[Fintype Agent]` only (sum over agents; `∀ g` quantifies goods);
  `budgetSetEndowment` needs `[Fintype Goods]`; `competitiveEquilibrium`
  needs both (it uses both).
- **`budgetSetEndowment` = P2 D2's "recoverable" form given a named home**
  (`budgetSet p (∑ g, p g * e g)`); it IS on the P5 carried-forward list
  ("+ endowment-relative budgetSet form") and gives glossary entry 26's
  `budget p (e i)` sketch a two-arg shape.
- **`utilityMaximization` (entry 28) stays folded** into `maximizes` (the
  glossary's own formal view says "no standalone declaration") — decision D5.
- **Entries 21–24 stay glossary-only** (exchangeEconomy, priceVector,
  allocation, endowment — each entry: "realized as types; no declaration
  proposed"). They appear as types/function roles in signatures, as in fwt1.

## 2. Decisions table (D1–D9, proposals + alternatives)

| # | Decision | Proposal | Alternatives |
|---|---|---|---|
| D1 | marketClearing signature | `{Agent Goods} [Fintype Agent] (e x : Agent → bundle Goods)` — minimal constraint set | +`[Fintype Goods]` (uniformity only); raw `Agent → Goods → ℝ` (no Core `bundle`) |
| D2 | competitiveEquilibrium shape | `structure … : Prop where feasible; maximizes`, direct maximization reading | weak-form + nonsatiation (meaning change — rejected); plain def with bundled conjunction |
| D3 | endowment-relative budget set | dedicated `budgetSetEndowment` in Constraints | inline recovery `budgetSet p (∑ g, p g * e g)` — zero new declarations |
| D4 | `[Nonempty Agent]` placement | on the theorem (definition stays total) — matches fwt1 | on the definition (changes the reviewed meaning) |
| D5 | utilityMaximization (entry 28) | stays glossary-only, folded into `maximizes` | standalone predicate `utilityMaximization u B x := x ∈ B ∧ ∀ y ∈ B, u y ≤ u x` (criterion 7 borderline) |
| D6 | FWT theorem boundary | in-batch; name `competitiveEquilibrium_paretoEfficient` (P2 T1/T2 pattern; 2-iteration proof budget; baseline closure) | declarations-only batch (defer boundary); name `firstWelfareTheorem` |
| D7/D8 | module layout / budgetSetEndowment home | new `Equilibrium.lean` + one decl in `Constraints` + one theorem in `Theorems` | all new content in `Equilibrium.lean` (loses the constraint-vocabulary home) |
| D9 | no tooling deltas (D3 CI grep, verify-side scaffolding signal, `none`-kind removal) | confirm | opt in (task allows "unless the CTO opts in") |

## 3. Read-back of locked decisions (presented first — not reopened)

- Gate 6 CLOSED; Gate 7 = the equilibrium-family declarations slice
  (DECISION_LOG 25; P5 packet §5.1).
- Entries 21–28 **meanings LOCKED** (DECISION_LOG 17; registry v1.0.0) — no
  meaning changes (that would be a major registry bump + re-review); only
  status moves (core-candidate → core), recorded as registry change-log rows,
  not a version bump.
- P2 D2 deferred the endowment-relative budgetSet form to this slice
  (recoverable); it is now on the table as a declaration.
- fwt1 vocabulary seeded from reviewed artifacts only (design §2 rule 1):
  accepted EI `artifacts/local/a3/eis/fwt1/rev-2.json`, mapping report
  `artifacts/local/a3/formal/fwt1/rev-1.json`, gap-ack + axiom records
  under `artifacts/local/a3/reviews/fwt1/`, VERIFIED bundle
  `bundle-fwt1-r1-35615e`, reviewer proof `artifacts/local/fwt1/proof_input.lean`.
- fwt1 itself stays an A3 test record (design §2 rule 5) — the Core theorem
  boundary is a NEW proposal, not a re-import.
- Promotion = 7 criteria + per-declaration CTO gate + D3 collision check;
  no model-only promotion; no v3 material (ledger K1–K6).
- Axiom baseline `[propext, Classical.choice, Quot.sound]`; beyond needs
  per-run review. Explicit type params, specific Mathlib imports only, no
  Mathlib root collisions, no empty modules, no commits without approval,
  attribution footer on every doc.

## 4. Deliberately NOT in scope

B2 proof loop; corpus; retrieval; release; production `VERIFIED` claims
importing Core; P4-deferred tooling (D3 CI grep, verify-side scaffolding
soft signal, `mapping_kind: none` removal); demand/choice correspondences;
representation theorems; entries 21–24 declarations; v3 material; A3 code
changes; registry meaning changes.

## 5. Resume instructions (on CTO verdict)

1. On approval → draft `lean_workspace/.a3-candidates/gate7-check/Check.lean`
   (gitignored; NOTE the gitignored path is `lean_workspace/.a3-candidates/`
   — a root `.a3-candidates/` does not exist) with `#check` on every
   declaration + `#print axioms` on the theorem boundary. Record
   expectations FIRST (CTO preference, prediction-first): ≤2 proof-port
   iterations, 0 D3 collisions, baseline axiom closure.
2. `lake env lean` the check file; capture VERBATIM kernel output (build
   success + axiom closure) into the review package.
3. Review package `docs/gate7/G7_REVIEW_BATCH.md` (P2_REVIEW_BATCH pattern:
   batch table, per-declaration ontology records with D3 collision rows +
   fwt1 anchors, 7-criteria checklist, D1–D9 verdicts, NOT-in-batch list,
   expectations-vs-actual table). Registry change-log rows: entries 25/26/27
   → core; entry 7's variant note now points at `budgetSetEndowment`.
4. CTO gate → per-declaration approval records + DECISION_LOG items 26+ →
   commit/PR per the established flow (dispatch scaffold+a1 against the
   branch, verify checks green via the check-runs API latest-run-per-name,
   `merge_pr.py <PR> clear-checks`, `verify_protection.py` after).
5. pytest baseline 156 must stay green (no Python changes expected in this
   slice).

**Attribution:** prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This proposal
authorizes nothing.
