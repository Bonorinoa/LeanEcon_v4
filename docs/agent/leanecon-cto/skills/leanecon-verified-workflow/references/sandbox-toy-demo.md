# Sandbox toy demo — validating LeanEcon design decisions in the pinned workspace

When/why: the CTO reviews design gates cautiously and wants a COMPILED toy
of the design's central mechanics before approving implementation (asked
explicitly before Gate 6 Core work). This recipe was proven 2026-08-06 on
the Gate 6 Core design (toy `LeanEcon.Core.Sandbox`). Use it for any
design-gate validation and for Core/A3 changes where the mechanics are
unclear.

## Placement rules (module naming from path)

- Toy module file: `lean_workspace/LeanEcon/<Area>/<File>.lean` => module
  name `LeanEcon.<Area>.<File>`. It becomes part of the `LeanEcon`
  lean_lib (lakefile package) and is importable by name — the ONLY reason
  to put it under `LeanEcon/`. Do NOT put it under `.a3-candidates/`
  (not part of the lib; cannot be imported by name).
- Candidates: `lean_workspace/.a3-candidates/<sandbox>/<run>/Candidate.lean`
  (gitignored at repo root). Module name for a candidate is just
  `Candidate` (path-derived), same as real A3 runs.
- The lakefile sets `autoImplicit false` / `relaxedAutoImplicit false`:
  declare binder types explicitly (plain `Type` worked for the toy;
  `Type u` needs `universe u`).

## Imports (toy modules)

`import Mathlib.Data.Real.Basic` + `import Mathlib.Tactic` suffice for ℝ,
`Set`, `Fintype`, and `∑` (Finset sum) notation — no `import Mathlib`
wholesale, matching the Core import policy. Verified on mathlib v4.32.2.

## Commands (run from lean_workspace/, with `~/.elan/bin` on PATH)

```bash
lake build LeanEcon.Core.Sandbox        # ~13s with Mathlib prebuilt (~3000 jobs)
lake env lean .a3-candidates/sandbox-core/run-1/Candidate.lean
```

Append `#print axioms <theorem>` lines INSIDE the candidate file — the
verifier does the same; the output line is the trust artifact.

## Expected outputs (verbatim, 2026-08-06)

- Toy module build: `✔ [2997/2997] Built LeanEcon.Core.Sandbox (13s)`.
- Stage A (A3-local scaffolding) and Stage C (imports toy Core):
  `'<thm>' depends on axioms: [propext, Classical.choice, Quot.sound]`
  — Core declarations add ZERO new axioms (design invariant holds in
  practice; this is a headline result to show the CTO).
- Stage C-bad (invented Core id, e.g. `budgetSetX`): `error: Function
  expected at budgetSetX … unknown identifier … typo or a missing import
  or open statement`, exit 1 => verifier records `LEAN_SYNTAX_ERROR`.
  The kernel arbitrates invented names — no model output or reviewer
  wish makes an undeclared identifier meaningful.

## Teaching structure the CTO responded well to

1. Three-layer picture FIRST (Mathlib = general math / Core = economics
   vocabulary / A3 candidates = disposable per-claim wrappers) before any
   Lean syntax.
2. Mapping reports at maturity stages — the same claim as
   `local_definition` (today) vs `glossary_term` (interim) vs `core`
   (target). The reviewer-facing table is what makes Core's value visible
   WITHOUT reading Lean; every economic decision stays reviewable.
3. Real compile output including a deliberate failure — never hand-waved
   snippets.
4. State-machine table: which actor touches Core at each step; Core is
   consulted twice (meaning at review via the EI, syntax at the kernel via
   imports) and is NEVER written by the pipeline (agents only read
   Core/glossary context and report identifiers).
5. Failure-modes table + a one-breath "why this shape" rationale.

## Hygiene and cleanup

- After the demo: remove the toy module dir, the candidate dirs, and the
  module's build artifacts (`find .lake -path '*LeanEcon/<Area>*' -delete`),
  then `lake build LeanEcon.A1` to confirm the tracked workspace still
  builds. Verify `git status` shows no new tracked files.
- The cleanup `rm`/`find -delete` command WILL trip the terminal approval
  gate — expect it, and if it comes back BLOCKED, do not retry: state that
  the scratch is untracked/harmless, ask via clarify, and adjust.
- **Document cleanup status honestly in the walkthrough doc.** If removal
  is still pending approval when you write it, say "compiled and
  demonstrated; removal awaiting approval" — never claim a deletion that
  did not happen (the project's whole culture is honest records).
- Sandbox files are NOT Core declarations: state it, and that nothing was
  committed or promoted. The walkthrough doc lives with the design package
  (e.g. `docs/gate6/references/core-toy-walkthrough.md`) and counts as a
  design-package reference, not implementation.

## Context facts learned the same session

- `leanecon_v3` GitHub repo is ARCHIVED (read-only): pushes are rejected;
  the freeze commit is already on `main`. Check `archived` via the GitHub
  API before any push attempt (token in the profile env; those heredoc
  calls may also trip the approval gate).
- The migration plan (`v3/.hermes/plans/2026-08-04_LeanEcon_v4_migration_plan.md`)
  is UNTRACKED and local-only (not in the archive) — preserve it into v4
  docs before any future local deletion.
