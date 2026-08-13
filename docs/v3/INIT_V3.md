# INIT_V3 — proposed v2→v3 roadmap (Phoenix → constrained auto-formalize)

**Status:** Phase 0 **approved as proposed** 2026-08-12. Phase 1
**implemented** on branch `v3/phase1-wire-loop` 2026-08-13 (live
first_try_valid **1/3**, sole-author **0%**). Not a tag promise.
No PR until later phases have verifiable checks. Empty `clarify`
is still not consent.
**Base:** `main` @ `9c12936` = tag `v2.0.0` Phoenix, package `2.0.0`,
pytest **176**, remote **main-only**.
**Authority this does not override:** `docs/gate3/DECISION_LOG.md`
(31–40; item 40 = direction lock), `docs/releases/v2.0.0.md`,
`docs/releases/v2-surface.md`, v1 surface freeze, reviewer policy
(`docs/gate3/08-reviewer-policy.md`).
**Companions:** `docs/v3/METRICS.md` (metric contract),
`docs/v3/PLAN.md` (Phase 1 execution card),
`docs/v3/INIT_PROMPTS.md` (session prompts).

---

## 0. What is true on disk (recon, this session)

| Fact | Evidence |
|---|---|
| Phoenix shipped | tag `v2.0.0`, package `2.0.0`, builder `leanecon-a3-2.0.0` |
| Models run live | interpret = `mistral-medium-3-5`; formalize = `labs-leanstral-1-5` |
| Formalizer is not statement-faithful | scorecard: ~1/8 then **0/3** first-try valid (v2p1); **0%** sole-author of VERIFIED |
| `--from-file` is recovery | live path first; reviewer-authored formal after static reject |
| `revise_loop` is on the **live** path (this branch) | `a3_runner.formalize_claim` calls `revise_statement_draft`; `MAX_REVISION_ATTEMPTS=3`; 4 new tests; suite **180**. Not on `origin/main` until a PR merges |
| `skeleton` is a **library** | `src/leanecon/skeleton.py`; not imported by `a3_runner`; measurement deferred |
| Live `formalize` runs the bounded loop | audit-clean → `FORMALIZED` (probe is a signal); exhausted budget → `FAILED`, no artifact |
| Probe is a signal, not a pass | non-compiling statement is still `FORMALIZED` and reviewable |
| Compile ≠ pass | B2 spike: 2/8 false greens (`sorryAx` with exit 0) |
| Reviewer + 12-check bundle | `VERIFIED` is system-only; AI reviewer authorized (item 31); CTO accountable |

Library ≠ product. On **this branch** the import exists. On `origin/main`
/ tag `v2.0.0` it does not. The 60–70% draft target is still **not
earned** (live first_try_valid 1/3; probe fail on both FORMALIZED).

---

## 1. Why v3 exists

v2 Phoenix shipped the *foundation*: HITL verified workflow, live
Mistral drafts, an exercised AI reviewer, and two unused harnesses.

Direction lock (DECISION_LOG 40, 2026-08-12):

> Constrained auto-formalization of natural language (and later a mix of
> typing + LaTeX) into formal representations this system already knows
> how to audit (today: EI + mapping report + Lean 4; later: graphs /
> embeddings / other IRs the prover agent can consume). Decomposition,
> kernel-feedback loops wired into the CLI, and richer IRs build **on**
> Phoenix — they do not replace the reviewer or the axiom audit.

The 60–70% “model drafts the first stretch” target is the **v3
measurement goal**. It is **not earned** until `docs/v3/METRICS.md`
says so on a frozen held-out split.

The older roadmap line (“corpus-grade published claims + multi-domain +
multi-reviewer”) is **not** the v3.0.0 promise. That is later
(v3.x / v4). A corpus on a 0% sole-author formalizer is architecture
theatre.

---

## 2. Proposed v3.0.0 promise

On **simple claims** (v1/v2 envelope: consumer / CE / FWT vocabulary,
no new Core, no game theory):

