# Out-of-sample (OOS) batch report — whole-system test before extension

> Status: **complete** (2026-08-08). Three custom claims walked through the
> live A3 pipeline after Gate 7 Core landed. No system extension in this
> batch — evaluation only. Expectations were recorded BEFORE runs
> (`artifacts/local/oos-expectations.md`). **Immediate F1 lifecycle fix**
> (post-report): `ACCEPTED→FAILED` / `FAILED→FAILED` / `BLOCKED→FAILED`
> added; oos2 replay re-checked `replay_ok=true`. Remaining items → Gate 8
> (`docs/gate8/INIT_GATE8.md`).
>
> Attribution: Prepared by Hermes Agent (Nous Research) under CTO
> direction; the CTO remains the sole semantic approver.

## 0. Executive summary

| Claim | Domain | Endpoint | Bundle | Headline signal |
|---|---|---|---|---|
| **oos1** | Equilibrium (IR at CE) | **VERIFIED** | `bundle-oos1-r1-478aeb` (12/12 incl. **12_core_pin**) | First live claim with Core pin; formalizer emitted vacuous `True` placeholders; reviewer proof used Gate 7 vocabulary |
| **oos2** | Consumer theory (budget expansion) | **VERIFIED** | `bundle-oos2-r1-6c1bee` (12/12 incl. **12_core_pin**) | Formalizer 2× blocked on `:=`; reviewer formal + proof; **replay_ok=false** (lifecycle gap) |
| **oos3** | Game theory (mixed Nash) | **FORMALIZED** (stop) | none (proof out of slice) | Formalizer 2× **D1-blocked** (scaffolding labeled `core`); zero Core vocabulary — extension signal |

**pytest:** 156 passed (unchanged). **No code changes** in this batch.

## 1. What the system is (reconfirmed live)

Not an agent system. Single-claim sequential lifecycle:

```
ingest → interpret → review → formalize → gap-ack → verify → axiom-approve → bundle → replay
```

- **2 LLM calls** per claim (interpret=`mistral-medium-3-5`, formalize=`labs-leanstral-1-5`)
- No retrieval, corpus, subagents, decomposition, or B2 proof loop
- Kernel + human review are load-bearing; models are drafting aids

## 2. Predictions vs actuals (15/15 scored)

| # | Predicted | Actual | Verdict |
|---|---|---|---|
| 1 | ingest PASS ×3 | DRAFT PROJECT ×3 | ✅ |
| 2 | oos1 EI non-null CE concept | `solution_concept: "Walrasian equilibrium"`, 3 ambiguities | ✅ |
| 3 | oos2 EI null concept | `null`, 2 ambiguities | ✅ |
| 4 | oos3 EI Nash concept | `"Nash equilibrium (mixed strategies)"`, 2 amb + degradation | ✅ |
| 5 | formalize fails/inverts | oos1: vacuous True + probe FAIL; oos2: 2× `:=`; oos3: 2× D1 | ✅ (richer) |
| 6 | oos1 core rows attempted | **ZERO core rows** — all `local_definition` + `h_* : True` | ⚠️ direction wrong; failure class worse |
| 7 | oos2 budgetSet rows | model never stored an artifact (blocked at `:=`) | ⚠️ N/A model; reviewer formal used core FQ |
| 8 | oos3 zero core rows | model *claimed* core with bare types → **D1 rejected** (no artifact) | ✅ D1 live (via mislabel path) |
| 9 | oos1 proof ≤2 iters | 1 iteration; baseline axioms | ✅ |
| 10 | oos2 proof 2–4 iters | ~2 (empty-goods edge + DecidableEq); baseline | ✅ |
| 11 | oos3 statement compiles | reviewer placeholder formalized; proof out of slice | ✅ (as designed) |
| 12 | axiom first-run loop | oos1 + oos2 both AXIOM_VIOLATION → approve → VERIFIED | ✅ |
| 13 | 12_core_pin live | **PASS** on oos1 + oos2 (Core imports pinned to `650f98eb4fe0…`) | ✅ |
| 14 | replay PASS | oos1 ✅; **oos2 ❌** lifecycle gap (see §4) | ⚠️ split |
| 15 | 156 green | 156 passed | ✅ |

