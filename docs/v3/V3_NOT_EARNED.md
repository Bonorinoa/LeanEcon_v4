# v3.0.0 — verdict MISSED (do not tag)

**Status:** held-out scored 2026-08-13 (v3h+v3h2) and 2026-08-16
(v3h3 sealed). 60–70% **NOT met**. **Do not tag.** Package on this
branch is `3.0.0.dev0`. INIT_V3 Phase 5 earn rule is not met.

## Held-out numbers (frozen split, final pipeline)

| Claim | Attempts | Outcome | Probe | draft_complete |
|---|---|---|---|---|
| v3h-A | 3 | FORMALIZED | TRUE | ✅ |
| v3h-B | 3 | FAILED | n/a | ❌ |
| v3h-C | 3 | FORMALIZED | FALSE | ❌ |
| v3h-D | 2 | FORMALIZED | TRUE | ✅ |

- first_try_valid **0/4**; attempts_to_valid A=3 / D=2 / B,C null
- draft_complete **2/4 = 50%** (threshold 3/4)
- sole_author_verified **0%**; 60–70% **MISSED**
- Probe instrument amended (axiom-wrap) — measurement fix, documented
  in METRICS §3.1; no prompt was tuned to the held-out set.

### v3h3 (sealed, 2026-08-16) — n=5, spent

draft_complete **0/5**, first_try **1/5** (C only), sole-author **0**.
Need 3/5. **MISSED.** Combined with v3h+v3h2: **2/13 ≈ 15%**.
Manifest: `docs/eval/v3h3-manifest.json`. Do not re-run.

## Why the branch exists

Loop wired, scorer + CI, skeleton CLI, probe feedback in the loop,
held-out scored. All unreleased on `v3/phase1-wire-loop`.

## What v3.0.0 would still need

- draft_complete ≥ 60% on held-out **or** a CTO-approved narrowed
  promise (e.g. "within-budget valid, probe optional" — a real
  definition change, CTO decision)
- README non-claims + DECISION_LOG items + builder bump
- `docs/releases/v3.0.0.md` + CTO-approved tag

## Tag rule

No `v3.0.0` from this packet. This file is not a release packet.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
