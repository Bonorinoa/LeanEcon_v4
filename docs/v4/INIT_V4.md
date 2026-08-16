# INIT_V4 — wire intelligence into the verifiable state machine

**Status:** DIRECTION LOCKED 2026-08-16 (CTO: narrow v3; dedicate
v3→v4 development to wiring intelligence). **Not an implementation
authorization.** No v4 code, no model swap, no new holdout, no tag
from this file. Empty clarify ≠ consent.

**Parent:** `docs/releases/v3.0.0.md` (Verifiable State Machine,
narrowed). **Base when v3 ships:** that tag. Until then, this is
the next-train brief on `v3/phase1-wire-loop`.

**Authority this does not override:** DECISION_LOG 1–47, reviewer
policy, kernel axiom audit, bundle 12-check, F1 lifecycle rule,
sealed-eval protocol, spent-holdout rule.

---

## 0. Why v4 exists

v3 is the **machine**: a single-claim lifecycle whose `VERIFIED`
label is kernel- and bundle-gated, with models allowed to draft
and required to fail honestly.

v4 is the **intelligence attached to that machine**. Draft-complete
on simple-class holdouts is **2/13 ≈ 15%**. first_try is 1/13.
Sole-author of `VERIFIED` is 0%. Prompt hardening and a third
sealed set did not move the number. The bottleneck is the draft
transitions (`interpret`, `formalize`, and only later `verify`
assist) — not another lifecycle feature.

Krakauer: do not add a second machine. Wire better drafts into
the one we already audit.

## 1. Proposed v4.0.0 promise (not earned)

On the **same simple-class envelope** (consumer / CE / FWT Core,
no new game theory):

1. Interpret and formalize drafts are produced by models that are
   *selected and measured* against `formalizer-sealed-1`, not by
   hope.
2. A new frozen holdout (not v3h / v3h2 / v3h3) is scored once,
   prediction-first. The 60–70% draft-complete target **returns
   here**, or is narrowed again in writing.
3. The v3 state machine is unchanged as the audit spine:
   reviewer owns meaning; `#print axioms` / `sorryAx` is the only
   pass; compile exit 0 is not a pass.
4. `--from-file` remains recovery.

### Non-claims (v4.0.0 does not start as)

- Unattended `VERIFIED`; production SLA; "solved autoformalization."
- B2 tactic search as a ship requirement (compile ≠ pass still holds;
  a later v4.x spike needs its own compiled toy and axiom-gated
  success).
- Agents, retrieval corpus, Nash Core, product UI, public API,
  embeddings-as-product, LaTeX parser.
- Retuning spent holdouts.
- Weakening EI / bundle / Core / reviewer policy.

## 2. What "wiring intelligence" means (and does not)

| In | Out |
|---|---|
| Measure-then-change the formalize (then interpret) draft_fn | New lifecycle states "because the model is an agent" |
| Model / prompt / repair-feedback work on **dev** cases only | Re-running v3h / v3h2 / v3h3 |
| One new sealed holdout after the change is frozen | Hand-edited scorecards |
| Keep FORMALIZED = audit-clean; probe is signal + loop feedback | Treating `revise_loop.accepted` as VERIFIED |
| Optional: AI-reviewer quality study (second rater) | Replacing the reviewer |
| Optional later: axiom-gated proof assist (B2 lesson) | Exit-0 tactic soup |

## 3. Phases (proposed; each is its own gate)

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | This file, approved or amended | authorize Phase 1 only |
| 1 | Intelligence brief: failure-class inventory from spent sets + a **dev-only** experiment card (no holdout) | go / iterate / halt |
| 2 | One frozen change (prompt, wrapper, or model pin) + fixture scorer still green | go / revert |
| 3 | New sealed holdout, predictions first, one pass | 60–70% met / miss / narrow |
| 4 | `docs/releases/v4.0.0.md` | tag / amend |

No phase auto-promotes. WIP limit: one open product promise (v3
must be tagged or explicitly parked before v4 is claimed on `main`).

## 4. Stop points

1. **Now.** Direction is locked. Do not implement Phase 1 in the
   same breath as the v3 narrow.
2. After a v3 tag (or a written "park v3, start v4 on this branch").
3. After Phase 1 brief — wait for "approve as proposed."
4. Never score a spent holdout as progress.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
