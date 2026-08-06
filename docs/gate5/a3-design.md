# Gate 5 — A3 Minimal Verified Workflow: Design Review Package

**Status:** design review only — no implementation, no schema freeze, no commit.
This document specifies the **inner workings** of the A3 workflow so the CTO can
interpret evaluation results before any code is written.

**Contracts this design implements:** Gate 5 of the migration plan, plus locked
Gate 3 contracts (`docs/gate3/02–07`, `DECISION_LOG.md`) and the EI design
approval of 2026-08-05 (Option B, four locked decisions). The EI schema remains
a draft to be exercised by A3; every draft exercise is flagged below.

**Reader:** no Lean knowledge required. Lean is referenced only through its
role as the kernel checker and through plain-language names.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction;
the CTO remains the sole semantic approver.

---

## 0. Scope

**In scope (Gate 5 exit evidence):** interpretation service (`mistral-medium-3-5`),
formalization service (`labs-leanstral-1-5`), verifier + pinned-workspace
interface, approval-event capture, state-transition validation, artifact and
bundle export, proven/failed input statement with sanity-check metadata, and a
trace-replay test. Proofs are **manually supplied** (reviewer or reviewed v4
fixture); no `sorry`/`admit` is accepted for `VERIFIED`.

**Explicitly out of scope:** B2 bounded proof loop, `prove_or_repair` calls,
LeanEcon Core declarations (Gate 6), retrieval, production `VERIFIED` claims,
corpus expansion. No runtime component may call a provider directly or read
credentials; the Gate 3/A1 boundary rules carry over unchanged.

---

## 1. Lifecycle in A3: states, triggers, and the BLOCKED/FAILED/REJECTED branch

A3 uses the full ten-state lifecycle from `docs/gate3/02`. The cardinal rule:
**only a human reviewer emits `ACCEPTED` or `REJECTED`; the system emits every
processing state and `FAILED`/`BLOCKED`; `VERIFIED` is emitted only by the
bundle validator after all checks pass.**

### 1.1 State meanings as A3 uses them

| State | Meaning in A3 | Who may enter it | Terminal? |
|---|---|---|---|
| `DRAFT` | Claim record created with classification; not yet interpreted | system (ingest) | no |
| `INTERPRETED` | Schema-valid EI candidate produced; meaning not yet approved | system (interpret) | no |
| `REVIEW_REQUIRED` | Human semantic decision required before formalization | system (validate) | no |
| `ACCEPTED` | Reviewer approved the interpretation | **reviewer only** | no |
| `REJECTED` | Reviewer rejected meaning/assumptions | **reviewer only** | yes, for this revision |
| `FORMALIZED` | Candidate Lean statement + mapping report exist, linked to accepted EI | system (formalize) | no |
| `PROVING` | Verification attempt running | system (verify start) | no |
| `VERIFIED` | Complete bundle satisfies the strict bar | system (bundle validator) | yes, for this revision |
| `FAILED` | Work ran and produced a negative result (compile, sorry, axiom, timeout, invalid provider output) | system | retryable via new attempt/revision |
| `BLOCKED` | Evaluation could not safely run (outage, unpinned workspace, policy denial) | system | retryable when blocker clears |

### 1.2 Transition table with triggers

| From | To | Trigger | Actor |
|---|---|---|---|
| `DRAFT` | `INTERPRETED` / `BLOCKED` | interpretation attempt succeeds / provider unavailable | system |
| `INTERPRETED` | `REVIEW_REQUIRED` / `FAILED` | EI schema-valid / provider output unusable (`PROVIDER_INVALID_OUTPUT`) | system |
| `REVIEW_REQUIRED` | `ACCEPTED` / `REJECTED` | human review decision (+ `none_noted` acknowledgement when required) | **reviewer** |
| `ACCEPTED` | `FORMALIZED` / `BLOCKED` | formalizer available and candidate structurally valid / unavailable | system |
| `FORMALIZED` | `PROVING` / stays `FORMALIZED` | verification attempt starts / mapping report incomplete or proof input missing or sorry found | system |
| `PROVING` | `VERIFIED` / `FAILED` / `BLOCKED` | bundle validator / negative result / could not run | system |

No transition may skip `REVIEW_REQUIRED` for a new interpretation, and a
changed **accepted** interpretation invalidates all downstream artifacts
(§3.4). `REJECTED` is terminal for that revision; the reviewer or the claimant
opens a new revision at `DRAFT`.

### 1.3 Branch diagram

