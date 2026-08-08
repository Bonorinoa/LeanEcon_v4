# v1 reviewer runbook

Supported entrypoint for **all** live A3 commands:

```bash
scripts_local/a3_run.py <subcommand> ...
```

Never rely on bare `python -m leanecon.a3_runner` after editing `src/` without
reinstall — stale wheels can drop `12_core_pin` (OOS F2).

## Happy path (canonical)

```bash
# 1. ingest
scripts_local/a3_run.py ingest --claim-id my1 --claim-text "..."

# 2. interpret (live)
scripts_local/a3_run.py interpret --claim-id my1

# 3. review — human OR AI
scripts_local/a3_run.py review --claim-id my1 --decision approve \
  --reviewer Bonorinoa [--acknowledge-none-noted]
# or:
scripts_local/a3_run.py review --claim-id my1 --decision approve \
  --reviewer hermes --reviewer-kind ai [--acknowledge-none-noted]

# 4a. formalize (live model draft)
scripts_local/a3_run.py formalize --claim-id my1

# 4b. OR recovery when model is blocked / unsuitable
scripts_local/a3_run.py formalize --claim-id my1 --from-file candidate.json
# candidate.json:
# {
#   "statement": "theorem t ... : Prop",
#   "target_theorem": "t",
#   "mapping_report": [ ... ]
# }

# 5. gap-ack if gaps present
scripts_local/a3_run.py gap-ack --claim-id my1 --reviewer Bonorinoa --notes "..."

# 6. verify with reviewer proof (fixture or authored)
scripts_local/a3_run.py verify --claim-id my1 --proof path/to/proof.lean

# 7. axiom loop if AXIOM_VIOLATION
scripts_local/a3_run.py axiom-approve --claim-id my1 --reviewer Bonorinoa \
  --axioms "propext,Classical.choice,Quot.sound"
scripts_local/a3_run.py verify --claim-id my1 --proof path/to/proof.lean

# 8. evidence
scripts_local/a3_run.py bundle --claim-id my1
scripts_local/a3_run.py replay --claim-id my1
scripts_local/a3_run.py status --claim-id my1
```

## After Core-importing VERIFIED

Open `artifacts/local/a3/bundles/<id>/manifest.json` and confirm:

- `dependency_audit.core_imports`
- `workspace_identity.core_revision`
- checklist item `12_core_pin` via `bundle` command

## Prediction-first (CTO preference)

Before live claim batches, write `artifacts/local/<batch>-expectations.md`
with numbered pass/fail predictions, then compare actuals.

## AI reviewer notes

- Identity required; kind auto-inferred for `hermes`, `ai`, `leanecon-ai`, …
- `none_noted` still requires `--acknowledge-none-noted`
- CTO remains accountable (`docs/gate3/08-reviewer-policy.md`)
