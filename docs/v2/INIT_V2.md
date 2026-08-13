# INIT_V2 — LeanEcon v1→v2 Plan

**Status:** APPROVED 2026-08-08 (CTO, "Approve as proposed"). Phases 1–3
contract SHIPPED as **v2.0.0 Phoenix** (item 40). Phase 3 measurement
deferred to v3. Auto-formalize direction recorded, not claimed as met.
**Date:** 2026-08-08 (approved); status updated 2026-08-12
**Repo state:** Phoenix ship on `v2/phase3-skeleton`; tags v0.2.0/v0.3.0/v1.0.0
pending `v2.0.0`; pytest 176 green
**Scope:** Approved v1→v2 plan. Phase 1 zero-code; Phases 2–3 additive to
the v1 surface; Phase 4 = this Phoenix tag.

---

## 1. Goal and promise

### Goal

Move from *"v1: a reviewer, via the supported CLI, turns an English claim
into a kernel-checked VERIFIED bundle"* to *"v2: on simple claims, the model
drafts the first 60–70% (interpretation, formal statement with bounded
kernel-feedback revision, proof skeleton); the reviewer closes the last 30%
and the kernel axiom audit guarantees soundness."*

v2 **sharpens** v1; it does not weaken it. The reviewer (human or AI) and the
kernel axiom audit remain non-bypassable. `VERIFIED` stays bundle-gated
(12 checks incl. `12_core_pin`); a bare compile exit 0 stays **NOT a pass**
(B2 spike: `apply?`/`simp` fabricated `sorry` bodies with exit 0 on 2/8
targets — fwt1, oos1b).

### Sharpened promise statement (v2)

1. On **simple claims** (operationally: single-claim sequential pipeline,
   v1-surface vocabulary, no new Core declarations, no game theory), the
   model produces a **draft interpretation**, a **draft formal statement**
   (revised against kernel feedback in a bounded 2–3 attempt loop), and a
   **draft proof skeleton** (Phase 3).
2. The **reviewer — human or AI** (DECISION_LOG 31, `docs/gate3/08-reviewer-policy.md`)
   — approves meaning and owns the final proof. The CTO remains the
   accountable semantic authority.
3. **The kernel axiom audit (`#print axioms` / `sorryAx` absent) is the only
   pass gate** for anything that reaches the kernel. Nothing compiles-green
   without the audit. No exception.
4. Every AI-assisted step is **bounded, audit-gated, and spot-checked** by
   the CTO or designated human reviewer; agreement is measured, not assumed.

### Non-claims (v2 does NOT promise)

- Fully autonomous proving; unattended `VERIFIED`; production SLA on
  time-to-`VERIFIED`.
- Agents, retrieval corpus, or game-theory Core.
- Any path that bypasses the reviewer or the kernel axiom audit.
- Any weakening of the v1 frozen surface (EI 1.0.0, bundle 1.0.0/12 checks,
  Core P2+G7 freeze, CLI subcommands — `docs/releases/v1-surface.md`).
- Model correctness — only bounded, audited drafting.

---

## 2. Phased plan

Four phases, each ending at a CTO gate. No phase auto-promotes. Phase 1 is
**zero new code**. Phase 4 is release. Phases 2–3 are additive to the v1
surface; any CLI/schema addition must be backwards-compatible, documented,
and shipped with `docs/releases/v2.0.0.md` + tag per the earn rule.

### Phase 1 — Exercise the AI reviewer on fresh OOS claims (zero new code)

**Deliverable:** A prediction-first, measured agreement record of the AI
reviewer (`--reviewer hermes --reviewer-kind ai`) vs. CTO spot-checks on
2–4 fresh out-of-sample claims. No source changes.

**Procedure (order matters):**

