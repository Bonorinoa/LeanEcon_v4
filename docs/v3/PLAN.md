# PLAN — v3 Phase 1 (wire the loop)

**Status:** Phase 1 implemented on `v3/phase1-wire-loop` (2026-08-13).
Stage 0 approved as proposed. Live same-text set scored honestly
(first_try_valid 1/3). No PR until remaining v3 phases have
verifiable checks.
**Parent:** `docs/v3/INIT_V3.md` (defaults D1–D5) + `docs/v3/METRICS.md`.
**Base:** `main` @ `9c12936` / tag `v2.0.0`, pytest 176.
**This card is Phase 1 only.** Phases 2–5 stay in INIT_V3 until their
own gate.

Empty `clarify` ≠ consent. “Looks done” ≠ consent. Stage 1 starts only
on an explicit CTO line: **approve as proposed** / **proceed as
proposed** / a written amend-then-go.

---

## Definition of Ready (Phase 1)

- [x] Written exit criteria (this file + INIT §4 Phase 1).
- [x] In / out of scope listed.
- [x] Defaults D1–D5 named (INIT §3) — waiting on CTO lock.
- [x] Predictions file exists **before** any live run
      (`artifacts/local/v3-p1-expectations.md`).
- [x] Files likely touched listed (below).
- [x] Stop points listed (below).

## Definition of Done (Phase 1)

- Red tests written first and watched fail, then green.
- pytest: 176 + new tests, no regression.
- `a3_runner` imports `leanecon.revise_loop`; live `formalize_claim`
  calls `revise_statement_draft`; `--from-file` unchanged.
- Formal artifact carries `revision_attempts` + `revision_history` on
  success; exhausted budget → `FAILED`, no artifact.
- If a new failure path appears, `lifecycle.TRANSITIONS` updated in
  the **same** change (F1). Expected: no new edges.
- Predictions-vs-actuals filled after (not before) the live run.
- Scorecard updated honestly; `sole_author_verified` stays 0% unless
  a model proof actually verified.
- README not lying (library ≠ product sentence flips only after the
  import exists).
- No merge, no tag, no DECISION_LOG item without CTO authorization.

---

## In scope

- TDD wiring of `revise_loop` into **live** `formalize_claim`.
- Attempt log on the formal artifact (success) / state-event detail
  (exhausted budget).
- Tests for contamination, budget cap, attempt-2 success.
- Honest scorecard rows + predictions file.
- Optional docs touch: README “libraries” line, ENGINEERING_LOG note
  — only after the import exists, in the same PR.

## Out of scope (even after approval)

- New CLI subcommands or flags.
- Skeleton CLI / `skeleton` import.
- New IRs, graphs, embeddings, LaTeX parser.
- Core declarations / Nash / game theory.
- Product UI, agents, corpus, public API.
- Scorer script (`eval_formalizer.py`) — that is Phase 2.
- Held-out v3 claim drafting — Phase 2.
- `v3.0.0` tag. Weakening the audit gate.
- Re-formalizing VERIFIED v2p1-A/B/C in place (use same-text new ids).
- Merge without explicit CTO authorization.

---

## Files likely touched (Stage 1, after approval)

| Path | Why |
|---|---|
| `tests/test_a3_runner.py` (or new `tests/test_formalize_revise_loop.py`) | red tests first |
| `src/leanecon/a3_runner.py` | `formalize_claim` calls the loop; persist history |
| `src/leanecon/lifecycle.py` | **only if** a new failure path appears |
| `docs/eval/formalizer-scorecard.md` | honest v3-p1 rows after live / tests |
| `artifacts/local/v3-p1-expectations.md` | predictions **before** live (gitignored) |
| `README.md` | flip “library, not CLI” once the import is real |

Do **not** touch: `skeleton.py`, Core Lean, schemas, reviewer policy,
bundle checklist, `formalize_from_candidate` contracts (except that
they keep working).

---

## TDD order (do not invert)

