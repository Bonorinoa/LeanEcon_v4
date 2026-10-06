# Safe to continue developing LeanEcon? — verdict

**Date:** 2026-10-06 · **Main:** `978ffa8` (PR #24) · **Pin:** `openrouter/free`

Scope: is the repo safe to keep developing on now that Mistral is
unsubscribed and OpenRouter is the single provider? Evidence only —
no new product promise.

## Verdict

**Yes for development; no for trusting `VERIFIED` semantics yet.**

The repo, history, CI, tests, provider boundary, and audit trail are
in a state you can build on. Two things are *known-unfinished* and are
recorded rather than hidden: the VERIFIED-binding holes, and the
free-router runtime cost.

## What is verified green

| Check | Evidence |
|---|---|
| Tests | `pytest -q` → **266 passed** on `main` |
| Lint/format | `ruff format --check` + `ruff check` on src tests scripts → clean |
| CI on `main` | `scaffold-check` SUCCESS on `978ffa8`; `a1-tests` green on the PR |
| Release truth | `scripts/check_release_state.py` → OK (`4.0.0.dev0`, latest release v3.5.0) |
| Branch protection | restored exactly (`scaffold-check`, 1 review, `enforce_admins`) |
| Open PRs | none |
| Branches | **`main` only** (local + remote) |
| Provider boundary | adapter renamed; architecture tests forbid Mistral ids/credential |
| Mistral removal | `adapters/mistral.py`, `MISTRAL_API_KEY`, `api.mistral.ai` gone; only historical eval records name them |
| Disk cruft | stale `build/` (184K, gitignored, held a dead `mistral.py`) removed |
| Code graph | codebase-memory project deleted + reindexed: route is now `https://openrouter.ai/api/v1/chat/completions`; the stale Mistral route/layer is gone |

Merge-only indexing note: `index_repository` **never prunes**, so the
dead Mistral nodes survived a reindex. A `delete_project` + reindex was
required. Do that after any file deletion/rename if traversal matters.

## What was fixed in this pass

- **Interpret provenance** (PR #24): the EI artifact and the
  `INTERPRETED` event now bind `provider` / `model` / `request_id`;
  the accepted-EI digest names the model. This was a real defect the
  orfree E2E exposed — formalize recorded its model, interpret lost it.

## What is *not* fixed (known, recorded)

| Risk | Where | Blast radius |
|---|---|---|
| VERIFIED-binding holes: kernel checks the proof file not stored-signature+body; gap-ack/axiom/approval = last record on the claim; bundle schema 1.0.0 with one `result` field | `docs/v4/VERIFIED-BINDING-CANDIDATES.md` | Trust in `VERIFIED`, not the dev loop |
| Free-router runtime: interpret 14–88s, formalize 207–315s, observed 600s timeout and 217s empty-content draw | `docs/eval/orfree-e2e-results.md`, `docs/eval/pin-probe-results.md` | Dev-loop ergonomics; unattended runs |
| Account guardrails shrink the free pool — the #3 free model by usage is 404 from this account | `docs/eval/pin-probe-results.md` | Pin choice; **user-account decision** |
| `P5` semantic fidelity unmeasured | all E2E docs | Product claim |
| Historical docs still name Mistral ids | release packets/scorecards | Intentional — records of what ran |

## Gates before this becomes a *product* claim

1. CTO decision on the OpenRouter account data-policy setting
   (agent must not change it).
2. A pin decision with evidence, if runtime is to be improved.
3. The VERIFIED-binding work, re-implemented against `main`
   (not resurrected from the dropped stash).

## Recommendation

Continue development on `main`. Treat `VERIFIED` as
"kernel-accepted + bundle-validated under the current schema", **not**
as a hedged trust claim, until the binding holes are closed. Expect
multi-minute formalize calls and design unattended runs around that.

**Pin:** keep `openrouter/free`. A faster named candidate exists
(`cohere/north-mini-code:free`) but lost one formalize draw in three —
not enough to swap (see `docs/eval/pin-probe-results.md`). Any pin
change needs a powered dev-fixture A/B first.

**Attribution:** Hermes Agent under CTO direction. CTO is the sole
semantic approver.
