# v3 claim split (Phase 2)

**Status:** Phase 2 draft on `v3/phase1-wire-loop`. The **dev/regression**
and **v2-memory** rows are frozen. **Held-out** texts are PROPOSED —
do not ingest until the CTO approves the English.

Scoring: `scripts/eval_formalizer.py` (no provider). Live scorecard is a
separate credentialed command. 60–70% is illegal until held-out exists
**and** is scored.

## Dev / regression (scorer fixtures; do not tune prompts only to these)

From `docs/eval/v1-claim-set.md`:

| Claim id | Role |
|---|---|
| c1–c4 | walkthrough VERIFIED (reviewer proofs) |
| fwt1 | FWT / inversion class |
| oos1, oos2 | OOS + `12_core_pin` |
| oos3 | boundary (not scored for the 60–70% target) |

Committed synthetic cases live in `tests/fixtures/eval/formalizer/` and
are what CI scores. They are **not** the live claims.

## v2 memory (Phase 1 live set — comparable to 0/3)

Same `source_text` as VERIFIED `v2p1-A/B/C`, new ids (INIT_V3 D4):

| id | Live outcome (2026-08-13) | first_try_valid | attempts_to_valid |
|---|---|---|---|
| v3p1-A | FORMALIZED, probe fail, 4 gaps | true | 1 |
| v3p1-B | FAILED, no artifact (`:=` + D1) | false | null |
| v3p1-C | FORMALIZED after 2, probe fail, 10 gaps | false | 2 |

Do **not** re-formalize `v2p1-*`.

## Held-out v3 (4–6 new simple-class texts) — PROPOSED, not ingested

Freshness rule: no verbatim overlap with c1–c4, fwt1, oos1–3, v2p1,
v3p1. Envelope: existing Core only; no calculus demand, no existence /
Nash. CTO approves English **before** `ingest`.

Draft candidates will be written here only after a freshness pass over
every existing `source_text`. Until then this split has **zero** held-out
rows and **no** 60–70% number.

## Boundary (honesty set — not in the target)

| id | Why excluded |
|---|---|
| oos3 | mixed Nash; no game-theory Core |

## How to score

```bash
PYTHONPATH=src .venv/bin/python scripts/eval_formalizer.py \
  --fixtures tests/fixtures/eval/formalizer \
  --json-out artifacts/local/eval-formalizer.json
```

CI runs the same command without writing gitignored artifacts (exit 0 +
`provider_calls == 0`).

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