```text
                    ┌──────────────────────────────────────────────────────┐
                    │                  system commands                     │
                    └──────────────────────────────────────────────────────┘

  DRAFT ──interpret──▶ INTERPRETED ──validate──▶ REVIEW_REQUIRED
    │                        │                         │
    │ provider down          │ provider malformed      │
    ▼                        ▼                         ▼
 BLOCKED                  FAILED                    [human gate]
 (PROVIDER_UNAVAILABLE)   (PROVIDER_INVALID_OUTPUT)   │
                                                      ├── reviewer: ACCEPTED ──────────────▶ ACCEPTED
                                                      └── reviewer: REJECTED ──(terminal)──▶ REJECTED
                                                                                               │
                                                                          new revision ──▶ DRAFT

 ACCEPTED ──formalize──▶ FORMALIZED ──(mapping complete + proof input)──▶ PROVING
    │                        │                                            │
    │ provider down          │ gaps or no proof: stays FORMALIZED        │
    ▼                        ▼ (visible, no state change)                ├── bundle validator ──▶ VERIFIED
 BLOCKED                                                                    │
 (PROVIDER_UNAVAILABLE)                                                    ├── negative result ──▶ FAILED
                                                                           │    (LEAN_SYNTAX_ERROR, SORRY_FOUND,
                                                                           │     AXIOM_VIOLATION, PROOF_TIMEOUT)
                                                                           └── could not run ──▶ BLOCKED
                                                                                (WORKSPACE_UNPINNED, PROVIDER_UNAVAILABLE,
                                                                                 LSP_UNAVAILABLE, RESTRICTED_BLOCKED)
```

### 1.4 Why the three exits are distinct (contract, not convenience)

| Exit | Meaning | Typical reason codes | Reviewer action |
|---|---|---|---|
| `BLOCKED` | The run could not happen safely. Nothing about the claim was decided. | `PROVIDER_UNAVAILABLE`, `WORKSPACE_UNPINNED`, `LSP_UNAVAILABLE`, `RESTRICTED_BLOCKED`, `INPUT_REJECTED` (policy denial) | none — rerun when the blocker clears |
| `FAILED` | The run happened and produced a negative, recorded result. | `LEAN_SYNTAX_ERROR`, `SORRY_FOUND`, `AXIOM_VIOLATION`, `PROOF_TIMEOUT`, `PROVIDER_INVALID_OUTPUT` | depends on code — see §8.4 |
| `REJECTED` | A human rejected the **meaning**. Never a proof or system failure. | `USER_REJECTED`, `SEMANTIC_AMBIGUITY` | decide whether a new revision is warranted |

---

## 2. Data flow: components, objects, digests vs payloads, redaction

### 2.1 Component map

```text
 CTO / reviewer ──review commands + proof input──▶  a3_runner  ──▶ EventLog (append-only JSONL)
      ▲                                                 │││
      │                                        ┌────────┤├─────────┐
      │                                        │        ││         │
      │                            interpretation ◀┘└▶ provider    │
      │                            formalization ───▶ boundary ───▶ Mistral
      │                                        │        (adapter,   │  interpret → mistral-medium-3-5
      │                                        │         redact)   │  formalize → labs-leanstral-1-5
      │                                        │                   │
      │                                        └──▶ verifier ───▶ pinned workspace (lake env lean,
      │                                                     #print axioms)
      │                                        │
      │                                        └──▶ bundle builder ──▶ artifacts/a3/<bundle_id>/
      │                                                     (+ manifest.json)
      ▼
  bundle + trace (human-readable)
```

Only `leanecon.adapters.mistral` may touch the Mistral API or read
`MISTRAL_API_KEY`. The runner and all A3 services talk only typed payloads and
typed failures — the Gate 4 architecture-boundary tests are extended to cover
the new modules (§9).

### 2.2 Objects that move between components

| Object | Produced by | Consumed by | Persisted? | Digest? |
|---|---|---|---|---|
| `ClaimRecord` (claim_id, revision, source_text, classification) | ingest | interpretation, bundle | yes (artifact store) | yes |
| `EICandidate` (schema-valid EI JSON, revisioned) | interpretation | review, formalization, bundle | yes | yes |
| `ReviewRecord` (decision, reviewer, notes, event_ref, flags) | reviewer command | state machine, bundle | yes | yes |
| `FormalizationCandidate` (Lean statement, mapping report, provenance) | formalization | verifier, bundle | yes | yes |
| `ProofSource` (Lean proof text; from reviewer file or reviewed fixture) | reviewer/fixture | verifier, bundle | yes | yes |
| `VerificationRecord` (compile result, sorry check, axiom audit, diagnostics) | verifier | bundle | yes | yes |
| `AxiomReviewRecord` (per-run reviewer axiom approval → `axiom_approval_ref`) | reviewer | bundle validator | yes | yes |
| `VerificationBundle` (manifest + referenced artifacts) | bundle builder | reviewer | yes | manifest digest |
| `Event` (envelope per gate3/02) | every component | EventLog, replay | yes (JSONL) | **no — digests live on artifacts and the bundle, not events** |

### 2.3 Digests vs payloads (Gate 3 rule)