1. **Draft claim texts** — 2–4 fresh OOS claims in the simple
   consumer/equilibrium class (v1 envelope: preferences, budget, utility,
   CE/FWT vocabulary; no new Core, no Nash/game theory). Never-before-run
   texts; re-use of canonical texts under new ids (c1r2 pattern) only if
   needed to isolate a specific question.
2. **Predictions first** — write numbered pass/fail expectations (step,
   expected behavior, confidence, rationale) to
   `artifacts/local/v2-p1-expectations.md` BEFORE any run (fwt1/OOS
   methodology, CTO preference).
3. **CTO approves the claim texts** (semantic authority) before ingest.
   Empty `clarify` response is NOT consent.
4. **Run the full walkthrough** via `scripts_local/a3_run.py` only, with
   `--reviewer hermes --reviewer-kind ai` for `review`, `gap-ack`, and
   `axiom-approve` (policy §2/§5: `none_noted` still requires
   `--acknowledge-none-noted` for AI too). Full sequence: `ingest →
   interpret → review(ai) → formalize (live; `--from-file` recovery if
   2× static reject) → gap-ack(ai) → verify → axiom-approve(ai) → bundle →
   replay`.
5. **CTO spot-checks every AI review decision** (accept/reject, gap-acks,
   axiom approvals) — agreement or disagreement recorded per claim, per
   decision type.
6. **Evidence packet** — expectations-vs-actual table, per-claim verdict
   table (AI decision, CTO spot-check, agree/disagree, rationale), bundle +
   replay outputs, pytest still green (168), scorecard v2 baseline rows
   (see §3).

**Acceptance criteria:**

- All 2–4 claims complete the walkthrough with `reviewer_kind=ai` recorded
  on every review record; no CLI/entrypath workarounds.
- Zero silent bypasses: every `VERIFIED` still passes the 12-check bundle
  validator (incl. `12_core_pin`) and the kernel axiom audit; any AI
  decision that would have slipped a vacuous/inverted statement is caught
  by the CTO spot-check and recorded as a disagreement.
- Agreement rate and disagreement log are in the packet.
- `git status` shows **no tracked source changes** from Phase 1.

**CTO gate:** approve the agreement record → authorize Phase 2; or direct
AI-reviewer prompt/policy iteration first; or halt v2.

**Evidence expected:** `artifacts/local/v2-p1-expectations.md` (pre-run),
Phase 1 record (agreement table + disagreements + scorecard v2 rows),
green pytest, zero-code diff.

---

### Phase 2 — Bounded kernel-feedback revision loop (TDD, audit-gated)

**Deliverable:** A bounded (2–3 attempt) revision loop in which the model's
formal-statement draft is validated and revised against **kernel feedback**
(static rejects, compile probe, vacuity warning, D1/D4 checks — the v1
formalization tooling) with the **kernel axiom audit as the success gate**.
This is the B2 lesson encoded as product: **no naive "compile → success"**
— a candidate that compiles but fails the `sorryAx` audit is FAILED, full
stop.

**TDD order:**

1. **Red:** fixture tests first — (a) a B2-style contaminated candidate
   (`apply?`/`simp` fabricated `sorry` body, exit 0) must be rejected by
   the loop's audit gate; (b) the attempt budget (2–3) is enforced — no
   silent 4th attempt; (c) a genuinely clean one-liner candidate (c1–c4 /
   oos1a class) passes within budget. Watch them fail.
2. **Green:** minimal loop implementation — per-attempt kernel feedback
   surfaced verbatim (stderr tail, `#print axioms` output, vacuity/D1/D4
   signals) to the model; attempts logged; final verdict = audit-gated.
3. **Regression:** every new failure path updates
   `lifecycle.TRANSITIONS` **in the same change** (F1 rule) and keeps
   `replay_ok=true`; pytest suite green; `a3_run.py` remains the only live
   entrypoint (D2/`12_core_pin` must not silently drop).

**Acceptance criteria:**

- The contaminated-candidate fixture is caught by the audit gate (never
  "green" on exit code).
