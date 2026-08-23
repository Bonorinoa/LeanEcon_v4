# v3.5.0 → v4.0.0 — target states and sprint development plan

**Status:** PLAN FOR APPROVAL. Not an implementation authorization.
**Date:** 2026-08-23. Base: `main` @ `12e267c` = tag `v3.0.0`, suite 229.
**Companions:** `docs/v3.5/BRIEF.md` (model/literature/opinion/fidelity),
`docs/v3.5/state-machine-flow.html` (I/O map).
**Authority this does not override:** DECISION_LOG 1–49, reviewer policy,
kernel axiom audit, bundle 12-check, sealed-eval protocol, spent-holdout
rule. Empty clarify ≠ consent.

---

## 0. Correction of record

Earlier notes said `sanitize_core_mapping_rows()` was unimplemented
behind RED tests. Repo inspection 2026-08-23: **both** repair levers
(`sanitize_signature_draft`, `sanitize_core_mapping_rows`) are
implemented in `formalization.py` and invoked in `a3_runner.py`
(pre-audit, with `repair_notes` appended to `revision_history`).
The mechanical-repair work is **landed**, not pending. Consequence:
v3.5 opens at P2 (elaboration), with no debt carried from sprint-1.

Also: `docs/eval/` carries the established prediction-first pattern
(`v4h1-expectations.md` + `v4h1-manifest.json`). This plan reuses it.

---

## 1. Target state — v3.5.0 "Intelligence"

**One sentence:** the same machine, the same ten states, the same
gates and reviewer authority — such that on a fresh sealed holdout
of simple-class claims, at least 60% of claims reach `FORMALIZED`
with a signature that actually **elaborates** in the pinned
workspace, within the existing three-attempt budget, with zero new
lifecycle states and zero weakened checks.

**What is different when it ships (user-visible):**

| Aspect | v3.0.0 today | v3.5.0 |
|---|---|---|
| Formalize success bar | audit-clean (P1∧P3) | audit-clean ∧ probe signal tracked; repair targets P2 |
| Probe role | recorded, unused for repair | structured stderr feeds one bounded in-budget repair |
| Failure labels | ad-hoc stderr strings | every FAILED event labeled by fidelity property P1–P6 |
| Draft-complete (fresh sealed) | 15% (v3-era sets, stale) | ≥60% target, or a written miss naming the next property |
| Lifecycle / gates / reviewer policy | — | **unchanged** |

**What ships in the repo:** probe-repair stage (new module +
wiring), fidelity-property labeling on failure events, fresh sealed
holdout `v35h1` with expectations+manifest, dev-fixture model A/B
card (evidence only), `DEVELOPMENT.md` reverted to `3.5.0.dev0`,
release packet + tag after the promise is earned.

**Explicit non-goals:** no `lean-lsp-mcp` / MCP integration, no
proof generation or tactic search, no multi-claim graphs, no
retrieval corpus, no product UI, no unattended `VERIFIED`, no
`MVP_MODEL_MAP` edit inside v3.5 (A/B produces evidence and a
recommendation; a swap is its own later decision), no taxonomy
catalog, no gate or schema weakening.

---

## 2. Target state — v4.0.0 "Agentic"

**One sentence:** drafts become tool-using — after formalize, a
repair/prove assistant works interactively against Lean under a
**fixed signature** (skeletons with `-- GAP:` markers first, hole
closing second), while model selection per capability becomes a
measured harness; `VERIFIED` remains kernel-and-bundle-gated and
the reviewer keeps sole semantic authority.

**What is different when it ships:**

| Aspect | v3.5.0 | v4.0.0 |
|---|---|---|
| Lean interaction | one-shot compile probes | interactive session (LSP/MCP or our own `lake env lean` harness) behind a typed tool boundary |
| Repair | statement-level, prompt-based | goal-conditioned edits under frozen signatures (M2F staging [8]) |
| Proof | reviewer authors; kernel audits | assistant drafts skeleton steps; reviewer edits/approves; kernel still the only pass |
| Model choice | single pin + A/B evidence | per-capability selection harness over sealed dev fixtures |
| `opinion` | optional consultative side-door | may graduate to a second-rater quality study; auto-accept still requires explicit policy amendment |

