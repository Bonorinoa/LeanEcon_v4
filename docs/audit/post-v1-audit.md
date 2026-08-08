# LeanEcon v4 Post-v1.0.0 Audit Report
**Date:** 2026-08-08 (post-ship)  
**Auditor:** Independent subagent (Hermes, leanecon-cto profile)  
**Scope:** Code, docs, Core, tests, governance — evidence-based, focused on post-v1 drift/outdated items.  
**Repo state at audit:** main @ bf177e4 (v1.0.0 merge), tags v0.2.0/v0.3.0/v1.0.0, 168 pytest green.

## Executive Summary
v1.0.0 shipped cleanly (PR #13, 2026-08-08) with supported HITL verified workflow, AI reviewer, `--from-file` recovery, eval skeleton, and surface freeze. State is solid: tests pass, Core builds, lifecycle/D1/D2/D4 contracts hold, bundles include `12_core_pin`. No critical breakage.

**Key outdated post-v1 items identified:**
- Gate 8 INIT brief remains active but is explicitly superseded historical context.
- DECISION_LOG item 35 (second GitHub approver) still open (governance hygiene).
- Cold clean-clone full walkthrough deferred (reproducibility risk).
- Pre-v1 references and comments in scattered docs/code not yet pruned.
- Post-v1 backlog (B2, Core minors) not yet scoped.

No evidence of semantic drift, broken invariants, or test failures. Package version, README, releases/*, and DECISION_LOG are truthful.

## Evidence Inventory (current state)
- **Code (src/leanecon/ + lean_workspace/LeanEcon/):** 
  - Python: a3_runner.py, lifecycle.py, bundle.py (12 checks incl. 12_core_pin), formalization.py (D1/D4), lean_probe.py (D2), reviewer_policy.py (human|ai). All use scripts_local/a3_run.py entrypoint.
  - Lean Core: 7 modules (Primitives, Preferences, Constraints, Choice, Utility, Equilibrium, Theorems); P2 + Gate 7 batch promoted (9 decls + 3 theorem boundaries). Builds cleanly (`lake build LeanEcon.Core.Primitives`).
  - A1.lean: workspace probe only.
- **Docs:** README.md (v1 promise + explicit non-claims accurate), ENGINEERING_LOG.md (ends at v1 ship), docs/releases/v1.0.0.md + v1-runbook.md + v1-surface.md (complete), docs/gate3/DECISION_LOG.md (items 1–35, 31–34 locked/shipped).
- **Tests:** 168/168 passed (34.89s) via .venv/bin/python -m pytest; includes bundle validation, lifecycle transitions, probe tests, replay_ok fixtures. `@requires_workspace` tests exercised real lake env.
- **Governance:** DECISION_LOG 31–35 cover AI reviewer, --from-file, releases, surface freeze, approver. CTO remains accountable semantic authority. Release process followed (annotated tags + evidence packets).
- **Artifacts:** artifacts/local/a3/ (gitignored, OOS runs), tests/fixtures/lean/ (committed walkthrough proofs), references/ (limited; v1-ship details in releases/).

**Verification commands executed:**
- `git status`, `git tag`, `git log --oneline -10`
- `python -m pytest -q` (via project .venv)
- `lake build LeanEcon.Core.*` (in lean_workspace)
- File reads: README, pyproject.toml (v=1.0.0), ENGINEERING_LOG, DECISION_LOG tail, v1.0.0.md, Core/*.lean, gate8/INIT_GATE8.md, core-glossary-detail.md
- Grep for TODO/FIXME/Gate 8/v0.1

## Outdated Items (post-v1 ship focus)
1. **docs/gate8/INIT_GATE8.md** (high visibility): Still present as active file; content states "deferred to a new session" and "Gate 8 does not start from 'build agents'". Superseded by v1 ship outcomes (references/v1-ship-2026-08-08.md per skill, releases/v1.0.0.md). Cross-refs in 25+ places. Risk: new operators may treat as current plan.
2. **DECISION_LOG item 35**: "Second GitHub approver — Still open; interim single-maintainer + required CI". Governance risk for future PRs (self-approval impossible without second account; interim procedures documented but not ideal long-term).
3. **Cold clean-clone walkthrough**: Deferred in v1.0.0.md exit criteria. P5 pattern + clean_clone_check.sh exist, but no evidence of recent execution in this env post-ship. Reproducibility risk (env drift, lake cache, Mathlib tail OOM).
4. **Scattered pre-v1 / Gate 8 prose**: 
   - Code comments (e.g., test_a3_runner.py: "# v0.2: formalize --from-file")
   - docs/gate3/ references to Gate 8 phases.
   - ENGINEERING_LOG has accurate v1 section but older Gate 5/6 entries could be summarized.
5. **Post-v1 backlog not actioned**: B2 (bounded proof) thin optional; Core family minors; agents/corpus/Nash parked. No new files or scoping docs yet.
6. **README table**: Accurately lists v1 shipped but could add explicit "Post-v1 status" row or link to this audit.
7. **.hermes/ in repo root**: Untracked (from profile session); should remain gitignored or moved.

No other drift found (no version skew in pyproject, no broken imports, no stale schemas, Core registry matches promotions up to v1.0.0 with some core-candidate entries expected).

## Suggested Next Steps (prioritized by impact × risk)
**P0 (High impact, High risk — address immediately):**
- Resolve item 35: Provision second GitHub account or adopt org-level CODEOWNERS + branch protection update. Update DECISION_LOG with resolution. (Prevents merge-gate friction; aligns with Gate 2 intent.)
- Archive/mark Gate 8 INIT: Move to `docs/gate8/historical/` or add prominent "SUPERSEDED — see v1.0.0.md and references/v1-ship-2026-08-08.md" header + update cross-refs. Prevents operator confusion.

**P1 (High impact, Medium risk):**
- Execute cold clean-clone walkthrough (use `scripts_local/clean_clone_check.sh` or P5 recipe). Record in `docs/audit/clean-clone-2026-08-08.md`. Mitigates env-specific assumptions.
- Prune/update pre-v1 comments: Batch edit code/tests for v0.2/v0.3 references; add "post-v1" note to gate8/INIT if kept. Low effort, high hygiene.

**P2 (Medium impact, Low-Medium risk):**
- Scope B2 thin optional prototype (if CTO opts in): bounded proof search with hard budgets; start with sandbox toy per skill. Park otherwise.
- Core family minors: Review glossary for next batch (e.g., expand Equilibrium or add D3 collision candidates); follow Gate 6 P2–P5 workflow only on CTO slice approval.
- Add post-v1 section to README.md and ENGINEERING_LOG.md (link this audit); optional `docs/releases/v1.1.0.md` stub if minor bump needed.

**P3 (Low impact, Low risk):**
- Update skill `leanecon-verified-workflow` if any new pitfalls discovered during audit (none found).
- Verify remote tags/PR status via `gh` (if GitHub token present); confirm v1.0.0 on origin.
- Optional: Add `docs/audit/` index or integrate into release process.

**Out of scope (per v1 non-claims):** Full agents, corpus, autonomous formalizer, production SLA, broad library.

## Recommendations
- **Truth surfaces first:** After any post-v1 work, update DECISION_LOG + releases/* + README before code/docs changes.
- **Evidence-first:** For next gate/slice, write prediction file + expectations.md before runs (as in fwt1/oos batch).
- **Reproducibility:** Prioritize clean-clone before any env-dependent claims.
- **Governance:** Treat item 35 as blocking for v2+ release train.

**Files created/modified during audit:**
- Created: `docs/audit/post-v1-audit.md` (this report)
- No other modifications (read-only audit; no patches applied).

**Issues encountered:** None blocking. Pytest required project .venv (hermes venv lacks deps); lake requires lean_workspace cwd. All resolved via explicit paths.

**Overall grade:** v1 state is production-ready for supported workflow. Audit confidence: high (full test run, live builds, primary sources read). No invented claims — all backed by tool output and file contents.

Next action for CTO: Approve P0 items or provide slice for P2.