- **Payloads retained:** claim text, accepted EI revisions, formal statement +
  mapping report, proof source, diagnostics, reviewer records, bundle artifacts.
  These are the trust artifacts a reviewer must be able to re-inspect.
- **Payloads not retained by default:** raw provider responses (the model's full
  reply text). Only the **validated** output (EI candidate, formal statement)
  becomes an artifact; the raw response is never stored. Provider request
  digests and policy metadata are retained.
- **Events never carry content digests** (Gate 3 decision 4). `trace_ref` values
  link events to artifacts whose digests live in the bundle manifest.

### 2.4 Redaction: where and when

Redaction happens **at the provider boundary, before transmission** (existing
`data_policy.redact` + adapter boundary in `src/leanecon/`): secret/credential
fields are removed, secret-shaped values scrubbed, sealed-gold/hidden-evaluation
markers deny the request with `INPUT_REJECTED`, and unknown classification
fails closed to `RESTRICTED` (`RESTRICTED_BLOCKED`). A3 adds no second egress
path: the interpret and formalize requests are the only provider calls, and a
`RESTRICTED` claim is denied **at ingest** — it never reaches interpretation.
Proof input is manual, so proofs make **no provider call at all** in Gate 5.

| Egress point | Payload | Model (config) | Class |
|---|---|---|---|
| `interpret` | claim text + approved context | `mistral-medium-3-5` | `PROJECT` default; `PUBLIC` only if CTO classified the claim so |
| `formalize` | **accepted** EI + formalization context (glossary refs, workspace identity names) | `labs-leanstral-1-5` | same as claim |
| proof | none (manual) | — | — |

The formalizer receives only accepted EI and approved context — never hidden
gold, never the evaluator's intended statement, never v3 material.

---

## 3. Interpretation service contract

### 3.1 Input / output

- **Input:** `ClaimRecord` (English text) + typed policy metadata.
- **Output:** versioned `EconomicInterpretation` candidate validated against the
  draft schema (`references/gate3/ei_schema_draft.json`) plus business rules.
- **Failure semantics:** outage/credential/retry-exhausted →
  `BLOCKED`/`PROVIDER_UNAVAILABLE`; malformed or schema-invalid output →
  `FAILED`/`PROVIDER_INVALID_OUTPUT`. A degraded-but-valid output is usable only
  when the capability contract says the limitation is safe; the degradation
  flag is recorded and the claim stays reviewable (DEGRADED is a process note,
  never approval).

### 3.2 What the candidate contains (draft-schema fields)

`claim` (canonical + source text), `context` (domain tags, definitions,
ontology refs), `objects` (id/kind/role), `assumptions` (proposed vs accepted —
at production time `accepted` is empty; only the reviewer moves assumptions),
`quantifiers`, `conclusion` (+ solution/equilibrium concept), `ambiguities`
(with concrete alternatives), `provenance` (source anchor, mapping method),
`confidence`, `degradation_flags`, `review` (decision `PENDING`, reviewer null,
event_ref null), `data_classification`. The candidate is a **meaning
hypothesis**, never a proof or a hidden answer key.

### 3.3 `none_noted` + reviewer acknowledgement (EI design decision 2)

When the interpreter finds no ambiguity, `ambiguities` is empty and the
candidate carries an explicit `none_noted: true` marker (proposed draft-schema
exercise). The workflow then enforces:

1. The review command **requires** an acknowledgement flag
   (`acknowledges_none_noted: true`) in the review record when `none_noted` is
   set. Without it the command is rejected, the claim stays `REVIEW_REQUIRED`,
   and no state-change event is emitted.
2. If `ambiguities` is non-empty, no acknowledgement is needed, but the
   reviewer is expected to address the ambiguity list (typically by choosing an
   alternative, which becomes an accepted-assumption/definition decision).
3. Automated triage (`semantic_triage`) can flag questions and set
   `confidence`, but can never set `review.decision` to `APPROVED` — the schema
   const and the review-command path both enforce this.

*Flagged:* the exact `none_noted` representation is a draft-schema exercise for
A3; see Open Question 1.

### 3.4 Acceptance and invalidation

- An accepted EI revision is **immutable by content digest**. Editing it
  produces a **new revision**, never a mutation.
- Every downstream artifact (formalization, proof, bundle) records the EI
  revision digest it was built from. The artifact store keeps the chain; a
  change to an accepted interpretation marks every downstream artifact
  `SUPERSEDED` (append-only flag — nothing is deleted), and the workflow
  refuses to start `PROVING` or emit `VERIFIED` on a stale chain. The trace
  shows the supersede event; the old bundle remains readable but is visibly
  invalid for the new revision.

---

## 4. Formalization contract

### 4.1 Input / output

- **Input:** the **accepted** EI (by digest) + formalization context
  (reviewed glossary refs, workspace identity) — never the raw English claim
  alone, never hidden gold.
- **Output:** `FormalizationCandidate` = Lean statement text + **mapping
  report** + provenance.
