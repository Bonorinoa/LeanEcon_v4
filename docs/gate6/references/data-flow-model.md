# Gate 6 — Core-era data flow model (claims, declarations, glossary, kernel feedback)

> Status: design reference, part of the Gate 6 package — **awaiting CTO
> approval** along with `../a3-core-design.md`. Prepared 2026-08-06.
> Reader: no Lean knowledge required.
>
> This document answers: how do claims, EIs, mapping reports, Lean
> statements, kernel feedback, glossary entries, and Core declarations
> actually move between agents, the reviewer, and the harness? Where do
> the contracts bite? What is new in the Core era vs the Gate 5 model?

## 1. The model at a glance

Gate 5 already defined a data-flow model (`docs/gate5/a3-design.md` §2):
typed objects between components, digests on artifacts (never on events),
redaction at the single provider boundary. Core does not replace it; Core
adds **two new asset classes** (glossary registry, Core module tree) and
**one new write path** (promotion — the only way declarations enter
Core). The diagram below is the Core-era model.

```text
                       ┌────────────────────────────────────────────────────┐
   WRITE PATH (human-gated, ONE way):                                       │
   CTO approves → glossary entry / Core declaration added → registry/module │
   └────────────────────────────────────────────────────────────────────┘
        ▲                                                              │
        │ reads (context)                        imports (workspace)    ▼
┌──────────────────┐   context   ┌──────────────┐            ┌────────────────────┐
│ GLOSSARY REGISTRY│◀────────────┤ formalization│◀─accepted─┤  review (CTO)      │
│ meaning, aliases,│             │ (agent:      │   EI      │  EI + mapping      │
│ status ladder    │             │  labs-leanstral)          │  report review     │
└──────────────────┘             └──────────────┘            └────────────────────┘
                                         │                          ▲
              EI candidate (schema-valid)│                          │ review record
                                         ▼                          │
        ┌────────────┐   interpret  ┌──────────────┐   validate   ┌──────────────┐
 claim  │  ingest    │─────────────▶│interpretation│─────────────▶│REVIEW_REQUIRED│
 ─────▶ │ (DRAFT)    │              │ (agent:      │              └──────────────┘
        └────────────┘              │  mistral-medium-3-5)              │
              │                     └──────────────┘                    │ ACCEPTED / REJECTED
              ▼                                                         ▼
        ┌──────────────────────────────────────────────────────────────────┐
        │ a3_runner (harness): state machine, artifact store, event log    │
        │   artifacts/local/a3/{claims,eis,formal,reviews,bundles}         │
        │   events: artifacts/local/a3-events/*.jsonl (append-only,        │
        │   NO content digests — locked Gate 3 decision)                   │
        └──────────────────────────────────────────────────────────────────┘
                                         │
              statement + mapping report │ (FormalizationCandidate)
                                         ▼
        ┌────────────┐  verify (lake env lean + #print axioms)  ┌────────────────────┐
        │ CORE MODULE│◀────────────────────────────────────────▶│ verifier (kernel)  │
        │ tree       │   imports Core + Mathlib                  │ compile result,   │
        │ (workspace,│                                           │ sorry scan, axiom │
        │  git-pinned)│                                          │ audit             │
        └────────────┘                                           └────────────────────┘
              ▲                                                           │
              │ proof source (reviewer-supplied)                          │ VerificationRecord
              │                                                           ▼
        ┌────────────┐  bundle builder (11 checks)          ┌──────────────────────┐
        │ ProofSource│─────────────────────────────────────▶│ VerificationBundle   │
        └────────────┘                                      │ + manifest (digests, │
                                                            │  workspace_identity, │
                                                            │  dependency_audit)   │
                                                            └──────────────────────┘
```

Trust rule of the model: **the pipeline only reads Core/glossary; only a
human-gated promotion writes them.** Agents (interpret, formalize) never
write Core; the kernel never writes Core; the harness only imports it at
verify time.

## 2. Objects that move between components (Core-era inventory)

Gate 5 objects are unchanged; the Core-era additions are marked **NEW**.

