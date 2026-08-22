# Phase 4 — decomposition (SKIPPED)

**Decision:** skip to release review. No runner change.

INIT_V3 Phase 4 requires a **2-subgoal toy compiled in the pinned
workspace** before any lifecycle change. Parent `VERIFIED` only if every
child is `VERIFIED` plus a composition proof.

That is a new claim-family (multi-claim), not earned by Phases 1–3:

| Gate | Status |
|---|---|
| Phase 1 loop | live; first_try_valid **1/3** |
| Phase 2 scorer | fixtures + CI; held-out **empty** |
| Phase 3 skeleton | CLI + verify gate; live measurement **halted** |
| 60–70% | **not met** (illegal without held-out) |

Adding parent/child claim state without a compiled toy would be
architecture theatre (Krakauer). Out: graphs, embeddings, retrieval,
parallel agents — unchanged.

**Resume:** sandbox-toy in `lean_workspace/.a3-candidates/` first, then
a separate CTO gate.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
