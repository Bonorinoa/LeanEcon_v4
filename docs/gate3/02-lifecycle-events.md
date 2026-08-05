# 3.2 Lifecycle and Event Contracts

These contracts make outcomes distinguishable to a reviewer who need not inspect Lean. A claim is an economic assertion; a capability is a service function such as interpretation or formalization.

## Claim lifecycle

Proposed state set follows the plan:

`DRAFT → INTERPRETED → REVIEW_REQUIRED → ACCEPTED → FORMALIZED → PROVING → VERIFIED`

**Important distinction:** `INTERPRETED` is not `FORMALIZED`. `INTERPRETED` means the system produced a structured, human-readable reading of the English claim. `FORMALIZED` means a candidate Lean statement was written from an accepted interpretation. Interpretation is meaning; formalization is a mathematical statement to be checked.

`REVIEW_REQUIRED` is intentionally narrow: it is the semantic human-review gate for meaning, assumptions, and ambiguities after interpretation. Provider outages, missing workspace pins, and policy denials are `BLOCKED`; proof failures are `FAILED`. Later human approvals are recorded as approval events rather than placed in a vague general-purpose human-in-the-loop state.

Failure exits: any active processing state may reach `FAILED` when work ran and produced a negative result, or `BLOCKED` when a prerequisite/capability prevented evaluation. `REJECTED` is a reviewer decision from `REVIEW_REQUIRED`.

| State | Meaning | Terminal? |
|---|---|---|
| `DRAFT` | User claim exists but has not been interpreted. | No |
| `INTERPRETED` | Versioned interpretation was produced; not approved. | No |
| `REVIEW_REQUIRED` | Human decision is required before formalization. | No |
| `ACCEPTED` | CTO/authorized reviewer approved the interpretation. | No |
| `REJECTED` | Reviewer rejected meaning or assumptions. | Yes for this revision |
| `FORMALIZED` | Candidate formal statement exists and links to accepted interpretation. | No |
| `PROVING` | Bounded verification/proof work is running. | No |
| `VERIFIED` | Complete verification bundle satisfies the strict bar. | Yes for this revision |
| `FAILED` | Evaluation ran but statement, proof, or validation failed. | Retryable only through a new attempt/revision |
| `BLOCKED` | Evaluation could not safely run, e.g. outage, missing pin, or policy denial. | Retryable when blocker clears |

Only a reviewer may emit `ACCEPTED` or `REJECTED`. The system may emit processing states and `FAILED`/`BLOCKED`, but never semantic approval or `VERIFIED` without bundle validation.

## Capability metadata

These labels are diagnostic vocabulary, not claim states. They answer whether a dependency can perform the next step:

- `HEALTHY` — usable within the configured probe.
- `DEGRADED` — usable with a recorded limitation.
- `UNAVAILABLE` — do not start the dependent step; the claim outcome is normally `BLOCKED`, not `FAILED`.

For MVP, emit them only for A1 diagnostics and as state-dependent metadata in a verification bundle. Do not require a capability snapshot on every lifecycle event. Numeric thresholds, sampling windows, dashboards, and SLOs are deferred.

## Minimal reason-code registry

Start with the codes needed by A1/A3: `SEMANTIC_AMBIGUITY`, `USER_REJECTED`, `LEAN_SYNTAX_ERROR`, `SORRY_FOUND`, `AXIOM_VIOLATION`, `PROOF_TIMEOUT`, `PROVIDER_UNAVAILABLE`, `INPUT_REJECTED`, `WORKSPACE_UNPINNED`, and `LSP_UNAVAILABLE`. Add a code only when a real failure cannot be represented clearly by the existing set.

Codes are stable identifiers, not prose. `HEALTH_CHECK` is an event type, never a claim state.

## Minimal event envelope

Every event has: `schema_version`, `event_id`, `event_type`, `run_id`, `claim_id` (nullable only for standalone health checks), `emitted_at` (UTC), `source_component`, `actor`, `state_before`, `state_after`, `reason_codes[]`, `payload_class`, and `trace_ref`. Content digests belong in artifact metadata and the verification bundle, not every event. Capability snapshots are emitted only for diagnostics and bundle metadata.

Events are append-only. Corrections append a new event rather than mutating history.

## Transition rules

| From | To | Trigger |
|---|---|---|
| `DRAFT` | `INTERPRETED` / `BLOCKED` | System interpretation attempt. |
| `INTERPRETED` | `REVIEW_REQUIRED` / `FAILED` | Schema-valid interpretation or unusable output. |
| `REVIEW_REQUIRED` | `ACCEPTED` / `REJECTED` | Human reviewer decision. |
| `ACCEPTED` | `FORMALIZED` / `BLOCKED` | Formalizer available and output valid. |
| `FORMALIZED` | `PROVING` / `FAILED` | Verification attempt begins or candidate invalid. |
| `PROVING` | `VERIFIED` / `FAILED` / `BLOCKED` | Bundle validator, negative result, or inability to evaluate. |

No transition may skip `REVIEW_REQUIRED` for a new interpretation. A changed accepted interpretation invalidates downstream artifacts and starts a new revision.