1. Natural-language input (plain text first; `$...$` tolerated as
   characters, not a TeX parser) is drafted into the existing audited
   IRs: Economic Interpretation + mapping report + Lean 4 statement.
2. Live `formalize` runs the bounded kernel-feedback revision loop
   (`revise_loop`, budget `MAX_REVISION_ATTEMPTS=3`). A first-try-valid
   or within-budget-valid **statement** is the model’s job; `--from-file`
   remains honest recovery, not the default.
3. An optional proof-skeleton draft (`skeleton`) may be offered later
   (Phase 3). Unrefined skeletons never enter `verify`.
4. Quality is **measured** on a frozen claim split. The 60–70% target
   is defined in `docs/v3/METRICS.md` **before** anyone claims it.
   Phase 1 may only fill a **manual** table against those definitions;
   a committed scorer is Phase 2.
5. The reviewer (human or AI) still owns meaning. The kernel axiom
   audit (`#print axioms` / `sorryAx` absent) is still the only pass
   gate. `VERIFIED` stays 12-check bundle-gated.

### Non-claims (v3.0.0 does NOT promise)

- Unattended `VERIFIED`; production SLA; “solved autoformalization.”
- Graphs, embeddings, or a second IR **as a ship requirement**
  (research spikes only, CTO opt-in).
- Agents / retrieval corpus / Nash or game-theory Core / product UI /
  public HTTP API.
- Any path that bypasses the reviewer or `#print axioms` / `sorryAx`.
- Weakening EI 1.0.0, bundle 1.0.0 / 12 checks, Core P2+G7, or the
  v2 CLI subcommand set. Additive flags only if a later phase names them.
- Phase 1 does **not** add CLI subcommands or flags.

---

## 3. Proposed defaults this packet asks the CTO to lock

Approve-as-proposed means these five defaults. Amend any of them in
writing; do not leave them implicit.

| ID | Default | Why |
|---|---|---|
| D1 | **Phase 1 = wire the loop**, not scorer-first, not skeleton, not IR | Cheapest library → product; metrics are defined now, scored by hand until Phase 2 |
| D2 | Loop retries **only while `audit` fails** (statement + D4 + mapping/D1). A statically clean, non-compiling statement is still `FORMALIZED` (probe remains a signal). `revise_loop.accepted` (audit∧probe) is **not** the FORMALIZED predicate | Preserves today’s “reviewer owns the statement; kernel arbitrates at verify” |
| D3 | Exhausted budget → `FAILED`, **no formal artifact** (same as today’s static reject). `revision_history` goes on the FAILED state-event `detail`. Accepted loop → history on the formal artifact | Preserves the “rejected candidate writes nothing” guard |
| D4 | Live re-run uses **same-text new claim ids** (c1r2 pattern). Do not re-formalize VERIFIED v2p1-A/B/C | Isolates the pipeline change |
| D5 | `PROVIDER_UNAVAILABLE` → `BLOCKED` immediately (not an attempt). Parse / `INVALID_OUTPUT` / audit fail **do** consume an attempt | Distinguishes outage from bad drafts |

Open only if the CTO rejects a default. No other Phase 1 decisions.

---

## 4. Phases

Four product phases + a release. Phase 0 is this polish.
No phase auto-promotes. WIP limit: one open product promise.

### Phase 0 — Polish this packet (docs only) — **this session**

**Deliverable:** this file + `METRICS.md` + `PLAN.md`.
**Acceptance:** CTO “approve as proposed” (or amend). No code.
**Gate:** approve → authorize **Phase 1 only**.

### Phase 1 — Wire the loop (the missing product)

**Why first:** `revise_loop.py` exists and is tested; live `formalize`
does not call it.

**Deliverable (live path only):** `formalize_claim` invokes
`revise_statement_draft` with injected `draft_fn` / `audit` / `probe`.

