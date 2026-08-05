# Verification Manifest Field Rationale

| Field group | Why it exists |
|---|---|
| Claim/interpretation/formal/proof digests | Prevents substitution between meaning, statement, and checked artifact. |
| Workspace identity | Makes the checker environment reproducible instead of implicit. |
| Axiom/dependency audit | Shows what trusted assumptions and libraries support the result. |
| Trace references | Allows reconstruction from user input through approval and verification. |
| Capability snapshots | Explains degraded or unavailable conditions at evaluation time. |
| Sanity checks and result | Preserves both successful and failed input evaluation context. |
| Reproducibility | Identifies commands, versions, builder, timestamps, and environment identity. |
| Retention policy | Prevents accidental retention of sensitive provider payloads. |
