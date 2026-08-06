# LeanEcon v4

**LeanEcon v4** is a clean-room rebuild of LeanEcon: an economics-formalization
collaborator that takes English economic claims through reviewed interpretation,
Lean 4 formalization, and kernel-checked verification — producing auditable
traces and verification bundles rather than bare "compiles" claims.

## Product thesis

Economics claims are easy to state and hard to pin down. LeanEcon v4 pairs a
Mistral-backed interpretation/formalization workflow with a pinned Lean 4 +
Mathlib workspace so that a claim is only ever labeled `VERIFIED` when both
conditions hold:

1. **Kernel-checked** — the formal statement compiles in the pinned workspace
   with no `sorry`, and the axiom/dependency audit is part of the record.
2. **Auditable provenance** — the exact English claim, the accepted
   interpretation, the formal statement, approval events, and run traces are
   linked in a verification bundle that can be replayed and inspected.

Semantic approval is human-owned: Mistral may triage, but only the CTO or an
authorized reviewer approves meaning. `VERIFIED` requires the complete bundle,
not merely successful compilation.

## MVP sequence

- **A1 — Diagnostics**: health-first foundation. Pinned Lean/Mathlib build,
  compiler probe, LSP status, provider connectivity, typed failure paths.
- **A3 — Verified workflow**: claim → interpretation → review → formal statement
  → Lean verification → auditable verification bundle and trace.
- **B2 — Bounded proof**: automated proof search with hard wall-clock, step, and
  repair budgets; stop on success, no progress, or budget exhaustion.

A3 proceeds only when A1 is fully green. B2 proceeds only when A3 is sound.

## Relationship to v3

- **v3 is archived historical evidence.** `leanecon_v3` is frozen at tag
  `v3-freeze-20260804` (commit `3765578eab460f9de189e40fe9b9d33ccf197baa`) and
  is retained only as an immutable experimental record.
- **v4 is a clean-room rebuild.** No v3 custom Lean, Python, prompts, schemas,
  orchestration, tests, evaluation code, CI, Dockerfiles, provider logic, or
  configuration is copied. Every relationship to a v3 artifact is recorded in
  the migration ledger with an explicit disposition: `import`, `adapt`,
  `rebuild`, `inspiration`, or `historical-discard`.
- **No v3 implementation or `.codebase-memory` is imported.** v3 scores are
  never presented as comparable v4 scores.
- The governance scaffold in this repository is authored from first principles
  for v4.

## Repository status

- **Gate 2** complete: governance scaffold (this branch baseline).
- **Gate 3** closed: contracts, migration ledger, and trust boundaries —
  see [`docs/gate3/`](docs/gate3/) (review package) and
  [`references/gate3/`](references/gate3/).
- **Gate 4 (A1)** closed: health-first diagnostics under
  [`src/leanecon/`](src/leanecon/) with acceptance tests in
  [`tests/`](tests/); all ten criteria green.
- **Gate 5 (A3)** in review: design approved (`docs/gate5/a3-design.md`,
  CTO 2026-08-06) and the minimal verified workflow implemented — staged,
  uncommitted, awaiting CTO review. LeanEcon Core (Gate 6) and the B2 proof
  loop remain out of scope.

## A3 workflow CLI

The verified workflow is driven by `python -m leanecon.a3_runner`:

```text
ingest        create a claim revision (DRAFT)
interpret     run interpretation (live)            -> INTERPRETED -> REVIEW_REQUIRED
review        reviewer decision: approve | reject  -> ACCEPTED | REJECTED
formalize     run formalization (live)             -> FORMALIZED (or stays with gaps)
gap-ack       reviewer acknowledges mapping gaps   (enables PROVING)
axiom-approve reviewer approves the axiom list     (per-run reviewer record)
verify        proof input -> PROVING -> VERIFIED | FAILED | BLOCKED (+ bundle)
bundle        re-validate the current bundle (11-item checklist)
replay        trace replay (deterministic validation)
status        claim state and artifact references
```

Review commands require a reviewer identity (`--reviewer <id>` or
`LEANECON_REVIEWER_ID`). Only a human reviewer may emit `ACCEPTED` or
`REJECTED`; `VERIFIED` requires the complete verification bundle, not
merely compilation. Live runs load credentials via
`scripts_local/a3_walkthrough.py` (profile env, never printed).

## Credit & attribution

Implementation work in this repository is performed by an AI assistant (Hermes
Agent, by Nous Research) under the direction of the CTO. Commits are pushed
through the CTO's GitHub account (`@Bonorinoa`); the assistant has no separate
GitHub identity. The CTO remains the sole semantic reviewer and approver, and
no semantic judgment or release decision is delegated to an automated agent.

## License

Apache-2.0. See [LICENSE](LICENSE).