- **Failure semantics:** same as §3.1, mapped to `BLOCKED`/`FAILED` on the
  `ACCEPTED → FORMALIZED` transition.

### 4.2 The mapping report (EI design decision 3)

One row per **material** EI element:

| Column | Meaning |
|---|---|
| `ei_element_id` | stable id from the accepted EI (object, assumption, quantifier, conclusion, solution concept, definition ref) |
| `ei_element_kind` | object / assumption / quantifier / conclusion / solution / definition |
| `lean_identifier` | Mathlib identifier, glossary term, or A3-local scaffolding definition name |
| `mapping_kind` | `mathlib` \| `local_definition` \| `glossary_term` |
| `status` | `mapped` \| `unmapped` \| `deferred` (deferred only for expository context items) |
| `provenance` | how the mapping was chosen |
| `note` | free-text justification, visible to the reviewer |

Because LeanEcon Core does not exist yet (Gate 6), economics vocabulary maps
either to Mathlib structure (sets, functions, orders, finsets) or to **A3-local
scaffolding definitions** — small definitions written inside the candidate file
(e.g. a budget set as a set of bundles), clearly labeled A3-local scaffolding,
reviewed through the mapping report and statement text, and **never promoted to
Core** without the Gate 6 process. The statement text itself is part of the
bundle, so nothing is hidden from review.

### 4.3 Why the report is required before `PROVING`

1. It is the reviewer's semantic bridge: the CTO reads **rows**, not Lean.
2. It makes every vocabulary choice visible — no silently invented definitions.
3. It forces the formalization to confront meaning first: an element that
   cannot be mapped is a **visible gap**, not a hole to paper over with a
   made-up definition.
4. It is a locked design decision (07, decision 3).

### 4.4 Missing mappings as visible gaps

- **Material elements** (objects with roles, assumptions, quantifiers,
  conclusion, solution concept) must be `mapped`; if any is `unmapped`, the
  candidate is delivered with the gap list visible and the claim **stays
  `FORMALIZED`** — the workflow refuses to start `PROVING` until either the gap
  is closed (new formalization attempt) or the reviewer records a **gap
  acknowledgement** (same per-run reviewer-record mechanism as axiom approval).
- **Expository elements** may be `deferred` with a note; deferral never blocks.
- Gaps are a state, not a failure code: no new reason codes are added (see
  Open Question 9).

---

## 5. The verifier

### 5.1 Building the candidate in the pinned workspace

1. Workspace pin is checked first (`lean-toolchain` + Mathlib revision in
   `lakefile.lean`); unpinned → `BLOCKED`/`WORKSPACE_UNPINNED` (existing
   `read_workspace_identity`).
2. The candidate module is written to a per-run path inside the workspace
   (e.g. `lean_workspace/LeanEcon/A3/<claim>/<run>/`), never committed, with a
   module name derived from the claim id (sanitized). Proof source is spliced
   into the theorem body.
3. Verification runs `lake env lean <candidate>` (recorded command, cwd =
   workspace root) so the kernel checks against the pinned Mathlib. Wall-clock
   timeout → `FAILED`/`PROOF_TIMEOUT`. Exit code ≠ 0 → compile diagnostics are
   captured (stderr tail) → `FAILED`/`LEAN_SYNTAX_ERROR`.
4. The verifier never mutates anything outside its per-run directory and never
   touches the tracked `A1.lean` probe.

### 5.2 `sorry`/`admit` detection — two layers

1. **Static scan** (existing `check_sorry_free`): fast, deterministic, catches
   literal `sorry`/`admit` in the source before any Lean work; a hit refuses
   the attempt start.
2. **Kernel-level audit** (authoritative): after successful compile, the
   verifier asks the kernel for the theorem's axiom set (`#print axioms
   <theorem>`). A `sorry` elaborates to the `sorryAx` axiom; its presence in
   the audit ⇒ `FAILED`/`SORRY_FOUND` even if the static scan was evaded.

Both layers must pass for `VERIFIED` (bundle item 5).

### 5.3 Axiom/dependency audit and `axiom_approval_ref`

- After a successful compile, `#print axioms <theorem>` yields the complete
  transitive axiom closure (e.g. `propext`, `Classical.choice`,
  `quot.sound` — standard Mathlib axioms; anything declared with `axiom` in
  the candidate appears too). The module imports and the Mathlib pin are
  recorded as the dependency audit.
- The axiom list is compared against the **per-run reviewer record**
  (`axiom_approval_ref`): reviewer identity, timestamp, approved axiom list,
  and the run/bundle it covers (Gate 3 decision 8; no repo-wide allowlist in
  MVP).
