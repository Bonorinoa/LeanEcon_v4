# Core declaration promotion — full procedure + P2 worked example

Backs SKILL.md §8. The class of work that promotes LeanEcon Core
vocabulary declarations (started at Gate 6 P2, 2026-08-06). Design
authority: `docs/gate6/a3-core-design.md` (§7 promotion criteria) and
`docs/gate6/IMPLEMENTATION_PLAN.md` (phases P1–P5, per-phase CTO gates).

## 1. The ontology record template (per declaration)

```text
- Economic view: plain-language meaning, as reviewed
- Formal view:   Lean type/signature sketch + Mathlib reuse
- Assumptions:   minimal assumptions; stronger/weaker variants
- Axiom audit:   expected axioms (baseline unless noted)
- D3 collision:  no Mathlib root-namespace name reuse (checked)
- Examples:      example / counterexample where useful
- Source:        accepted EI definition id + claim id (anchors)
- Approval:      reviewer, date, DECISION_LOG item + PR ref
```

## 2. The 7 promotion criteria (a3-core-design.md §7)

1. Plain-language economic meaning (economic view) — reviewed.
2. Lean type/signature explanation (formal view) — reviewed.
3. Assumptions + stronger/weaker variants listed.
4. Dependency/axiom audit (baseline only) **+ namespace collision check
   (D3)** — the fully-qualified name must not collide with any imported
   dependency's namespace; unqualified use in candidates must not shadow
   imported Mathlib identifiers.
5. Examples and counterexamples where useful.
6. A CTO approval record (reviewer, date, ref) in the ontology record +
   DECISION_LOG.
7. Needed by a reviewed claim or a planned slice — no orphan declarations.

No batch shortcuts: even when the CTO approves the batch in one message,
record per-declaration approval records.

## 3. Compile-before-review evidence pattern

```bash
# from lean_workspace/ (PATH needs ~/.elan/bin)
lake build LeanEcon.Core.Theorems            # builds the chain: Theorems -> Choice/Utility -> Primitives
lake build LeanEcon.Core.Preferences LeanEcon.Core.Constraints   # standalone modules NOT in that chain
```

Check file recipe (gitignored, under `.a3-candidates/<name>/Check.lean`):

```lean
import LeanEcon.Core.<each module>
open LeanEcon.Core
#check <Area>.<declaration>          -- one per declaration
#print axioms <Area>.<theoremBoundary>   -- theorem boundaries only
```

Run `lake env lean .a3-candidates/<name>/Check.lean`. Expected: every
`#check` resolves; every `#print axioms` shows the baseline
`[propext, Classical.choice, Quot.sound]` (or fewer — never more; a
`sorryAx` in the closure while the file has compile errors is error
residue, not a real sorry).

## 4. Review-package structure (what the CTO reads)

- **Batch table**: `# | Declaration | Area | Seeded by | Kind | Compiles | Axioms`
- **Ontology records**: one per declaration (§1 template).
- **7-criteria checklist**: batch-wide table; criterion 6 marked "⬅️ this
  review".
- **Decisions table**: `D1..Dn | Question | Proposal | Alternatives` — the
  CTO answers "approve as proposed" or per-item. Include scope questions
  (e.g. income-form budgetSet only, strong-componentwise reading,
  vocabulary-anchor aliases) so approval is meaningful, not rubber-stamp.
- **"Deliberately NOT in this batch"**: equilibrium family, demand/choice
  correspondences, A3 code changes (P4), v3 material, model-authored
  declarations.
- **Process notes**: file locations (untracked until commit), build
  commands, what happens after approval.

## 5. After approval

1. Patch the review package: status header -> APPROVED; add §Approval
   records table (declaration | approved | reviewer | ref).
2. Add DECISION_LOG items (batch approved; commit pending) + resolutions
   incorporated.
3. Commit (branch `gate6/p<phase>-<name>`), push, open PR
   (`scripts_local/open_pr.py <branch> <title-file> <body-file>`).
4. Merge per §4 quirks of the SKILL.md: dispatch scaffold+a1 (API-created
   PRs may not auto-trigger), verify checks green directly (latest run per
   name), `merge_pr.py <PR> clear-checks`, then verify protection restored
   exactly (`verify_protection.py`). Post-merge: sync local main
   (`fetch` + `--ff-only`), delete the feature branch (separate command —
   combined commands with `git branch -d` trip the approval gate).

## 6. P2 worked example (2026-08-06, merged as PR #8)

Batch: `bundle` (Primitives, abbrev, explicit `Goods` param),
`weakPreference` (Preferences, abbrev), `budgetSet` (Constraints, def,
income form `{x | Σ pᵢ·xᵢ ≤ m}`, endowment form deferred to Gate 7),
`attainableSet` (Choice, thin def carrying the c1 reviewed reading),
`utility` (Utility, abbrev), `strictlyIncreasing` (Utility, def,
componentwise strong reading + c3 direction convention `y ≤ x → y ≠ x →
u y < u x`) + theorem boundaries `budgetExpansion_nonShrinking` (c1
family) and `strictlyIncreasing_strictPref` (c3 family).

Verdicts D1–D6: all approved as proposed. Evidence: 3000/3000 jobs build;
both theorem boundaries audit to baseline; no Mathlib collisions; specific
imports only. Approval records in `docs/gate6/P2_REVIEW_BATCH.md` §6;
DECISION_LOG items 20–21; merge `bd71bb885b31`.

## 7. Relationship to the plan

- P1: schema-freeze docs commit (EI schema `$comment` + DECISION_LOG) —
  merged PR #7.
- P2: first Core batch — merged PR #8.
- P3: glossary registry v1. P4: A3 contract deltas D1/D2/D4 (mapping-kind
  `core`, fully-qualified rows, Core pin in bundle, namespaced
  scaffolding). P5: clean-clone evidence + Gate 6 exit package.
- Equilibrium-family declarations (`competitiveEquilibrium`,
  `marketClearing`, `paretoEfficiency`) are glossary-only until the Gate 7
  slice — never promote them early to "complete" the vocabulary.

**Attribution:** prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