| Object | Produced by | Consumed by | Persisted | Digest |
|---|---|---|---|---|
| `ClaimRecord` | ingest | interpretation, bundle | yes | yes |
| `EICandidate` | interpretation | review, formalization, bundle | yes | yes |
| `ReviewRecord` | reviewer | state machine, bundle | yes | yes |
| `GlossaryRef` **NEW** | accepted EI (`ontology_refs`/`context.definitions`) | formalization context, mapping report | in EI | via EI digest |
| `FormalizationCandidate` (statement + mapping report) | formalization | verifier, review, bundle | yes | yes |
| `MappingReport` (rows: `core`/`glossary_term`/`mathlib`/`local_definition`) | formalization | review, bundle | yes | yes |
| `ProofSource` | reviewer/fixture | verifier, bundle | yes | yes |
| `VerificationRecord` (compile, sorry, axiom audit) | verifier | bundle | yes | yes |
| `AxiomReviewRecord` | reviewer | bundle validator | yes | yes |
| `GlossaryEntry` **NEW** | review/promotion process | formalization context, mapping report | registry + EI | registry digest |
| `CoreDeclaration` **NEW** (Lean source + ontology record + approval ref) | promotion process | formalization context, verifier imports, bundle | workspace git + ontology record | yes |
| `VerificationBundle` | bundle builder | reviewer | yes | manifest digest |
| `Event` | every component | EventLog, replay | JSONL | **no** (locked) |

## 3. What is new in the Core era (vs the Gate 5 model)

1. **Glossary read at formalize.** The formalizer's context grows from
   "accepted EI + workspace identity" to "accepted EI + glossary refs +
   Core identifiers". It still never sees gold; the glossary refs are the
   *meaning anchors* it may cite in mapping rows.
2. **Core import at verify.** The verifier compiles candidates that
   `import LeanEcon.Core.*`. Kernel feedback (`VerificationRecord`)
   now covers Core declarations too: a Core module that misbehaves
   (fails to compile, needs a new axiom) fails the same checks as any
   Mathlib usage.
3. **Core pin in the bundle (contract delta — see §5).** Today the bundle
   records `workspace_identity` (toolchain, Mathlib, manifest digest) and
   `dependency_audit` (imports, Mathlib revision). With Core, a
   `VERIFIED` claim must be reproducible against the **exact Core
   revision** used — the bundle needs a Core pin, or "VERIFIED against
   what Core?" is unanswerable. This is the strongest reason the model
   matters: reproducibility is a bundle contract, and the bundle has no
   field for Core today.
4. **Promotion path outside the pipeline.** Glossary entries and Core
   declarations are written by a human-gated process (author → CTO
   approval → record), never by agents or harness. The state machine
   never has a "Core" state; Core is an *asset store*, not a lifecycle
   stage.
5. **Mapping rows carry the semantic bridge.** `glossary_term` rows cite
   meaning anchors; `core` rows cite **fully-qualified** Lean identifiers
   (namespace-prefixed, see §5). The reviewer reads rows; the kernel
   checks identifiers; the mapping report is the reconciliation.

## 4. Where the contracts play their critical role

| Edge / store | Contract | Why it's critical here |
|---|---|---|
| Every state change | Gate 3 `02-lifecycle-events.md` — event envelope, transition table | The trace is the audit surface; events never carry digests (locked), so artifacts+manifest carry the evidence |
| Agents ↔ providers | Gate 3 `04-provider-contracts.md` + A3 §2.4 redaction | Formalizer receives accepted EI + glossary/Core context ONLY; no gold, no v3, single egress boundary |
| Outbound enforcement | Gate 3 `06-outbound-data-enforcement.md` | `RESTRICTED` deny at ingest; redaction before transmission; no second egress path introduced by Core |
| Mapping report | A3 §4 + Gate 6 §4 (target contract) | One row per material EI element; `core`/`glossary_term`/`mathlib`/`local_definition`; unmapped blocks `PROVING` |
| Verification | A3 §5 (kernel check, sorry scan, axiom audit) | Kernel arbitrates invented identifiers; axiom closure must stay baseline |
| Bundle | Gate 3 `05-verification-bundle.md` + A3 §6 (11 checks) | Reproducibility metadata — **gains the Core pin** (§5) |
| Core/glossary writes | Gate 6 §7 (promotion criteria) | The only write path; per-declaration CTO approval; contamination rules (no gold, no provider logic) |
| Replay | A3 §7.5 (deterministic re-validation) | Replay recomputes digests from stored payloads — glossary/Core digests must be recomputable (registry + workspace are inputs) |

Yes — this is exactly where the contracts bite. The typed-object table
(§2) IS the contract surface between components; the envelope is the
audit surface; the bundle is the evidence surface; the mapping report is
the semantic bridge. Core does not loosen any of them; it adds two new
contract surfaces (§5).

## 5. Contract deltas proposed for CTO approval (Core-era)

These tighten the existing contracts; none changes a locked decision.

