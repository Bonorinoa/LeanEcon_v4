# Progress audit — 2026-08-12 (post-break stand)

CTO asked: progress since v3 migration, stand vs stated
objectives, and whether any application merits UI/UX now.
Repo-first audit (not chat memory). Worktree:
`/Users/bonorinoa/Desktop/leanecon_v4_work`.

## Four-layer stand (always report separately)

| Layer | 2026-08-12 fact |
|---|---|
| `origin/main` | `18beaa9` (PR #15 Phase 2 merge). Package **1.0.0**. Tags `v0.2.0`/`v0.3.0`/`v1.0.0` only. DECISION_LOG on main ends at item **36**. README on main has **no** v2-in-progress row. INIT_V2 on main still reads `PROPOSED`. |
| Open PRs | **#16** open, mergeable, last update 2026-08-09 — skeleton contract + post-merge truth-surface (DECLOG 37–38, INIT_V2 “SHIPPED”, README v2 row). |
| Local checkout | Was on dirty `v2/phase3-skeleton` @ `040f38c`, **not** main. |
| Uncommitted | `docs/releases/v2.0.0.md`, `v2-surface.md`, scorecard v2 edits, `spikes/`, clean-clone audit, bot-prep drafts. **No v2.0.0 tag.** |

Do **not** quote INIT_V2 / README / DECISION_LOG from the working branch as if they describe `origin/main`. On 2026-08-12 the branch INIT_V2 header said “Phase 3 contract slice merged (PR #16)” while #16 was still open.

## Earned vs promised

| Promise | Status |
|---|---|
| v1 HITL verified workflow | **Earned** (PR #13). 11 local VERIFIED claims (c1–c4, fwt1, oos1–2, v2p1-A/B/C); oos3 FORMALIZED (Nash, outside Core); c1r2 FAILED (formalizer retest). |
| v2 “model drafts 60–70%” | **Not earned.** Formalizer live 0/3 first-try on v2p1 (6/6 static reject). `revise_loop` is on main as a **library** — `a3_runner` does not import it. `skeleton` lives only on #16; never run live; edit-distance / time-to-VERIFIED deferred. 0% sole-author of VERIFIED. |
| v2.0.0 tag | Packet drafted, uncommitted. Tagging now would overclaim. |

Core freeze unchanged: 9 decls + 3 theorem boundaries (P2 + G7).

## UI/UX verdict (CTO question, 2026-08-12)

**No product UI.** The only evidenced application is CTO + Hermes at the CLI walking simple consumer/CE claims to audited bundles. Bottleneck is formalizer fidelity + Lean proof authorship, not discoverability. A reviewer console would not unlock a new user or claim class.

Later maybe (not now): a **read-only bundle viewer** for already-VERIFIED exhibits (FWT, IR-at-CE) after v2 is honestly tagged or the promise is narrowed. Not a workflow UI. Not an API-as-a-service revival of v3.

v3 identity (“auto-formalizer and verifiable API”) was **not** rebuilt. Ledger: API/planner/prover = REBUILD, not started.

## Resume options left on the table (empty reply ≠ consent)

1. Merge PR #16 (skeleton + truth-surface gap).
2. Do **not** tag v2.0.0 unless the promise is rewritten down to “AI reviewer exercised + library harnesses.”
3. Track `spikes/001-bounded-search/` with the next docs PR.
4. Optional Phase 4.x: actually measure edit-distance / time-to-VERIFIED.

**Attribution:** Hermes under CTO direction; CTO sole semantic approver.