**Sequencing rule (kept from INIT_V4):** Agentic work begins only
when P2 is no longer the binding constraint — i.e., after v3.5's
sealed result lands. Building interactive Lean tooling before we
produce elaborating statements would be architecture theatre.

**Explicit non-goals (v4.0.0):** unattended `VERIFIED`, production
SLA / public API, multi-claim dependency graphs and retrieval
(deferred to v4.x), replacing the reviewer, weakening EI/bundle/
Core/reviewer policy.

---

## 3. Sprint plan — v3.5.0

Six phases, each with its own gate. Calendar estimate ≈ 2 weeks at
current cadence. Every eval step is prediction-first; spent sets
(v3h*, v4h1, v4smk) stay spent except as dev fixtures.

### Phase 0 — branch and bookkeeping (~½ day)
- Branch `v35/intelligence-sprint` from `main@12e267c`.
- Revert `DEVELOPMENT.md` to `3.5.0.dev0`; align `BUILDER_IDENTITY`.
- DECISION_LOG entry: adopt fidelity properties **P1–P6**
  (BRIEF §4) as the failure-labeling ontology; retire the
  observed-error-taxonomy idea (prior L2) as a category error.
- **Gate G0:** full suite green; `check_release_state.py` accepts
  the dev suffix.

### Phase 1 — metrics audit + baseline measurement, dev only (1–2 days)
- Motivation: v4h1's probe numbers were invalidated by the wrap
  bug (fixed in `verifier.py` 2026-08-17); we have no trustworthy
  post-repair P2 baseline. The metric layer itself was last touched
  2026-08-13 (probe-wrap operationalization) and predates both
  repair levers — see D5 below.
- **D5 metrics audit first:** map `eval_formalizer.static_reject_class`
  buckets onto fidelity properties P1–P6; harden the string-matching
  classifier (`":= "` substring matches are brittle); split the
  `draft_complete` conjunction into `audit_clean_rate` and
  `elaborates_rate` components so a partial result like v4h1
  (100% clean, 0% elaborates) stays legible per component;
  re-freeze definitions in `docs/v3.5/METRICS.md`.
- Write `docs/eval/v35-baseline-expectations.md` **before** running:
  predicted P1/P2/P3 pass rates on dev fixtures (v2p1-A/B, v4smk-A/B
  texts), predicted failure-property mix.
- Run the fixture scorer; label every outcome P1–P6.
- **Gate G1 (go / iterate / halt):** inventory delivered and matches
  the plan's assumptions. Halt if baseline already ≥60% P2 on dev —
  then Phase 2 shrinks to "keep probe visible," and we go to
  Phase 4 early.

### Phase 2 — L1 probe-in-loop repair (2–4 days)
- Experiment card first: hypothesis, mechanism split
  (**mechanical**: structured stderr extraction, deterministic;
  **heuristic**: repair-prompt wording — named separately, per
  standing CTO preference), fixtures, metrics (P2 rate,
  `attempts_used` distribution, regression guard on audit-clean
  rate), rollback trigger.
- TDD: RED tests before implementation — probe-repair consumes the
  normal attempt budget; provider `UNAVAILABLE` raises out (never
  burns an attempt); a clean-elaborating draft passes untouched;
  exhausted budget leaves NO artifact; `repair_notes` provenance
  preserved.
- Implementation: new module (e.g. `probe_repair.py`) called from
  the formalize path after a failed probe, feeding
  `_revision_feedback_block`. Sanitizer scope stays P1/mechanical-P3
  only — it must never touch conclusions (P4/P5).
- **Gate G2 (go / revert):** fixture scorer green; no weakening of
  exact-budget / no-artifact assertions; P2 rate improves on dev
  without regressing P1∧P3.