- **First-run flow (designed to be honest):** the first `PROVING` attempt on a
  candidate surfaces the axiom list; if any axiom is not yet approved the
  result is `FAILED`/`AXIOM_VIOLATION`, and the **bundle carries the full
  plain-language axiom list** so the CTO can review it without reading Lean.
  The CTO then issues the axiom review record; the next attempt on the same
  `FORMALIZED` candidate passes. The walkthrough will exercise exactly this
  loop.
- Unapproved axiom with no reviewer record → `FAILED`/`AXIOM_VIOLATION`, never
  silent acceptance.

### 5.4 What makes a result VERIFIED vs FAILED vs BLOCKED

| Outcome | Requires |
|---|---|
| `VERIFIED` | all 11 bundle items (§6.2) true: compile OK, no sorry (both layers), every axiom approved, workspace pinned, digests and approval chain intact, manifest valid |
| `FAILED` | work ran and any negative result was recorded (syntax, sorry, axiom, timeout, invalid provider output) |
| `BLOCKED` | evaluation could not safely run (outage, unpinned workspace, LSP unavailable, policy denial) |

`VERIFIED` is emitted only by the bundle validator after the full checklist —
never by the compiler alone, never by the model.

---

## 6. The verification bundle

### 6.1 What it is

A directory `artifacts/a3/<bundle_id>/` containing `manifest.json` plus the
referenced artifacts (claim, accepted EI revision, formal candidate + mapping
report, proof source as evaluated, verification record/diagnostics, reviewer
records, trace excerpt or trace refs). The **proven or failed input statement
(Lean source) is always retained** for audit, together with sanity-check
metadata describing the state in which it was evaluated — success and failure
bundles are structurally identical.

### 6.2 Manifest fields (Gate 3, 05) — meaning and how to read them

| Manifest field | Meaning | How a reviewer reads it |
|---|---|---|
| `bundle_schema_version` | version of the manifest format | fixed `1.0.0` for MVP |
| `bundle_id` | unique id of this bundle | reference it in any discussion of the result |
| `claim_id`, `claim_revision` | which claim, which revision | check it is the revision you reviewed |
| `claim_digest` | SHA-256 of the claim text | anchors the exact English input |
| `interpretation_digest` | SHA-256 of the accepted EI | verify it matches the EI you approved |
| `formal_statement_digest` | SHA-256 of the Lean statement | anchors the checked math |
| `proof_artifact_digest` | SHA-256 of the proof source as evaluated | anchors the proof, including failed ones |
| `workspace_identity` | Lean toolchain, Mathlib pin, manifest/lock digest | confirms the pinned environment |
| `axiom_audit` | the axiom closure + `sorryAx` absence | the kernel-level no-sorry evidence |
| `axiom_approval_ref` | per-run reviewer record covering this run | confirms a human approved the axiom set |
| `dependency_audit` | module imports + Mathlib revision | shows what libraries support the result |
| `trace_refs` | links: claim ↔ approval ↔ formalization ↔ proving ↔ verification ↔ bundle | replay path (§7.4) |
| `capability_snapshots` | `HEALTHY`/`DEGRADED`/`UNAVAILABLE` at evaluation time | explains degraded conditions |
| `sanity_checks` | workspace probe, time/budget used, compiler version, file digests | describes the state in which the input was evaluated |
| `result` | `VERIFIED` \| `FAILED` \| `BLOCKED` | the headline |
| `failure_reasons` | reason codes + detail | the why, if not VERIFIED |
| `reproducibility` | commands, versions, timestamps, builder identity, environment | enables re-running |
| `created_at`, `builder_identity`, `retention_policy` | when, who/what built it, how long payloads are kept | governance metadata |

### 6.3 Worked (illustrative) happy-path manifest

```json
{
  "bundle_schema_version": "1.0.0",
  "bundle_id": "bundle-c1-r1-x7k2",
  "claim_id": "claim-c1", "claim_revision": 1,
  "claim_digest": "a1b2…",
  "interpretation_digest": "c3d4…",
  "formal_statement_digest": "e5f6…",
  "proof_artifact_digest": "a7b8…",
  "workspace_identity": {"toolchain": "leanprover/lean4:v4.32.2",
                         "mathlib": "v4.32.2",
                         "manifest_digest": "c9d0…"},
  "axiom_audit": {"axioms_used": ["propext", "Classical.choice", "quot.sound"],
                  "sorryAx_present": false},
  "axiom_approval_ref": "axrec-c1-r1-2026-08-06",
  "dependency_audit": {"imports": ["Mathlib.Data.Real.Basic", "Mathlib.Tactic"],
                       "mathlib_revision": "v4.32.2"},
  "trace_refs": ["trace-c1-r1"],
  "capability_snapshots": {"interpret": "HEALTHY", "formalize": "HEALTHY",
                           "lean_workspace": "HEALTHY"},
  "sanity_checks": {"workspace_probe": "pinned", "elapsed_ms": 41230,
                    "lean_version": "4.32.2", "candidate_digest": "e5f6…"},
  "result": "VERIFIED",
  "failure_reasons": [],
  "reproducibility": {"commands": ["leanecon a3 run claim-c1 --proof fixture-1"],
                      "builder": "hermes-agent", "created_at": "2026-08-06T14:00:00Z"},
  "created_at": "2026-08-06T14:00:00Z",
  "builder_identity": "leanecon-a3-0.1.0",
  "retention_policy": "payloads kept; raw provider responses not retained"
}
```

