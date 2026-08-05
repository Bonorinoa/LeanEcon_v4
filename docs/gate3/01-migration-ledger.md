# 3.1 Migration Ledger

The ledger is a governance record, not a copy list. Every v3 class is treated as evidence, an idea source, or historical material. Under E2-1, custom implementation defaults to `REBUILD`, `INSPIRATION`, or `HISTORICAL-DISCARD`; `IMPORT` and `ADAPT` require a written CTO exception. No exceptions are proposed here.

## Full schema

| Field | Meaning |
|---|---|
| `artifact_id` | Stable v4 ledger identifier. |
| `artifact_class` | Major class, not every file. |
| `v3_evidence` | Frozen tag/commit and representative paths. |
| `observed_scope` | What the class contained, without reproducing implementation. |
| `disposition` | `REBUILD`, `INSPIRATION`, `HISTORICAL-DISCARD`, or approved exception. |
| `e2_1_default` | Whether the disposition is the plan default. |
| `exception_justification` | Required and non-empty only for import/adapt. |
| `v4_destination` | Contract or future implementation area. |
| `trust_boundary_notes` | Leakage, provenance, or authority constraints. |
| `required_tests` | Tests required when implementation is authorized. |
| `residual_risk` | Risk left for CTO review. |
| `reviewer` | `CTO` for semantic approval; `Hermes Agent` for preparation. |
| `decision` | `PROPOSED — CTO REVIEW REQUIRED`. |

## Populated major-class ledger

| ID | Artifact class / frozen evidence | Observed scope | Disposition | v4 destination | Boundary and required tests |
|---|---|---|---|---|---|
| L1 | Lean workspace: `lean_workspace/`, toolchain, lake manifest | Lean modules, package metadata, theorem metadata | REBUILD | Gate 4 pinned workspace; later Core design | Rebuild declarations from approved contracts; clean-clone build, no-sorry scan, dependency/axiom audit |
| L2 | Economics/formal libraries: `lean_workspace/LeanEcon/**` | Domain-facing formal material across micro, macro, equilibrium, optimization, games | REBUILD | Gate 6 Core | No v3 declaration copied; CTO promotion record, semantic review, counterexample tests |
| P1 | Python services: `src/api`, `formalizer`, `planner`, `prover`, `lean`, `observability`, retrieval, guardrails | API, orchestration, provider-facing and Lean-facing behavior | REBUILD | `src/` only after Gate 4 contracts | Boundary tests, typed failures, deterministic replay, no gold access |
| P2 | Prompts and provider logic: `src/**/prompts.py`, provider modules, skills | Prompt templates, model routing, provider assumptions | REBUILD | Adapter contracts and controlled prompt assets | Core cannot contain model IDs or credentials; malformed-output and outage tests |
| S1 | Schemas/models/events: service models and event payloads | Input/output and observability shapes | REBUILD | Gate 3 contract schemas; implementation later | Schema validation, version compatibility, digest and trace linkage |
| T1 | Tests: `tests/` | Unit, API, Lean, state-machine, evaluation and guardrail tests | INSPIRATION | New contract and boundary tests | Do not port blindly; gold-isolation, egress, lifecycle, verification tests |
| C1 | CI: `.github/workflows/ci.yml`, `lean-base-image.yml` | Build/test automation | REBUILD | v4 CI after contracts and implementation | Clean checkout, pinned dependencies, secret scan, schema and boundary tests |
| D1 | Docker: `Dockerfile*`, ignore file | Runtime/build images | REBUILD | Gate 4 reproducible environment | Digest-pinned image/build, no secret inclusion, clean build |
| C2 | Config/deployment: `pyproject.toml`, `railway.toml`, `.env.example`, editor config | Dependencies, runtime and deployment settings | REBUILD | v4 configuration after contract approval | Unknown settings fail closed; credential names only; reproducibility checks |
| D2 | Evaluation/benchmark artifacts: `benchmark_baselines/`, `evals/`, `data/` | Scores, fixtures, evaluation harness and data | INSPIRATION + HISTORICAL-DISCARD | New evaluator-side corpus, separately authored | v3 scores not comparable; sealed gold inaccessible to runtime; provenance tests |
| H1 | Documentation/logs/skills: `docs/`, `skills/`, README | Historical explanations and operating lessons | INSPIRATION; selected history only | Compact v4 docs and evidence references | No wholesale prose/code copy; attribution and source references |
| X1 | `.codebase-memory/` | Generated graph/index state | HISTORICAL-DISCARD | Never enters v4 | Do not migrate; no dependency or release use |
| X2 | Generated/cache/secrets candidates | Build output, caches, credentials, transient payloads | HISTORICAL-DISCARD | None; retain only in frozen v3 if needed | Never migrate or stage; secret scanning and artifact exclusion tests |

## Exception register

**None proposed.** Any future `IMPORT` or `ADAPT` must identify exact source, license/provenance, copied surface, contamination review, destination, tests, and CTO approval before use.

**Attribution:** Ledger prepared by Hermes Agent under CTO direction; dispositions require CTO approval.