- Attempt counter enforced; exhausted budget surfaces FAILED honestly and
  hands the reviewer `formalize --from-file` (v1 recovery unchanged).
- Live run on the Phase 1 claim set: per-claim attempt counts, audit
  outcomes, and reviewer-correction delta recorded (scorecard v2).
- No lifecycle/replay regressions (F1 rule); bundle still 12-check gated.

**CTO gate:** approve the loop record (failure modes, attempt
distribution, audit-gate regression evidence) → authorize Phase 3 and/or
v2 release prep; or restrict loop bounds; or halt.

**Evidence expected:** new tests (contamination gate, budget, replay),
updated `docs/eval/formalizer-scorecard.md` v2 (attempts-to-valid,
audit outcomes, first-try rate delta vs v1 ~1/8), Phase 2 loop record.

---

### Phase 3 (optional) — Proof-skeleton drafting assist

**Entry condition:** Phase 2 CTO gate passed AND loop record shows the
bounded assist measurably reduces reviewer correction load without false
greens. If the condition fails, Phase 3 is **not** started — the decision
and rationale are recorded.

**Deliverable:** A model-drafted proof **skeleton** (explicit `have h1 : P :=
by …` chain with clearly marked gaps) that the reviewer refines into the
kernel-passing proof. The skeleton is a drafting artifact — it never
enters `verify` unrefined (gaps would fail the axiom audit; that is by
design). Reviewer refinement is measured, not assumed.

**TDD:** skeleton-format contract tests (structure, gap marking, no
smuggled fabricated bodies); the audit gate on the final refined proof is
unchanged.

