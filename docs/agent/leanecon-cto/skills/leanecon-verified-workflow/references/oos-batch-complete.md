# OOS batch complete outcomes (2026-08-08)

Companion to `references/oos-batch-2026-08-08.md` (procedure) — this file
holds **final** results + F1–F5. CTO report: `docs/gate7/OOS_BATCH_REPORT.md`.
F1 landed PR #12 (`5f720f8`). F5 + Gate 8 primary resolved in **v1.0.0**
(PR #13 / `bf177e4`) — see `references/v1-ship-2026-08-08.md`. Gate 8 INIT
is superseded historical context.

## Final outcomes

| Claim | Endpoint | Bundle | Formalizer | Notes |
|---|---|---|---|---|
| oos1 IR at CE | **VERIFIED** | `bundle-oos1-r1-478aeb` 12/12 + **12_core_pin** | vacuous True hyps, 0 core rows | Reviewer proof; Core imports; replay ✅ |
| oos2 budget expand | **VERIFIED** | `bundle-oos2-r1-6c1bee` 12/12 + **12_core_pin** | 2× `:=` no artifact | Reviewer formal inject; Nonempty+DecidableEq Goods; replay ✅ after F1 |
| oos3 mixed Nash | **FORMALIZED** | none | 2× D1 reject | zero core rows; proof out of slice |

## Ops rules (learned live)

1. **Always `scripts_local/a3_run.py` for verify/bundle/replay/status** (not
   only interpret/formalize). Bare `python -m leanecon.a3_runner` can use a
   stale wheel and emit VERIFIED bundles **without** `core_imports` /
   `core_revision` / check 12 (oos1 first bundle `…1ae62e`).
2. After Core-importing VERIFIED, open `manifest.json` and confirm
   `dependency_audit.core_imports` + `workspace_identity.core_revision`.
3. If formalize leaves `formal_rev=None` after 2 identical static rejects:
   **`scripts_local/a3_run.py formalize --from-file candidate.json`**
   (v1.0.0; same D1/D4/static contracts; provenance
   `reviewer_authored_formal`). Do **not** ad-hoc store-inject.
4. Predictions-first: `artifacts/local/<batch>-expectations.md` before ingest.
5. When the runner emits a new failure edge, **add it to
   `lifecycle.TRANSITIONS` in the same change** or replay will fail (F1).

## Findings F1–F5

| Id | Finding | Status |
|---|---|---|
| **F1** | `ACCEPTED→FAILED` / `FAILED→FAILED` / `BLOCKED→FAILED` missing from TRANSITIONS → replay_ok=false after static formalize reject | **FIXED** PR #12 + `test_formalize_static_rejection_edges_are_legal`; oos2 replay_ok |
| **F2** | Stale install drops D2 — always a3_run.py or reinstall | ops rule (standing) |
| **F3** | Formalizer still drafting-only: vacuity / `:=` / D1 mislabel (oos1–3). D1 earned keep on oos3 | known |
| **F4** | Interpreter misses `[Nonempty Goods]` + `[DecidableEq Goods]` for strict budget expansion (parallel fwt1 Nonempty Agent) | proof authoring |
| **F5** | No CLI for reviewer formal when model never stores artifact | **RESOLVED v1.0.0 PR #13** — `formalize --from-file`; see `v1-ship-2026-08-08.md` |

## Extension stance

Do **not** open post-v1 work on agents/subagents/retrieval/corpus first.
OOS failed on formalizer compliance, lifecycle table completeness (F1,
fixed), and missing reviewer-formal CLI (F5, fixed in v1) — not missing
orchestration. Post-v1: optional thin B2; domain Core only with promotion
criteria; AI reviewer authorized under DECISION_LOG 31.

**Attribution:** Hermes Agent under CTO direction; CTO accountable semantic
authority (AI reviewers authorized DECISION_LOG 31).
