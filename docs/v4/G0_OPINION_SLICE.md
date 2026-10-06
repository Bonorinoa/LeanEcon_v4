# G0 — Opinion side-door slice proposal (v4, slice 1)

**Date:** 2026-09-07 · **Branch:** `v4/opinion-slice` (proposal + implementation)
**Parent:** `docs/v4/INIT_V4_AGENTIC.md` · **Status:** **APPROVED
(2026-09-07, "proceed as suggested") + IMPLEMENTED on the branch** —
D1–D4 approved as proposed, D5 pedagogical mode IN (DECISION_LOG 55);
implementation lands `leanecon.opinion` + `cmd_opinion`, suite 262 green,
deterministic tests only (provider_calls=0). Merge CTO-gated.
**Locked refs:** DECISION_LOG 51/D3 (consultative `opinion` side-door is
first-class v4 work, consultative only, NEVER authorized to emit
ACCEPTED); DL 31 (reviewer policy); DL 46 (narrowed promise: product =
audited single-claim lifecycle).

## Why this slice first (CTO direction 2026-09-07)

Opinion was chosen as v4 slice 1 over agentic tool-using repair: it is a
pure addition to the product surface — no lifecycle transition, no
budget consumption, no reviewer-policy change — and it is the surface
that matches the stated direction of LeanEcon as an educational
technology (a curious user or learner asks the system for its own read
of an in-flight claim walkthrough and compares it with their own).

## What the opinion side-door is

A consultative request/response path on the A3 walkthrough. The user (or
a calling program) asks the system for **its own review of an artifact
in an in-flight claim walkthrough**. The system emits a structured,
labeled opinion bound to a specific immutable artifact revision. It:

- **never** emits ACCEPTED / REJECTED (DL 51/D3);
- **never** transitions lifecycle state (lifecycle table untouched);
- **never** gates PROVING/VERIFIED (bundle 12 checks untouched);
- is recorded with provenance `consultative_opinion`, distinct from
  review records (`reviewer_kind` human|ai|auto per DL 31 policy).

## Mechanism split (principled vs heuristic — house discipline)

| Part | Kind | Content |
|---|---|---|
| Machine analysis | **principled** | reuse of shipped deterministic signals over the target artifact revision: audit/static list, probe `probe_failure_class` (P2 taxonomy), P1–P6 property labels, mapping-gap classification, vacuity/inversion flags, deterministic Diagnosis directive (`leanecon.probe_repair`) |
| Model-authored opinion | **heuristic** | prose grounded in the artifact + the machine block above; explicitly labeled AI-opinion, provenance consultative |
| Report assembly | **principled** | fixed schema; machine block always present and authoritative; prose never overrides a machine signal (e.g. cannot claim audit-clean over a `sorry`) |

No new model powers, no sanitizer scope growth, no new lifecycle states,
no ACCEPTED path, no UI.

## In / out of scope (slice 1)

| In | Out |
|---|---|
| `opinion` subcommand + events + artifact dir (`artifacts/local/a3/opinions/<claim>/rev-N.json`) | VERIFIED-exhibit opinions (parked "bundle viewer maybe" — separate decision) |
| Target surfaces: (a) interpretation + accepted EI, (b) formal draft + mapping report, (c) walkthrough packet summary | UI/UX of any kind |
| Snapshot semantics: opinion binds to one immutable artifact revision | Re-litigating P5 semantic fidelity or re-opening spent sets |
| Deterministic unit tests (`provider_calls=0`) + optional CTO-gated live smoke | Any change to review records, lifecycle, bundle checks, MAX_REVISION_ATTEMPTS |

## Files likely touched (implementation phase)

`src/leanecon/opinion.py` (new), `src/leanecon/a3_runner.py`
(`opinion` subcommand), event emission, tests
(`tests/test_opinion_*.py`), docs row in README/ENGINEERING_LOG.
`MVP_MODEL_MAP` read-only (opinion reuses the interpret/triage model
unless D1 says otherwise).

## Definition of done (slice 1)

- Deterministic tests green, fixture scorer `provider_calls=0`, suite
  count grows only by new tests.
- Opinion artifact schema validated; provenance `consultative_opinion`;
  no lifecycle transition possible from the code path (test).
- Machine block renders identically for the same artifact revision
  (determinism test over a stored fixture claim).
- Optional live smoke (separate CTO gate; spends quota): one in-flight
  claim, predictions first.

## Open decisions for the CTO

| Ref | Decision | Proposal |
|---|---|---|
| D1 | Opinion model | **RESOLVED 2026-09-07:** reuse interpret/triage pin. Slug updated 2026-10-06 (DL 57) to `openrouter/free` with interpret; never a distinct formalizer identity. |
| D2 | Target surfaces in slice 1 | (b) formal draft + mapping report first (highest-value: that is where fidelity failures live); (a)+(c) later. |
| D3 | Prose grounding enforcement | Hard: opinion prose must cite artifact content; machine block cannot be contradicted (deterministic guard where checkable). |
| D4 | Where opinions are recorded | New event kinds `opinion_requested` / `opinion_emitted` + artifact dir; excluded from bundle 12 checks (they are verification evidence, not opinions). |
| D5 | Educational framing | **RESOLVED 2026-09-07: pedagogical mode is IN slice 1** — schema carries a first-class pedagogical field: learner-facing explanation of the failure (P1–P6 terms where possible) + what to try next. Not a flag bolted on later; designed in. |

## Non-goals (unchanged doctrine)

No proof generation (B2 stands: compile ≠ pass). No agentic repair in
this slice. No UI. No API shape. No new lifecycle states.

Attribution: prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