### Phase 3 — formalize-model A/B, dev only (1–2 days, may overlap P2)
- Card: labs-leanstral-1-5 vs mistral-medium-3.5 vs mistral-small-4
  on identical prompts/fixtures; predictions first; scored by the
  same P1–P6 rubric; cost noted.
- Output: evidence + recommendation **only**. No config edit.
- **Gate G3:** results recorded in `docs/eval/`; swap question
  handed to CTO as a separate future decision.

### Phase 4 — freeze + fresh sealed holdout (1 day prep + 1 day run)
- Freeze all intelligence changes. Assemble `v35h1`: fresh
  simple-class claim texts (consumer / CE / FWT Core envelope, no
  reuse of v3h/v3h2/v3h3/v4h1 texts), manifest + predictions
  committed **before** any run, one scoring pass.
- **Gate G4:** earn rule — draft_complete ∧ probe-elaborates ≥60%,
  else a written miss naming the binding property and the next
  lever. Spent-set retuning remains forbidden.

### Phase 5 — optional `opinion` side-door (2 days, only if CTO opts in)
- Consultative only, exactly as BRIEF §3: no transitions, no new
  event type, `SEMANTIC_TRIAGE` capability, opinions append-only.
- Ship only if Phases 0–4 land with slack; otherwise parked to v4.
- **Gate G5:** design pass approved by CTO before any code.

### Phase 6 — release (½ day)
- Release packet with earned promise; `DEVELOPMENT.md` truth
  surface updated; README refresh rides along; tag `v3.5.0` only
  after G4 is met or the miss is formally accepted as a narrowed
  promise in writing.
- **Gate G6:** release-state check + full suite green on the tag.

---

## 4. v4.0.0 sketch (order-of-work only; detailed cards come after v3.5)

1. **Tool boundary spike:** typed wrapper around interactive Lean
   (evaluate `lean-lsp-mcp` subprocess vs our own `lake env lean`
   driver; pick ONE; axiom-gated like everything else).
2. **Skeleton-then-close staging:** formalize emits skeleton steps;
   close-holes pass runs under frozen signatures; unresolved
   `-- GAP:` continues to block verify (existing contract).
3. **Selection harness:** generalize the Phase-3 A/B into a
   repeatable per-capability evaluation over sealed dev fixtures.
4. **Opinion graduation study:** second-rater agreement measurement
   (human vs AI reviewer on held-out EI judgments); any authority
   change goes through DECISION_LOG, never silently.

Each numbered item is its own gated phase in the v4 train; nothing
here authorizes code.

---

## 5. Decisions requested now

| # | Decision | Recommendation | Status |
|---|---|---|---|
| D1 | Approve phase order and gates G0–G6 | Approve as written | **pending CTO** |
| D2 | Probe-repair budget semantics: inside `MAX_REVISION_ATTEMPTS=3` vs a separate probe budget | Inside the 3 — no silent budget expansion; revisit only with evidence that budget truncation (not failure classes) binds | **under discussion** |
| D3 | `opinion` in v3.5 (Phase 5) or park to v4 | Park unless slack | **DECIDED 2026-08-23: park to v4** |
| D4 | Keep labs-leanstral pin through v3.5; decide swaps only on sealed evidence | Confirm | **DECIDED 2026-08-23: pin kept** |

Additional decision raised 2026-08-23:

| # | Decision | Recommendation |
|---|---|---|
| D5 | Metrics re-audit before sealed scoring (see §Phase 1 amendment): map `static_reject_class` buckets to P1–P6, harden the string-matching classifier, split `draft_complete` into `audit_clean_rate` / `elaborates_rate` so the v4h1 partial result remains legible, and re-freeze `docs/v3/METRICS.md` → `docs/v3.5/METRICS.md` | Adopt as part of Phase 1 |

Empty clarify ≠ consent. Implementation starts only after D1 lands.