---

## 7. The trace

Every step emits one append-only event (envelope per `docs/gate3/02`,
implemented in `events.py`). `HEALTH_CHECK` stays an event type, never a claim
state. The runner writes its EventLog under `artifacts/local/a3-events/`.

### 7.1 Happy path (walkthrough claim)

| # | event_type | actor | state_before → state_after | reason_codes | trace_ref |
|---|---|---|---|---|---|
| 1 | `CLAIM_STATE_CHANGED` | system | – → `DRAFT` | — | run |
| 2 | `CLAIM_STATE_CHANGED` | system | `DRAFT` → `INTERPRETED` | — | run |
| 3 | `CLAIM_STATE_CHANGED` | system | `INTERPRETED` → `REVIEW_REQUIRED` | — | run |
| 4 | `CLAIM_STATE_CHANGED` | **reviewer** | `REVIEW_REQUIRED` → `ACCEPTED` | — | approval event ref |
| 5 | `CLAIM_STATE_CHANGED` | system | `ACCEPTED` → `FORMALIZED` | — | run |
| 6 | `CLAIM_STATE_CHANGED` | system | `FORMALIZED` → `PROVING` | — | run |
| 7 | `VERIFICATION_COMPLETED` | system | `PROVING` → `VERIFIED` | — | bundle id |
| 8 | (bundle event) | system | — | — | bundle id |

### 7.2 Semantic-rejection path

| # | event_type | actor | before → after | reason_codes |
|---|---|---|---|---|
| 1–3 | as above | system | … → `REVIEW_REQUIRED` | — |
| 4 | `CLAIM_STATE_CHANGED` | **reviewer** | `REVIEW_REQUIRED` → `REJECTED` | `SEMANTIC_AMBIGUITY` or `USER_REJECTED` |

Revision is terminal. If the reviewer wants to proceed, a new revision re-enters
at `DRAFT` with a revised claim or EI; no artifact of the rejected revision is
reused downstream.

### 7.3 Proof-failure path

| # | event_type | actor | before → after | reason_codes |
|---|---|---|---|---|
| 1–6 | as happy path | … | … → `PROVING` | — |
| 7 | `VERIFICATION_COMPLETED` | system | `PROVING` → `FAILED` | `SORRY_FOUND` / `LEAN_SYNTAX_ERROR` / `AXIOM_VIOLATION` / `PROOF_TIMEOUT` |

A failure bundle is emitted with `result: FAILED`, the retained input
statement, and `failure_reasons`. Retry is a new attempt (revised proof input,
or a new axiom review record, or a revised statement — depending on the code;
§8.4).

### 7.4 Provider / workspace-outage path

| # | event_type | actor | before → after | reason_codes |
|---|---|---|---|---|
| 1 | `CLAIM_STATE_CHANGED` | system | – → `DRAFT` | — |
| 2 | `CLAIM_STATE_CHANGED` | system | `DRAFT` → `BLOCKED` | `PROVIDER_UNAVAILABLE` (interpret down) |
| — or — | | | | |
| 5 | `CLAIM_STATE_CHANGED` | system | `ACCEPTED` → `BLOCKED` | `PROVIDER_UNAVAILABLE` (formalizer down) |
| — or — | | | | |
| 7 | `VERIFICATION_COMPLETED` | system | `PROVING` → `BLOCKED` | `WORKSPACE_UNPINNED` / `LSP_UNAVAILABLE` |

Blocker clears → rerun resumes from the last durable state (events + artifacts
are replayed or continued; no state is fabricated).

### 7.5 Trace replay

Replay is a **deterministic validation of recorded history**, not a
re-execution of side effects:

1. Read the EventLog for a `run_id`; read the referenced artifacts by
   `trace_ref` (claim, EI, candidate, proof, records).
2. Re-validate every event envelope (existing `validate_event`), re-walk the
   state machine against the transition table, and recompute every artifact
   digest from stored payloads.
3. Re-run the bundle validator on the stored artifacts (no provider calls, no
   Lean rebuild — digests are recomputed locally).
4. Report `REPLAY_OK` or a list of mismatches (event, expected, found).

This is the Gate 5 "trace reconstruction succeeds" exit evidence, and it is
also the regression test for the state machine (§9).

---

## 8. Reading a bundle — the CTO guide

### 8.1 What `VERIFIED` proves

- The **accepted formal statement** (as recorded in the mapping report and
  statement artifact) is accepted by Lean's kernel in the **pinned workspace**
  (toolchain + Mathlib revision recorded).
