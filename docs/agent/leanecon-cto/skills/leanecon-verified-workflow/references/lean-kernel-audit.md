# Lean kernel verification from Python (pinned workspace)

Techniques proven in the Gate 5 A3 verifier (`src/leanecon/verifier.py`).
Workspace: Lean v4.32.2 + Mathlib v4.32.2 via elan (`~/.elan/bin` on PATH).

## Running the kernel check

```bash
cd lean_workspace
lake env lean <file.lean>      # exit 0 = kernel accepted; diagnostics on stderr
```

- `lake env lean` resolves Mathlib imports from the pinned workspace. Run
  with cwd = workspace root. `lake`/`lean` missing from PATH => treat as
  BLOCKED/WORKSPACE_UNPINNED, never silent fallback.
- Timeout => PROOF_TIMEOUT (a negative result, not a blocker).

## Candidate file placement — the module-name-from-path pitfall

Files inside a `lean_lib` dir (e.g. `LeanEcon/`) get a module name INFERRED
from their file path; if it doesn't match, compilation fails. Per-run
candidates therefore live OUTSIDE the lib tree:

```
lean_workspace/.a3-candidates/<claim>/<run>/Candidate.lean   (gitignored)
```

Sanitize CLI-supplied claim/run ids before using them in paths
(`sanitize_module_part` — `../evil` -> `___evil`). Path traversal is a real
risk with user-supplied ids.

## The axiom audit: `#print axioms` has TWO output formats

Append the query to the COMPILED file (it is a compiler directive, not part
of the statement artifact — digests cover the source without it):

```lean
#print axioms <theorem_name>
```

Format 1 — non-empty axiom set:
```
'name' depends on axioms: [propext, Classical.choice, Quot.sound]
```
Format 2 — EMPTY axiom set (different sentence! the parser bug of 2026-08-06):
```
'name' does not depend on any axioms
```

The regex must handle BOTH. Zero-axiom theorems are common for pure set/logic
statements (subset rewrites, IsTrans projections).

## sorry detection — two layers

1. Static scan over source text (fast). MUST strip Lean comments first
   (`--` line comments, `/- ... -/` block comments incl. multi-line) — a
   comment mentioning the word "sorry" (e.g. documenting a rejected
   formalizer candidate) false-positives the naive scan.
2. Kernel audit (authoritative): a `sorry`/`admit` elaborates to the
   `sorryAx` axiom — its presence in `#print axioms` output => SORRY_FOUND
   even if the static scan was evaded. The compile still exits 0 with a
   warning, so the audit is the real gate.

## Wrong-theorem proof input

If the proof input declares a DIFFERENT theorem than the target, the
appended `#print axioms <target>` fails compilation ("unknown identifier")
=> honest FAILED/LEAN_SYNTAX_ERROR. The proof input must declare the
formalizer's `target_theorem` name.

## Axiom baselines

- Mathlib baseline (unfolded monotonicity, strict mono, most ℝ statements):
  `propext`, `Classical.choice`, `Quot.sound`.
- Pure set/logic statements (subset + rw, IsTrans projection): NO axioms.
- A declared `axiom foo : ...` in the candidate shows up in the audit as
  `foo` — unapproved => AXIOM_VIOLATION (the honest first-run loop).

## Bundle/replay interplay

- A FAILED bundle can legitimately pass all 11 checks when the failure was
  audit-layer (compile_ok True, reason set) — replay's consistency rule is
  manifest.result == verification.outcome (VERIFIED additionally requires
  all checks).
- `IsTrans.trans` takes EXPLICIT `a b c` binders (`hr.trans a b c hab hbc`);
  `Transitive` is deprecated in Mathlib v4.32.
