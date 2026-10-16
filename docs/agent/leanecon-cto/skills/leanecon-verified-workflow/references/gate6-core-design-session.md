# Gate 6 Core design session — 2026-08-06 (consumer side of the handoff)

Context: Gate 6 (LeanEcon Core design) initialized from
`docs/gate6/INIT_GATE6.md` in a fresh session; test baseline 137 green on
`main @ 7921e7b` (the INIT's `14b2f0e` was superseded by PR #6 — always
re-check `git log` rather than trusting the INIT's recorded sha).

## What was produced (v4 worktree, untracked — design only, no commits)

- `docs/gate6/a3-core-design.md` — the design (411 lines): vocabulary
  scope + namespace skeleton, glossary seed, canonical element-id scheme,
  mapping-report target contract, schema-freeze proposal, v3
  dispositions, promotion criteria, open questions.
- `docs/gate6/references/core-glossary-detail.md` — 20-term glossary with
  Lean signature sketches + ontology-record template (242 lines).
- `docs/gate6/references/schema-freeze-proposal.md` — exact freeze record
  (92 lines).

## Live-evidence paths used (artifact -> design input)

| Artifact | Location | What it feeds |
|---|---|---|
| Accepted EI | `artifacts/local/a3/eis/<claim>/rev-2.json` | glossary seed, element ids, ambiguities/decisions, ontology_refs |
| Mapping report | `artifacts/local/a3/formal/<claim>/rev-1.json` | id-scheme deviations (`object:u`, titles), mapping-kind usage, gap classes |
| Gap-ack record | `artifacts/local/a3/reviews/<claim>/gap-1.json` | record shape: `acknowledged_gap_ids`, `formal_rev`, `kind: gap`, `notes`, `reviewer`, `event_ref` |
| Reviewer proof fixtures | `tests/fixtures/lean/c{1..4}_*.lean` | the load-bearing statements; target theorem names `leanecon_c{1..4}_*`; what Core identifiers must serve |

## Canonical element-id scheme (Gate 6 made it normative for mapping reports)

`claim` | `<object id verbatim>` | `assumption:<i>` | `definition:<i>` |
`quantifier:<i>` | `conclusion` | `solution_concept`

- Ids used verbatim from the accepted EI; `object:u`-style or title ids =
  `id_scheme_deviation` gap class (Gate 5 hardening), NOT missing rows.
- Assumption/definition/quantifier indices fixed at EI creation; a
  reviewer proposed->accepted move preserves the id (move = event, not
  renumbering).
- Completeness: every material element gets exactly one row; unmapped
  material rows block PROVING until reviewer gap-ack.

## Mapping-kind target contract (post-Core)

`mathlib` | `core` (NEW) | `glossary_term` | `local_definition`; status
`mapped | unmapped | deferred` (deferred only for expository items).

- `core` = a promoted `LeanEcon.Core.*` declaration — what the EI's
  `ontology_refs` point AT; strongest evidence a reviewer can get.
- `glossary_term` = reviewed meaning with NO Lean declaration yet
  (interim, carries promotion plan or deferral).
- `local_definition` = A3-local scaffolding (MVP only, never promoted
  without the Gate 6 process).
- Proposed drop of `mapping_kind: none` (seen on `solution_concept`
  rows): unmapped = status only, empty `lean_identifier`. OPEN Q2.

## Glossary seed rules (proven pattern)

Seed ONLY from reviewed artifacts (accepted EIs, CTO-approved claims,
mapping reports). Status ladder: `glossary-only` -> `core-candidate` ->
`core`; mathlib terms referenced, never duplicated. Collapse near-synonyms
to one canonical entry and record aliases (e.g. `monotone_nondecreasing` /
`order_preservation`; `weak_preference` / `preference_relation`). Entries
that carry review decisions (`attainableSet` reading chosen at c1 review;
`strictlyIncreasingUtility` componentwise reading at c3) prove the
glossary records meanings, not names. c1-c4 exercise 20 distinct terms:
7 core-candidates, 8 mathlib, 5 glossary-only.

## Schema-freeze proposal (summary)

Freeze the exercised draft AS-IS at `1.0.0`: `none_noted`,
nullable `review.reviewer`/`review.event_ref` while PENDING,
`review.acknowledges_none_noted` — all live-tested at Gate 5 (four EIs
exercised the nullable fields; `none_noted` enforcement gate
test-verified, no live hit). Mechanics: CTO approval + DECISION_LOG entry
+ `$comment` freeze note in the file (draft 2020-12 allows `$comment`);
file stays at `references/gate3/ei_schema_draft.json` (no relocation
churn). Versioning: additive optional = minor; meaning/requiredness
changes = major, new `$id`. Rationale for 1.0.0 over 1.1.0: no released
consumers, no prior frozen version (OPEN Q4).

## Open questions pending CTO approval (design §8)

1. Bundle family: `Goods -> ℝ` with `[Fintype Goods]` vs `Fin n -> ℝ` vs
   per-claim `ℝ` (c1 fixture uses `ℝ` directly).
2. Drop `mapping_kind: none`? (proposed: yes)
3. Assumption id stability across proposed->accepted moves (proposed:
   preserve index).
4. Freeze at 1.0.0 vs 1.1.0 (proposed: 1.0.0).
5. Initial slice = strictly the four claims' vocabulary (demand/
   equilibrium deferred to Gate 7).
