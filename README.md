# LeanEcon v4

**LeanEcon v4** is a clean-room rebuild of LeanEcon: an economics-formalization
collaborator that takes English economic claims through reviewed interpretation,
Lean 4 formalization, and kernel-checked verification — producing auditable
traces and verification bundles rather than bare "compiles" claims.

**Current release: v1.0.0** (package version in `pyproject.toml`).

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

Semantic approval is owned by an **authorized reviewer (human or AI)** under
CTO policy (`docs/gate3/08-reviewer-policy.md`). Models may draft; the CTO
remains the accountable semantic authority. `VERIFIED` requires the complete
bundle validator (12 checks, including `12_core_pin` when Core is used), not
merely successful compilation.

### v1 promise

A human or AI reviewer, using the supported CLI, can turn an English economic
claim into a kernel-checked Lean statement with an auditable verification
bundle and replayable trace, against a pinned Lean/Mathlib workspace and a
versioned LeanEcon Core, with models used only as optional drafting aids.

### Explicit non-claims (v1)

- No autonomous formalization (models are drafting aids; formalizer is not statement-faithful)
- No B2 bounded proof loop / auto-prove
- No multi-agent orchestration, retrieval corpus, or production VERIFIED SLA
- No broad economics library (thin Core: micro/consumer + CE/FWT spine)

## MVP sequence

- **A1 — Diagnostics**: health-first foundation. ✅
- **A3 — Verified workflow**: claim → interpretation → review → formal → Lean
  verification → auditable bundle and trace. ✅ (v1 surface)
- **B2 — Bounded proof**: automated proof search with hard budgets. ❌ post-v1

## Relationship to v3

- **v3 is archived historical evidence.** `leanecon_v3` is frozen and retained
  only as an immutable experimental record.
- **v4 is a clean-room rebuild.** No v3 custom Lean, Python, prompts, schemas,
  orchestration, tests, evaluation code, CI, Dockerfiles, provider logic, or
  configuration is copied. Every relationship to a v3 artifact is recorded in
  the migration ledger with an explicit disposition.
- No v3 implementation or `.codebase-memory` is imported. v3 scores are never
  presented as comparable v4 scores.

## Repository status

| Milestone | Status |
|---|---|
| Gate 2 governance scaffold | ✅ closed |
| Gate 3 contracts + trust boundaries | ✅ closed (`docs/gate3/`) |
| Gate 4 A1 diagnostics | ✅ closed |
| Gate 5 A3 verified workflow | ✅ closed (walkthrough + hardenings) |
| Gate 6 LeanEcon Core (P1–P5) | ✅ closed |
| Gate 7 equilibrium-family Core | ✅ closed (PR #11) |
| OOS batch + F1 lifecycle fix | ✅ complete (PR #12) |
| **v0.2** reviewer recovery + AI reviewer + ops | ✅ shipped |
| **v0.3** eval skeleton | ✅ shipped |
| **v1.0.0** supported verified workflow | ✅ shipped |
| **v2 in progress** — plan `docs/v2/INIT_V2.md` | ✅ Phase 1: AI reviewer exercised (3 claims VERIFIED, 100% agreement, zero code) · ✅ Phase 2: revise loop merged (PR #15) |

Evidence packets: `docs/releases/`. Decision log: `docs/gate3/DECISION_LOG.md`.

## A3 workflow CLI

Supported live entrypoint (always prefer this after src edits):

```bash
scripts_local/a3_run.py <subcommand> [args...]
# sets PYTHONPATH=src + profile credentials; never print secrets
```

Console script (after `uv pip install .`): `leanecon-a3`.

```text
ingest        create a claim revision (DRAFT)
interpret     run interpretation (live)            -> INTERPRETED -> REVIEW_REQUIRED
review        reviewer decision: approve | reject  -> ACCEPTED | REJECTED
              (--reviewer required; --reviewer-kind human|ai|auto)
formalize     live formalization OR --from-file    -> FORMALIZED | FAILED
gap-ack       reviewer acknowledges mapping gaps   (enables PROVING)
axiom-approve reviewer approves the axiom list     (per-run reviewer record)
verify        proof input -> PROVING -> VERIFIED | FAILED | BLOCKED (+ bundle)
bundle        re-validate the current bundle (12-item checklist)
replay        trace replay (deterministic validation)
status        claim state and artifact references
```

Reviewer-authored formal recovery (when the model is blocked):

```bash
scripts_local/a3_run.py formalize --claim-id oos2 --from-file path/to/candidate.json
# candidate JSON: {statement|statement_text, target_theorem, mapping_report}
```

Review commands require a reviewer identity (`--reviewer <id>` or
`LEANECON_REVIEWER_ID`). See `docs/gate3/08-reviewer-policy.md` and
`docs/releases/v1-runbook.md`.

## LeanEcon Core (v1 freeze)

Promoted vocabulary under `lean_workspace/LeanEcon/Core/` (9 declarations +
3 theorem boundaries): Primitives, Preferences, Utility, Constraints,
Choice, Equilibrium, Theorems — including `competitiveEquilibrium_paretoEfficient`
(FWT). Promotion criteria and ontology records: Gate 6/7 review packages.

## Credit & attribution

Implementation work in this repository is performed by an AI assistant (Hermes
Agent, by Nous Research) under the direction of the CTO. Commits and PRs may be
pushed through:

- the CTO's GitHub account (`@Bonorinoa`), and/or
- the dedicated automation contributor (`@hermessinho`)

The CTO remains the **accountable semantic authority** for all meaning,
interpretation, Core ontology, and policy decisions. `@hermessinho` is an
operational/implementation contributor only — it does not self-approve
economics content or bypass reviewer gates. Authorized AI reviewers (when
acting on claims) follow `docs/gate3/08-reviewer-policy.md`.

Bot token safety: store a limited-scope PAT as `LEANECON_BOT_TOKEN` (see
`scripts/github_token.py`). Prefer it for bot-authored push/PR; keep the CTO
token for branch-protection relax/restore flows.

## License

Apache-2.0. See [LICENSE](LICENSE).
