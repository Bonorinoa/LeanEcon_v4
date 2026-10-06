# Gate 3 Decision Log — CTO Response

**Status:** Gate 3 closed; docs-only commit authorized; Gate 4 authorized for A1 diagnostics only. No implementation has been performed. CTO closure response: Y to all five questions.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 1 | E2-1 ledger | Approved as proposed; no `IMPORT`/`ADAPT` exceptions; `.codebase-memory` excluded | **LOCKED** |
| 2 | Lifecycle | `REVIEW_REQUIRED` is semantic-only; `INTERPRETED` is distinct from `FORMALIZED` | **LOCKED** |
| 3 | Capability labels | S3a: `HEALTHY`/`DEGRADED`/`UNAVAILABLE` for diagnostics and bundle metadata only | **LOCKED** |
| 4 | Observability | Minimal append-only event envelope; no health matrix or SLOs | **LOCKED** |
| 5 | EconomicInterpretation/Core | Option B design direction approved as proposed (2026-08-05); all four design decisions locked; schema remains draft until A3 | **LOCKED — DIRECTION APPROVED; NO SCHEMA FREEZE** |
| 6 | Provider contracts | Provider-neutral capability boundary and approved MVP model mapping | **LOCKED** |
| 7 | Verification bundle | Strict `VERIFIED` requirements, including kernel check and reproducibility metadata | **LOCKED** |
| 8 | Axiom/dependency authority | Per-run reviewer record referenced by `axiom_approval_ref` | **LOCKED** |
| 9–11 | Outbound policy | MVP-thin: single boundary, secrets redaction, gold/v3-hidden denial, `RESTRICTED` hard deny; full policy deferred | **LOCKED** |
| 12 | Docs-only commit | Approved after closure review | **AUTHORIZED** |
| 13 | Gate 4 | A1 diagnostics only | **AUTHORIZED — SCOPED** |
| 14 | Attribution | Hermes Agent (Nous Research) credited under CTO direction; CTO remains semantic authority | **LOCKED** |

## Resolutions incorporated in this amendment

- `INTERPRETED` means a structured, human-readable meaning artifact; `FORMALIZED` means a candidate Lean statement derived from an accepted interpretation.
- `REVIEW_REQUIRED` is the semantic review gate for meaning, assumptions, and ambiguities—not a generic bucket for every human pause. Operational blockers remain `BLOCKED`; proof failures remain `FAILED`; later approvals are events.
- `HEALTHY`/`DEGRADED`/`UNAVAILABLE` are diagnostic/probe output only, used for A1 diagnostics and verification-bundle metadata. No health matrix, SLOs, sampling windows, or dashboard is proposed.
- Event observability is reduced to an append-only minimal envelope. Digests remain on trust artifacts/bundles rather than every event.
- Axiom authority is a per-run reviewer record referenced by `axiom_approval_ref`; no repository-wide allowlist is required for MVP.
- Outbound policy is reduced to an MVP floor: one provider boundary, secrets/credential redaction, gold/v3-hidden-artifact denial, `RESTRICTED` denied outright, and no restricted opt-in mechanism until needed. Full classification/PII/retention policy is future work before external users.

## Closure answers

The CTO answered **Y** to all five closure questions:

1. `REVIEW_REQUIRED` is a semantic-only human review gate.
2. Capability vocabulary is S3a: `HEALTHY`/`DEGRADED`/`UNAVAILABLE`, diagnostics and bundle metadata only.
3. The MVP-thin outbound posture is approved.
4. The EI/Core design discussion is approved as the next design artifact; no A3 or Core implementation proceeds before design review.
5. Gate 4 authorization is limited to A1 diagnostics only.

Gate 3 is closed. The package is authorized for a docs-only commit. Gate 4 A1 may begin only within the scope recorded above; A3, Core implementation, full outbound policy, and production `VERIFIED` claims remain excluded.

**Attribution:** Prepared by Hermes Agent (Nous Research) under direction of the CTO. The CTO remains the sole semantic approver.

**No implementation:** This package authorizes only the Gate 3 documentation commit. It does not authorize A3, LeanEcon Core implementation, full outbound policy, or production `VERIFIED` claims.

