# v3 metrics — what we measure, what we don’t

**Status:** Phase 0 approved. Phase 1 implemented (live 1/3 first-try).
Phase 2 scorer exists on this branch (`leanecon.eval_formalizer`).
Held-out scored 2026-08-13: draft_complete **2/4 (50%)** — verdict
**MISSED**. Hand-edited numbers after this file’s scorer exists are a bug.
**Question this answers:** are the current evals objective measures of
system quality?

Short answer: **the harness soundness checks are objective. The model-
quality and semantic-fidelity “scorecards” are not.** v3 should stop
hand-writing tables and start scoring committed artifacts. Phase 1 may
fill a **manual** table against the definitions below; a committed
scorer is Phase 2. Hand-edited numbers after Phase 2 exist are a bug.

---

## 1. Two different things we keep conflating

| Layer | Question | Can a machine decide it? |
|---|---|---|
| **Harness soundness** | Did this formal object survive the kernel + bundle contract? | **Yes.** Lean + 12-check validator. |
| **Process integrity** | Did the lifecycle/replay match what the runner emitted? | **Yes.** `replay_ok`. |
| **Draft hygiene** | Did the model emit sorry / a proof body / a bare Core id? | **Mostly yes.** Static scanners. |
| **Model quality** | How often does the model produce a *usable* statement? | **Yes, if we define “usable” and run a scorer.** We have not. |
| **Semantic fidelity** | Does the Lean statement *mean* the English claim? | **No, not fully.** Reviewer-owned. Heuristics only. |
| **Operator skill** | How fast can *this team* reach VERIFIED? | Measurable, but it is not system quality. |

`VERIFIED` on a claim whose proof was reviewer-authored is evidence
about the **harness**, not about the **formalizer**. Counting 11
VERIFIED claims as model progress is a category error. The scorecards
already say this (“0% sole-author”); the milestone table still reads
like a win-count.

---

## 2. What we have today (inventory)

### 2.1 Objective, mechanical, trustworthy

These are real quality measures of the *verifier and contracts*:

| Instrument | What it decides | Limit |
|---|---|---|
| `#print axioms` / `sorryAx` absent | This proof of *this* statement is not sorry-contaminated | Says nothing about whether the statement is the claim |
| Bundle 12-check + `12_core_pin` | Provenance complete; Core pin fresh | Same |
| `replay_ok` | Event/lifecycle consistency | Same |
| Static `sorry` / `:=` / D1 / D4 | Draft is not immediately illegal | False-positive history (declaration-unaware `:=`); now declaration-aware |
| Compile probe | Statement parses/elaborates | **Not a pass.** B2: exit 0 + sorry body on 2/8 |
| pytest (176) | Harness regressions | Not model quality |
| Clean-clone recipe | Reproducible install | Ops, not formalizer |

These stay the **hard gates**. Nothing in v3 may weaken them.

### 2.2 Named, partially collected, not a measurement system

| Name | Where | What’s wrong |
|---|---|---|
| Formalizer scorecard | `docs/eval/formalizer-scorecard.md` | Hand-coded qualitative rows; n=8 then n=3; “vacuous / inversion / mixed” are reviewer labels; no script regenerates the table |
| Interpreter scorecard | `docs/eval/interpreter-scorecard.md` | “churn common” is not a count; no accepted-vs-draft diff |
| AI-review agreement | v2p1 record | 3/3 vs the same CTO who designed the claims; no second rater; tiny n |
| Predictions-first tables | `artifacts/local/*-expectations.md` | Excellent *scientific hygiene* (beliefs vs workings). They measure whether **we** predicted the pipeline, not whether the pipeline is good |
| Claim-set freeze | `docs/eval/v1-claim-set.md` | Endpoint list, not a train/held-out split; v2p1-A/B/C never added |
| time-to-VERIFIED | named in v0.3 / INIT_V2 | **Never computed** |
| `skeleton_edit_distance` | library function | **Never applied** to a live draft vs a verified proof |
| 60–70% draft target | v2 promise / DECLOG 40 | **No operational definition until this file** |

### 2.3 Actively misleading if treated as model quality

