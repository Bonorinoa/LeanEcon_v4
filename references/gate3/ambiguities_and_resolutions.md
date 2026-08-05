# Ambiguities and Proposed Resolutions

| ID | Plan gap | Proposed resolution | Impact if wrong | CTO sign-off |
|---|---|---|---|---|
| A1 | Plan lists lifecycle states but not transition retry semantics. | Ten listed states; `REVIEW_REQUIRED` is semantic-only; `BLOCKED` is retryable; `FAILED` requires a new attempt/revision. | Retry/reporting semantics differ. | CTO approved |
| A2 | Capability thresholds are unspecified. | S3a diagnostic labels only; no thresholds, health matrix, or SLOs in Gate 3. | Health labels may be coarse. | CTO approved |
| A3 | Axiom authority is unspecified. | Per-run reviewer record referenced by `axiom_approval_ref`; no repo-wide allowlist for MVP. | Trust review remains per run. | CTO approved |
| A4 | Digest algorithm and scope are unspecified. | SHA-256 for trust artifacts/bundles; event envelope remains minimal. | Canonicalization is Gate 4 detail. | CTO approved |
| A5 | Restricted opt-in UX/API is unspecified. | `RESTRICTED` is hard-denied in MVP; no opt-in mechanism until needed. | Future restricted use requires new policy decision. | CTO approved |
| A6 | Project-data default is unspecified. | `PROJECT` is the default development class through the single boundary; gold/v3-hidden material remains denied. | External-user policy is deferred. | CTO approved |
| A7 | Model fallback/version pinning is unspecified. | No silent fallback; exact pin policy is Gate 4 operational work. | Availability may be lower. | CTO approved |
| A8 | Event standard is unspecified. | Use a small project envelope, not a dependency on CloudEvents; preserve equivalent causal fields. | Interoperability versus simplicity tradeoff. | CTO approved — covered by decision 4 |
| A9 | “Staged uncommitted” can mean index or worktree. | Stage only package files in Git index; docs-only commit is authorized after CTO closure. | CTO review workflow differs. | Resolved — docs-only commit authorized |
| A10 | v3 paths tempt import/adapt. | No exceptions proposed; all custom implementation is rebuild/inspiration/discard. | Any exception would require explicit provenance review. | CTO approved — covered by decision 1 |
| A11 | Second CODEOWNERS slot is reserved but no bot exists. | Leave `@Bonorinoa` as sole current owner; do not invent a second identity. | Review enforcement remains interim governance. | Already approved in Gate 2 |
