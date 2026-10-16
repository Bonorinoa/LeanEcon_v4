---
name: leanecon-verified-workflow
description: "Use when working on LeanEcon A3 verified workflow, Core promotion (Gate 6+), release versioning (v0–v3), or progress/checkpoint audits."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [LeanEcon, Lean, Verification, Kernel, Walkthrough, Axioms]
    related_skills: [python-packaging, github-repo-management]
---

# LeanEcon A3 Verified Workflow

Use this umbrella for LeanEcon's A3 claim lifecycle, Lean kernel evidence,
Core vocabulary promotion, evaluation, releases, and checkpoint audits. Keep
this file for rules that apply on most runs; load the linked reference for
procedure or historical evidence.

## Authority and evidence

- Treat the repository's current `main` truth surfaces, frozen schemas, and
  lifecycle code as authoritative; treat this skill and chat as operator
  guidance because cached prose can drift.
- Separate shipped state, the current checkout, open PRs, and uncommitted
  drafts in every status report because a feature branch is not a release.
- Read the accepted interpretation, mapping report, formal statement, proof
  input, bundle manifest, and event trace before claiming semantic success
  because `VERIFIED` proves derivability of the accepted formal rendering,
  not truth of the economic claim.
- Preserve negative evidence and failed attempts because the workflow is an
  audit trail, not a success-only demo.
- Record the exact source artifact and command for every material conclusion
  because model prose and exit codes are not evidence grades.

## Safe A3 entry path

Run the live workflow through the repository wrapper, not a possibly stale
installed module:

```bash
.venv/bin/python scripts_local/a3_run.py <subcommand> ...
```

The wrapper supplies the source path, profile environment, and tool paths.
Use it for `ingest`, `interpret`, `review`, `formalize`, `gap-ack`,
`axiom-approve`, `verify`, `bundle`, `replay`, `opinion`, and `status`.

- Do not invoke `python -m leanecon.a3_runner` for live verification after
  source edits because it can load an installed copy and omit source-pinned
  checks.
- Do not invoke local scripts as executables; call them with the project
  Python because their file mode is not guaranteed to be executable.
- Never inline credentials in commands or logs; load the profile environment
  through the wrapper because shell history and approval surfaces can leak
  secrets.
- Confirm the active provider and model pin from repository truth before a
  live run; do not restore or swap a provider from memory.
- Treat provider timeouts, empty responses, and policy denials as evidence of
  runtime or availability failure, not as permission to silently change the
  experiment.

## Lifecycle and review invariants

- Let only an authorized human or AI reviewer emit `ACCEPTED`, `REJECTED`,
  gap acknowledgements, or axiom approvals because interpretation and
  formalization models cannot self-certify meaning.
- Keep `BLOCKED`, `FAILED`, and `REJECTED` distinct: blocked means the run
  could not safely proceed, failed means it ran negatively, and rejected is a
  terminal semantic decision.
- Treat `VERIFIED` and `REJECTED` as terminal for a revision; ingest a new
  revision for changed meaning because post-hoc mutation destroys provenance.
- Update lifecycle transition tables and replay tests in the same change as
  every new runner failure path because replay must describe actual emissions.
- Require `formalize --from-file` for reviewer-authored recovery because
  ad-hoc store injection bypasses the contract and provenance.
- Acknowledge mapping gaps before verification and preserve reviewer identity
  and reviewer kind because the bundle must show who accepted the meaning.

## Formalization and Lean proof rules

- Review `statement_text`, the target theorem, and the mapping report before
  accepting a formal candidate because compiling syntax can still be vacuous,
  inverted, or semantically incomplete.
- Treat the formalizer as a drafting aid; use reviewer-authored Lean when the
  model repeatedly violates static contracts because prompting is not a
  verification method.
- Compile the exact proof input before review and require a kernel axiom audit
  (`#print axioms`) with no `sorryAx`; a zero exit code alone is insufficient.
- Keep theorem declarations, scaffolding definitions, and static scans
  declaration-aware because a global punctuation or text match can reject
  valid Lean or accept a contaminated proof.
