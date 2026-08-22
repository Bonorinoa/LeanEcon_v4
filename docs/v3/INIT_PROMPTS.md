# LeanEcon v2→v3 — session initialization prompts

Paste one into a **new** Hermes session (profile `leanecon-cto`,
cwd = `/Users/bonorinoa/Desktop/leanecon_v4_work`). A new session has
no memory: everything needed is inline or in the read-first list.

State as of 2026-08-12: `main` @ `9c12936`, tag `v2.0.0` Phoenix,
package `2.0.0`, pytest 176, remote main-only. hermessinho bot ACTIVE.
Suggested packet: `docs/v3/INIT_V3.md` + `docs/v3/METRICS.md` (not
approved).

**For a strong MoA / high-horsepower model:** use Prompt B, and do not
weaken the Phase 0 hard-stop. Horsepower without a metric contract
will implement the wrong thing quickly.

---

## PROMPT A — Polish only (no implementation)

```
You are starting a fresh session on LeanEcon v4
(/Users/bonorinoa/Desktop/leanecon_v4_work), profile leanecon-cto.
You have NO memory of prior sessions. Reconstruct from the repo.

JOB: polish the suggested v2→v3 roadmap into a plan the CTO can
approve. DESIGN ONLY. Do NOT implement, do NOT commit, do NOT run
live claims, do NOT open a UI, do NOT add Core declarations.

## Read first, in order
1. README.md (v2 Phoenix promise + non-claims)
2. docs/releases/v2.0.0.md + docs/releases/v2-surface.md
3. docs/gate3/DECISION_LOG.md items 31–40 (esp. 40 = v3 direction)
4. docs/v3/INIT_V3.md (SUGGESTED roadmap — your raw material)
5. docs/v3/METRICS.md (eval honesty — your metric raw material)
6. docs/eval/formalizer-scorecard.md + interpreter-scorecard.md + v1-claim-set.md
7. spikes/001-bounded-search/README.md (compile ≠ pass)
8. Skill: leanecon-verified-workflow (§2 walkthrough, §4 pitfalls,
   §7 handoff, library ≠ product)

## Locked (do NOT reopen)
- Reviewer (human|ai) + kernel axiom audit are non-bypassable.
- VERIFIED is 12-check bundle-gated. Bare lake exit 0 is not a pass.
- revise_loop and skeleton are libraries until wired; do not claim
  they are the live formalize path until a3_runner imports them.
- Models run live (mistral-medium-3-5 interpret, labs-leanstral-1-5
  formalize); --from-file is recovery; formalizer 0% sole-author.
- No agents, corpus, Nash Core, product UI, embeddings-as-product.
- Empty clarify ≠ consent. Stop at the gate.

## Deliverable
Rewrite (in place, still uncommitted until the CTO says commit):
- docs/v3/INIT_V3.md — status still PROPOSED until CTO approves
- docs/v3/METRICS.md — operational 60–70% definition + scorer contract
- a one-page docs/v3/PLAN.md: phases, in/out, files likely touched,
  stop points, Definition of Ready/Done

Then STOP. Present the diffs as a review packet. Do not implement
Phase 1.

Attribution footer on every file: Hermes under CTO direction; CTO
sole semantic approver.
```

---

## PROMPT B — Polish, then implement Phase 1 after the CTO gate (recommended for MoA)

```
You are starting a fresh session on LeanEcon v4
(/Users/bonorinoa/Desktop/leanecon_v4_work), profile leanecon-cto.
You have NO memory of prior sessions. Reconstruct from the repo.
You are a strong model; that is not permission to skip gates.

JOB (two stages, hard stop between them):
  STAGE 0 — polish the suggested v3 roadmap (docs only).
  STOP and wait for an explicit CTO approval of Stage 0
  (“approve as proposed” / “proceed as proposed” / a written
  amend-then-go). Empty clarify ≠ consent. Do not start Stage 1
  because the plan “looks done.”
  STAGE 1 — only after that approval: implement Phase 1 as locked
  in the polished INIT_V3 (default suggestion: wire revise_loop
  into live formalize). TDD. Predictions before any live run.

## Read first, in order
1. README.md
2. docs/releases/v2.0.0.md + v2-surface.md
3. docs/gate3/DECISION_LOG.md items 31–40
4. docs/gate3/08-reviewer-policy.md
5. docs/v3/INIT_V3.md + docs/v3/METRICS.md + docs/v3/INIT_PROMPTS.md
6. docs/eval/formalizer-scorecard.md + interpreter-scorecard.md + v1-claim-set.md
7. src/leanecon/revise_loop.py + tests/test_revise_loop.py
   + src/leanecon/a3_runner.py (confirm revise_loop is NOT imported)
8. spikes/001-bounded-search/README.md
9. Skill: leanecon-verified-workflow (especially §4 F1 lifecycle,
   library ≠ product, a3_run.py only, merge_pr.py clear-checks)

## Locked
- Same locks as Prompt A.
- Always .venv/bin/python scripts_local/a3_run.py for live A3.
- New failure paths update lifecycle.TRANSITIONS in the SAME change.
- hermessinho (--bot) for push/PR; CTO token for merge. Do not merge
  without explicit CTO authorization.
- Baseline: pytest 176 green on v2.0.0; do not regress.

## Stage 0 deliverable
Polished INIT_V3 + METRICS + docs/v3/PLAN.md. Then STOP.

## Stage 1 (only if approved) — default slice if the polished plan
keeps Phase 1 as “wire the loop”
- Red tests first for: contamination still fails; budget cap;
  attempt-2 success records attempts=2.
- Minimal wiring: a3_runner live formalize calls revise_loop;
  attempt log on the formal artifact; exhausted budget → FAILED
  → existing --from-file.
- No new CLI subcommands unless the polished plan says so.
- No skeleton CLI, no IR, no Core, no UI.
- Predictions file BEFORE any live re-run.
- Evidence: pytest green, import exists, scorecard/scorer updated
  honestly (0% sole-author unless a model proof actually verified).

## Out of scope even after approval
Agents, corpus, Nash Core, embeddings, product UI, v3.0.0 tag,
weakening the audit gate.

Attribution on every tracked file. CTO remains sole semantic approver.
```

---

## PROMPT C — Continue a v3 sprint already in flight

```
You are continuing LeanEcon v4 v3 work
(/Users/bonorinoa/Desktop/leanecon_v4_work), profile leanecon-cto.
Reconstruct from the repo; do not trust chat memory.

## Read first
1. git status -sb && git log -5 --oneline --decorate && git describe
2. docs/v3/INIT_V3.md (check Status: SUGGESTED vs APPROVED)
3. docs/v3/PLAN.md and docs/v3/METRICS.md
4. docs/gate3/DECISION_LOG.md tail (items ≥ 40)
5. Current branch / open PRs via the GitHub API (not just the worktree)
6. Skill: leanecon-verified-workflow

## Rules
- If INIT_V3 is still SUGGESTED, you are in Stage 0: docs only.
- If Stage 1 was authorized, implement only the locked slice.
- Predictions before live runs. a3_run.py only. F1 rule. No merge
  without explicit CTO authorization.
- Report: main SHA · phase · in-scope · out-of-scope · top risk
  (≤5 lines), then the next Ready item.

Do not reopen locked decisions. Do not tag v3.0.0.
```

---

**Attribution:** Hermes Agent (Nous Research) under CTO direction;
CTO remains the sole semantic approver.
