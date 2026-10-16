# Gate 5 — A3 minimal verified workflow: design review (2026-08-06)

CTO approved the design **as-is**; the Appendix A canonical claims (EI
acceptance test) still await CTO review before any A3 implementation.
Artifacts at the time: `docs/gate5/a3-design.md` + `docs/gate5/ALTERNATIVES_SUMMARY.md`
— staged (`git add docs/gate5/`), **uncommitted**; commit requires separate
authorization.

## A3 architecture (from the approved design)

New modules under `src/leanecon/`: `interpretation.py` (EI validation),
`formalization.py` (candidate + mapping report), `verifier.py`, `bundle.py`,
`trace_replay.py`, `a3_runner.py`, claim/artifact store, review-record store.
**Reused unchanged:** `events.py`, `data_policy.py`, `providers.py`,
`adapters/mistral.py` (+ `MVP_MODEL_MAP`), `gold_isolation.py`, `lean_probe.py`
(identity + sorry helpers). Only new dependency proposed: `jsonschema`.

## Locked design decisions (each was an open question at review time)

1. **`none_noted`**: explicit marker field in the EI candidate + REQUIRED
   reviewer acknowledgement flag in the review record; approval refused
   without it (draft-schema exercise — schema still not frozen).
2. **Axiom-approval loop**: first run with an unapproved axiom ⇒
   `FAILED`/`AXIOM_VIOLATION` with the plain-language axiom list in the bundle;
   reviewer per-run record (`axiom_approval_ref`) closes it; retry passes on
   the same `FORMALIZED` candidate. No repo-wide allowlist in MVP.
3. **Mapping gaps**: unmapped *material* EI elements (objects, assumptions,
   quantifiers, conclusion, solution concept) block `PROVING` entry until a
   reviewer gap-acknowledgement record exists; expository elements may be
   `deferred`. Gaps are a state, not a new reason code.
4. **A3-local scaffolding definitions** in candidate files: allowed for MVP,
   clearly labeled, reviewed via mapping report + statement text, NEVER
   promoted to Core without the Gate 6 process.
5. **Proof input manual only**: reviewer file or reviewed v4 fixture; no
   `prove_or_repair` call in Gate 5; provenance recorded.
6. **Verifier**: `lake env lean <candidate>` in the pinned workspace with the
   recorded command; kernel-level `sorry`/`admit` detection via `#print axioms`
   (`sorryAx` presence) layered over the static `check_sorry_free` scan;
   wall-clock timeout ⇒ `FAILED`/`PROOF_TIMEOUT`.
7. **Candidate files**: generated per-run under
   `lean_workspace/LeanEcon/A3/<claim>/`, gitignored, never committed; only
   reviewed fixtures are committed.
8. **No new reason codes for A3** — the locked registry already covers every
   A3 failure.

## Canonical claims (Appendix A — awaiting CTO review)

Selection criteria: small, economically meaningful, formalizable in Mathlib +
minimal scaffolding, each exercising a different frame element.

- **C1** budget expansion ⇒ attainable set does not shrink — ambiguity fork
  ("attainable" vs "chosen"), object roles, local scaffolding, mapping gap.
- **C2** weak-preference transitivity — Mathlib relation, quantifier order,
  glossary refs.
- **C3** strictly increasing utility ⇒ componentwise order implication — strict
  vs weak comparison; `SORRY_FOUND` temptation.
- **C4** monotone f:ℝ→ℝ preserves order — pure Mathlib anchor, calibrates the
  machinery.

Each needs a Gate 7-style record (English, approved EI, intended formal
statement, known proof boundary, expected failure modes, provenance) before
use; the first walkthrough claim needs the full record, the others at least EI
approval.

## Reading-a-bundle doctrine (for interpreting any future A3 result)

**VERIFIED proves:** kernel acceptance of the formal statement in the pinned
workspace; no `sorry`/`admit` (static + kernel layers); every axiom on the
approved per-run list; digest chain claim → EI → statement → proof → approval
intact. **VERIFIED does NOT prove:** economic truth, interpretation fidelity,
or that the formal statement models the economics — semantic correctness stays
with the CTO (EI + mapping report review).

Reason codes → action: `PROVIDER_UNAVAILABLE` / `WORKSPACE_UNPINNED` /
`LSP_UNAVAILABLE` ⇒ **retry**; `LEAN_SYNTAX_ERROR` / `SORRY_FOUND` /
`PROOF_TIMEOUT` ⇒ **revise**; `AXIOM_VIOLATION` ⇒ reviewer record, then retry;
`SEMANTIC_AMBIGUITY` / `USER_REJECTED` ⇒ **new revision**;
`RESTRICTED_BLOCKED` / `INPUT_REJECTED` ⇒ policy blocker.

## Baseline at design time

44/44 pytest tests green on the clean worktree (`HEAD 72cf26e`); baseline
verified with real tool output before writing the package.
