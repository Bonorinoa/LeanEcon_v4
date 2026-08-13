# v3.0.0 — NOT EARNED (do not tag)

**Status:** draft honesty packet. **Do not tag.** INIT_V3 Phase 5 earn
rule is not met.

## What this branch has

| Phase | Commit | Check |
|---|---|---|
| 1 wire the loop | `47472bc` | pytest 180 at land; live v3p1 first_try **1/3** |
| 2 scorer | `a2ede92` | 9 fixture tests; `provider_calls==0`; CI hook |
| 3 skeleton CLI | `8ba7510` | 5 tests; unresolved gaps block verify |
| 4 decomposition | skipped | `docs/v3/PHASE4_SKIP.md` |
| suite now | | **194** |

## What v3.0.0 would have required

- Scorer numbers on a **frozen held-out** split
- Honest 60–70% verdict (met / missed / narrowed)
- Held-out claims CTO-approved and ingested
- README non-claims + DECISION_LOG items
- Builder bump

## Honest verdict

**Missed.** first_try_valid 1/3 on v2-memory. Both FORMALIZED statements
failed the compile probe. Sole-author VERIFIED **0%**. Held-out row
count **0**. Claiming 60–70% would be a lie.

`--from-file` remains recovery. Reviewer + `#print axioms` / `sorryAx`
unchanged.

## Tag rule

No `v3.0.0` from this packet. Ship Phase 1–3 as a **v2.x / unreleased
branch** only after CTO review + PR. This file is not `docs/releases/v3.0.0.md`.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
