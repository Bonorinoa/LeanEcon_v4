# v4 intelligence sprint — Day 1–3 record (2026-08-17)

Branch `v4/intelligence-sprint` (off the v3 ship branch). CTO goal:
≥50% intelligence improvement, full experiment permission.

## Day 1 — failure-class inventory (method worth reusing)

Mine `artifacts/local/a3-events/*.jsonl` for
`source_component=a3-formalize` + `detail.revision_history`. Tag per
attempt: proof_body (`:=`), sorry, mapping_d1, d4_namespace, probe
stderr classes. 24 attempts / 8 events gave: proof_body ×6, sorry ×6,
mapping_d1 ×5, d4_namespace ×3.

**Key insight:** v3h2-A repeated the IDENTICAL reject on attempts 1–3.
Verbatim feedback text does not change model behavior. When a loop
burns its budget on identical rejects, the fix is mechanical repair
before audit, not better prose in the feedback block.

## Day 2 — lever: mechanical signature repair

- `sanitize_signature_draft()` in `formalization.py`: strips
  theorem-style proof bodies (declaration-aware via `_decl_head`),
  removes residual sorry/admit, re-homes root-namespace scaffolding
  under `A3Scaffolding`. Called in `draft_fn` BEFORE audit; repair
  notes appended to `revision_history` as an entry with
  `repair_notes` key.
- Format exemplar (GOOD/BAD signature) added to `formalize_prompt`.
- **Audit gate, kernel probe, reviewer policy untouched.** The repair
  surface ⊂ audit surface; anything the sanitizer cannot fix still
  FAILs through the normal path.

### Test-contract lesson (generalizes)

Six v3 tests encoded "dirty draft burns an attempt." After the repair
lever, dirty-but-repairable drafts are accepted at attempt 1 — that is
the intended behavior change, not a regression. Correct response:
rewrite those tests to the new contract while PRESERVING the old
invariants on a violation OUTSIDE the repair surface (unparseable JSON
response, D1 bare-core mapping rows). Never weaken the no-artifact /
exact-budget assertions.

Regex/boolean pitfall hit live: an `and/or` precedence bug in the
body-cut condition passed some tests and silently mis-cut others —
the "clean draft untouched" and "wrapped continuation" tests caught
both (trailing newline eaten by `splitlines`/`join`; body lines after
the `:=` line surviving). Always test the no-op case AND the
multi-line-body case.

## Day 3 — live smoke (predictions first)

v4smk-A/B = same texts as v2p1-A/B under new ids (D5 comparison).

| claim | baseline | v4 result |
|---|---|---|
| v4smk-B (v2p1-B text) | always FAILED (sorry+`:=`) | **FORMALIZED** within budget — first clean ever |
| v4smk-A (v2p1-A text) | always FAILED (`:=`+D4) | FAILED on **D1 core rows** (`attainableSet p e`, bare names) |

The repaired classes stayed fixed. The remaining killer is D1
core-row discipline — a MAPPING-REPORT surface, still mechanical.

## Day 3+ — planned extension (RED tests written, NOT implemented)

`sanitize_core_mapping_rows(report)`:
1. Trim application args off core-row identifiers
   (`attainableSet p e` → `attainableSet`).
2. Promote known bare Core names to FQ ids (`attainableSet` →
   `LeanEcon.Core.Choice.attainableSet`) using a table built from
   `lean_workspace/LeanEcon/Core/*.lean` declarations.
3. Downgrade unfixable core rows to `local_definition` (honest: not
   Core vocabulary).

Tests: `tests/test_sanitize_core_mapping.py` (5 cases, currently
failing = RED). Known Core areas: Choice, Constraints, Preferences,
Theorems, Primitives, Utility, Equilibrium.

## Token posture observation (2026-08-17)

Profile `GITHUB_TOKEN` (CTO) returned **401** on /user; only
`LEANECON_BOT_TOKEN` (hermessinho) authenticated. Consequence: no
protection relax/merge possible until the CTO rotates the token.
Diagnostic pattern: `artifacts/local/whoami_tokens.py` — prints login
only, never the token. Verify before assuming either token works.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