---

# Gate 6 — LeanEcon Core design and implementation plan (CLOSED 2026-08-06)

**Status:** Gate 6 closed by CTO approval; design package approved as
proposed; the EI schema is frozen; the implementation plan is authorized
with per-phase CTO gates. The fwt1 live test (First Welfare Theorem,
VERIFIED end-to-end) is part of the package evidence.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 15 | Core design (`docs/gate6/a3-core-design.md`) | Approved as proposed; contract deltas D1–D4 adopted (fully-qualified `core` rows; Core pin in bundle; namespace collision check; namespace-scoped scaffolding); open questions resolved per §8 | **LOCKED — DESIGN APPROVED** |
| 16 | EI schema freeze (`references/gate3/ei_schema_draft.json`) | Exercised draft frozen as normative `1.0.0` (`none_noted`, nullable `review.reviewer`/`event_ref` while PENDING, `acknowledges_none_noted`); `$comment` freeze note added | **FROZEN — 1.0.0** |
| 17 | Glossary registry (`references/core-glossary-detail.md`) | Approved; 28 entries seeded from c1–c4 + fwt1; equilibrium-family entries (21–28) glossary-only/core-candidate, declarations deferred to Gate 7 | **LOCKED** |
| 18 | Implementation plan (`docs/gate6/IMPLEMENTATION_PLAN.md`) | Approved; P1–P5 with per-phase CTO gates; P1 (docs-only schema-freeze commit) is the next action | **AUTHORIZED — PLAN** |
| 19 | fwt1 live test (`references/fwt1-test-record.md`) | VERIFIED end-to-end (bundle-fwt1-r1-35615e); formalizer failed structurally — reviewer-in-the-loop confirmed load-bearing; equilibrium vocabulary added as glossary-only meanings | **EVIDENCE** |

## Resolutions incorporated in this amendment

- The mapping report's `core` rows carry fully-qualified identifiers (D1);
  the bundle records the Core revision (D2); Core promotion includes a
  Mathlib namespace-collision check (D3); A3-local scaffolding is
  namespace-scoped (D4).
- No equilibrium-family declarations before the Gate 7 slice; no B2 proof
  loop, corpus work, or release artifacts in Gate 6.
- v3 Core-adjacent material stays `rebuild`/`inspiration`/
  `historical-discard`; no `import`/`adapt` exceptions.

**No implementation beyond the plan:** P1 (schema-freeze docs commit/PR)
may begin; P2 (first Core promotion batch, 6 declarations + 2 theorem
boundaries) begins only after P1 merge and the per-declaration review
gates.

---

# P2 — First Core promotion batch (APPROVED 2026-08-06)

**Status:** P2 batch approved by the CTO as proposed (verdicts D1–D6);
per-declaration approval records in `docs/gate6/P2_REVIEW_BATCH.md` §6.
The batch compiles in the pinned workspace with baseline axiom closures.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 20 | P2 batch: `bundle`, `weakPreference`, `budgetSet`, `attainableSet`, `utility`, `strictlyIncreasing` + theorem boundaries `budgetExpansion_nonShrinking` (c1), `strictlyIncreasing_strictPref` (c3) | Approved as proposed (D1–D6); per-declaration approval records recorded | **PROMOTED — BATCH APPROVED** |
| 21 | P2 commit/PR (Core modules + review package) | Commit follows this approval; CI gates + merge flow per the established procedure | **PENDING COMMIT** |

Resolutions incorporated:

- `budgetSet` is income-form only; the endowment-relative form is
  recoverable and deferred to the Gate 7 equilibrium slice (D2).
- `strictlyIncreasing` uses the strong componentwise reading and the c3
  direction convention (D3).
- Module layout: six area modules; no empty Equilibrium module (D4).
- `weakPreference`/`utility` approved as vocabulary-anchor aliases (D5).
- No equilibrium-family declarations, no demand/choice correspondences, no
  A3 code changes in this batch (P4).

---

# P3 + P4 — Glossary registry v1 and A3 contract deltas (APPROVED 2026-08-06)

