# Reviewer policy — human and AI (v1)

> **Status:** LOCKED 2026-08-08 (DECISION_LOG item 31). Supersedes the
> Gate 3 prose that restricted semantic approval to humans only.
>
> **Attribution:** Hermes Agent (Nous Research) under CTO direction; the
> CTO remains the accountable semantic authority.

## 1. Promise

An **authorized reviewer** — human or AI — may emit:

- `ACCEPTED` / `REJECTED` (semantic review of an EconomicInterpretation)
- gap acknowledgements (`gap-ack`)
- axiom approvals (`axiom-approve`)

`VERIFIED` remains **system-only**, gated on the bundle validator (kernel
check + twelve-item checklist including `12_core_pin` when Core is used).
Models used for interpret/formalize are **drafting aids**, not reviewers,
unless they act through the review CLI with an explicit reviewer identity.

## 2. Identity and kind

| Field | Rule |
|---|---|
| `--reviewer` / `LEANECON_REVIEWER_ID` | **Required** non-empty identity string |
| `--reviewer-kind` / `LEANECON_REVIEWER_KIND` | `human` \| `ai` \| `auto` (default `auto`) |

**Auto inference** (`leanecon.reviewer_policy`):

- `ai` if identity matches
  `^(ai|hermes|hermes-agent|leanecon-ai)([:_-].+)?$` (case-insensitive)
- otherwise `human`

Explicit kind always wins over inference (e.g. `--reviewer Bonorinoa --reviewer-kind ai`
is legal and recorded as AI).

## 3. Accountability

| Role | Owns |
|---|---|
| **CTO** | Accountable semantic authority; Core ontology; release tags; policy changes |
| **Authorized AI reviewer** | May approve/reject under this policy for workflow acceleration; decisions are audited |
| **System** | Processing states, FAILED/BLOCKED, VERIFIED via bundle validator only |

AI approval does **not** transfer accountability. Every review record stores
`reviewer` + `reviewer_kind` for audit.

## 4. Unchanged gates

- `none_noted` still requires `--acknowledge-none-noted` (human **and** AI)
- RESTRICTED / gold isolation / outbound policy unchanged
- Bundle checklist and kernel sorry/axiom rules unchanged
- No silent self-approval by the interpret/formalize models

## 5. CLI examples

```bash
# Human
scripts_local/a3_run.py review --claim-id c1 --decision approve \
  --reviewer Bonorinoa --acknowledge-none-noted

# AI (auto-inferred kind)
scripts_local/a3_run.py review --claim-id c1 --decision approve \
  --reviewer hermes --acknowledge-none-noted

# AI (explicit kind)
scripts_local/a3_run.py gap-ack --claim-id c1 --reviewer leanecon-ai:v1 \
  --reviewer-kind ai --notes "gaps are evaluation signals"
```

## 6. Ops

Supported live entrypoint: **`scripts_local/a3_run.py`** (sets `PYTHONPATH=src`
and loads credentials). Bare `python -m leanecon.a3_runner` after src edits
can use a stale install and drop D2 (`12_core_pin`) — see OOS F2.
