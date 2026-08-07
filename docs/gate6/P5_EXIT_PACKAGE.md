# Gate 6 — Exit evidence packet (P5)

> Status: **APPROVED by the CTO 2026-08-06 — Gate 6 CLOSED.** The exit
> evidence below was verified (all real tool output); the ledger update +
> this packet are committed as the closing docs (DECISION_LOG item 25).
> Gate 7 (equilibrium-family declarations, per-declaration promotion)
> is the authorized next slice.
>
> Authority: design + plan approved (DECISION_LOG 15–18); P1–P4 merged
> (PRs #7–#10); P5 = clean-clone reproduction, ledger update, agreement
> check, live Core-import verification, this packet.

## 0. Exit evidence summary (migration-plan Gate 6 criteria)

| Criterion | Evidence | Status |
|---|---|---|
| Approved design | DECISION_LOG 15; `a3-core-design.md` + references; PR #7 | ✅ |
| First reviewed Core sample builds from a **clean clone** | P5.1 clean-clone reproduction (§2.2) | ✅ |
| No v3 custom Lean copied | Ledger K1–K6 (no IMPORT/ADAPT exceptions); P5.3 marker scan (§2.4) | ✅ |
| Ontology and Lean declarations agree | P5.3 mechanical agreement check (§2.4) | ✅ |
| Migration ledger records every v3 relationship | `docs/gate3/01-migration-ledger.md` Core-specific register (P5.4) | ✅ |
| Per-phase CTO approval records | DECISION_LOG 16–24 + P2/P4 review packages (§3) | ✅ |

## 1. Phase execution record (P1–P5)

| Phase | Deliverable | Merged | Tests |
|---|---|---|---|
| P1 | EI schema freeze 1.0.0 (docs-only) | PR #7 | 137 green |
| P2 | First Core batch: 6 declarations + 2 theorem boundaries | PR #8 | 137 green |
| P3 | Glossary registry v1 (28 entries + change log) | PR #9 | 137 green |
| P4 | A3 contract deltas D1/D2/D4 (+ D3 docs) | PR #10 | **156 green** |
| P5 | Clean-clone reproduction, ledger, agreement check, live Core-import verification, this packet | pending CTO review | 156 green |

## 2. Evidence detail

### 2.1 Design and batch builds (P2, verbatim — `docs/gate6/P2_REVIEW_BATCH.md`)

```
$ lake build LeanEcon.Core.Theorems   (builds the batch chain)
✔ [3000/3000] Built LeanEcon.Core.Theorems (1.6s)
Build completed successfully (3000 jobs).

$ lake env lean .a3-candidates/p2-check/Check.lean
LeanEcon.Core.Constraints.budgetSet {Goods : Type} [Fintype Goods] (p : Goods → ℝ) (m : ℝ) :
  Set (Primitives.bundle Goods)
LeanEcon.Core.Utility.strictlyIncreasing {Goods : Type} (u : Primitives.bundle Goods → ℝ) : Prop
LeanEcon.Core.Theorems.budgetExpansion_nonShrinking {Goods : Type} {Bold Bnew : Set (Primitives.bundle Goods)}
  (h : Bold ⊆ Bnew) : Choice.attainableSet Bold ⊆ Choice.attainableSet Bnew
LeanEcon.Core.Theorems.strictlyIncreasing_strictPref {Goods : Type} {u : Primitives.bundle Goods → ℝ}
  (hu : Utility.strictlyIncreasing u) {x y : Primitives.bundle Goods} (hxy : y ≤ x) (hne : y ≠ x) : u y < u x
'LeanEcon.Core.Theorems.budgetExpansion_nonShrinking' depends on axioms: [propext, Classical.choice, Quot.sound]
'LeanEcon.Core.Theorems.strictlyIncreasing_strictPref' depends on axioms: [propext, Classical.choice, Quot.sound]
```

### 2.2 Clean-clone reproduction (P5.1, verbatim)

Fresh clone of `Bonorinoa/LeanEcon_v4` at `504b987` into `/tmp/leanecon-p5-clean`,
then the plan's evidence command, then pytest in a fresh venv:

```
$ git clone https://github.com/Bonorinoa/LeanEcon_v4.git /tmp/leanecon-p5-clean
504b987 docs(gate6): sync bundle checklist (12_core_pin) and plan status (P1-P4 done)

$ lake build LeanEcon.Core.Theorems LeanEcon.Core.Preferences LeanEcon.Core.Constraints LeanEcon.Core.Utility
✔ [3001/3002] Built LeanEcon.Core.Constraints (6.9s)
✔ [3002/3002] Built LeanEcon.Core.Theorems (1.5s)
Build completed successfully (3002 jobs).

$ .venv/bin/python -m pytest -q
156 passed in 35.66s
```

Environment notes (honest reproduction conditions):
- Mathlib `v4.32.2` compiled **from source** in the clone — this machine's
  toolchain has no `lake exe cache` facility, so no olean cache fetch
  (the standard fresh-clone path on machines with the cache facility is
  faster; the result is identical).
- The full-Mathlib tail (heavy Analysis/MeasureTheory modules) exceeded
  24 GB RAM at default parallelism (12 jobs) and had to be finished with
  `lake build Mathlib -- -j4`; the Core-module closure built at full
  parallelism (first run: `lake build LeanEcon.Core.*` completed, 3002
  jobs, before the memory-heavy tail was attempted).
- Python venv pinned to **3.11** (the project baseline). A default `uv
  venv` (3.12) breaks jsonschema/rpds resolution under the Hermes session
  PYTHONPATH — a real environment pitfall worth recording (see skill).
- The `import Mathlib` probe contract (formalize prompt) requires the
  complete Mathlib build (`Mathlib.olean`), not just the Core closure —
  the closure alone leaves `test_probe_statement_compiles_real_workspace`
  failing.

### 2.3 Live Core-import verification (P5.2 — closes the D2 risk-register loop)

The risk register required D2 to land before any claim imports Core; this
demonstrates the Core-era flow works end-to-end. Candidate
(`lean_workspace/.a3-candidates/p5-check/Check.lean`, gitignored):
a reviewer-shaped proof importing `LeanEcon.Core.Theorems` +
`LeanEcon.Core.Constraints`, restating the c1-family boundary with
fully-qualified Core identifiers (D1 style). Verbatim kernel output:

```
$ lake env lean .a3-candidates/p5-check/Check.lean
'p5_core_import_candidate' depends on axioms: [propext, Classical.choice, Quot.sound]
EXIT=0
```

Core-importing candidate compiles in the pinned workspace; axiom closure
is exactly the Mathlib baseline — "Core adds no axioms" holds live.

D2-pinned sample bundle (constructed record from the real kernel output;
`bundle-c-p5-r1-8315f3`):

```
workspace_identity: {
  "core_revision": "ef0a5386884bc73ee40cd778afe966ae971585f7688550acd3f5da60960031ec",
  "mathlib": "v4.32.2", "pinned": true, "toolchain": "leanprover/lean4:v4.32.2", ... }
dependency_audit: {
  "core_imports": ["LeanEcon.Core.Constraints", "LeanEcon.Core.Theorems"],
  "imports": [...same...], "mathlib_revision": "v4.32.2" }
result: VERIFIED
  [x] ... all 11 original checks ...
  [x] 12_core_pin: Core imports [...] pinned to ef0a5386884b… digest matches workspace
independent recompute of core_revision: ef0a5386884bc73e …
```

### 2.4 Ontology–declaration agreement + no-v3-copy check (P5.3, mechanical)

```
declarations found in Core tree: 8
  attainableSet (Choice.lean), budgetExpansion_nonShrinking (Theorems.lean),
  budgetSet (Constraints.lean), bundle (Primitives.lean),
  strictlyIncreasing (Utility.lean), strictlyIncreasing_strictPref (Theorems.lean),
  utility (Utility.lean), weakPreference (Preferences.lean)
A ok: entries 1, 6, 7, 9, 12, 13 -> core + declared (6/6)
B ok: budgetExpansion_nonShrinking (entry 8, c1); strictlyIncreasing_strictPref (entry 13, c3)
C: no equilibrium declarations / no Equilibrium module (checked)
D: no v3 markers in Core modules (checked)
P5.3 ontology-declaration agreement check PASSED
```

### 2.5 Migration ledger (P5.4)

`docs/gate3/01-migration-ledger.md` gains the Core-specific disposition
register K1–K6 (Preamble rebuild/inspiration; scratch + benchmark +
theorem-stub claim set historical-discard; `preamble_library.py`
rebuild/inspiration; v3 docs historical). No IMPORT/ADAPT exceptions.

## 3. Approval records index

| Item | Ref |
|---|---|
| EI schema FROZEN 1.0.0 | DECISION_LOG 16 |
| Glossary registry locked (28 entries) | DECISION_LOG 17 |
| Implementation plan authorized (P1–P5) | DECISION_LOG 18 |
| fwt1 live test evidence | DECISION_LOG 19 |
| P2 batch approved (per-declaration records) | DECISION_LOG 20 + `P2_REVIEW_BATCH.md` §6 |
| P3 registry v1 approved + merged | DECISION_LOG 22, PR #9 |
| P4 deltas approved (D1–D8) | DECISION_LOG 23 + `P4_REVIEW_BATCH.md` §3 |
| Gate 6 design approved (incl. v3 dispositions §6) | DECISION_LOG 15 |

## 4. Contamination / non-goals confirmation

- No v3 custom Lean copied into `LeanEcon/Core/**` (marker scan PASSED);
  no IMPORT/ADAPT exceptions in the ledger.
- No benchmark gold, intended statement, or v3 theorem stub in Core, the
  corpus, or the runtime (K4/K5 dispositions).
- No provider logic, prompts, or adapter code inside Core (P2 code review).
- No equilibrium-family declarations (entries 21–28 stay glossary-only;
  Gate 7 slice).
- No B2 proof loop, no production `VERIFIED` claims, no release artifacts.

## 5. Open items for Gate 7 (out of scope, carried forward)

1. Equilibrium-family declarations (`marketClearing`, `competitiveEquilibrium`,
   `paretoEfficiency` + endowment-relative `budgetSet` form) with
   per-declaration promotion (ontology records + CTO gate).
2. B2 proof loop; corpus expansion; retrieval; release.
3. Production `VERIFIED` claims importing Core (the P5.2 flow, now
   D2-pinned, is the template).
4. Optional: D3 CI grep; verify-side scaffolding soft signal; `none`
   mapping-kind removal (all recorded in `P4_REVIEW_BATCH.md` decisions).

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This packet
authorizes nothing; Gate 7 begins only after CTO approval.