- The proof contains **no `sorry`/`admit`** — confirmed twice (static scan and
  kernel axiom audit).
- Every axiom used is on the **per-run reviewer-approved list**
  (`axiom_approval_ref`).
- The chain of digests holds: claim → accepted EI → formal statement → proof →
  verification, each approved by a recorded human event where the contract
  requires one.

### 8.2 What `VERIFIED` does **not** prove

- It does **not** prove the English claim is economically true.
- It does **not** prove the interpretation captures the claim's intended
  meaning — that is the reviewer's judgment, exercised at `REVIEW_REQUIRED`
  over the EI and later over the mapping report.
- It does **not** prove the formal statement faithfully models the economics —
  the mapping report is the evidence for that, and it is reviewed, not
  kernel-checked.
- It does not say anything about other claims, other revisions, or unmodeled
  ambiguity. **Semantic correctness is the reviewer's; kernel correctness is
  the verifier's.** A `VERIFIED` bundle is only as good as its accepted EI and
  mapping report.

### 8.3 Where to look first in a bundle

1. `result` + `failure_reasons` — headline and why.
2. `interpretation_digest` — matches the EI you approved?
3. mapping report — every material element mapped, and the chosen identifiers
   match your reading of the EI.
4. `axiom_audit` + `axiom_approval_ref` — no `sorryAx`, and a human approved
   the axioms.
5. `workspace_identity` + `reproducibility` — the environment is the pinned one.
6. `sanity_checks` + `capability_snapshots` — the state the run happened in.

### 8.4 Reason codes → action

| Reason code | Meaning | Action |
|---|---|---|
| `PROVIDER_UNAVAILABLE` | outage / credential / retries exhausted | **retry** when the provider is back |
| `WORKSPACE_UNPINNED`, `LSP_UNAVAILABLE` | environment not ready | **retry** after fixing the workspace |
| `PROOF_TIMEOUT` | verification exceeded the time budget | **retry** with more budget, or **revise** the proof |
| `LEAN_SYNTAX_ERROR` | statement/proof does not compile | **revise** the statement/proof (formalization or proof input) |
| `SORRY_FOUND` | incomplete proof placeholder | **revise** the proof — never acceptable for `VERIFIED` |
| `AXIOM_VIOLATION` | axiom used but not yet approved | **reviewer record**: approve the axiom list (no claim edit needed), then retry |
| `PROVIDER_INVALID_OUTPUT` | model returned unusable content | **retry**; if persistent, **revise** the prompt/context |
| `SEMANTIC_AMBIGUITY`, `USER_REJECTED` | human rejected meaning | **new revision** of claim/EI, re-review |
| `RESTRICTED_BLOCKED`, `INPUT_REJECTED` | data-policy denial | **resolve policy/classification** — a blocker, not a claim defect |

---

## 9. Test plan

Existing A1 suite (44 tests) stays green and unchanged; A3 adds its own.

| Test class | Proves | A1 reuse | New A3 work |
|---|---|---|---|
| EI schema + business rules (jsonschema) | candidate validity; `PENDING`-only at production; classification match | — | `interpretation.py` + tests |
| `none_noted` enforcement | approval refused without reviewer acknowledgement | — | review-command tests |
| State-machine transitions | every allowed/forbidden edge; no skipping `REVIEW_REQUIRED`; reviewer-only `ACCEPTED`/`REJECTED` | `events.py` | table-driven transition tests |
| Digests & invalidation | accepted-EI change ⇒ downstream `SUPERSEDED`, no stale `VERIFIED` | `data_policy.canonical_digest` | artifact-store tests |
| Mocked-provider services | valid / malformed / outage outputs → typed `HEALTHY` / `PROVIDER_INVALID_OUTPUT` / `PROVIDER_UNAVAILABLE` | mock-transport pattern from `test_provider_boundary.py` | service-level tests |
| Mapping-report completeness | gaps block `PROVING`; gap acknowledgement unblocks | — | `formalization.py` + tests |
| Verifier (real pinned workspace) | valid theorem → `VERIFIED`; syntax error → `FAILED`; `sorry` → `FAILED`/`SORRY_FOUND`; unapproved `axiom` → `FAILED`/`AXIOM_VIOLATION`; timeout → `FAILED`/`PROOF_TIMEOUT` | `lean_probe` identity/sorry helpers | `verifier.py` + workspace-marked tests (skip gracefully when Lean absent, as in `test_lean_probe.py`) |
| Bundle validator | each of the 11 checklist items fails independently | — | `bundle.py` + tests |
| Trace replay | scripted run → replay equality (states, digests, bundle) | `EventLog` | `trace_replay.py` + test |
| Gold isolation / data policy | no provider egress for `RESTRICTED`/gold; no raw provider payload retention | `data_policy.py`, `gold_isolation.py`, `test_architecture_boundary.py` | extend AST scans to A3 modules; retention test |
| End-to-end walkthrough (live, `--live`) | one complete canonical claim: English → review → formalize → manual proof → `VERIFIED`, with bundle + replay | `a1_runner.py` structure | `a3_runner.py` `--live` mode |

