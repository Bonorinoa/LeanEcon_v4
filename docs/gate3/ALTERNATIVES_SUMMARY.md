# Decisions and Alternatives Summary

| Topic | Alternatives considered | Proposed resolution | CTO? |
|---|---|---|---|
| Ledger | Copy/adapt broadly; E2-1 default; discard all history | E2-1: rebuild custom implementation, use inspiration for lessons, historical-discard unsafe/generated material; no exceptions | Yes |
| Lifecycle richness | Minimal states; plan's ten states; add audit state | Use plan's ten states; represent audit as a bundle/event, not another claim state | Yes |
| `BLOCKED` | Terminal failure; retryable operational outcome | Retryable when blocker clears; new attempt/event preserves history | Yes |
| Interpretation schema | Free-form JSON; minimal fields; explicit versioned contract | Explicit v1 fields with additive evolution and immutable accepted revisions | Yes |
| Verification | Compile-only; checklist with waivers; strict bundle | Strict all-required bundle; waiver changes release posture | Yes |
| Axiom policy | Any compiling axiom; hard-coded list; reviewed policy artifact | Reviewed allowlist/policy artifact, exact contents deferred as a named decision | Yes |
| Provider design | Vendor IDs in core; one vendor-specific service; capability core + adapters | Capability core; adapters own vendor details; MVP mapping documented only | Yes |
| MVP models | Lock model IDs everywhere; aliases/fallbacks; configured mapping | Map the two named models outside core; no silent fallback in MVP | Yes |
| Data classes | Allow all project data; two classes; three classes fail-closed | `PUBLIC`/`PROJECT`/`RESTRICTED`, unknown→restricted; restricted per-run opt-in | Yes |
| Project opt-in | No opt-in; all project opt-in; policy-controlled approved-provider use | Proposed approved-provider use with audit; CTO must decide whether project also needs per-run opt-in | Yes |
| Restricted opt-in shape | Env flag; durable permission; run-scoped approval | Per-run approval event with scope, approver, expiry, and payload digest | Yes |
| Event standard | CloudEvents dependency; ad hoc events; small project envelope | Small project envelope with equivalent causal fields; no dependency chosen | Yes |
| Staging | Worktree only; Git index staging | Stage docs only, uncommitted, so CTO can inspect exact package | No |