1. **Red.** Three tests against `formalize_claim` with injected
   `draft_fn` / `audit` / `probe` (or a test seam that does not
   require a live provider):
   1. Contamination still fails (sorry / theorem `:=`); no artifact;
      audit wins over a naive compiling probe.
   2. Budget cap: four dirty drafts offered → exactly 3 consumed →
      `FAILED`; no 4th provider call.
   3. Attempt-2 success: dirty then audit-clean → `FORMALIZED` and
      `revision_attempts == 2` on the written candidate.
2. Watch them fail (`ModuleNotFoundError` on the new seam, or
   single-shot behaviour).
3. **Green.** Minimal wiring in `formalize_claim` only.
   `cmd_formalize` live branch stays `formalize_claim(...)`.
   `--from-file` stays `formalize_from_candidate`.
4. Existing `tests/test_revise_loop.py` (3) stay green — do not
   rewrite the library unless a real bug appears.
5. Full suite: `.venv/bin/python -m pytest -q`.

## Wiring contract (do not invent a second loop)

```
formalize_claim:
  draft_fn(history) -> statement str
      adapter.request(FORMALIZE) with prior Feedback verbatim in prompt
      parse; stash {statement, target_theorem, mapping_report}
      parse fail / INVALID_OUTPUT -> consume attempt (INIT D5)
      PROVIDER_UNAVAILABLE -> return BLOCKED immediately (not an attempt)
  audit(stmt) -> problems
      validate_statement_text + validate_scaffolding_namespace
      + validate_mapping_report(stashed mapping, accepted EI)
  probe(stmt) -> (compiles, stderr)
      probe_statement_compiles  # signal only (INIT D2)

  if last attempt audit-clean:
      write formal artifact + revision_attempts + revision_history
      return FORMALIZED   # even if probe failed
  else:
      no artifact; state event detail has history
      return FAILED       # existing --from-file recovery
```

`revise_loop.accepted` (audit ∧ probe) is **not** the FORMALIZED
predicate. Do not change `revise_statement_draft` to paper over that;
the runner decides FORMALIZED from audit-clean + last stashed parse.

## Predictions protocol (before any live A3)

Write `artifacts/local/v3-p1-expectations.md` first:

| # | Step | Expected | Confidence | Rationale |
|---|---|---|---|---|
| … | … | pass/fail + artifact keys | 0–1 | why we believe it |

Then run, via **only**:

```bash
.venv/bin/python scripts_local/a3_run.py <subcommand> ...
```

Same-text new claim ids (INIT D4). Append actuals. Do not edit the
prediction column after the fact.

Suggested live set: three new ids whose `source_text` equals
v2p1-A/B/C (c1r2 pattern). Do not ingest until predictions exist.
Live formalize still needs credentials; if the key 402s, record
BLOCKED honestly — that is not a code bug.

## Evidence checklist

- [ ] Red → green transcript (test names + first fail + pass).
- [ ] `python -c "import leanecon.a3_runner as r; import leanecon.revise_loop"`
      and a grep showing the import in `a3_runner.py`.
- [ ] pytest count ≥ 179 (176 + ≥3), all green.
- [ ] Scorecard: first-try / attempts / sole-author **0%** unless a
      model proof verified.
- [ ] Predictions-vs-actuals table.

## PR / merge (only if CTO later asks to ship)

- Branch off `main`. hermessinho (`open_pr.py --bot`) for push + PR.
- CTO token for merge. `merge_pr.py <PR> clear-checks` only after
  explicit merge authorization and green check-runs.
- Do not tag. Do not push to `main` directly.

## Stop points

1. **Now (Stage 0).** Docs written. Wait.
2. After reds fail: implement, do not expand scope.
3. After greens: write predictions **before** live.
4. After live: fill actuals + scorecard; stop for Phase 1 gate.
5. Never merge / tag from this card alone.

## Top risk

Wiring the loop does not change labs-leanstral. Expect another 0/N
first-try-valid. That is still a product win if FAIL is honest,
budget-capped, and the attempt log exists. Claiming 60–70% from
Phase 1 is a lie.

---

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
The CTO remains the accountable semantic authority and sole semantic
approver.
