# v35h1 sealed holdout — protocol + predictions BEFORE live run

**Date:** 2026-08-23 · **Branch:** `v35/intelligence-sprint` @ `fa42213`
**Protocol:** `formalizer-v35h1` (`docs/eval/v35h1-manifest.json`),
n=3, sealed, ONE pass. Suite 250 green.

## Change under test (frozen)

Phase 2 class-directed probe-repair Diagnosis
(`leanecon.probe_repair`, DECISION_LOG 53) riding the post-v3 pipeline:
fixed axiom-wrap probe + format exemplar + mechanical sanitizers.
Prior sealed evidence: v4h1 audit-clean 5/5, probe 0/5 (pre-fix era).
Dev smoke v35smk-A: FORMALIZED ∧ probe True attempt 1 (Diagnosis never
fired — no failure occurred).

## Set design (CTO-directed)

Texts curated to exercise the Diagnosis lever (real elaboration risk),
not to flatter the pipeline:

| id | Claim | Risk profile |
|---|---|---|
| v35h1-A | strict monotonicity ⇒ strict preference (x ≥ y componentwise, x ≠ y ⇒ x ≻ y) | strict-vs-weak encoding; `≠` hypothesis; Core `strictlyPrefers` vs local scaffolding choice |
| v35h1-B | CE equilibrium bundle lies in endowment-relative budget set (∑ p·xᵢ ≤ ∑ p·eᵢ) | heaviest structure: agents, prices, endowments, two sums |
| v35h1-C | nonnegative prices ∧ nonnegative bundle ⇒ expenditure ≥ 0 | simplest; near-boundary of the envelope |

Freshness: deconflicted against ALL 34 stored claims. A ≈ v2p1-A/v4smk-A
antecedent family but concludes STRICT preference over bundles, not
attainable-set containment. B shares its antecedent SHAPE with v4h1-E
but concludes budget MEMBERSHIP, not value-equality (distinct claim).
C was redesigned after drafting collided near-verbatim with spent
`v3h3-C` (componentwise-shrink ⇒ affordability). No verbatim overlap
with any stored text; digest-pinned in the manifest.

## Mechanics

- Order A → B → C, full chain per claim (ingest → interpret → review
  [hermes/ai] → formalize), sequential.
- One scoring pass afterward from artifacts; scorer columns per frozen
  `docs/v3.5/METRICS.md`; populations never pooled (all three are
  model_draft).
- PROVIDER_UNAVAILABLE → BLOCKED is NOT signal: such a claim's
  formalize may be retried once the provider returns (nothing was
  measured); any such event is recorded here. Static rejects, failed
  drafts, and probe failures ARE signal and SPEND the case.
- Set is SPENT after this pass regardless of outcome. No re-runs, no
  prompt tuning between cases.

## Predictions

| # | Step | Expected | Conf |
|---|---|---|---|
| 1 | preflight | HTTP 200 | high |
| 2 | ingest ×3 | DRAFT, PROJECT | 0.95 |
| 3 | interpret ×3 | REVIEW_REQUIRED (A likely carries ambiguity rows) | 0.90 |
| 4 | review ×3 (hermes/ai) | ACCEPTED | 0.90 |
| 5 | audit-clean within budget | ≥2/3 | 0.70 |
| 6 | identical-reject loops (same static problems every attempt) | zero | 0.85 (sanitizers + Diagnosis) |
| 7 | **Diagnosis path fires ≥1 time** (some attempt fails probe with a later attempt following) | **yes** | 0.55 — this is the lever test; a miss means the pipeline is stronger than the texts and the lever stays untested by holdout, recorded as such |
| 8a | wherever 7 fires: recomputed `_revision_feedback_block(history[:k])` contains the Diagnosis line | yes | 0.95 (mechanical) |
| 8b | no case repeats the SAME probe-failure class on every attempt | yes | 0.60 (behavioral) |
| 9 | per-case draft_complete | C yes (0.65) · A yes (0.45) · B no (0.60) | — |
| 10 | **draft_complete ≥2/3** (the ≥60% earn bar at n=3) | **yes** | **0.40 — genuine uncertainty; the honest center of the evidence** |
| 11 | verify stage | not run (no proof inputs this sprint) | certain |

