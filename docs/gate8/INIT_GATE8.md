# Gate 8 — Init brief (deferred to a new session)

> Status: **SUPERSEDED by v1.0.0 ship (2026-08-08).** Primary slice
> (`formalize --from-file`), AI reviewer policy, eval skeleton, and release
> packets landed on the v1 ship train (DECISION_LOG 31–34). Retain this
> brief as historical handoff context; do not re-open Gate 8 as a separate
> feature gate unless CTO re-authorizes post-v1 work.
>
> Authority: Gate 6 CLOSED (DECISION_LOG 25); Gate 7 equilibrium batch
> APPROVED+MERGED (DECISION_LOG 26–27, PR #11); OOS batch report
> `docs/gate7/OOS_BATCH_REPORT.md`; P5 open items 2–4 still open.

## 0. Read first (in order)

1. This brief (§1–§5)
2. `docs/gate7/OOS_BATCH_REPORT.md` — whole-system evaluation; findings F1–F5
3. `docs/gate7/G7_REVIEW_BATCH.md` — what Core now contains (equilibrium family)
4. `docs/gate6/P5_EXIT_PACKAGE.md` §5 — carried-forward open items
5. `docs/gate3/DECISION_LOG.md` items 15–27
6. Skill `leanecon-verified-workflow` (§2 walkthrough, §4 pitfalls, §8 Core)

## 1. What is true on `main` when Gate 8 opens

| Fact | Evidence |
|---|---|
| Core has **9 promoted declarations** + **3 theorem boundaries** | P2 (6+2) + G7 (4+1 FWT); modules under `lean_workspace/LeanEcon/Core/` |
| A3 contracts D1/D2/D4 live | P4 PR #10; OOS confirmed D1 (oos3) + D2 `12_core_pin` (oos1/oos2) |
| Pipeline is single-claim sequential — **not** multi-agent | OOS report §1; no retrieval/corpus/subagents/decomposition in `src/` |
| Formalizer is a drafting aid only | oos1 vacuous True; oos2 2× `:=`; oos3 2× D1; fwt1 structural inversion |
| Immediate F1 lifecycle fix (if cleanup PR merged) | `ACCEPTED→FAILED`, `FAILED→FAILED`, `BLOCKED→FAILED` legal; oos2 replay green |

**Baseline:** pytest 156 + F1 tests (expect 157+); main-only branches; use
`scripts_local/a3_run.py` for **all** A3 CLI (PYTHONPATH=src + credential).

## 2. Locked decisions — do not reopen

- Reviewer-in-the-loop; kernel arbitrates; models draft only
- No v3 import/adapt; Core promotion = 7 criteria + CTO per declaration
- EI schema frozen 1.0.0; glossary registry v1 (status moves ≠ version bump)
- No production `VERIFIED` marketing without bundle validator + Core pin
- Gate 8 does **not** start from "build agents" — product is a verified claim pipeline

## 3. Proposed Gate 8 scope (pick a slice; do not boil the ocean)

### 3.1 Recommended primary slice — **Reviewer recovery + pipeline completeness**

| Item | Why | Acceptance |
|---|---|---|
| **`formalize --from-file`** (or equivalent) | OOS F5: oos2/oos3 needed ad-hoc store inject after model block; no first-class path | CLI accepts reviewer statement + mapping report JSON; validates D1/D4; writes formal rev; emits legal transitions; tests |
| Lifecycle/replay regression lock | F1 fixed immediately; Gate 8 adds end-to-end mocked test that ACCEPTED→FAILED→…→VERIFIED replays clean | `replay_ok` on fixture trace |
| Ops: document `a3_run.py` as the only supported live entrypoint | F2 stale install dropped D2 | skill + README/runbook note; optional console-script warning when site-packages ≠ src digest |

### 3.2 Secondary slice (only if primary done) — **B2 proof loop (thin)**

| Item | Why | Non-goals |
|---|---|---|
| Wire `Capability.PROVE_OR_REPAIR` as optional assist | Contract exists; unused | Fully autonomous proving; hiding reviewer ownership |
| Bounded repair attempts + always surface kernel errors | Honest failure | Silent fallback between models |

### 3.3 Explicitly out of Gate 8 unless CTO opts in

| Item | Reason to defer |
|---|---|
| Multi-agent orchestration / subagents / claim decomposition | OOS did not fail for lack of agents |
| Corpus + smart retrieval + embeddings | No multi-claim reuse pressure yet; zero code today |
| Game-theory / Nash Core declarations | oos3 extension signal only — needs promotion criteria + claims first |
| Production public VERIFIED corpus | Needs recovery path + ops hardened first |
| P4 leftovers: D3 CI grep, verify-side scaffolding soft signal, `none` kind removal | Optional tooling; not load-bearing |

## 4. Suggested Gate 8 phases

| Phase | Deliverable | CTO gate |
|---|---|---|
| G8.0 | Re-read this brief + OOS report; confirm slice | approve slice |
| G8.1 | `formalize --from-file` + tests + runbook | approve code |
| G8.2 | Optional thin B2 assist (if authorized) | approve design then code |
| G8.3 | One OOS replay (oos2-class) end-to-end on recovery path | evidence packet |
| G8.4 | Exit notes + DECISION_LOG | close or carry forward |

## 5. Process notes for the new session

- Worktree: expect `main` after cleanup PR merge; `git status` clean; pytest green
- Skills: `leanecon-verified-workflow`, `python-packaging`
- scripts_local: `a3_run.py`, `open_pr.py`, `check_pr_ci.py`, `merge_pr.py <PR> clear-checks`, `verify_protection.py`, `push_main.py`
- **Never** `python -m leanecon.a3_runner` alone for live/ops after src edits — use `a3_run.py` or reinstall
- Prediction-first on any live claim run
- Stop for CTO at each deliverable; empty clarify ≠ consent
- Attribution footer on every doc

## 6. Discussion prompts for CTO (open Gate 8 with answers)

1. Is **G8.1 reviewer formal-from-file** the right primary slice, or should Gate 8 jump to **B2** / **corpus**?
2. Any **domain** priority for the next Core vocabulary (still micro/consumer, or open game theory from oos3)?
3. Should production **VERIFIED** claims be a Gate 8 exit criterion or a later gate?
4. Keep **main-only** branch hygiene and PR flow unchanged?

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This brief
authorizes nothing; Gate 8 begins only after the new session's CTO gate.
