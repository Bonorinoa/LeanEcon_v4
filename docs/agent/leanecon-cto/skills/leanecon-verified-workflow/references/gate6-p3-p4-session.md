# Gate 6 P3/P4 execution session (2026-08-06)

Continuation record for the Gate 6 phase work started after P2 merged.
Main at session start: bd71bb8 (P2 merged). **P3 was approved as
proposed, pushed, PR #9 merged (main @ 697f79a). P4 was then EXECUTED
in the same session; the CTO review gate is open on
`docs/gate6/P4_REVIEW_BATCH.md` (nothing committed for P4 yet).**

## P3 — glossary registry v1 (APPROVED 2026-08-06, MERGED PR #9)

- `docs/gate6/references/core-glossary-detail.md` → **Registry v1.0.0**:
  version header + `## Change log` table (version|date|change|kind).
  Versioning rules: entry additions = minor; meaning changes = major
  (downstream re-review); status moves = change-log rows, not bumps.
- Single source of truth declared in the header; EI `context.definitions`
  = per-claim copies (source anchors, immutable per revision);
  `a3-core-design.md` §2 index superseded as design-time snapshot.
- **The mechanical check caught REAL drift:** six P2-promoted
  declarations (entries 1, 6, 7, 9, 12, 13) still read `core-candidate`
  (0 entries marked core before the pass). Fix: status → **core** with
  approval refs (DECISION_LOG item 20, `P2_REVIEW_BATCH.md` §6, PR #8).
  Ladder after fix: core 6, core-candidate 3 (25/26/27 deferred),
  mathlib 7, glossary-only 12 = 28.
- Equilibrium family (21–28) verified glossary-only/core-candidate; no
  declarations (Gate 7 slice).
- Commit `fc5756a` → branch `gate6/p3-glossary-registry-v1` → PR #9
  (docs-only; dispatch scaffold+a1; merge with `merge_pr.py 9 clear-checks`;
  protection restored exactly, verified). P3 verdict wording: "approve as
  proposed" covered the push+PR+merge.
- Reusable check: `scripts/glossary_registry_check.py` in this skill.

## P4 — D1/D2/D4 contract deltas (EXECUTED 2026-08-06; gate open)

Follow-up session: execute per `IMPLEMENTATION_PLAN.md` §5 after the P3
verdict. All additive; the 137-test baseline must stay green; new tests
extend the A3 suites with the mocked-provider pattern (autouse
`a3_runner.probe_statement_compiles` patch already exists in
tests/test_a3_runner.py).

- **D1** (`src/leanecon/formalization.py`): add `core` to `MAPPING_KINDS`
  (keep `none` — the §4 "drop none" is Open Q2, deliberately OUT of P4
  scope; flag in the review package). Check in `validate_mapping_report`:
  mapped `core` rows must match
  `^LeanEcon\.Core\.[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$`
  (prefix + ≥2 dotted components per the namespace skeleton; bare ids and
  `LeanEcon.Core.X`-only flagged). Reverse check (a `LeanEcon.Core.*` id
  on a non-core row) proposed, not implemented. Update `formalize_prompt`.
- **D2** (`lean_probe.py` + `bundle.py`): `WorkspaceIdentity` gains
  `core_revision` = content digest of the merged Core tree
  (`lean_workspace/LeanEcon/Core/*.lean`, sorted, concatenated, passed to
  `canonical_digest` — no import cycle: data_policy imports stdlib only).
  `build_bundle` writes `workspace_identity.core_revision` +
  `dependency_audit.core_imports` (union of Core imports from the formal
  statement AND the proof source — the kernel compiles the proof, so the
  pin must cover it). Validator check `12_core_pin`: core imports ⇒ pin
  present; when the manifest workspace path is readable, recomputed digest
  must match (the data-flow §8 "stale pin" flow). Separate check 12 chosen
  over folding into check 7 (distinct failure reason); update the
  "eleven/11-item" string references in bundle.py, a3_runner.py,
  trace_replay.py (gate3/05 itself needs NO edit — check 7's
  "Mathlib/package revisions" language already covers a Core pin).
  Manifest `schema_version` policy proposal: keep 1.0.0 (additive fields,
  validator is the only consumer, historical bundles predate the fields).
- **D4** (`formalization.py`): `validate_scaffolding_namespace(statement)`
  — lexical namespace-depth scan; root-namespace
  `abbrev|def|structure|class|inductive|instance` flagged; `theorem`
  deliberately NOT flagged (it is the candidate's target). HARD rejection
  at formalize (PROVIDER_INVALID_OUTPUT, sibling of
  `validate_statement_text`, no artifact written) — NOT a verify-side
  check, because the c1–c4 reviewer fixtures put scaffolding at root and
  must keep verifying. `formalize_prompt` gains the
  `namespace A3Scaffolding.<claim>` rule.
- **D3** (docs only): `collision_check:` field added to the
  ontology-record template in the registry (v1.1.0 change-log row,
  additive). CI-grep proposal: per-promotion-batch `#check` probes of
  Core declaration names against Mathlib root names (kernel-arbitrated),
  or a committed Mathlib root-name reference list.
- Review package: `P2_REVIEW_BATCH.md` pattern — decisions table, exact
  diffs, evidence, "deliberately NOT in this batch" list (drop-none,
  verify-side scaffolding check, reverse FQ check).

## P4 execution outcomes (same session)

- **Surfaced finding, fixed as root cause:** `validate_statement_text`'s
  `\s:=` regex rejected the D4 acceptance candidate (`abbrev Bundle := ℝ`
  namespaced scaffolding) — proof-body checks must be declaration-aware
  (see SKILL.md §4 pitfall; regression test
  `test_validate_statement_text_allows_definitional_body`).
- Implemented per the design decisions above, PLUS: `CORE_IDENTIFIER_RE`
  (≥2 dotted components after `LeanEcon.Core.`); `compute_core_revision`
  in `lean_probe.py` (content digest, `None` when no Core tree); check
  `12_core_pin` includes STALE-pin comparison when the manifest
  workspace_root is readable, honest presence-only fallback otherwise;
  `formalization.py` module docstring updated (was stale: "No LeanEcon
  Core exists yet").
- Verification: **156 passed** (137 baseline + 19 new: 6 D1, 7 D2,
  3 D4-unit, 2 D4-e2e via FakeAdapter, 1 regression). No Lean builds
  needed (no Lean source changed).
- CTO decisions requested (D1–D8 in `docs/gate6/P4_REVIEW_BATCH.md`):
  D1 FQ pattern ≥2 components; D2 keep schema_version 1.0.0; D3 separate
  check 12; D4 include stale-pin compare; D5 hard rejection at formalize;
  D6 no verify-side proof check (reviewer-owned fixtures at root);
  D7 keep `mapping_kind: none` in the enum (Open Q2 drop later); D8 D3
  CI-grep proposal only.
- Post-approval: DECISION_LOG items 22–24 (P3 merged; P4 approved; commit
  pending) + commit/PR per the standard flow.

Attribution: prepared by Hermes Agent (Nous Research) under CTO direction;
the CTO remains the sole semantic approver.