**Score:** 12 solid ✅, 3 ⚠️ nuances (all informative, none silent).

## 3. Per-claim detail

### 3.1 oos1 — Individual rationality at CE (flagship)

**Claim:** At any competitive equilibrium, every consumer weakly prefers their allocation to their endowment: `u_i(e_i) ≤ u_i(x_i)`.

| Stage | Result |
|---|---|
| interpret | ACCEPTED after CTO review (pure exchange; `u(e)≤u(x)`; no extra utility axioms) |
| formalize | FORMALIZED; probe FAILED; vacuity warning (`True`); 9 gaps; **0 `core` rows** |
| gap-ack | 9 gaps acknowledged as evaluation signals |
| proof | Reviewer-authored; imports `Constraints`, `Equilibrium`, `Primitives`; 1 iter |
| verify | first-run axiom loop → VERIFIED |
| bundle | **12/12** including `12_core_pin: [Constraints, Equilibrium, Primitives] @ 650f98eb4fe0…` |
| replay | `replay_ok=true` (14 events, 0 problems) |

**Proof idea:** endowment ∈ budgetSetEndowment (value ≤ value) ⇒ maximization ⇒ `u(e) ≤ u(x)`.

**Ops note:** first VERIFIED bundle (`…1ae62e`) was built with a **stale installed package** (no PYTHONPATH=src) → missing `core_imports`/`core_revision`. Re-verify via `scripts_local/a3_run.py` (sets PYTHONPATH=src) produced the D2-correct bundle `…478aeb`. **Always use `a3_run.py` or reinstall after src edits.**

### 3.2 oos2 — Budget set strictly expands under income rise

**Claim:** Finite goods, prices > 0, m1 < m2 ⇒ `budgetSet p m1 ⊂ budgetSet p m2`.

| Stage | Result |
|---|---|
| interpret | ACCEPTED (proper superset; continuous bundles) |
| formalize | **2× PROVIDER_INVALID_OUTPUT** (`theorem … :=` proof body) — no artifact |
| recovery | Reviewer-authored formal candidate injected (FQ `core` rows for `budgetSet`) |
| proof | Reviewer-authored; needs `[Nonempty Goods] [DecidableEq Goods]` (empty-goods edge) |
| verify | axiom loop → VERIFIED; **12_core_pin** on Constraints+Primitives |
| replay | **`replay_ok=false`** — see §4 |

### 3.3 oos3 — Mixed Nash existence (boundary / extension signal)

**Claim:** Finite strategic-form game ⇒ mixed-strategy Nash exists.

| Stage | Result |
|---|---|
| interpret | ACCEPTED (finite players+strategies; strict deviation) |
| formalize | **2× D1 rejection** — rows labeled `core` with bare types (`ι : Type u`, etc.) |
| recovery | Reviewer formal with **zero `core` rows** (glossary_term + local_definition) |
| endpoint | **FORMALIZED** — proof deliberately out of slice (fixed-point machinery) |

**Extension signal:** Core has no game-theory vocabulary. A Nash/existence slice would need new glossary entries + promotion criteria, not just pipeline work.

## 4. System findings (actionable)

### F1. Lifecycle gap — formalize rejection transitions (oos2 replay) — **FIXED (immediate)**
`lifecycle.TRANSITIONS` allowed `ACCEPTED → FORMALIZED | BLOCKED` but **not** `ACCEPTED → FAILED`. The runner still emitted `ACCEPTED → FAILED` on `PROVIDER_INVALID_OUTPUT`, and `FAILED → FAILED` on a second identical rejection. Trace replay correctly flagged these as illegal.

