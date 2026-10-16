# Gate 6 P5 — exit evidence session (2026-08-06)

Records the P5 class of work: clean-clone reproduction, live Core-import
verification (closing the D2 risk-register loop), ontology–declaration
agreement check, ledger update, and the gate-closing ceremony. All
verbatim evidence is committed in `docs/gate6/P5_EXIT_PACKAGE.md`
(commit `6778e98`); the reproduction script is
`scripts_local/clean_clone_check.sh`.

## 1. Clean-clone reproduction (plan §6.1)

Recipe: fresh clone → `lake build LeanEcon.Core.Theorems Preferences
Constraints Utility` → fresh venv → pytest. Verbatim result:

```
$ lake build LeanEcon.Core.Theorems LeanEcon.Core.Preferences LeanEcon.Core.Constraints LeanEcon.Core.Utility
✔ [3001/3002] Built LeanEcon.Core.Constraints (6.9s)
✔ [3002/3002] Built LeanEcon.Core.Theorems (1.5s)
Build completed successfully (3002 jobs).

$ .venv/bin/python -m pytest -q
156 passed in 35.66s
```

Environment pitfalls (also in SKILL §4, "Clean-clone reproduction"):
- `uv venv` defaults to the newest Python; MUST pin `--python 3.11`
  (baseline) or jsonschema/rpds breaks under the Hermes session
  PYTHONPATH (hermes' 3.11 site-packages shadow the venv; `rpds.rpds`
  is a compiled 3.11-only extension).
- The formalize probe prepends `import Mathlib` → requires the COMPLETE
  Mathlib build (`Mathlib.olean`), not just the Core dependency closure.
  `lake build LeanEcon.Core.*` alone leaves
  `test_probe_statement_compiles_real_workspace` failing.
- No `lake exe cache` facility on this machine → fresh clones compile
  mathlib from source; the memory-heavy tail (Analysis/MeasureTheory)
  OOMs at default 12-job parallelism on 24 GB RAM. Finish with
  `lake build Mathlib -- -j4` (lake 5 has no `-j` short flag; pass
  `-- -jN`).
- Hermes background wrappers can report "exited" while the lake/lean
  process tree SURVIVES and keeps building — `ps aux | grep bin/lake`
  before assuming a build died; poll the build log directly. A killed
  build resumes incrementally (trace-based up-to-date checks).
- Reusing a different checkout's olean cache does NOT help here: lake's
  trace hashes don't match across workspace paths, so it recompiles.

## 2. Live Core-import verification (D2 risk-register loop)

The risk register required D2 to land before any claim imports Core;
P5.2 demonstrated the Core-era flow works. Pattern (reuse for Gate 7
batch evidence):

1. Write a Core-importing candidate to `lean_workspace/.a3-candidates/
   <tag>/Check.lean`: fully-qualified Core identifiers (D1 style, no
   `open`), theorem restating a reviewed Core theorem boundary, proof by
   the imported boundary, `#print axioms <name>` at the end.
2. `lake env lean` it — expect the baseline closure verbatim:
   `'<name>' depends on axioms: [propext, Classical.choice, Quot.sound]`
   (this is the "Core adds no axioms" live proof).
3. Build a SAMPLE bundle with `build_bundle` using the REAL statement,
   proof and workspace: `write_ei` (accepted) + `write_formal` (imports
   incl. `LeanEcon.Core.*`) + verification record constructed from the
   real kernel output (clearly labeled sample — not a claim walkthrough)
   + `axiom_record` = baseline. `validate_bundle` must show all 12
   checks incl. `12_core_pin: ... digest matches workspace`; recompute
   `compute_core_revision(workspace)` independently and compare.
   Real manifest sample (bundle-c-p5-r1-8315f3): `core_revision`
   `ef0a5386…` (sha256), `core_imports` = the Core imports.

## 3. Ontology–declaration agreement check (plan §6.3)

Mechanical script pattern: parse Core module declarations
(`^(abbrev|def|structure|class|theorem)\s+<name>`), the registry's
`**core**` entries (kebab id → camelCase map), and the P2_REVIEW_BATCH
records. Rules A–D:
- A: every registry entry marked `core` has a matching declaration in
  the Core tree, and vice versa;
- B: theorem boundaries map to a registry entry + claim family;
- C: deferred core-candidates (equilibrium family) have NO declarations
  and no module file;
- D: no v3 markers (`Preamble`, `local_gate_`, uuid shapes) inside Core.
Result: "P5.3 ontology-declaration agreement check PASSED" (8
declarations, 6/6 core↔decl, T1/T2 recorded).

## 4. Gate-closing ceremony (repeatable for Gate 7+)

1. **Exit packet** (`docs/gate6/P5_EXIT_PACKAGE.md` is the template):
   migration-plan exit-criteria table, phase execution record, verbatim
   evidence per criterion (build output, kernel output, manifest), an
   "environment notes / honest reproduction conditions" subsection
   (state what was compiled vs reused, memory caps, python pins),
   approval-record index, contamination/non-goals confirmation, open
   items carried forward.
2. **Ledger**: Core-specific disposition register (K1–K6 style rows) in
   `docs/gate3/01-migration-ledger.md` — operationalize the design's
   v3-disposition table with the ledger's field shape.
3. **DECISION_LOG**: closure item (`# P5 — Gate 6 exit package
   (APPROVED ... — GATE 6 CLOSED)`) recording the exit criteria met.
4. **Plan status sync**: `IMPLEMENTATION_PLAN.md` header → "P1–P5
   executed; Gate N CLOSED", next gate named.
5. Final pytest, commit (docs), push directly to main with
   `scripts_local/push_main.py` (CTO-authorized direct push — null the
   reviews requirement + clear checks, restore exactly in `finally`),
   `verify_protection.py`, single-branch confirmation.
6. Update memory: phase-state entry → closed-state entry (compact).

Attribution: prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