- Declare the verifier's `target_theorem` at the module root because the
  verifier resolves and audits that exact name.
- Confirm Core-importing bundles contain the dependency audit, workspace
  identity, and `12_core_pin` evidence because a green proof without the pin
  is not a verified Core result.
- Re-run replay after lifecycle or artifact changes because event ordering and
  artifact references are part of the product contract.

## Prediction-first evaluation

- Commit numbered predictions, confidence, and hurt bars before live probes
  because post-hoc scoring turns a test into a rationalization.
- Keep claim text fresh and deconflicted, and use the sealed-set protocol for
  holdouts because prompt tuning on spent examples invalidates measurement.
- Score stored artifacts rather than subprocess exit status because commands
  can exit successfully while a claim or provider result is `FAILED`.
- Separate CI fixture evidence from live provider evidence and record provider
  calls, latency, formal artifacts, and traces because they answer different
  questions.
- Do not change a provider pin on a small noisy sample; browse candidates and
  run a powered A/B only after a pre-committed trigger because runtime
  variance is not a causal improvement.

## Core promotion and gate handoff

- Promote vocabulary declarations only from reviewed economic concepts and
  accepted artifacts because a model's glossary or textbook list is not design
  authority.
- Compile every proposed Core module and inspect declaration signatures,
  namespace collisions, examples, and baseline axioms before review because
  paper designs hide Lean failures.
- Keep a per-declaration review package, explicit in/out-of-scope decisions,
  and CTO approval records because Core changes alter the semantic contract.
- When deferring a gate, write a self-contained init document with scope,
  locked decisions, evidence paths, acceptance criteria, and stop points
  because the next session must not reconstruct intent from chat.
- Stop at the designated CTO gate before implementation, Core declarations,
  commits, tags, or merges when the gate is unresolved because an empty or
  conditional response is not approval.

## Release and checkpoint audits

- Distinguish internal gates from product versions because a gate number is
  not a SemVer promise.
- Earn a release only with its release packet, tag, and repository evidence;
  a version string or branch name alone is not a release.
- For “where do we stand?” audits, inspect remote `main`, open PRs, local
  checkout, and drafts separately because each surface can report a different
  state.
- Report current versus desired state, evidence grade, hygiene, and open
  decisions in separate fields because progress claims otherwise overstate
  readiness.
- Keep CTO ownership of economics meaning, Core ontology, scope, and tags;
  authorized AI reviewers and bot contributors may perform only their
  explicitly delegated review or operational roles.

## Reference routing

Load the matching support file before doing detailed work:

| Task | Reference |
|---|---|
| A3 walkthrough, claim curation, or evaluation evidence | `references/walkthrough-2026-08-06.md`, `references/v2-phase1-claim-curation.md` |
| Formal recovery and release runbooks | `references/v1-ship-2026-08-08.md`, `references/oos-batch-complete.md` |
| Lean proof authoring or kernel audit | `references/lean-proof-patterns.md`, `references/lean-kernel-audit.md` |
| Core design, promotion, or gate handoff | `references/core-promotion-workflow.md`, `references/gate6-core-design-session.md`, `references/gate6-p5-exit-session.md` |
| Probe repair, sealed evaluation, or v3/v4 measurement | `references/v35-phase2-probe-repair.md`, `references/v35-g3-sealed-holdout-2026-08-23.md`, `references/v3-phase1-3-2026-08-13.md`, `references/v4-direction-and-release-tag.md` |
| Release roadmap or progress audit | `references/release-roadmap-v0-to-v3.md`, `references/progress-audit-2026-08-12.md` |
| Registry consistency check | `scripts/glossary_registry_check.py` |
| Reviewer-authored formal input | `templates/from_file_candidate.json` |

When a reference contains a date, issue number, branch name, or incident
record, use it as historical evidence only; verify current repository state
before applying the lesson.

## Attribution

Prepared by Hermes Agent under CTO direction. The CTO remains accountable for
economic meaning, Core ontology, scope, and release decisions; authorized AI
reviewers and operational bots do not replace that authority.