**Status:** P3 registry v1 merged (PR #9); P4 batch approved by the CTO as
proposed (verdicts D1–D8 in `docs/gate6/P4_REVIEW_BATCH.md` §3). The
137-test baseline stays green (156 passed with the 19 new P4 tests).

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 22 | P3 glossary registry v1 (`references/core-glossary-detail.md`): version header + change log; six P2 promotions reflected (entries 1, 6, 7, 9, 12, 13 → core); equilibrium family (21–28) glossary-only/core-candidate | Approved as proposed; merged PR #9 | **MERGED** |
| 23 | P4 batch: D1 (`core` mapping kind + fully-qualified `LeanEcon.Core.<Area>.<name>` ids), D2 (Core pin `workspace_identity.core_revision` + `dependency_audit.core_imports` + check `12_core_pin`), D4 (namespace-scoped A3-local scaffolding, hard-rejected at formalize), D3 (collision-check review item in the ontology-record template, docs) | Approved as proposed (D1–D8); `bundle_schema_version` stays 1.0.0 (additive); `mapping_kind: none` retained in the enum; D3 CI-grep proposal-only | **APPROVED** |
| 24 | P4 commit/PR (code + tests + review package) | Commit follows this approval; CI gates + merge flow per the established procedure | **PENDING COMMIT** |

Resolutions incorporated:

- D1: the FQ pattern requires `LeanEcon.Core.<Area>.<name>` (≥2 dotted
  components after the prefix — the §1.3 namespace skeleton); bare or
  Area-less ids are flagged.
- D2: `bundle_schema_version` stays 1.0.0 (additive fields; validator is
  the only consumer; historical bundles re-validate); `12_core_pin` is a
  distinct checklist item, including stale-pin detection (manifest vs
  workspace digest) when the workspace is available.
- D4: hard rejection (PROVIDER_INVALID_OUTPUT, no artifact) at formalize;
  the verifier path for reviewer-authored proofs is untouched.
- Surfaced finding fixed as root cause: the `:=` proof-body check is now
  declaration-aware (`theorem`/`lemma`/`example`/`axiom` only) so
  namespaced scaffolding definitions (`abbrev Bundle := ℝ`) are legal;
  regression test `test_validate_statement_text_allows_definitional_body`.
- No verify-side scaffolding check, no `mapping_kind: none` removal, no
  Core-importing claim run (P5 evidence), no equilibrium declarations.

---

# P5 — Gate 6 exit package (APPROVED 2026-08-06 — GATE 6 CLOSED)

**Status:** Gate 6 closed by CTO approval of the P5 exit package. All
exit criteria met (clean-clone reproduction green, ledger complete, no v3
copy, ontology–declaration agreement, live Core-import verification).

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 25 | P5 exit package: clean-clone reproduction (`lake build LeanEcon.Core.*` = 3002 jobs, pytest 156 green in a fresh clone), Core-specific ledger register K1–K6 (Preamble rebuild/inspiration, scratch + benchmarks + theorem-stub claim sets historical-discard, `preamble_library.py` rebuild/inspiration, v3 docs historical), ontology–declaration agreement check (PASSED), live Core-import verification closing the D2 risk-register loop (baseline axiom closure; `12_core_pin` passes on a real digest), exit evidence packet (`docs/gate6/P5_EXIT_PACKAGE.md`) | Approved; **Gate 6 CLOSED** — Gate 7 (equilibrium-family declarations, per-declaration promotion) authorized as the next slice | **CLOSED** |

Resolutions incorporated:

- Clean-clone reproduction is reproducible via
  `scripts_local/clean_clone_check.sh` (python 3.11 baseline; mathlib
  from source on this machine; `-- -j4` for the memory-heavy tail).
- The `import Mathlib` probe contract requires the complete Mathlib build
  (`Mathlib.olean`), not just the Core closure — recorded in the packet
  and the skill.
- No v3 material copied into `LeanEcon/Core/**`; no IMPORT/ADAPT
  exceptions; equilibrium-family declarations remain glossary-only until
  the Gate 7 slice (per-declaration CTO promotion).

---

# Gate 7 — Equilibrium-family Core batch (APPROVED 2026-08-06)

**Status:** Gate 7 equilibrium-family batch approved by the CTO as
proposed (slice D1–D9 tabled in-session; review package
`docs/gate7/G7_REVIEW_BATCH.md`). All Lean compiled before review
(verbatim kernel evidence; baseline axiom closure on the theorem AND all
four defs); 9/9 expectations confirmed; pytest 156 green. This closes P5
exit-packet open item 1 (equilibrium-family declarations).

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 26 | Gate 7 batch: `budgetSetEndowment` (Constraints), `marketClearing`, `competitiveEquilibrium`, `paretoEfficiency` (new Equilibrium module), theorem boundary `competitiveEquilibrium_paretoEfficient` (Theorems, fwt1 family) | Approved as proposed; per-declaration approval records `G7_REVIEW_BATCH.md` §8 | **PROMOTED — BATCH APPROVED** |
| 27 | Gate 7 commit/PR (Core modules + review package + registry change-log rows) | Commit follows this approval; CI gates + merge flow per the established procedure | **PENDING COMMIT/PR** |

Resolutions incorporated:

- `budgetSetEndowment` lands the P2-D2-deferred endowment-relative form as
  a dedicated declaration in Constraints (D3); definitionally the
  documented recovery `budgetSet p (∑ g, p g * e g)`.
- `competitiveEquilibrium` uses the direct utility-maximization reading
  (D2); `[Nonempty Agent]` lives on the theorem, not the definition (D4 —
  the fwt1 semantic gap carried into Core explicitly, matching the fwt1
  proof header).
- `utilityMaximization` (entry 28) stays glossary-only, folded into
  `maximizes` (D5).
- Registry: entries 25/26/27 core-candidate → core (change-log rows, no
  version bump); entry 7 variant note updated; entries 21–24 stay
  glossary-only (realized as types — no declarations proposed).
- No tooling deltas (D9): D3 CI grep, verify-side scaffolding signal,
  `mapping_kind: none` removal all deferred as recorded in
  `P4_REVIEW_BATCH.md`.

---

# OOS evaluation + immediate cleanup (2026-08-08) — Gate 8 handoff

**Status:** Out-of-sample batch complete (evaluation only). Immediate F1
lifecycle fix authorized as cleanup before Gate 8. Gate 8 scope deferred
to a new session via `docs/gate8/INIT_GATE8.md`.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 28 | OOS batch (oos1 IR@CE VERIFIED+12_core_pin; oos2 budget expansion VERIFIED+12_core_pin; oos3 Nash FORMALIZED boundary; report `docs/gate7/OOS_BATCH_REPORT.md`) | Authorized evaluation; findings F1–F5 recorded | **EVIDENCE** |
| 29 | Immediate F1 fix: lifecycle edges `ACCEPTED→FAILED`, `FAILED→FAILED`, `BLOCKED→FAILED` + regression test; oos2 replay_ok confirmed | Cleanup before Gate 8 (not a feature gate) | **PENDING COMMIT** |
| 30 | Gate 8 init brief (`docs/gate8/INIT_GATE8.md`): primary slice = reviewer `formalize --from-file` + pipeline completeness; B2 thin optional; agents/corpus/game-theory Core deferred | Handoff for new session — slice confirmation at G8.0 | **HANDOFF** |

Resolutions incorporated:

- Product confirmed single-claim sequential pipeline (no agents/retrieval).
- D1 earned keep on oos3; D2 `12_core_pin` earned keep on oos1/oos2 (via
  `a3_run.py` / PYTHONPATH=src — bare install can drop the pin).
- F1 is table completeness (runner already emitted the edges); not a
  behavior change to formalize rejection semantics.
- Gate 8 must not reopen "build agents first"; bottlenecks are formalizer
  compliance, reviewer recovery CLI, and lifecycle/ops completeness.

---

# v1 ship train — AI reviewer + releases v0.2 / v0.3 / v1.0 (2026-08-08)

**Status:** CTO-approved ship path. Tags `v0.2.0`, `v0.3.0`, `v1.0.0`.
No mandatory `docs/STATUS.md`. Reviewer may be **human or AI**; CTO remains
accountable semantic authority.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 31 | AI reviewer policy: authorized AI agents may emit ACCEPTED/REJECTED, gap-ack, and axiom-approve under `docs/gate3/08-reviewer-policy.md`; records store `reviewer` + `reviewer_kind`; `none_noted` ack still required; CTO accountable | Approved (v1 promise edit) | **LOCKED** |
| 32 | `formalize --from-file` (and statement/mapping split files): reviewer-authored formal recovery with full D1/D4/static contracts; provenance `reviewer_authored_formal` | Approved (Gate 8 / v0.2 primary) | **SHIPPED** |
| 33 | Release train: annotated tags v0.2.0 (foundation), v0.3.0 (eval skeleton), v1.0.0 (supported verified workflow); evidence in `docs/releases/*`; no mandatory STATUS.md | Approved | **SHIPPED** |
| 34 | v1 surface freeze: CLI subcommands, EI 1.0.0, bundle 1.0.0 (12 checks), Core P2+G7 freeze, builder `leanecon-a3-1.0.0`; explicit non-claims (no B2, no agents, no corpus SLA) | Approved | **LOCKED — v1.0.0** |
| 35 | Second GitHub approver | Resolved by activating formal bot contributor `@hermessinho` (item 36); interim single-maintainer merge scripts remain for protection relax until dual-approval is routine | **RESOLVED (bot slot filled)** |
| 36 | Formal bot contributor `@hermessinho`: CODEOWNERS second slot; limited-scope PAT as `LEANECON_BOT_TOKEN`; dual-token loader `scripts/github_token.py`; bot may push/PR implementation work; CTO remains sole semantic authority for meaning/Core/policy | Activated 2026-08-08 (classic PAT + collaborator Write) | **LOCKED — ACTIVE** |

Resolutions incorporated:

- Gate 3 “human only” actor prose is superseded for **review commands** by
  item 31; interpret/formalize models remain drafting aids and do not
  self-certify meaning.
- `scripts_local/a3_run.py` is the only supported live entrypath (OOS F2).
- Package version bumped to `1.0.0` in `pyproject.toml` with the v1 tag.
- Item 35 second-contributor slot is filled by `@hermessinho` (ops +
  implementation). Semantic approval is still CTO-owned; bot does not
  self-approve meaning or Core promotions.

---

# v2 — Phase 1 evidence + Phase 2 ship (2026-08-09)

**Status:** Phase 1 complete (AI reviewer exercised end-to-end on 3 fresh
OOS claims; zero source changes). Phase 2 bounded revision loop shipped
via PR #15 (merge `18beaa9`).

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 37 | v2 Phase 1: AI reviewer exercised on v2p1-A/B/C — all VERIFIED (12/12 bundles incl. `12_core_pin`), AI-review agreement 3/3, zero source changes; expectations-first records `artifacts/local/v2-p1-expectations.md` + `v2-p1-record.md`; scorecard v2 `docs/eval/formalizer-scorecard.md` | Approved 2026-08-09 | **EVIDENCE** |
| 38 | v2 Phase 2: bounded kernel-feedback revision loop (`src/leanecon/revise_loop.py`, `MAX_REVISION_ATTEMPTS=3`, audit gate authoritative over naive compile; 3 Red-first tests; suite 171) + approved plan `docs/v2/INIT_V2.md` | Approved; merged PR #15 (`18beaa9`) | **SHIPPED** |

Resolutions incorporated:

- Phase 2 adds no lifecycle edges (F1 rule: no `TRANSITIONS` change);
  `replay_ok` and the 12-check bundle gate unchanged.
- `v2.0.0` tag deferred to Phase 4 (earn rule); README reflects v2
  in-progress status (no overclaim).
- Phase 3 (proof-skeleton assist) continues on `v2/phase3-skeleton`.

---

# v2.0.0 Phoenix — Phase 3 contract + release (2026-08-12)

**Status:** CTO authorized the Phoenix tag on 2026-08-12 (push remaining
changes, merge if checks green, tag v2, delete inactive branches).
Auto-formalize of NL (later LaTeX) into formal IRs the prover can
consume is the **v3 direction**, not an abandoned promise.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 39 | v2 Phase 3: proof-skeleton contract (`src/leanecon/skeleton.py`, 5 Red-first tests, suite 176); edit-distance / time-to-VERIFIED measurement deferred | Authorized with the Phoenix ship | **SHIPPED (contract)** |
| 40 | v2.0.0 Phoenix release: package `2.0.0`, builder `leanecon-a3-2.0.0`, `docs/releases/v2.0.0.md` + `v2-surface.md`, B2 spike tracked, clean-clone P1 recorded; 60–70% draft target recorded as v3 measurement goal | Authorized 2026-08-12 | **SHIPPED** |

Resolutions incorporated:

- Phoenix claims the assist *foundation*, not measured 60–70% model-draft
  completion. Models run live (`interpret` / `formalize`); `--from-file`
  remains load-bearing recovery.
- `revise_loop` and `skeleton` stay library modules (not CLI). Wiring
  them into `formalize` / a prover agent is v3 work.
- B2 spike (`spikes/001-bounded-search/`) is tracked evidence that
  compile≠pass; no auto-prove ships in v2.
- Direction lock for v3 (this item, not a v3 design): constrained
  auto-formalize of natural language (and later typing + LaTeX) into
  formal representations (today EI + mapping + Lean; later graphs /
  embeddings / other IRs) that a prover agent can process, with
  decomposition and kernel-feedback loops on top. Reviewer + axiom
  audit remain non-bypassable.

---

# v3 — constrained auto-formalize (branch-local, 2026-08-16)

**Status:** recorded on `v3/phase1-wire-loop`. **Not merged. Not tagged.**
Items below are branch facts pending CTO merge/tag authorization.
Empty clarify ≠ consent.

| # | Item | CTO disposition | Package state |
|---|---|---|---|
| 41 | v3 Phases 1–3 on this branch: live `revise_loop` in `formalize_claim`; deterministic fixture scorer + CI (`provider_calls=0`); additive `skeleton` CLI with gap-blocked verify; Phase 4 skipped | executed locally; merge pending | **BRANCH — PENDING MERGE** |
| 42 | Honest 60–70% verdict: draft-complete **2/8 (25%)**, first_try **0/8**, sole-author **0%** on spent splits v3h+v3h2. Target **MISSED**. Do not re-run spent holdouts | recorded 2026-08-13 | **EVIDENCE — NOT A TAG** |
| 43 | Development truth surface: package `3.0.0.dev0`, builder `leanecon-a3-3.0.0.dev0`, `docs/releases/DEVELOPMENT.md`, `scripts/check_release_state.py` fail-closed in CI. Final `3.0.0` requires the matching tag at HEAD | implemented this session | **BRANCH — PENDING MERGE** |
| 44 | Sealed eval protocol `formalizer-sealed-1` (`leanecon.eval_protocol`): hygiene / kernel / semantic fidelity stay uncollapsed; next holdout is text-free; B2 proving is **not** a v3.0.0 earn criterion | implemented this session | **BRANCH — PENDING MERGE** |
| 45 | `v3.0.0` tag | not authorized by this amendment | **PENDING explicit tag line** |
| 46 | v3 promise **narrowed** to **Verifiable State Machine**: the product is the audited single-claim lifecycle (live loop, skeleton side-door, scorer, sealed eval). 60–70% draft-complete is **not** a v3 claim (2/13 ≈ 15% combined, all sets spent) | Authorized 2026-08-16 | **LOCKED — NARROWED** |
| 47 | v4 direction: wire intelligence into that state machine (`docs/v4/INIT_V4.md`). No v4 implementation from this item. Spent holdouts stay spent. B2 still not a ship requirement | Authorized as direction 2026-08-16 | **LOCKED — DIRECTION ONLY** |

---

# v4 intelligence sprint (branch-local, 2026-08-17)

**Status:** recorded on `v4/intelligence-sprint`. **Not merged.**
Sprint pre-authorized end-to-end by the CTO ("full permission to run
experiments"); ≥50% draft-quality target stated up front.

| # | Item | Disposition |
|---|---|---|
| 48 | Mechanical signature repair before audit (`sanitize_signature_draft` + `sanitize_core_mapping_rows`) + format exemplar in the formalize prompt. Audit gate, kernel probe, reviewer policy untouched. Repair notes recorded in revision history. | **implemented; suite 224 green** |
| 49 | v4h1 sealed holdout (`formalizer-v4h1`, n=5, one pass): audit-clean within budget **5/5** (baseline 2/13 ≈ 15%); probe compiles 0/5; **draft_complete 0/5** — the ≥50% draft-complete target is **NOT met** under the v3 definition. Probe/elaboration is the next lever class. Set spent. | **recorded honestly; MISS on the strict metric** |

Resolutions incorporated:

- A package/builder bump is a worktree fact, not a published release.
- CI fixture scoring and live held-out scoring are different evidence
  grades. Semantic review counts are not a substitute for the kernel
  axiom audit.
- Bounded proving remains out of v3.0.0 (B2 spike: compile ≠ pass).
- 2026-08-16: original auto-formalize@60–70% promise is withdrawn
  for v3 and moved to v4 (item 47). v3 names the machine, not the
  draft rate.

---

# v3.5 intelligence sprint (branch `v35/intelligence-sprint`, 2026-08-23)

**Status:** recorded on `v35/intelligence-sprint` (cut from
`main` @ `12e267c` = tag `v3.0.0`). Phase order approved by the CTO
in chat 2026-08-23 ("i approve the phase order"); each later phase
still passes its own gate (G1–G6 in `docs/v3.5/SPRINT-PLAN.md`).

| # | Item | Disposition |
|---|---|---|
| 50 | Fidelity-property ontology **P1–P6** (surface legality / elaboration / contract / substance / semantic fidelity / proof adequacy — BRIEF §4) replaces the planned observed-failure taxonomy as the failure-labeling object. Observed rejects are measurements *of* property violations, not categories. New errors are labeled by violated P; if none fits, the object is amended. Mechanical repair may touch P1 and mechanical-P3 only, never conclusions (P4/P5) | **ADOPTED** (CTO directive against observation-derived taxonomies) |
| 51 | v3.5.0 sprint approved: phases G0–G6 (`docs/v3.5/SPRINT-PLAN.md`) targeting ≥60% audit-clean ∧ elaborates on a fresh sealed holdout. Sub-decisions: **D3** consultative `opinion` side-door PARKED to v4; **D4** formalize pin stays `labs-leanstral-1-5`, model swaps only on sealed evidence; **D2** probe-repair consumes the normal `MAX_REVISION_ATTEMPTS=3` budget — revisit only with Phase-1 truncation evidence | **APPROVED 2026-08-23** |
| 52 | Metrics re-audit rides Phase 1 (D5): map scorer buckets onto P1–P6, harden string-matched `static_reject_class`, split `draft_complete` into `audit_clean_rate` / `elaborates_rate` so partial results stay legible, re-freeze definitions as `docs/v3.5/METRICS.md`. Last metric-layer change was 2026-08-13 (probe-wrap); both repair levers postdate it | **APPROVED as part of Phase order** |
| 53 | Phase 2 / G2 — L1 probe-repair diagnosis (experiment card `docs/v3.5/experiments/L1-probe-repair-card.md`): a deterministic, total-over-classifier-outputs class→directive table (`leanecon.probe_repair`) appends one Diagnosis line to `_revision_feedback_block` when an attempt failed the compile probe; audit-failed and clean histories render byte-for-byte unchanged; D2 budget untouched. Record correction: `formalize_claim`'s old "dummy loop probe" docstring was false since the v3 wire-up — the real probe has always run inside the loop (artifact evidence: v4smk/v4h1 = 3 audit-clean attempts, probes all False); docstring corrected, no behavior change from that fix | **implemented on branch @ `84bf361`; suite 250 green**; G2 optional smoke (CTO-approved): fresh claim `v35smk-A` (same-text technique off `v4smk-B`) reached **FORMALIZED with fresh probe True on attempt 1** — success criterion met, but the Diagnosis path never fired (no probe failure occurred), so the run does not evidence the lever itself; predictions/actuals in `docs/eval/v35-g2-smoke-predictions.md` |
| 54 | G3 — sealed holdout `formalizer-v35h1` (`docs/eval/v35h1-manifest.json`, n=3, ONE pass, predictions pre-committed @ `5f60ee2`): audit-clean **3/3**, probe compiles **2/3**, **draft_complete 2/3 = 0.667 ≥ 0.60 — the v3.5 earn target is MET on fresh sealed evidence** (v4h1 was 0/5 under the same strict definition). Diagnosis lever exercised live for the first time: recovery pair on A (`instance_synthesis` directive → next attempt compiles); honest non-repair on B (identical type error repeated despite directive; attempt 1 additionally burned by a stale Core `.olean` — build-freshness check mandated before future passes). Texts deconflicted against all stored claims (C redesigned after near-verbatim collision with spent v3h3-C). Set SPENT. Details: `docs/eval/v35h1-expectations.md`, payload `docs/eval/v35h1-score.json` | **recorded honestly; TARGET MET** |

---

# v4 agentic line (branch `v4/opinion-slice`, 2026-09-07)

**Status:** opened from `main` @ `2948e63` (= tag `v3.5.0`). G0 packet
(`docs/v4/G0_OPINION_SLICE.md`) + implementation live on the branch.
Merge CTO-gated (empty clarify ≠ consent; PR + governance amendments
land together).

| # | Item | Disposition |
|---|---|---|
| 55 | v4 slice 1 — **consultative opinion side-door** (DL 51/D3 as first-class v4 work). Sub-decisions resolved by the CTO in chat 2026-09-07: **D1** opinion reuses the interpret/triage pin (`Capability.OPINION` → `mistral-medium-3-5`; never the formalizer pin); **D2** slice-1 surface = formal draft + mapping report; **D3** prose grounding — machine block deterministic and authoritative, opinion prose can never override it, no verdict vocabulary (structural guard + `validate_opinion_artifact`); **D4** opinions recorded as `opinion_requested`/`opinion_emitted`/`opinion_failed` event kinds + `opinions/<claim>/rev-N.json` artifacts, excluded from the bundle 12-check list (they are not verification evidence); **D5** pedagogical mode is a first-class schema field (`--pedagogical` → learner explanation + what-to-try). Powers: consultative only — never ACCEPTED/REJECTED, never a lifecycle transition (test-pinned: state + EI/formal/review record counts unchanged after an opinion). `leanecon.opinion` module + `cmd_opinion` (suite 262 green; deterministic tests only, provider_calls=0 via FakeAdapter) | **APPROVED 2026-09-07 ("proceed as suggested")** — implemented on branch @ v4 `4.0.0.dev0`; merge CTO-gated |
| 56 | D4 A/B **HELD** by CTO 2026-09-07 (supersedes same-day earlier "run the A/B now" direction): keep `labs-leanstral-1-5` pinned until retirement forces the decision. Consequences recorded in `docs/v4/experiments/D4-model-ab-card.md`: the ~Sept 20 re-pin deadline lapses; the swap becomes a forced move at the reported Labs retirement (2026-09-30) or on a 404 at run time; a mid-sprint retirement risks an evidence discontinuity on the formalizer pin. Re-open trigger: 404/401/retirement notice on the pinned model, or CTO direction | **HELD — recorded; SUPERSEDED by 57** |
| 57 | Mistral unsubscribed. Live provider is OpenRouter only: every capability pinned to `openrouter/free` via `leanecon.adapters.openrouter.OpenRouterAdapter` and `OPENROUTER_API_KEY`. Retired: `adapters/mistral.py`, `MISTRAL_API_KEY`, `api.mistral.ai`, `mistral-medium-3-5`, `labs-leanstral-1-5`. Paid OpenRouter routers (`openrouter/auto`, `typesafe/jev-router`) are **not** the live pin (they bill at the routed model). HuggingFace is a complementary open-weight catalog, not a second live adapter — inference for Leanstral-class models is a hardware project (see `docs/v4/PROVIDER_CUTOVER.md`). D1 still: opinion reuses the interpret *slot*. A 402 is a paid-path bug, not a cue to fund an account. Historical eval records keep the model ids that actually ran | **APPROVED 2026-10-06 (CTO: deprecate Mistral; OpenRouter single provider)** |

