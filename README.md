# LeanEcon v4

**LeanEcon v4** is a clean-room rebuild of LeanEcon: an economics-formalization
collaborator that takes English economic claims through reviewed interpretation,
Lean 4 formalization, and kernel-checked verification — producing auditable
traces and verification bundles rather than bare "compiles" claims.

**Current supported release: v3.5.0 "Measured Elaboration"** (tagged on
`main` after PR #20 merges; see the release rule in
`docs/releases/DEVELOPMENT.md`). The `main` branch carries package
`3.5.0` / builder `leanecon-a3-3.5.0`. See `docs/releases/DEVELOPMENT.md`
and `docs/releases/v3.5.0.md`.

> Sequencing note while PR #20 is open: this worktree says final
> `3.5.0`; the tag `v3.5.0` is created at main HEAD immediately
> post-merge, per the earn rule ("tag only with
> `docs/releases/vX.Y.Z.md`" — satisfied).

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

### v1 promise (still true)

A human or AI reviewer, using the supported CLI, can turn an English economic
claim into a kernel-checked Lean statement with an auditable verification
bundle and replayable trace, against a pinned Lean/Mathlib workspace and a
versioned LeanEcon Core, with models used as drafting aids.

### v2 promise (Phoenix)

The v1 workflow, plus measured AI-reviewer exercise and audit-gated assist
libraries. Live `formalize` now runs the bounded revision loop
(`leanecon.revise_loop`, budget 3). `skeleton` is a drafting CLI
(`a3 skeleton`); unresolved gaps cannot reach `verify`.
Interpretation (`mistral-medium-3-5`) and formalization (`labs-leanstral-1-5`)
run live; `--from-file` is reviewer recovery when the formalizer is not
statement-faithful.

### v3 promise (Verifiable State Machine — narrowed)

The product is the **audited claim lifecycle**, not model draft quality.
Live `formalize` is a bounded state-machine transition; `skeleton` cannot
reach `verify` with gaps; `VERIFIED` stays kernel- and bundle-gated.
Draft-complete on frozen holdouts is **2/13 ≈ 15%** and is **not** a
v3 claim. Wiring intelligence into those transitions is **v4**
(`docs/v4/INIT_V4.md`).

### Explicit non-claims (v2 / v3)

- No autonomous / unattended `VERIFIED`; no production SLA
- Formalizer is not statement-faithful (live first-try valid 0/3 on v2p1)
- `revise_loop` is on the live `formalize` path; `skeleton` is a
  drafting CLI (`a3 skeleton`) that cannot reach `verify` with gaps
- No B2 auto-prove; no agents, retrieval corpus, or game-theory Core
- No graphs / embeddings / LaTeX ingest (v3 substrate)
- No broad economics library (thin Core: micro/consumer + CE/FWT spine)
- No path that bypasses the reviewer or the kernel axiom audit

## MVP sequence

- **A1 — Diagnostics**: health-first foundation. ✅
- **A3 — Verified workflow**: claim → interpretation → review → formal → Lean
  verification → auditable bundle and trace. ✅ (v1 surface)
- **B2 — Bounded proof**: automated proof search with hard budgets. ❌ spike only (`spikes/001-bounded-search/`; compile≠pass)

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
| **v2.0.0 Phoenix** assist foundation | ✅ shipped on `main` — AI reviewer exercised; `revise_loop` + `skeleton` were libraries at tag |
| **v3.0.0 Verifiable State Machine** | ✅ shipped & tagged 2026-08-22 (PR #19) — lifecycle is the product; loop + scorer + skeleton + sealed eval; draft promise narrowed off (2/13), recorded honestly |
| **v3.5.0 Measured Elaboration** | ✅ shipped (PR #20) — sealed `v35h1` draft_complete **2/3 ≥ 0.60**; class-directed probe-repair Diagnosis; P1–P6 fidelity ontology + frozen metrics (DECISION_LOG 50–54) |

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