**Impact (before fix):** any claim whose formalizer is statically rejected could not get `replay_ok=true` even if later VERIFIED via reviewer recovery.

**Fix landed (immediate post-OOS cleanup):** added `(ACCEPTED, FAILED)`, `(FAILED, FAILED)`, and `(BLOCKED, FAILED)` to `TRANSITIONS` + regression test `test_formalize_static_rejection_edges_are_legal`. **oos2 re-replay: `replay_ok=true`.**

### F2. Stale install hides D2 (oos1 first bundle)
`python -m leanecon.a3_runner` without `PYTHONPATH=src` used a pre-P4/P5 wheel → empty `core_imports`, no check 12. `a3_run.py` is correct. Document / consider making the console script always prefer src in dev, or pin reinstall in the skill (already noted; reinforced).

### F3. Formalizer still not statement-faithful (all three)
| Failure class | Claim |
|---|---|
| Vacuous placeholders (`h : True`) | oos1 |
| Proof body on theorem (`:=`) | oos2 (2/2) |
| Mislabeled `core` rows (D1 catch) | oos3 (2/2) |

**D1 earned its keep** on oos3 — without it, bare-type "core" rows would have polluted the store.

### F4. Semantic edges the interpreter misses (again)
| Edge | Claim | Parallel |
|---|---|---|
| `[Nonempty Goods]` for strict budget expansion | oos2 | fwt1 `[Nonempty Agent]` |
| `[DecidableEq Goods]` for point-mass witness | oos2 | new |

### F5. Reviewer-authored formal recovery has no first-class CLI
oos2/oos3 required a store-level inject script after model block. Works, but is outside `a3_runner`. A `formalize --from-file` (reviewer statement + mapping report) would make the recovery path auditable without ad-hoc scripts.

## 5. Implications — immediate vs Gate 8

| Bucket | Item | Status |
|---|---|---|
| **Immediate (this cleanup)** | F1 lifecycle transitions + test; oos2 replay green | **done** |
| **Immediate (this cleanup)** | OOS report + Gate 8 init brief committed; skill/ops note | **done** |
| **Immediate (ops habit)** | Always `scripts_local/a3_run.py` (or reinstall) — never bare `python -m` after src edits | documented |
| **Gate 8 primary** | `formalize --from-file` (reviewer recovery CLI) | proposed in `docs/gate8/INIT_GATE8.md` |
| **Gate 8 secondary** | Thin B2 proof-repair assist (optional) | proposed |
| **Gate 8+ / defer** | Corpus, retrieval, agents/subagents, game-theory Core, production VERIFIED corpus, P4 tooling leftovers | out of Gate 8 unless CTO opts in |

**Recommendation:** Gate 8 opens on **reviewer recovery + pipeline completeness**, not agents. See `docs/gate8/INIT_GATE8.md` §3–§6.

## 6. Artifact index

| Path | Role |
|---|---|
| `artifacts/local/oos-expectations.md` | pre-run predictions |
| `artifacts/local/a3/eis/oos{1,2,3}/` | EI revisions |
| `artifacts/local/a3/formal/oos{1,2,3}/` | formal candidates (oos2/3 reviewer-authored) |
| `artifacts/local/oos1/proof_input.lean` | IR-at-CE proof (Core) |
| `artifacts/local/oos2/proof_input.lean` | budget expansion proof (Core) |
| `artifacts/local/a3/bundles/bundle-oos1-r1-478aeb/` | D2-correct VERIFIED bundle |
| `artifacts/local/a3/bundles/bundle-oos2-r1-6c1bee/` | D2-correct VERIFIED bundle |
| `artifacts/local/a3-events/*.jsonl` | full traces |

## 7. Deliberately not done

- No code fixes (F1–F5 recorded only)
- No oos3 proof / VERIFIED (out of slice)
- No Core promotions from OOS vocabulary
- No commits (evaluation artifacts are gitignored under `artifacts/local/`)

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
