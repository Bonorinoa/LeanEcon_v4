# Skeleton measurement (v3 Phase 3)

**Status:** CLI shipped (`a3 skeleton`). Live edit-distance on v3p1
**halted** — no model-authored skeleton was produced for those claims.
Numbers below are **committed-fixture** distances only (library function
already existed). They are not a 60–70% claim.

## CLI

```bash
.venv/bin/python scripts_local/a3_run.py skeleton --claim-id <id> --file skel.lean
```

Unresolved `-- GAP:` / `sorry` / `?_` → `has_unresolved_gaps=true` →
`verify` refused. Claim state is not changed.

## Fixture measurement

| Pair | Distance | Note |
|---|---|---|
| identical skeleton | 0 | `skeleton_edit_distance(s, s)` |
| skeleton vs trivial close | >0 | `tests/test_skeleton_cli.py` |

Live v3p1-A/B/C: no skeleton artifact. `--from-file` proofs remain
reviewer-authored. time-to-VERIFIED not computed (confounded by human
latency; no ingest→VERIFIED on this branch for v3p1).

**Halt (INIT_V3 Phase 3 acceptance):** improve-or-halt → **halt live
measurement**. Product win is the verify gate, not a shorter proof.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
