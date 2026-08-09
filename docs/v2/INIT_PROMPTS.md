# LeanEcon v1→v2 — Session Initialization Prompts

Reusable prompts for starting fresh sessions. Paste one into a new Hermes
session (leanecon-cto profile, cwd = /Users/bonorinoa/Desktop/leanecon_v4_work).
Each is self-contained: a new session has no memory, so everything needed
is either inline or in the read-first list.

State as of 2026-08-08: main @ 49d7d7c, tags v0.2.0/v0.3.0/v1.0.0,
pytest 168 green. hermessinho bot contributor ACTIVE. B2 spike complete.

---

## PROMPT A — Design the v1→v2 plan (planning session; NO implementation)

```
You are starting a fresh session on the LeanEcon v4 repository
(/Users/bonorinoa/Desktop/leanecon_v4_work). You have NO memory of prior
sessions — reconstruct context from the repo and the files below. Your job
is DESIGN ONLY: produce a v1→v2 plan for CTO approval. Do NOT implement,
do NOT commit, do NOT run live claims.

## Read first, in order
1. README.md (product thesis, v1 promise, explicit non-claims)
2. docs/releases/v1.0.0.md and docs/releases/v1-surface.md (what v1 froze)
3. docs/gate3/DECISION_LOG.md items 31–36 (AI reviewer, from-file, releases,
   surface freeze, hermessinho bot, v2 direction)
4. docs/gate3/08-reviewer-policy.md (human|ai reviewer rules)
5. docs/audit/post-v1-audit.md (P0/P1/P2 next-step findings)
6. spikes/001-bounded-search/README.md (B2 spike verdict — the evidence
   that shapes v2's proof-assist constraints)
7. docs/eval/formalizer-scorecard.md + interpreter-scorecard.md (model
   baselines — what the LLMs do today)
8. Skill: leanecon-verified-workflow (§2 walkthrough, §7 gate handoff
   pattern, §8 Core promotion)

## Locked context (do NOT reopen)
- v1 promise: a human or AI reviewer, via the supported CLI, turns an
  English claim into a kernel-checked VERIFIED bundle with auditable
  provenance; models are drafting aids.
- Reviewer may be human or AI (DECISION_LOG 31); CTO remains the
  accountable semantic authority.
- VERIFIED is bundle-gated (12 checks incl. 12_core_pin) and the kernel
  axiom audit (#print axioms / sorryAx) is the ONLY pass gate. A bare
  compile exit 0 is NOT a pass (spike evidence: apply?/simp fabricate
  sorry bodies).
- AI reviewer is AUTHORIZED but has NEVER been exercised — exercising it
  is v2's zero-cost first move.
- B2: no naive "compile → success" loop. Any proof assist must be
  audit-gated and bounded.
- Hermessinho (bot) pushes/PRs implementation work; CTO token handles
  protection merges. CODEOWNERS: bot + CTO; Core/ semantics CTO-only.
- Baseline: pytest 168 green; always scripts_local/a3_run.py for live A3.

## v2 promise statements (CTO-approved direction; sharpen, don't weaken)
Primary: "The model does the first 60–70% of the work on simple claims
(interpretation draft, formal statement draft with bounded kernel-feedback
revision, proof-skeleton draft); the reviewer does the last 30% and the
kernel axiom audit guarantees soundness. Nothing compiles-green without
the audit."
Non-claims (v2 does NOT promise): fully autonomous proving; unattended
VERIFIED; production SLA; agents/corpus/game-theory Core; any path that
bypasses the reviewer or the audit.

## Deliverable
A written v1→v2 plan (docs/v2/INIT_V2.md) containing:
1. Goal + sharpened promise statement + non-claims
2. Phased plan (2–4 phases), each with: deliverable, acceptance criteria,
   CTO gate, evidence expected
3. Phase 1 must start with: exercise the AI reviewer on fresh OOS claims
   (predictions first, CTO approves claim text, reviewer=hermes
   --reviewer-kind ai, spot-check agreement) — zero new code
4. Phase 2: kernel-feedback revision loop (bounded 2–3 attempts, audit-
   gated, TDD)
5. Phase 3 (optional): proof-skeleton drafting assist (have-chain drafts,
   reviewer refines, measure edit distance / time-to-VERIFIED)
6. Measurement plan: formalizer scorecard v2, interpreter churn,
   AI-review agreement rate, time-to-VERIFIED delta
7. Risks + explicitly NOT in v2
8. Attribution footer: Hermes Agent under CTO direction; CTO sole
   semantic approver.

Stop after writing the plan. Wait for CTO approval. An empty clarify
response is NOT consent — hold and restate options as plain text.
```

