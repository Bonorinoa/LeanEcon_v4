# v3.5 metric definitions (frozen for this sprint)

**Status:** FROZEN 2026-08-23 (DECISION_LOG 52). Supersedes
`docs/v3/METRICS.md` §3 operationalization. Changes after this file
require a DECISION_LOG entry.

## Case-level columns (`eval_formalizer.score_case`)

| Column | Definition |
|---|---|
| `first_try_valid` | attempt 1 of `revision_history` is audit-clean (no `static_problems`). Probe not required. |
| `attempts_to_valid` | 1-based index of the first audit-clean attempt; `null` if none within budget. |
| `static_reject_class` | legacy histogram bucket of the blocking reject: `sorry` \| `proof_body` \| `d1` \| `d4` \| `other`. Strings are frozen by test contract. |
| `fidelity_property` | P1–P6 label per DECISION_LOG 50 (mapping below). |
| `probe_compiles` | fresh kernel signal on the accepted statement (`statement_probe`). |
| `probe_failure_class` | when probe failed: deterministic subclass of `stderr_tail` (taxonomy below). `null` when compiles or no signal. |
| `vacuity_flag` / `inversion_flag` | substance heuristics (P4 approximations; reviewer owns truth). |
| `draft_complete` | **strict conjunction:** audit-clean ∧ probe compiles ∧ non-vacuous ∧ non-inverted. The earn predicate. Never claimed from fixture sets. |

## Report-level rates

| Rate | Definition |
|---|---|
| `audit_clean_rate` | share of cases with `attempts_to_valid` ≠ null. |
| `elaborates_rate` | share with `probe_compiles` true. |
| `draft_complete_rate` | ≤ min(audit_clean_rate, elaborates_rate) by construction. |

The split exists so partial results stay legible without narration
(v4h1 was 100% clean / 0% elaborates).

## Fidelity-property ontology (P1–P6, DECISION_LOG 50)

Observed rejects are *measurements of* property violations.

| Property | Meaning | Decider | Bucket mapping |
|---|---|---|---|
| P1 surface legality | parseable, sorry-free Lean text | machine | `sorry`, `proof_body`, `other` |
| P2 elaboration | signature type-checks in pinned workspace | kernel signal | (probe column) |
| P3 contract | D1 FQ core ids, D4 namespaces, complete mapping | machine | `d1`, `d4` |
| P4 substance | non-vacuous, conclusion is the claim's conclusion | machine approximates; reviewer owns | vacuity/inversion flags |
| P5 semantic fidelity | Lean statement means the English claim | reviewer only | none |
| P6 proof adequacy | kernel derivation of this statement exists | kernel | verify stage only |

New errors get labeled by violated property. If none fits, amend the
ontology via DECISION_LOG — do not grow a bucket zoo.

## Probe-failure subclass taxonomy

`clean_or_no_signal`, `unknown_identifier`, `binder_annotation`,
`ambiguity`, `instance_synthesis`, `type_mismatch`, `unknown_universe`,
`recursion_depth`, `sorry`, `syntax`, `unclassified`.
Ordering note: identity errors match before type mismatches (an unknown
id cascades into type noise). A sorry-carrying compilation classifies as
`sorry` even though exit code is 0 — compile ≠ pass.

## Population rules (baselines and sealed sets alike)

- Partition by provenance: `model_draft` vs `reviewer_authored`
  (`source == "from_file"`, `reviewer_authored_formal`, or an
  all-`reviewer_authored_recovery` mapping report). **Never pool**.
- Sealed sets are spent after one pass; dev diagnostics never unspend
  them and never substitute for the fresh sealed holdout.
- Evidence grades: CI fixture scoring < dev diagnostic < sealed holdout.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
