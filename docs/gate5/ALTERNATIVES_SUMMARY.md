# Gate 5 Decisions and Alternatives Summary

Companion to [a3-design.md](a3-design.md). Each row records the alternatives
considered for a Gate 5 design point, the proposed resolution, and whether a
CTO decision is required. Nothing here is implemented or committed.

| # | Topic | Alternatives considered | Proposed resolution | CTO? |
|---|---|---|---|---|
| 1 | `none_noted` representation | Free-text "no ambiguities"; sentinel entry in `ambiguities`; explicit marker field | Explicit `none_noted: true` marker in the EI candidate plus a required reviewer acknowledgement flag in the review record; approval refused without it (draft-schema exercise) | Yes |
| 2 | Unapproved axiom on first proof attempt | `BLOCKED` pending review; silent acceptance; `FAILED`/`AXIOM_VIOLATION` with full list | `FAILED`/`AXIOM_VIOLATION` per gate3/05; bundle carries the plain-language axiom list; reviewer per-run record (`axiom_approval_ref`) closes it, then retry on the same candidate | Yes |
| 3 | Unmapped material EI elements | Silently omit; block formalization entirely; visible gaps blocking `PROVING` | Candidate delivered with visible gap list; `PROVING` refused until gaps closed or a reviewer gap-acknowledgement record exists (same mechanism as axiom records) | Yes |
| 4 | Economics vocabulary without Core | Use Mathlib only (limits claims); skip formalization of unmapped terms; A3-local scaffolding definitions | A3-local scaffolding definitions inside candidate files, labeled, reviewed via mapping report, never promoted to Core without Gate 6 | Yes |
| 5 | Proof source in Gate 5 | Auto-proof attempt (B2-lite); no proofs; manual input only | Manual only: reviewer file or reviewed v4 fixture; no `prove_or_repair` call; provenance recorded | Yes |
| 6 | EI validation | Hand-rolled validator; external schema library | Add `jsonschema` (standard, schema-driven; the draft schema is the source of truth) | Yes |
| 7 | Verifier invocation | `lake build` module target; raw `lean` on scratch file | `lake env lean <candidate>` in pinned workspace with recorded command; `#print axioms` for kernel-level audit | No |
| 8 | Candidate file lifecycle | Commit candidates as fixtures; fully ephemeral | Generated per-run under `lean_workspace/LeanEcon/A3/<claim>/`, gitignored; only reviewed fixtures committed | No |
| 9 | Reason-code registry | Add `LEAN_UNKNOWN_IDENTIFIER`, gap/ack codes | Registry unchanged; gaps and `none_noted` are reviewer-record mechanics, not failure codes | Yes |
| 10 | Canonical claims | Any 3–5 micro claims; claims from v3; proposals in Appendix A | Four proposed micro claims, each exercising a different frame element; CTO reviews before A3 (locked EI decision 4) | **Yes — required** |
| 11 | `INTERPRETED`→`REVIEW_REQUIRED` on invalid output | Go to `BLOCKED`; stay `INTERPRETED` | `FAILED`/`PROVIDER_INVALID_OUTPUT` per transition table (work ran, negative result) | No |
| 12 | Raw provider payload retention | Retain all responses for debugging; retain none | Retain only validated artifacts + digests; raw responses never stored by default (gate3/05) | No |
| 13 | Replay semantics | Re-execute provider calls; rebuild Lean | Deterministic re-validation of recorded events + digests; no network, no Lean rebuild | No |
| 14 | Reviewer identity | Anonymous review; per-command identity | Review commands require reviewer identity (env or flag) recorded in the event `actor` field | No |

**Attribution:** Prepared by Hermes Agent (Nous Research) under direction of the
CTO. The CTO remains the sole semantic approver.
