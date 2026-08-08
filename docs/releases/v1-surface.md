# v1.0.0 frozen surface

Breaking changes after this freeze require a major version bump.

## CLI (`leanecon-a3` / `python -m leanecon.a3_runner`)

Supported live wrapper: `scripts_local/a3_run.py`.

| Subcommand | Role |
|---|---|
| `ingest` | DRAFT claim revision |
| `interpret` | live interpret → REVIEW_REQUIRED |
| `review` | ACCEPTED \| REJECTED (`--reviewer`, `--reviewer-kind`) |
| `formalize` | live **or** `--from-file` / `--statement-file`+`--mapping-file` |
| `gap-ack` | acknowledge mapping gaps |
| `axiom-approve` | per-run axiom list |
| `verify` | proof → bundle → VERIFIED\|FAILED\|BLOCKED |
| `bundle` | re-validate current bundle |
| `replay` | deterministic trace replay |
| `status` | claim pointers |

## Schemas

- EI: `references/gate3/ei_schema_draft.json` @ **1.0.0**
- Bundle: `bundle_schema_version` **1.0.0**, checklist items 1–12 (`12_core_pin`)
- Events: append-only envelope (`leanecon.events`); digests on artifacts

## Provider capabilities (MVP map)

| Capability | Status in v1 |
|---|---|
| `interpret` | live (mistral-medium-3-5 via adapter) |
| `formalize` | live (labs-leanstral-1-5) + file recovery |
| `prove_or_repair` | **enum only — unused** |
| `diagnostic_probe` | A1 |

## Reviewer

`docs/gate3/08-reviewer-policy.md` — human or AI; CTO accountable.

## Core modules (v1 freeze)

`lean_workspace/LeanEcon/Core/{Primitives,Preferences,Utility,Constraints,Choice,Equilibrium,Theorems}.lean`
