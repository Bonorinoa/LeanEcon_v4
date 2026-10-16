# Release roadmap doctrine (pre-v1 → v3)

> Session origin: 2026-08-08 Gate 8 checkpoint audit + CTO-requested
> development/tagging plan. Full plan:
> `Desktop/leanecon_v4_work/.hermes/plans/2026-08-08_141539-release-roadmap-pre-v1-to-v3.md`
> (workspace-local; may not be committed). This reference is the durable
> operator cache.

## Versioning doctrine

| Tag | Product promise | Must not claim |
|---|---|---|
| **v0.x** | Dev / pre-release; APIs may break | Stability, corpus, autonomous formalization |
| **v1.0.0** | First *supported* verified workflow (English → reviewed EI → formal → kernel VERIFIED bundle) | Auto-proof, multi-agent, broad economics coverage |
| **v2.0.0** | Assisted proving + measured formalizer quality + Core depth in one family | General econ library, unattended pipelines |
| **v3.0.0** | Corpus-grade: published claims, eval harness, multi-domain Core, external reviewers | “Solved autoformalization” |

**Earn rule:** A SemVer tag requires `docs/releases/vX.Y.Z.md` evidence packet.
No tag for “we merged a lot.” Package was `0.1.0` with **no release tags** at
the 2026-08-08 checkpoint (`main` @ `5f720f8`).

**Gates ≠ SemVer.** Gate 8 work feeds **v0.2**, not “v8.”

**Four tracks (always on):** harness · Core · eval · collaboration. Never let
agents/demos outrun the first three. WIP limit: one open product promise.

## Why not v1 yet (2026-08-08 blockers)

| Gap | Source |
|---|---|
| No `formalize --from-file` (reviewer recovery outside audited CLI) | OOS F5, INIT_GATE8 |
| Ops footgun: bare `python -m` / stale install can drop `12_core_pin` | OOS F2 |
| README / ENGINEERING_LOG lag main (Gate 5 “in review” while G7+OOS done) | Checkpoint audit |
| No frozen release surface (CLI + schemas) | — |
| No clean-clone → walkthrough → VERIFIED release packet | P5 pattern exists; not release-tagged |
| Second approver / protection still interim | ENGINEERING_LOG |
| Formalizer quality only anecdotal (OK for v0) | Walkthrough + OOS |

**Not** v1 blockers: B2, agents, corpus, Nash Core.

## Phase map

| Phase | Tag | Focus |
|---|---|---|
| A | **v0.2.0** | Docs truth + `formalize --from-file` + single live entrypath (`a3_run.py`) |
| B | **v0.3.0** | Eval skeleton: freeze claim set, formalizer/interpreter scorecards |
| C | **v1.0.0** | Surface freeze, clean-clone packet, Core freeze, runbook, governance note, honest non-claims |
| D | v1.x | One Core family or harness polish per minor |
| E | **v2.0.0** | B2 budgets + HITL assist metrics + deeper Core |
| F | **v3.0.0** | Published corpus, multi-domain, multi-reviewer, public bench |

**Near-term backlog order:** docs truth → G8.1 from-file → ops pin → tag v0.2 →
eval skeleton → tag v0.3 → v1 freeze/packet → tag v1.

## Candidate v1 promise (edit only with CTO)

> A human reviewer, using the supported CLI, can turn an English economic claim
> into a kernel-checked Lean statement with an auditable verification bundle and
> replayable trace, against a pinned Lean/Mathlib workspace and a versioned
> LeanEcon Core, with models used only as optional drafting aids.

## Gold standards (steal process, not fake leaderboards)

| Phase | Anchors |
|---|---|
| v0.2 | RSE / reproducibility; Gate 3 contracts |
| v0.3 | LeanDojo methodology; miniF2F/ProofNet *split discipline* (not scores) |
| v1 | Mathlib culture; AFP/CompCert-style artifacts; JOSS-style installability |
| v2 | LeanDojo/ReProver pass@budget; time-to-VERIFIED + reviewer-edit distance |
| v3 | AFP norms; FAIR/datasheets; multi-reviewer process |

There is **no** established “autoformalize micro theory” leaderboard. Position:
Mathlib-grade definitions + bundle-grade claims + honest model-assist eval.

**North-star metrics:** time-to-VERIFIED (reviewer), edit distance from draft;
hard gates = full checklist, no sorry, Core pin when Core used.

## CTO decisions still open at plan write (confirm before Phase A)

1. Confirm or edit v1 promise text.
2. Confirm v0.2 = docs + `--from-file` + ops before B2/Core expansion.
3. Annotated tags `v0.2.0` / `v0.3.0` / `v1.0.0` + `docs/releases/*` — yes/no.
4. Mandatory `docs/STATUS.md` each release — yes/no.

## Checkpoint priors (honest product state)

- Harness + verification bar: trustworthy (A1–A3, Core pin, OOS).
- Models: drafting aids only; formalizer not statement-faithful.
- Gate 8: handoff only — no G8.1 code on main at checkpoint.
- B2 / agents / corpus: ~0% implemented; contracts only.
- Product = single-claim sequential HITL verified workflow + thin Core
  (9 decls + 3 theorem boundaries after G7).

**Attribution:** Hermes under CTO direction; CTO sole semantic approver.