---

## PROMPT B — Execute the v1→v2 implementation (execution session)

```
You are starting a fresh session on the LeanEcon v4 repository
(/Users/bonorinoa/Desktop/leanecon_v4_work). You have NO memory of prior
sessions — reconstruct context from the repo. The v1→v2 design exists at
docs/v2/INIT_V2.md (CTO-approved). Your job is to EXECUTE it slice by
slice with TDD, evidence-first, stopping at each CTO gate.

## Read first, in order
1. docs/v2/INIT_V2.md (the approved plan — your mandate)
2. README.md + docs/releases/v1-runbook.md (the v1 constitution)
3. docs/gate3/08-reviewer-policy.md (AI reviewer rules)
4. spikes/001-bounded-search/README.md (why audit-gating is non-negotiable)
5. docs/gate3/DECISION_LOG.md items 31–36
6. Skill: leanecon-verified-workflow

## Standing rules (never break)
- scripts_local/a3_run.py is the ONLY live A3 entrypoint (stale install
  drops 12_core_pin / D2).
- Kernel axiom audit (#print axioms, sorryAx absent) is the ONLY pass
  gate. Compile exit 0 without the audit = NOT a pass. No exceptions.
- Reviewer owns final proof; AI reviewer allowed (reviewer_kind=ai) but
  never self-approves its own meaning without CTO authorization; CTO is
  accountable semantic authority.
- No ad-hoc store-inject as method (formalize --from-file exists).
- Prediction-first: write expectations BEFORE live runs, compare after.
- TDD: failing test first, watch it fail, minimal code, regression suite.
- Stop for CTO at: claim-text approval, after each phase's evidence
  packet, before any policy/DECISION_LOG change, before merging.
- Empty clarify = hold; restate options as plain text.
- Hermessinho pushes/PRs via scripts_local/open_pr.py --bot; merges via
  merge_pr.py + verify_protection.py (CTO token). Attribution footer on
  every doc.

## Phase 1 (this session's first deliverable)
Exercise the AI reviewer end-to-end on 2 fresh OOS claims:
1. Draft 2 claim texts (simple consumer/equilibrium class) + write
   predictions (artifacts/local/v2-p1-expectations.md)
2. CTO approves claim texts (semantic authority) BEFORE ingest
3. Run the full walkthrough with --reviewer hermes --reviewer-kind ai for
   review / gap-ack / axiom-approve
4. CTO spot-checks the AI reviews; record agreement
5. Evidence packet: expectations-vs-actual table, bundle + replay outputs,
   pytest green, scorecard update
6. Stop for CTO verdict before Phase 2.

Then proceed to Phase 2 (kernel-feedback revision loop) and Phase 3
(proof-skeleton assist) per INIT_V2.md, same discipline.
```

---

## PROMPT C — Short continuation (same session, next slice)

```
Continue the LeanEcon v1→v2 execution per docs/v2/INIT_V2.md.
Current state: [CTO fills in: phase done / verdict]. Run the next planned
slice with the standing rules from PROMPT B (audit-gated, prediction-
first, CTO gates, a3_run.py only). Evidence packet before any merge.
```

**Attribution:** prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the accountable semantic authority and sole
semantic approver.