| Injection | Meaning |
|---|---|
| `draft_fn(history)` | one `adapter.request(FORMALIZE)` whose prompt includes verbatim prior `Feedback` (static problems + probe stderr); parse to statement + `target_theorem` + `mapping_report`; stash the parse; return the statement string |
| `audit(stmt)` | existing `validate_statement_text` + `validate_scaffolding_namespace` + `validate_mapping_report` (D1) against the stashed mapping + accepted EI; empty list = clean |
| `probe(stmt)` | existing `probe_statement_compiles` — **feedback only** (D2) |

`--from-file` / `--statement-file`+`--mapping-file` stay on
`formalize_from_candidate`. **No new CLI.**

**Persist (D3):**

- Audit-clean within budget → `FORMALIZED`; formal artifact gains
  additive keys `revision_attempts: int` and `revision_history: [...]`
  (serialised `Feedback`). Last stashed parse is the candidate.
- Budget exhausted (every attempt still has audit problems) → `FAILED`,
  no artifact; `detail.revision_history` + `detail.attempts_used` on
  the state event; operator uses existing `--from-file`.
- F1 rule: **no new lifecycle edges expected** (`ACCEPTED|FAILED|BLOCKED → FAILED`
  already exist). If a new failure path appears, update
  `lifecycle.TRANSITIONS` in the **same** change.

**TDD (red first, watch fail, then wire):**

1. Contaminated draft (`sorry` / theorem-body `:=`) still `FAILED`
   after the loop; never stored; audit wins even if a naive probe
   would say compiles.
2. Budget cap: a draft that never cleans yields exactly
   `MAX_REVISION_ATTEMPTS` provider drafts, then `FAILED`; no 4th.
3. A fixture that is dirty on attempt 1 and audit-clean on attempt 2
   is `FORMALIZED` with `revision_attempts == 2` on the artifact.

**Acceptance:**

- pytest green (176 + the new reds); no regression.
- `a3_runner` imports `leanecon.revise_loop` (library ≠ product flips).
- Predictions file written **before** any live re-run
  (`artifacts/local/v3-p1-expectations.md`).
- Live same-text new ids (D4) via
  `.venv/bin/python scripts_local/a3_run.py` only.
- Scorecard updated **honestly** (manual table allowed): 0% sole-author
  unless a **model** proof actually passed the axiom audit (it will not).

**Deliberately not in Phase 1:** skeleton CLI, new IRs, decomposition,
Core, UI, model swap, scorer script, v3.0.0 tag, agents, embeddings.

**Gate:** approve loop-live record → Phase 2, or halt.

### Phase 2 — Objective eval harness

**Why second:** without a scorer, Phase 1 “improvement” is another
handwritten table. Definitions live in `METRICS.md` from Phase 0;
this phase automates them.

**Deliverable:** `docs/eval/v3-claim-split.md` (frozen train/dev vs
held-out) + committed scorer (`scripts/eval_formalizer.py` or
equivalent) emitting JSON + markdown: `first_try_valid`,
`attempts_to_valid`, static-reject histogram, vacuity flag, D1 miss,
`sole_author_verified` (0 unless a model proof also passes the audit).

**Acceptance:** scorer is deterministic on committed fixtures (no live
provider for the regression job). Live scorecard is a **separate**
credentialed command. CI runs the fixture scorer. Hand-edits of
numbers are a bug.
**Gate:** approve the metric contract → Phase 3, or iterate definitions.

### Phase 3 — Skeleton assist, actually measured

**Entry:** Phase 1 live **and** Phase 2 scorer exist. If Phase 1 did
not move first-try / attempts-to-valid, **halt Phase 3** and record
why (INIT_V2 R8, still valid).

**Deliverable:** optional `formalize --skeleton` (or a `skeleton`
subcommand — the **first** allowed additive CLI, and only in this
phase) that writes a drafting artifact. `skeleton_edit_distance` +
ingest→VERIFIED wall-clock from events. Unresolved `-- GAP:` never
reaches `verify`.

**Acceptance:** measurement table on the Phase 1 claim set; improve
**or** documented halt.
**Gate:** promote / halt.

### Phase 4 — Decomposition (only if 1–3 earned)

