# fwt1 live-test record — First Welfare Theorem through the A3 pipeline

> Status: Gate 6 design evidence (2026-08-06). A live end-to-end test of
> the Gate 5 A3 pipeline on a non-trivial economic theorem, run AFTER the
> first Gate 6 design draft to test the system before proceeding.
> Expectations were recorded BEFORE the run (beliefs on record) and
> compared against actuals. Primary record (gitignored, machine-readable):
> `artifacts/local/fwt1-expectations.md` + the full trace/bundle under
> `artifacts/local/a3/` (claim fwt1 r1, bundle-fwt1-r1-35615e).

## 1. Claim under test

> "In an exchange economy, every competitive equilibrium allocation is
> Pareto efficient: if prices p and an allocation x form a Walrasian
> equilibrium given endowments e and utility functions u — each consumer
> maximizes their utility subject to their budget constraint and markets
> clear — then no other feasible allocation makes every consumer strictly
> better off."

First real theorem through the system: a summation/contradiction proof,
far beyond the trivial proofs of c1–c4. Also the first claim with a
non-null `solution_concept`.

## 2. Expectations recorded before the run (condensed)

| Step | Expected |
|---|---|
| ingest | PASS |
| interpret | PASS; schema-valid EI; solution_concept NON-null |
| review | PASS (approve) |
| formalize | **FAIL** — non-compiling statement and/or static rejection; id deviations |
| reviewer-authored statement+proof | compiles in 1–5 iterations (summation argument the risk) |
| verify | first run AXIOM_VIOLATION → axiom-approve → PASS |
| bundle + replay | PASS; solution_concept mapped |
| Overall | pipeline succeeds end-to-end ONLY via reviewer-authored input; the formalizer fails as predicted; the test validates the SYSTEM, not the model |

## 3. Actual results (2026-08-06)

| Step | Actual | Verdict |
|---|---|---|
| ingest | PASS — DRAFT, PROJECT | ✅ |
| interpret | PASS — schema-valid; `solution_or_equilibrium_concept: "Pareto efficiency of Walrasian equilibrium"` (non-null); 3 ambiguities; none_noted=false | ✅ |
| review | PASS — REVIEW_REQUIRED → ACCEPTED (rev 2) | ✅ |
| formalize | FAIL (richer than predicted): reached FORMALIZED, but **compile probe FAILED (exit 1)**; **Pareto content INVERTED into hypotheses** (`h_feasible_allocation : … → False` as an assumption); 8 gaps flagged (`definition:<i>` ids missing — report used definition TITLES); solution_concept row present (mapped to the hypothesis name) | ✅ direction correct; structural failure |
| reviewer-authored proof | **2 iterations** to green: (1) `abbrev FwtBundle := Goods → ℝ` made `Goods` an implicit param → inference failure at declaration headers; fixed by inlining `Goods → ℝ`; (2) `Finset.sum_lt_sum` wants all-≤ + one-strict → `Finset.sum_lt_sum_of_nonempty`. Axiom closure: `[propext, Classical.choice, Quot.sound]` | ✅ (2 ≤ 5) |
| verify | EXACTLY as predicted: PROVING → FAILED (AXIOM_VIOLATION: Classical.choice, Quot.sound, propext) → axiom record → re-verify → **all 11 bundle checks green** | ✅ to the letter |
| bundle + replay | PASS — bundle-fwt1-r1-35615e; replay_ok=true (12 events, 0 problems) | ✅ |

## 4. Findings (implications for Gate 6)

1. **The formalizer fails structurally, not cosmetically.** It encoded
   utility maximization and market clearing correctly, then wrote the
   Pareto claim as a HYPOTHESIS instead of the conclusion, and nothing
   compiled. This is a worse failure class than the c1–c4 id deviations —
   a trusted model output would have shipped an inverted theorem.
   Strengthens the reviewer-in-the-loop posture (§7 of the design).
2. **Every designed honest-failure mechanism fired and worked**: compile
   probe (caught the non-compiling statement at formalize), gap
   classification + gap-ack (8 gaps acknowledged as evaluation signals),
   first-run axiom loop (surface → approve → re-verify), reviewer-authored
   input, replay. The system held up exactly as designed.
3. **"Core adds no axioms" holds on a real theorem** — the FWT proof
   (budget sets, market clearing, Pareto contradiction, double-sum
   reordering) verified with the baseline closure.
4. **New vocabulary exercised** (→ glossary entries 21–28, glossary-only /
   core-candidate meanings; declarations deferred to Gate 7): exchange
   economy, price vector, allocation, endowment, market clearing,
   competitive (Walrasian) equilibrium, Pareto efficiency, utility
   maximization — plus the first non-null solution_concept mapping.
5. **Lean lessons for implementation** (→ plan risk register):
   - `abbrev` capturing a type variable (`abbrev FwtBundle := Goods → ℝ`)
     makes the variable an implicit parameter → declaration-header
     inference failure. Use explicit shapes (`Goods → ℝ`) or explicit
     parameters.
   - `Finset.sum_lt_sum` requires all-≤ plus one-strict;
     `Finset.sum_lt_sum_of_nonempty` is the all-strict variant.
   - Strong-form Pareto claims need `[Nonempty Agent]` — the empty-economy
     case is a real semantic edge the interpreter did not surface (the
     reviewer's proof header records it).
   - The EI's proposed assumptions (continuity, monotonicity, convexity,
     positivity) were NOT needed for the strong form under the direct
     maximization definition — a definition-strength tradeoff the
     reviewer records, not a claim defect.

## 5. Evidence paths

- Full expectations + comparison: `artifacts/local/fwt1-expectations.md`
- Accepted EI: `artifacts/local/a3/eis/fwt1/rev-2.json`
- Formalizer candidate (preserved as evaluation evidence):
  `artifacts/local/a3/formal/fwt1/rev-1.json`
- Reviewer-authored proof input: `artifacts/local/fwt1/proof_input.lean`
- VERIFIED bundle: `artifacts/local/a3/bundles/bundle-fwt1-r1-35615e/`
- Trace events: `artifacts/local/a3-events/*.jsonl` (claim fwt1 runs)
- Reviewer records (approval, gap-ack, axiom): `artifacts/local/a3/reviews/fwt1/`

All under `artifacts/local/` — gitignored, preserved as trace evidence,
nothing committed.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