**Measurement:** per claim, **edit distance** (lines/terms changed from
model skeleton to reviewer's verified proof) and **time-to-VERIFIED**
(ingest → VERIFIED wall-clock) vs. the v1 baseline (reviewer from
scratch, no skeleton). Halt criterion: if edit distance or time-to-
VERIFIED does not improve materially on the Phase 1 claim set, the phase
**halts with a written reason** — a clean outcome, not a failure.

**Acceptance criteria:** skeleton never verifies unrefined; measurement
table delivered; improvement threshold met OR documented halt.

**CTO gate:** approve promotion of skeleton assist into the v2 surface, or
halt Phase 3 (proceed to Phase 4 with Phases 1–2 only).

**Evidence expected:** skeleton-scorecard table, per-claim edit-distance /
time-to-VERIFIED log, Phase 3 record.

---

### Phase 4 — v2.0.0 release

**Deliverable:** `docs/releases/v2.0.0.md` (earn rule: tag only with the
release doc) + `v2-surface.md` + README v2 promise/non-claims + scorecard
v2 + DECISION_LOG items + tag `v2.0.0` after CTO approval. Attribution and
bot/CTO token flows unchanged (`scripts_local/open_pr.py --bot` for
implementation PRs; CTO merge via `merge_pr.py` + `verify_protection.py`).

**Acceptance criteria:** pytest green; every v2 claim's bundle revalidates;
README truth; tags on origin; DECISION_LOG updated before skill patch.

**CTO gate:** approve the release packet.

---

## 3. Measurement plan

| Metric | Where | Baseline (v1) | v2 target / use |
|---|---|---|---|
| Formalizer scorecard v2 | `docs/eval/formalizer-scorecard.md` | statement-valid first try ~1/8; static-reject catch high; reviewer proof load-bearing | attempts-to-valid per claim, audit outcomes, first-try rate delta, D1/vacuity/inversion rates — Phase 2 verdict input |
| Interpreter churn | `docs/eval/interpreter-scorecard.md` | reviewer revision churn common (rev-1 → rev-2) | revisions per claim, `none_noted` discipline, accepted-vs-draft delta — Phase 1 record |
| AI-review agreement rate | Phase 1 record | **never exercised** (v1) | per-claim, per-decision-type (review/gap-ack/axiom) agree/disagree vs CTO spot-check; 0 silent bypasses |
| Time-to-VERIFIED delta | bundle timestamps / run records | v1 walkthrough records | ingest→VERIFIED wall-clock per claim; Phases 2–3 improvement vs v1; no SLA implied |

All measurements are per-claim, recorded alongside artifacts/bundles, and
reported as aggregate tables. Predictions are always written before live
runs (CTO preference, fwt1/OOS methodology).

---

## 4. Risks

| # | Risk | Evidence | Mitigation |
|---|---|---|---|
| R1 | Proof-assist false green (compile 0, `sorry` body) | B2 spike: `apply?`/`simp` fabricated `sorryAx` on fwt1/oos1b, exit 0 | Kernel axiom audit is the ONLY pass gate; TDD contamination fixture (Phase 2 red); never gate on exit code |
| R2 | AI reviewer "agreement" ≠ correctness | AI reviewer never exercised (v1) | Phase 1 CTO spot-checks every decision; agreement + disagreement logged; policy unchanged (AI authorized, CTO accountable) |
| R3 | Auto-applied `exact?`/`apply?` circularity (suggestions referencing the theorem being defined) | B2 spike | Loop feeds diagnostics only — never auto-applies suggestions; reviewer owns final proof |
| R4 | Lifecycle/replay drift when adding loop failure paths | F1 (PR #12): runner emitted edges TRANSITIONS lacked | Same-change TRANSITIONS update + replay regression test (Phase 2 step 3) |
| R5 | Stale-install D2 drop (`12_core_pin` silently missing) | OOS F2 / oos1 | `a3_run.py` (PYTHONPATH=src) is the only live entrypoint; bundle revalidation in Phase 4 |
| R6 | Scope creep (agents/corpus/game-theory Core) | v1 non-claims; post-v1 audit P2 | Explicit non-claims; CODEOWNERS Core `@Bonorinoa` only; any Core touch needs a CTO slice |
| R7 | Reviewer rubber-stamping under automation pressure | n/a (new) | Spot-check protocol + disagreement log; bounded loop surfaces FAILED honestly, never "promotes" itself |
| R8 | Phase 3 skeleton = more review surface, not less | n/a (new) | Edit-distance / time-to-VERIFIED gates; clean halt outcome |

---

## 5. Explicitly NOT in v2

- No fully autonomous proving; no unattended `VERIFIED`; no production SLA.
- No agents, no retrieval corpus, no game-theory/Nash Core.
- No path bypassing the reviewer or the kernel axiom audit; no bare-compile
  pass criterion, anywhere.
- No weakening of the v1 freeze: EI 1.0.0, bundle 1.0.0 (12 checks +
  `12_core_pin`), Core P2+G7 freeze, CLI subcommands.
- No reopening of locked decisions (DECISION_LOG 1–36) or the v1 non-claims.
- No unapproved semantic content: CTO remains sole semantic approver for
  claims, Core, and policy; AI reviewer acts only under
  `docs/gate3/08-reviewer-policy.md`.

---

## 6. Gate summary

| Gate | Input to CTO | Decision options |
|---|---|---|
| Phase 1 | Agreement record, expectations-vs-actual, zero-code diff | Proceed to P2 / iterate AI reviewer / halt |
| Phase 2 | Loop record: contamination fixture green, budget enforced, attempt distribution, scorecard v2 | Proceed to P3 + release prep / restrict bounds / halt |
| Phase 3 (optional) | Edit-distance + time-to-VERIFIED table | Promote into v2 surface / halt (recorded) |
| Phase 4 | Release packet + revalidated bundles | Tag v2.0.0 / amend |

---

**Attribution:** This plan was prepared by Hermes Agent (Nous Research)
under CTO direction. The CTO remains the accountable semantic authority
and sole semantic approver for claims, Core, and policy. AI assistance in
this plan is drafting only; nothing here is approved without CTO review.
