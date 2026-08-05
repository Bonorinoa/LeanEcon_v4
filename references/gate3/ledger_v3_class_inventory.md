# Frozen v3 Class Inventory

Read-only inventory source: tag `v3-freeze-20260804`, commit `3765578eab460f9de189e40fe9b9d33ccf197baa`.

Observed top-level tracked classes: `.codebase-memory` (3 entries), `.github` (2 workflow entries), `lean_workspace` (65 entries), `src` (75 entries), `tests` (25 entries), `docs` (15 entries), `benchmark_baselines` (22 entries), `evals` (23 entries), plus Docker, deployment, configuration, skills, and repository metadata. Counts are inventory context, not migration quantities.

Representative evidence paths were inspected with `git ls-tree` only. The ledger intentionally records classes and paths, not copied implementation or hidden artifact content. `.codebase-memory` is explicitly historical-discard.