| # | Delta | Where | Why |
|---|---|---|---|
| D1 | `core` mapping rows carry **fully-qualified** `lean_identifier` (e.g. `LeanEcon.Core.Choice.attainableSet`, never bare `attainableSet`) | Gate 6 §4 target contract | Eliminates any ambiguity from `open`-based shadowing; the row must be resolvable as written |
| D2 | Bundle gains a Core pin: `workspace_identity.core_revision` (commit sha or manifest digest of the Core module tree) + `dependency_audit` records Core imports | Gate 3 `05` / A3 §6 manifest | Reproducibility: a `VERIFIED` claim must be reproducible against the exact Core revision |
| D3 | Promotion criteria gain a **collision check**: the fully-qualified name must not collide with any imported dependency's namespace, and unqualified use in candidates must not shadow imported Mathlib identifiers | Gate 6 §7 | Naming-overlap risk (§6) made a review item instead of a hope |
| D4 | A3-local scaffolding in candidates must be namespace-scoped (`namespace A3Scaffolding.<claim>`) instead of root-namespace | Gate 6 §4 / A3 §4 | Today's per-candidate `abbrev Bundle` lives in the root namespace and *can* shadow Mathlib within the file; namespacing removes the confound |

## 6. Naming-overlap risk (Q1) — where it is real and where it is not

- **Not a risk:** Core declarations live under `LeanEcon.Core.*`; Mathlib
  lives in the root namespace (e.g. `Set`, `Monotone`, `IsTrans`). The
  namespaces are disjoint; the kernel resolves fully-qualified names
  unambiguously. Core never re-defines Mathlib concepts (design §1.4).
- **Real, manageable risk:** (a) *unqualified* use after `open` — a
  candidate that opens both Core and Mathlib could hit a name clash; the
  mapping report must therefore use fully-qualified identifiers (D1);
  (b) Core choosing a name that Mathlib already owns at root (e.g. naming
  a Core def `Monotone`), which would shadow on `open` — prevented by a
  naming convention + collision check (D3); (c) **today's** A3-local
  scaffolding already pollutes the candidate's root namespace (`abbrev
  Bundle`), which is the same failure class one level down — fixed by
  namespace-scoped scaffolding (D4); (d) future external dependencies
  must each own a namespace and be listed in the dependency manifest —
  the pin (D2) makes the dependency set explicit.
- **Demonstrated live:** the toy walkthrough's bad-id candidate
  (`budgetSetX`) shows the kernel rejecting invented names; the same
  mechanism rejects accidental shadowing errors when they change meaning
  under the mapping report's review.

## 7. Core vs Glossary (Q2) — the one-line answer

> **Glossary = what terms MEAN (reviewed in English, no Lean required).
> Core = how meanings are ENCODED (Lean declarations the kernel checks).**
> The mapping report cites the glossary with `glossary_term` rows and Core
> with `core` rows; a term's promotion ladder (glossary-only →
> core-candidate → core) is the path from "meaning approved" to "meaning
> approved AND encoding machine-checked".

- A glossary entry needs no Lean; a Core declaration REQUIRES a glossary
  entry (its ontology record must carry the plain-language meaning).
- Glossary entries may be per-claim copies inside the EI
  (`context.definitions`) or registry entries
  (`references/core-glossary-detail.md`); Core declarations exist only in
  the workspace module tree, pinned and bundled.
- `mathlib` terms appear in the glossary as "referenced, never
  duplicated" (e.g. `transitivity` → Mathlib `IsTrans`).

## 8. Failure and edge flows (same objects, honest records)

| Failure | Objects produced | State | Visible where |
|---|---|---|---|
| Formalizer invents a Core id | `FormalizationCandidate` rejected pre-store (static validation) or `FAILED` at verify | stays `FORMALIZED` | trace + bundle (`LEAN_SYNTAX_ERROR`) |
| `object:u` id deviation | mapping report + gap list | stays `FORMALIZED` until gap-ack | mapping report, reviewer record |
| Axiom surprise from a Core declaration | `VerificationRecord` with axiom list | `FAILED`/`AXIOM_VIOLATION` | bundle §6.2 `axiom_audit` |
| Reviewer rejects a mapping | `ReviewRecord` (REJECTED) | revision terminal | trace |
| Stale Core pin | bundle validator rejects | `FAILED`/`bundle_validation_failed` | manifest vs workspace |

All failure bundles are structurally identical to success bundles (A3
§6.1): the input statement is retained, the reason codes are recorded,
and replay re-validates the recorded history.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This document is a
design reference; it authorizes nothing.