**Reused unchanged:** `events.py`, `data_policy.py`, `providers.py`,
`adapters/mistral.py` (+ `MVP_MODEL_MAP`), `gold_isolation.py`, and
`lean_probe.py` (identity + sorry helpers). **Extended:** none of the above is
modified in place; new A3 modules import them. The only new dependency
proposed is `jsonschema` for EI validation (Open Question 6).

---

## 10. Open questions and proposed resolutions

| # | Question | Proposed resolution | CTO decision needed? |
|---|---|---|---|
| 1 | `none_noted` representation in the draft schema | Explicit `none_noted: true` marker + review-record acknowledgement flag; approval refused without it | yes (schema exercise) |
| 2 | Axiom approval loop: first unapproved axiom ⇒ `FAILED`/`AXIOM_VIOLATION` with full list in bundle; reviewer record closes it | Per contract (gate3/05 FAILED includes disallowed axiom); keeps the registry stable | yes |
| 3 | Unmapped material elements block `PROVING` until a reviewer gap-acknowledgement record exists | Same per-run reviewer-record mechanism as axiom approval | yes |
| 4 | A3-local scaffolding definitions inside candidate files | Allowed for MVP, clearly labeled, reviewed via mapping report + statement text, never promoted to Core without Gate 6 | yes |
| 5 | Proof input sources | Reviewer-supplied file or reviewed v4 fixture (path + provenance recorded); fixtures committed under `tests/fixtures/` after CTO review; no `prove_or_repair` in Gate 5 | yes |
| 6 | EI validation dependency | Add `jsonschema` to project deps (standard, schema-driven); alternative is a hand-rolled validator | yes |
| 7 | Verifier invocation | `lake env lean <candidate>` with recorded command; `#print axioms` for the audit; time budget configurable (default 600 s) | no |
| 8 | Candidate files in workspace | Generated per-run under `lean_workspace/LeanEcon/A3/<claim>/`, gitignored, never committed; only reviewed fixtures are committed | no |
| 9 | Reason-code registry stability | No new codes for A3; gaps and `none_noted` are reviewer-record mechanics, not failure codes | yes (confirm) |
| 10 | Canonical claims (EI acceptance test) | Proposals in Appendix A; CTO reviews and approves before A3 implementation | **yes — required** |

---

## Appendix A — Proposed canonical claims (EI acceptance-test candidates)

These are **proposals for CTO review**, not approved content. Per the locked EI
design (decision 4), the CTO reviews the first 3–5 canonical claims as the
acceptance test of the EI frame **before A3 implementation**; the Gate 5
walkthrough uses one of the approved claims. Selection criteria: small,
economically meaningful, formalizable in Mathlib + minimal A3-local
scaffolding, and each exercising a different part of the frame.

| # | Claim (English, as entered by the CTO/author) | Exercises in the frame | Expected formalization | Expected failure modes |
|---|---|---|---|---|
| C1 | "If a consumer's feasible budget set expands while preferences remain unchanged, the consumer's attainable set does not shrink." | ambiguity resolution ("attainable set" vs "chosen set"); object roles; proposed assumption | local `BudgetSet`/`AttainableSet` scaffolding over sets; set-inclusion conclusion in Mathlib | `SEMANTIC_AMBIGUITY` at review; mapping gap on "attainable" |
| C2 | "Weak preference is transitive: if A ≽ B and B ≽ C then A ≽ C." | relation axioms; quantifier order; definition refs (glossary) | Mathlib relation + transitivity; near-zero scaffolding | `LEAN_SYNTAX_ERROR` on statement; axiom audit on Classical.choice |
| C3 | "If a utility function is strictly increasing, then x ≥ y componentwise and x ≠ y implies u(x) > u(y)." | strict vs weak comparison; componentwise order; conclusion strength | Mathlib orders on ℝ/vector order; local `u` definition | proof subtlety; `SORRY_FOUND` temptation |
| C4 | "A monotone nondecreasing function f : ℝ → ℝ preserves order: a ≤ b ⇒ f a ≤ f b." | pure Mathlib anchor (no scaffolding); quantifier order | direct Mathlib statement | minimal — calibrates the machinery |

Each canonical claim will, before use, get the Gate 7-style record (English
input, approved EI, intended formal statement, known proof or proof boundary,
expected failure modes, provenance, release designation) — at Gate 5 only the
first claim needs the full record; the others need EI approval at minimum.

---

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction.
The CTO remains the sole semantic approver. This document authorizes nothing;
A3 implementation proceeds only after CTO approval of this design, the
canonical claims, and the flagged open questions.