- **VERIFIED count / “walkthrough green.”** Reviewer wrote the proof.
- **Bundle revalidation 12/12.** Re-checking an old bundle does not
  test the formalizer.
- **pytest 176.** Tests the Python. The formalizer is not in the suite
  (live probes are mocked except one workspace test).
- **AI-review 3/3 agreement.** Agreement with the author is not
  inter-rater reliability and is not semantic correctness.

---

## 3. Proposed v3 metric contract

Define these **before** claiming any Phase 1 win. Thresholds may be
edited at the Phase 0 gate; the “scorer, not markdown” rule for
Phase 2+ must not be dropped.

### 3.1 Operational 60–70% (proposed definition)

On the **held-out simple-class set**, after the live loop (budget ≤ 3):

> **Draft-complete** = the formal artifact’s `statement_text` is
> statically valid (no sorry/admit, no theorem-body `:=`, D1/D4 clean)
> **and** the compile probe succeeds **and** `vacuity_warning` is
> false **and** a cheap inversion heuristic does not fire
> (conclusion is not a restated hypothesis).
>
> **60–70% met** = draft-complete on ≥ 60% of held-out claims
> *without* `--from-file`. Reviewer proofs do not count.

**Probe operationalization (amended 2026-08-13):** Lean requires a
body after a `theorem` conclusion, so a bare signature can never pass
`lake env lean` ("expected ':='") — the probe as first written made
draft-complete structurally unreachable for the signature-only
contract (live evidence: v3p1 and v3h rev-1 all failed). The probe now
rewrites the declaration to `axiom` and checks that the SIGNATURE
elaborates. This measures what §3.1 intended ("the model produced a
non-vacuous compiling signature"); it is a measurement change, not a
prompt tune — no held-out text was modified, and the kernel axiom
audit at verify is untouched (probe remains a signal, INIT_V3 D2).

This is still not semantic fidelity. It is “the model produced a
non-vacuous compiling signature the reviewer can argue with.” That is
the honest 60–70%. Meaning remains the reviewer’s.

**Phase 1 does not claim this number.** Phase 1 reports
`first_try_valid` and `attempts_to_valid` on the **v2-memory** set
(same-text new ids). The 60–70% number is illegal until Phase 2’s
held-out split exists and is scored.

### 3.2 Scorer outputs (per claim, then micro-average)

| Metric | Source | Objective? | Phase 1? |
|---|---|---|---|
| `first_try_valid` | attempt 1 of the loop: audit-clean (D2: probe is *not* required for FORMALIZED; for the 60–70% *target*, probe must also succeed — see §3.1) | yes | **manual** row |
| `attempts_to_valid` | 1..budget or `null` | yes | **manual**; artifact `revision_attempts` |
| `static_reject_class` | sorry / `:=` / D1 / D4 / other | yes | **manual** histogram |
| `probe_compiles` | `statement_probe` | yes (not a pass) | already on artifact |
| `vacuity_flag` | existing heuristic | yes, approximate | already on artifact |
| `inversion_flag` | new heuristic (conclusion vs hyps) | yes, approximate | **not Phase 1** (Phase 2) |
| `d1_core_fq` | mapping rows | yes | already on artifact |
| `sole_author_verified` | VERIFIED **and** proof provenance ≠ reviewer | yes; expect **0** | **must stay 0** unless a model proof passed `#print axioms` |
| `edit_distance` | skeleton → verified proof | yes, once Phase 3 exists | no |
| `time_to_verified_s` | first ingest event → VERIFIED event | yes, but confounded by human latency | no (named, not computed) |
| `reviewer_kind` / agreement | review records vs CTO spot-check | **partial** | keep, label as agreement not truth |

**`first_try_valid` vs FORMALIZED (INIT_V3 D2):** a statement can be
`FORMALIZED` (audit-clean, probe may fail) without being
draft-complete. Do not treat `state == FORMALIZED` as a quality win.

CI (Phase 2+) runs the scorer on **committed fixtures** (no provider).
Live scorecard is a credentialed command. Both write
`docs/eval/formalizer-scorecard.md` via generation, or a generated
`.json` that the markdown includes.

### 3.3 Proposed split

| Split | Claims | Use |
|---|---|---|
| Dev / regression | c1–c4, fwt1, oos1, oos2 | scorer fixtures; do not tune prompts only to these |
| v2 memory | v2p1-A/B/C **same-text new ids** (INIT_V3 D4) | comparable to the 0/3 baseline; Phase 1 live set |
| Held-out v3 | 4–6 **new** simple-class texts, CTO-approved before ingest | the 60–70% number (Phase 2+) |
| Boundary (not scored for the target) | oos3 Nash, existence, calculus | honesty set — expect FORMALIZED / FAIL |

Freshness rule from v2 still applies: read every existing `source_text`
before drafting a new held-out claim; no verbatim overlap.

### 3.4 What remains forever reviewer-owned

- “This Lean statement is what the English claim means.”
- Inversion that compiles (fwt1 class) — heuristic will miss clever
  ones.
- Assumption smuggling, empty-economy gaps (`[Nonempty Agent]`).
- Whether a Core promotion is the right vocabulary.

A 70% draft-complete formalizer can still be 0% semantically faithful.
The packet must keep saying that.

---

## 4. Phase 1 measurement table (locked for the wiring slice)

These are the **only** numbers Phase 1 is allowed to move. Baselines
are from `docs/eval/formalizer-scorecard.md` (v2, 2026-08-09).

| Metric | Definition | Baseline | Phase 1 target | How measured |
|---|---|---|---|---|
| Contamination still fails | A sorry / theorem-body `:=` draft is rejected by `audit` even if a naive probe would report compiles; no formal artifact written | library test + live v2p1-B `sorry` caught pre-kernel | **must remain true** (regression, not a rate) | red test on `formalize_claim` with injected draft_fn |
| Budget cap | Exactly `MAX_REVISION_ATTEMPTS` (3) provider drafts; no silent 4th | library test only (live path is single-shot today) | **must remain true** after wiring | red test: 4 dirty drafts offered, 3 consumed, `FAILED` |
| Attempt-2 success records 2 | Dirty attempt 1, audit-clean attempt 2 → `FORMALIZED` and `revision_attempts == 2` | not on the live path | **must be true** | red test + artifact key |
| Exhausted budget → FAILED | All attempts still have audit problems → `FAILED`, no artifact, `--from-file` still works | today’s static reject | **unchanged semantics** | red test + existing from-file tests stay green |
| pytest | suite size | **176** on `v2.0.0` | 176 + new reds, no regression | `.venv/bin/python -m pytest -q` |
| `a3_runner` imports `revise_loop` | library ≠ product check | **false** (2026-08-12) | **true** | `grep` / import test |
| First-try valid (live, v2-memory new ids) | attempt 1 audit-clean | **0/3** | **report honestly**; no success threshold | predictions file then live `a3_run.py` |
| Attempts-to-valid (live) | 1..3 or `null` | n/a (no loop on live path) | **report honestly** | artifact `revision_attempts` |
| Sole-author VERIFIED | VERIFIED with model-authored proof passing axiom audit | **0%** | **0%** unless a model proof actually verified | do not count `--from-file` proofs |

Predictions **before** the live re-run go in
`artifacts/local/v3-p1-expectations.md` (step, expected, confidence,
rationale). Fill actuals after. Do not retro-edit predictions.

---

## 5. Gold-standard orientation (steal process, not scores)

There is no “autoformalize micro theory” leaderboard. Do not publish
miniF2F/ProofNet numbers. Steal:

- **LeanDojo / miniF2F:** frozen split discipline; pass@k **with** an
  audit gate, never compile@k.
- **Mathlib / AFP:** artifact quality, axiom hygiene, no sorry.
- **This repo’s own B2 spike:** the negative control every scorer must
  include (sorry-contaminated exit-0 fixture → fail).

---

## 6. Predictions-first stays

CTO preference, unchanged: before a live run, write
`artifacts/local/<run>-expectations.md` (step, expected, confidence,
rationale), then a comparison table. That is how we check *our*
beliefs. It is **in addition to** the scorer, not a substitute.

---

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
Proposed only; CTO is the sole semantic approver.
