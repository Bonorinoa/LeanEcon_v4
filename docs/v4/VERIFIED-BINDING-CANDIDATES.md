# VERIFIED-binding candidates (not a sprint)

**Status:** diagnosis only. Extracted from uncommitted Codex
`trust-sprints-1-2` WIP (stash dropped 2026-10-06). Do **not**
re-apply that tree. Re-implement against `main` only if G0 picks
this slice.

These are fail-closed integrity holes in today's `VERIFIED` claim
(`origin/main` @ `07131db`). They are real. They are not the
product bottleneck after DL 57.

| Candidate | What `main` does today |
|---|---|
| Kernel checks the proof file, not stored signature + body | `verify_candidate` writes `--proof` + `#print axioms <name>` |
| Gap-ack / axiom / approval = last record on the claim | `list_review_records(...)[-1]` |
| Bundle schema 1.0.0, one `result` | no `verifier_outcome` split; no recomputed cross-digest graph |
| Same-name different proposition can compile | no `FORMAL_STATEMENT_MISMATCH` before Lean |

Threat model of the WIP (keep): the digest graph is not a signature.
An actor who rewrites the whole local store and rehashes is out of
scope.

**Attribution:** Hermes Agent under CTO direction.