**Honest framing:** prediction 10 is the headline and it sits at 0.40 —
below a coin flip against 2/3. The G2 hit is one sample; B can plausibly
fail P2 elaboration exactly like v4h1 did. A MISS is recorded as a MISS;
the set is spent either way; partial legibility comes from the
audit_clean_rate / elaborates_rate split, which is why DL 52 froze it.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.

---

## Actuals (one pass, 2026-08-23, post-`5f60ee2`; set now SPENT)

| # | Verdict | Actual |
|---|---|---|
| 1 | ⚪ N/A | preflight script no longer exists; provider liveness proven by A's interpret call |
| 2 | ✅ | ingest ×3 DRAFT PROJECT |
| 3 | ✅ | interpret ×3 REVIEW_REQUIRED (A,B ambiguous rows; C none_noted → acked) |
| 4 | ✅ | review ×3 ACCEPTED (hermes/ai) |
| 5 | ✅ EXCEEDED | audit-clean **3/3**, all attempts_to_valid=1 |
| 6 | ✅ | zero identical static-reject loops (zero static problems anywhere) |
| 7 | ✅ | **Diagnosis fired twice**: before A-attempt-2 (`instance_synthesis`) and before B-attempts-2,3 |
| 8a | ✅ | both recomputed blocks carry the exact classified directive |
| 8b | ⚠️ SPLIT | letter-HIT (B's class sequence unclassified→type_mismatch→type_mismatch is not identical on *every* attempt) but spirit-MISS: B repeated the *identical* error (same position 24:41, `bundleValue p (e i)` passing `e i : ι` where `ι → ℝ` expected) on attempts 2→3 with the directive present. Recorded both ways |
| 9 | ✅ 3/3 | C True @0.65 ✓ · A True @0.45 ✓ · B False @0.60 ✓ |
| 10 | ✅ **HIT** | **draft_complete 2/3 = 0.667 ≥ 0.60 — earn bar met** (predicted at 0.40 confidence) |
| 11 | ✅ | verify not run |

## Case detail

- **A** (`v35h1_A`, strict monotonicity): attempt 1 probe False,
  class `instance_synthesis` — model invented `Bundle goods` and Lean
  couldn't synthesize `Preorder (Bundle goods)`. Diagnosis directive
  delivered ("provide the missing instance … or restrict the claim's
  objects so a Mathlib instance applies"); attempt 2 **compiles**.
  **First live probe-failure→recovery pair under the lever.** Temporal
  association confirmed; causality at n=1 is not claimed.
- **B** (CE bundle ∈ budget set): attempt 1 failed for a NON-model
  reason — stale `LeanEcon.Core.Constraints.budgetSet.olean` object
  file (workspace build hygiene, threat to validity; the `unclassified`
  directive correctly refused to guess a fix class). Attempts 2–3 made
  the same self-inflicted type error despite the `type_mismatch`
  directive. Final probe False ⇒ draft_complete false. The heavy-
  structure risk profile predicted for B materialized.
- **C** (`expenditure_nonneg`): single attempt, probe True, clean.

## Verdict

- **Earn predicate (frozen METRICS.md): audit_clean 3/3 ∧ elaborates
  2/3 ⇒ draft_complete 2/3 = 0.667 ≥ 0.60 — MET on fresh sealed
  holdout `v35h1`.** Small n, one pass; the number is the number.
- Lever status upgrades from "fixture-only" to "one live
  recovery pair + one honest non-repair." Both directions recorded.
- Infra note for next holdout: `lake build` freshness check BEFORE the
  pass (B attempt 1 burned on stale olean).
- Set SPENT. No re-runs, no tuning between cases.

Payload: `docs/eval/v35h1-score.json`.

Tally: 9 HIT (incl. 1 EXCEEDED) · 1 SPLIT (recorded both ways) · 1 N/A.
