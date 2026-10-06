# INIT — v4 agentic sprint kickoff

**Written:** 2026-08-23, at the v3.5.0 ship boundary. For the session
that resumes work toward v4. Self-contained by design: read this, then
the read-first list, and you are initialized.

## Where things stand

- v3.5.0 "Measured Elaboration" ships the intelligence sprint: sealed
  holdout draft_complete **2/3 ≥ 0.60** (v4h1 era: 0/5), suite 250,
  DECISION_LOG 50–54. Release packet: `docs/releases/v3.5.0.md`.
- Approved release sequence: **Intelligence (done, v3.5.0) → Agentic
  (v4)**. The v4 promise is agentic capability: tool-using repair and
  assist under fixed signatures — NOT proof generation (B2 stands:
  compile ≠ pass).

## Locked decisions — do NOT reopen without CTO direction

| Ref | Decision |
|---|---|
| DL 50 | P1–P6 fidelity-property ontology is the labeling object; observed errors are measurements of property violations |
| DL 51/D2 | Probe repair consumes the normal MAX_REVISION_ATTEMPTS=3 budget; no silent expansion |
| DL 51/D3 | Consultative `opinion` side-door was parked **to v4 — it is now first-class v4 candidate work**, consultative only, NEVER authorized to emit ACCEPTED |
| DL 51/D4 | Formalize pin was `labs-leanstral-1-5`; **SUPERSEDED by DL 57** — live pin is `openrouter/free` |
| DL 52 | Metric definitions frozen in `docs/v3.5/METRICS.md`; amendments go through DECISION_LOG |

## Read-first (in order)

1. `docs/releases/v3.5.0.md` — what just shipped, and what deliberately didn't
2. `docs/v3.5/METRICS.md` — frozen metric vocabulary
3. `docs/v3.5/experiments/L1-probe-repair-card.md` — principled/heuristic split discipline
4. `docs/gate3/DECISION_LOG.md` items 44–54
5. `docs/v3.5/state-machine-flow.html` — info-flow explorer (schemas per state)

## Evidence base

- Sealed (spent): `formalizer-v35h1` 2/3 (`docs/eval/v35h1-expectations.md`,
  `v35h1-score.json`, manifest); v4h1 0/5; v3h/v3h2/v3h3 history.
- Dev baseline: model drafts elaborate 4/8; failures only
  `binder_annotation`+`syntax` (`docs/eval/v35-baseline-*`).
- Lever reality check: ONE live recovery pair (`instance_synthesis`),
  ONE non-repair (repeated identical type error despite directive).
  Any v4 claim of repair efficacy must be powered accordingly.

## Open questions for the kickoff (G0 slice material)

1. **Model posture:** **RESOLVED 2026-10-06 (DL 57).** Mistral
   unsubscribed. Live pin is OpenRouter `openrouter/free`. HuggingFace
   inference remains a future complementary path, not a second adapter.
2. **Opinion vs agentic-repair order:** which lands first in v4?
   (Opinion is pure-addition consultative surface; repair extends the
   Phase 2 mechanism with tool use.)
3. **Holdout sizing:** n=3 met the bar but proves little; propose
   n≥8 fresh sealed set with texts curated to stress the failure
   classes the Diagnosis table covers.
4. **Build-freshness gate:** automate the stale-`.olean` check before
   every probe pass (v35h1-B attempt 1 burned on it).
5. **Verify-stage metrics:** untouched this sprint; v4 candidate.

## Process notes (carried forward)

- Prediction-first: predictions committed before any live call; misses
  recorded as misses (`docs/eval/*-expectations.md` pattern).
- Empty clarify ≠ consent. Live smokes and holdouts spend quota — CTO
  gate each time. Sealed sets are spent forever.
- Same-text/new-id technique for dev-text reuse; deconflict ALL new
  texts against stored claims before sealing (v35h1-C collision caught).
- Run everything through `.venv/bin/python scripts_local/a3_run.py …`;
  bare `python -m leanecon.a3_runner` uses stale installs.
- Credentials at ship day: CTO profile GITHUB_TOKEN 401 (rotation
  still outstanding — blocks protection ops); LEANECON_BOT_TOKEN =
  hermessinho, push+PR only, cannot merge own PRs.
- Attribution: Hermes Agent (Nous Research) under CTO direction; CTO
  sole semantic approver; AI-authored work credited in docs.
