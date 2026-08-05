# 3.5 Auditable Verification Bundle

`VERIFIED` is a trust claim, not a synonym for “an automated tool returned success.” The bundle must let the CTO identify exactly what was interpreted, approved, checked, and under which environment.

## Required `VERIFIED` checklist

All items are required unless the CTO records a written waiver. A waiver changes the label or release posture; it must not silently preserve `VERIFIED`.

1. **Exact user claim** — original claim digest and retained audit representation.
2. **Accepted interpretation** — immutable content digest and human approval event.
3. **Accepted formal statement** — linked to the interpretation and approval revision.
4. **Kernel check** — Lean's trusted checker accepts the statement/proof in the pinned workspace.
5. **No incomplete proof** — no `sorry`, `admit`, or equivalent placeholder.
6. **Axiom/dependency audit** — complete transitive dependencies and axioms compared with an approved policy/allowlist.
7. **Pinned workspace identity** — Lean toolchain, Mathlib/package revisions, lock/manifest digest, and workspace identity.
8. **Content digests** — SHA-256 digests for claim, interpretation, formal statement, proof/source, diagnostics, and bundle manifest.
9. **Trace links** — claim revision ↔ approval ↔ formalization ↔ proving attempt ↔ verification event ↔ bundle.
10. **State-dependent metadata** — capability status, budgets, compiler result, sanity checks, and relevant limitations.
11. **Reproducible manifest** — inputs, versions, timestamps, builder identity, commands/entrypoint, and environment/container digest where applicable.

The proven or failed input statement remains available for audit. Sensitive provider payloads are not retained by default; digests and policy metadata are retained.

## Outcome distinctions

- `VERIFIED`: every requirement passes.
- `FAILED`: evaluation ran and the claim/proof failed, including syntax error, `sorry`, disallowed axiom, or kernel rejection.
- `BLOCKED`: safe evaluation could not occur, such as provider outage, missing workspace pin, unavailable LSP, or restricted data denied.
- `REJECTED`: human rejected the interpretation; not a proof failure.

## Bundle manifest fields

`bundle_schema_version`, `bundle_id`, `claim_id`, `claim_revision`, `claim_digest`, `interpretation_digest`, `formal_statement_digest`, `proof_artifact_digest`, `workspace_identity`, `axiom_audit`, `axiom_approval_ref`, `dependency_audit`, `trace_refs`, `capability_snapshots`, `sanity_checks`, `result`, `failure_reasons`, `reproducibility`, `created_at`, `builder_identity`, `retention_policy`.

`axiom_approval_ref` points to the per-run reviewer record containing reviewer identity, timestamp, approved axiom list, and the bundle/run it covers. A repo-wide axiom allowlist is not required for the MVP.

**Gate 4 boundary:** schema validation, replay tests, actual Lean checks, and policy implementation are not part of this package.

## Glossary

- **Kernel check:** acceptance by Lean's trusted checker, rather than an LLM assertion.
- **`sorry`/`admit`:** incomplete-proof placeholders; either invalidates `VERIFIED`.
- **Axiom:** an assumed proposition. The audit records which assumptions were used.
- **Dependency:** a library or declaration needed by the checked artifact.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction; the CTO approves the semantic and trust policy.
