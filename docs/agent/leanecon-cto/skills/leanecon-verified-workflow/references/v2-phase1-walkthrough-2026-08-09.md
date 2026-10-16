# v2 Phase 1+2 walkthrough (2026-08-09)

AI reviewer exercised end-to-end on 3 fresh OOS claims; bounded
revision-loop harness shipped (TDD). Full predictions-vs-actuals table in
`artifacts/local/v2-p1-record.md` (gitignored); this file is the
condensed durable record.

## Scope
- **Phase 1 (zero new code):** exercise the AI reviewer
  (`--reviewer hermes --reviewer-kind ai`) on 3 fresh OOS simple-class
  claims → predictions first, CTO approves claim text before ingest,
  CTO spot-checks every AI decision.
- **Phase 2:** `src/leanecon/revise_loop.py` bounded kernel-feedback
  revision loop (TDD).

## Claims (v2p1-A/B/C)
- **A** budget binds at an optimum (single agent): `budgetSetEndowment` +
  `strictlyIncreasing`, `[Nonempty Goods]` + strictly positive prices.
- **B** spending monotone in consumption: componentwise `x ≤ y`,
  nonneg prices → `(∑ p g * x g) ≤ (∑ p g * y g)` (pure Mathlib).
- **C** Walras' law (aggregate): `marketClearing` + per-agent budget
  binds → double-sum identity. "Budget binds" is a stated assumption,
  never derived from monotonicity.
All inside the v1 Core envelope — no new Core declarations.

## Provider 402 → resolution path (class-level)
- v1-era `MISTRAL_API_KEY` returned **HTTP 402** on `interpret`
  (surfaces as `FAILED` / `PROVIDER_INVALID_OUTPUT` — the adapter's
  `>= 400` catch-all; 401/429/5xx are UNAVAILABLE; INVALID_OUTPUT kinds
  get NO backoff retry by design). Not a code bug.
- Fix: rotate/fund the key in `~/.hermes/profiles/leanecon-cto/.env`,
  then secret-safe preflight (re-runnable:
  `scripts/mistral_preflight.py`) — prints presence/length/mtime/status
  only, never the key. Retry edge `FAILED → INTERPRETED` is legal.
- Do NOT blind-loop retries: each retry is preceded by a successful
  preflight + CTO signal. 2026-08-09 evidence: preflight status 200
  immediately after the v1→PAYG key swap.

## AI reviewer results
- 3/3 EI reviews ACCEPTED (`reviewer_kind=ai` on every record);
  CTO spot-check **3/3 agree (100%)** — prediction #8's "≥1
  disagreement" did NOT materialize (recorded as favorable deviation).
- Interpreter drift on C: `quantifiers` ADDED non-source conditions
  ("x,e non-negative", "p strictly positive") — neither is needed for
  Walras' law. Flagged at AI review, carried into the formal as 2
  `unmapped` rows, AI gap-acked. Evaluation signal, not a failure.

## Formalize: live rejects → reviewer recovery
- Live: 3/3 × 2 waves static rejects (proof-body `:=` on A/C; **`sorry`
  + `:=` on B — contamination caught pre-kernel** by
  `validate_statement_text`, B2 lesson live). Doctrine: no 3rd loop.
- `--from-file` (CTO-authorized): round 1 — B FORMALIZED, A/C FAILED on
  **D1** (`core` rows carrying bare ids `hu`/`hmax`/`hclear`/
  `market_clearing`); round 2 (one-line `mapping_kind` fixes →
  `local_definition`/`glossary_term`) — 3/3 FORMALIZED. Template:
  `templates/from_file_candidate.json`.

## Verify: two waves
- Wave 1: A `LEAN_SYNTAX_ERROR`; B/C `AXIOM_VIOLATION` (baseline closure
  only — needs per-run `axiom-approve`, then `FAILED → PROVING`).
- A diagnosis (manual `lake env lean` on the exact candidate):
  - `rw [Finset.sum_ite_eq]` FAILS when the bound variable is on the
    LEFT of `=` in the ite condition (`∑ g, if g = g0 then … else …`) —
    the `@[simp]` lemma fires where rw's pattern doesn't: use `simp`.
  - `field_simp` after `dsimp` may already close the goal; a trailing
    `ring` then errors "No goals to be solved" — drop it.
- Evidence-first pattern that saved a verify round: copy the fixed proof
  to `.a3-candidates/<claim>/manual-check/Candidate.lean`, append
  `#print axioms <target>`, `lake env lean` it, confirm EXIT 0 + baseline
  closure + no sorryAx BEFORE running `a3 verify`.
- Wave 2: **3/3 VERIFIED** — 12/12 bundle checks incl. `12_core_pin`
  (Core digest `650f98eb…`), `replay_ok=true`, axioms
  `[propext, Classical.choice, Quot.sound]` only.

## Phase 2 TDD (bounded revision loop)
- Red: `tests/test_revise_loop.py` → `ModuleNotFoundError:
  leanecon.revise_loop`. Green: 3 tests (contamination gate — sorry
  draft rejected by audit even when naive probe says "compiles"; budget
  `MAX_REVISION_ATTEMPTS=3` — no silent 4th; clean pass + revision
  history). Regression: 171 passed.
- F1 rule: no `TRANSITIONS` change needed — standalone harness with
  injected `audit`/`probe` boundaries; no runner/bundle edits.

## Ship + next steps
- PR #15 (`99f8c38`, 5 files: revise_loop.py, test_revise_loop.py,
  scorecard v2 section, `docs/v2/INIT_V2.md`, `INIT_PROMPTS.md`), bot
  push, CI green; **merge is CTO-only** (merge_pr.py + verify_protection.py).
- Phase 3 (proof-skeleton assist) kicked off on `v2/phase3-skeleton`,
  stacked on the Phase 2 branch → **rebase onto main after PR #15
  merges** to keep the Phase 3 diff clean. Red contract tests written:
  `tests/test_skeleton_contract.py` (have-chain structure, explicit
  annotated gaps, B2 no-smuggled-bodies flag, audit-gate-unchanged,
  edit-distance measurement). Halt-if-no-improvement criterion intact.

**Attribution:** Hermes Agent under CTO direction; CTO remains sole
semantic approver.