6. Glossary registry location = `docs/gate6/references/core-glossary-detail.md`.
7. Schema file location on freeze (proposed: keep + `$comment`).

## v3 dispositions (Core material; all rebuild/inspiration/historical)

- `lean_workspace/LeanEcon/Preamble/**` -> **rebuild** (scope taxonomy
  -> inspiration for the v4 namespace skeleton).
- `src/preamble_library.py` -> **rebuild** (concept -> inspiration for
  the ontology record).
- `benchmark_baselines/v3_alpha/tier1_core.json` +
  `evals/claim_sets/tier1_core_preamble_definable.jsonl` ->
  **historical-discard** (theorem stubs are gold-shaped; contamination
  rule: no benchmark gold enters Core). `theorem_stub` shape inspired the
  reviewed-fixture format (already independently re-authored at Gate 5).
- UUID-named scratch `.lean` files -> **historical-discard**.

## v3 clone cleanup record (CTO-approved 2026-08-06)

v3 frozen clone is now **source-only** (16G -> 44M). Deleted:
`lean_workspace/.lake` (12G), `.cache/uv` (3.4G), `.cache/lean_interact`
(170M), `.venv` (629M), `.pytest_cache`/`.ruff_cache`/`.coverage`.
Shared caches cleared on CTO choice: `~/.cache/uv` (4.7G),
`~/.cache/mathlib` (1.2G) — re-download on next use. KEPT: `~/.elan`
(5.9G — v4's lake builds depend on it; never delete), v4's own
`lean_workspace/.lake` (7.3G), and ALL v3 evidence (migration plan under
`.hermes/plans/`, `benchmark_baselines/`, docs, `.git`, `.env`,
`.codebase-memory`).

Safe-cleanup pattern for the frozen clone (reusable): (1) confirm every
target is gitignored (v3 `.gitignore` covers `.venv/`, `.cache/`,
`lean_workspace/.lake/`, `.pytest_cache/`, `.coverage`) so git status
stays clean; (2) `lsof +D .` to confirm nothing is running from the tree;
(3) classify: evidence (keep) vs build deps (delete) vs shared caches
(flag — delete only on explicit CTO choice); (4) a destructive `rm` on
user-owned material trips the terminal approval gate — present the exact
plan with before/after sizes and let the CTO pick scope via clarify;
never retry a blocked destructive command without fresh consent.
