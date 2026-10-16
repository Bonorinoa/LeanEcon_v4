# v3h3 sealed holdout (2026-08-16) — one pass, spent

**Branch:** `v3/phase1-wire-loop` @ `aacdadc`. No push/PR/tag.
**Protocol:** `formalizer-sealed-1` (`docs/eval/sealed-protocol.md`).
**CTO gate:** option (B) — park `v3.0.0` until a *new* sealed holdout
hits draft-complete ≥ 60%. This run was that holdout. It missed.

## Procedure (reuse for the next sealed set)

1. Inventory every `source_text` in `artifacts/local/a3/claims/*.json`
   plus Core declarations. Fresh = no verbatim overlap; simple-class
   only (existing Core; no calculus / existence / game theory).
2. Draft 4–6 texts in the **user-visible message** (not only in
   thinking). `n=5` makes the 60% bar exactly 3/5. Do **not** ask
   “approve as proposed” until the exact `source_text` is on screen.
3. Write predictions **before** ingest (`docs/eval/<id>-expectations.md`,
   no claim text). Owner copy of texts: `artifacts/local/<id>-owner.md`
   (gitignored). Seal with `leanecon.eval_protocol.seal_manifest`;
   commit only `docs/eval/<id>-manifest.json` (case_id + SHA-256).
4. Ingest (no provider). Preflight
   `scripts/mistral_preflight.py` (status only). Then
   `.venv/bin/python scripts_local/a3_run.py interpret|review|formalize`
   once per claim. Review: `--reviewer hermes --reviewer-kind ai`;
   add `--acknowledge-none-noted` when the EI says `none_noted`.
5. Score offline from artifacts + formalize-event `revision_history`.
   `FORMALIZED` is not draft-complete. Draft-complete needs audit-clean
   **and** probe compile **and** no vacuity/inversion.
6. Fill actuals. Mark the set **spent**. Do not retune or re-formalize
   it. Do not tag.

## Result

| id | Outcome | first_try | probe | draft_complete | Dominant reject |
|---|---|---|---|---|---|
| v3h3-A | FAILED ×3 | no | n/a | no | sorry then `:=` |
| v3h3-B | FORMALIZED @3 | no | FALSE | no | sorry on t1; probe syntax |
| v3h3-C | FORMALIZED @3 | **yes** | FALSE | no | probe `expected ':='` |
| v3h3-D | FAILED ×3 | no | n/a | no | `:=` then D4 (redefined `marketClearing` at root) |
| v3h3-E | FORMALIZED @2 clean | no | FALSE | no | sorry on t1; probe syntax |

- first_try **1/5**; draft_complete **0/5**; sole-author **0**
- Need 3/5. **MISSED.** Combined v3h+v3h2+v3h3 = **2/13 ≈ 15%**
- Spent claims (`v2p1-A` VERIFIED, `v3h-A` FORMALIZED) were untouched
- Probe misses on B/C/E were elaboration/syntax, not vacuity

## Scope that does not earn v3

Recovering a Codex “top 5” is not a license to implement B2 proving
or to retune spent holdouts. INIT_V3 earn rule is scorer numbers +
honest 60–70% (met / missed / narrowed) + CTO tag line. B2 stays out
(compile ≠ pass).

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