A claim may split into a **reviewed** list of sub-claims, each walking
the existing single-claim pipeline. No multi-agent orchestration.
Parent cannot be `VERIFIED` unless every child is `VERIFIED` and a
reviewer-authored (or loop-closed) composition proof exists. Start
with a 2-subgoal toy compiled in the pinned workspace (sandbox-toy
rule) before any runner change.

**Out:** graphs, embeddings, retrieval, parallel agents.

### Phase 5 — v3.0.0 release

Earn rule: `docs/releases/v3.0.0.md` + tag only after CTO approval.
Must include: scorer numbers on the frozen split, honest 60–70%
verdict (met / missed / narrowed), README non-claims, DECISION_LOG
items, builder bump. **Do not tag from Phase 1.**

---

## 5. IR suggestion (cut-ready)

| IR | Today | v3.0.0 | Later / spike only |
|---|---|---|---|
| English claim | ingest | unchanged | — |
| Economic Interpretation | live interpret | schema 1.0.0 frozen | — |
| Mapping report | live formalize | D1/D4 unchanged | — |
| Lean 4 statement | live / `--from-file` | loop-revised | — |
| Proof skeleton | library only | optional draft (P3) | — |
| Lean proof | reviewer | still reviewer | bounded assist after audit-gated spike |
| Graphs | none | **not in v3.0.0** | spike if a claim is blocked *because* we lack incidence |
| Embeddings | none | **not in v3.0.0** | retrieval is a corpus problem; we have no corpus |
| LaTeX | none | `$...$` as text in `claim_text` | real TeX parse only after a failed-text case |

Krakauer: do not add an IR the kernel cannot audit. Embeddings cannot
be `#print axioms`-checked.

---

## 6. Risks

| # | Risk | Evidence | Mitigation |
|---|---|---|---|
| V3-R1 | Implement before the metric contract exists | horsepower without a gate | Phase 0 hard-stop; Prompt B |
| V3-R2 | Wiring the loop still yields 0/N valid | v2p1 0/3 × 2 waves | Honest FAIL + feedback is still a product win; do not claim 60–70% |
| V3-R3 | False green via compile | B2 2/8 | audit gate unchanged; scorer must not use exit 0 |
| V3-R4 | Treating `revise_loop.accepted` as FORMALIZED | library requires probe | D2 |
| V3-R5 | New lifecycle edges break replay | F1 / PR #12 | same-change `TRANSITIONS` |
| V3-R6 | Scope: embeddings / UI / agents / Nash | v2 non-claims; item 40 | explicit non-claims; Core CODEOWNERS `@Bonorinoa` |
| V3-R7 | Optimizing the handwritten scorecard | n=8 qualitative | Phase 2 scorer + held-out |
| V3-R8 | Stale install drops `12_core_pin` | OOS F2 | always `a3_run.py` |
| V3-R9 | Disturbing VERIFIED claims | v2p1-A/B/C are evidence | D4 same-text new ids |

---

## 7. Explicitly NOT in this proposed v3.0.0

- Product UI / API-as-a-service / multi-agent orchestration.
- Embeddings, vector retrieval, or a published corpus.
- Game-theory / Nash Core; existence theorems as VERIFIED targets.
- Unattended VERIFIED; production SLA.
- Reopening DECISION_LOG 1–40 or the v1/v2 surface freeze.
- Weakening the kernel axiom audit.

---

## 8. Gate summary

| Gate | Input | Decision |
|---|---|---|
| Phase 0 | This INIT + METRICS + PLAN | Approve / amend / halt |
| Phase 1 | Loop-live record + tests + honest scorecard | Phase 2 / restrict / halt |
| Phase 2 | Scorer + frozen split + CI fixture run | Phase 3 / iterate metrics / halt |
| Phase 3 | Edit-distance + time-to-VERIFIED table | Promote / halt |
| Phase 4 | Toy decomposition + one worked claim | Opt in / skip to release |
| Phase 5 | `docs/releases/v3.0.0.md` | Tag / amend |

---

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
Proposed only; the CTO remains the accountable semantic authority
and sole semantic approver. Nothing here is approved without review.
