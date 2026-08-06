# Gate 6 INIT — LeanEcon Core design (initialize in a NEW session)

> Written 2026-08-06 (end of the Gate 5 session). Purpose: let a fresh
> session initialize Gate 6 with full context and evidence. The CTO deferred
> Gate 6 execution to a new session; this document is the handoff.
> Status: **not approved** — no Gate 6 work beyond planning has been done.

## What Gate 6 is

The migration plan's next gate: **design LeanEcon Core** — the controlled
formal vocabulary (definitions, ontology references, theorem namespaces) that
the EI's `context.definitions` / `context.ontology_refs` and the A3 mapping
report's `lean_identifier` / `mapping_kind` fields point AT. Core is the
target of the mapping report; A3 works without it today via Mathlib +
A3-local scaffolding, but production claims need a reviewed economics layer.

## Read first (in this order)

1. `docs/gate3/07-ei-core-design-proposal.md` — EI design (APPROVED 2026-08-05,
   Option B: controlled meaning frame + small reviewed glossary).
2. `docs/gate3/03-economic-interpretation-schema.md` + `references/gate3/ei_schema_draft.json`
   — schema stays DRAFT until A3 exercises it (A3 has now exercised it).
3. `docs/gate5/a3-design.md` — the A3 workflow Core must plug into
   (especially §4 mapping report + §5 verifier).
4. `docs/gate3/02-lifecycle-events.md`, `04-provider-contracts.md`,
   `05-verification-bundle.md`, `06-outbound-data-enforcement.md`.
5. The migration plan's Gate 6 section: `2026-08-04_LeanEcon_v4_migration_plan.md`.

## Evidence the Gate 5 walkthrough produced (use it)

- **Mapping reports on live claims** (local artifacts): `artifacts/local/a3/formal/c1..c4/rev-1.json`
  — the actual EI-element -> identifier rows the formalizer produced; c1's
  report cites a hypothesis absent from its statement; c2/c3 used non-canonical
  ids (`object:u`, definition titles). Skill reference
  `walkthrough-2026-08-06.md` summarizes per-claim.
- **Formalizer evaluation**: labs-leanstral-1-5 is not statement-faithful
  (1/4 sound) and does not comply with the canonical id contract; the new
  static validation rejects `:=`-bodies 2/2 on live retries. Posture:
  reviewer-authored proof fixtures; formalizer = drafting aid.
- **Id-scheme finding**: Core should define the canonical element-id scheme
  the mapping report must use (objects by id; `assumption:<i>`;
  `definition:<i>`; `conclusion`; `solution_concept`) — the formalizer's
  deviations are now classified (`id_scheme_deviation` vs `genuinely_missing`).
- **Draft-schema exercises**: `none_noted` + reviewer acknowledgement;
  nullable review fields while PENDING — these are now live-tested and should
  be frozen into the schema as part of Core work (CTO approval required).

## Known scope decisions (do not reopen without CTO)

- Option B controlled meaning frame + small reviewed glossary (locked 2026-08-05).
- Mapping report required before PROVING; unmapped = visible gap, reviewer
  acknowledges (locked).
- First 3–5 canonical claims = EI acceptance test — the four VERIFIED claims
  (c1–c4) now satisfy this; Core vocabulary should cover their elements
  (budget/attainable sets, weak preference/transitivity, strict monotonicity,
  order preservation).
- No B2 proof loop, no production VERIFIED claims, no LeanEcon Core
  declarations ship before Gate 6 approval.

## Acceptance criteria for the Gate 6 deliverable

Per the migration plan + project conventions (compact, high-information):
1. A design document (docs/gate6/) defining: Core vocabulary scope, the
   reviewed glossary (start with the four canonical claims' terms), the
   canonical element-id scheme, the mapping-report target contract, and the
   schema freeze proposal (exercised draft -> frozen with CTO approval).
2. Explicit `import/adapt/rebuild/inspiration/historical` dispositions for
   any v3-era Core material (v3 is frozen evidence; no wholesale copying).
3. Open questions flagged with proposed resolutions; STOP for CTO approval
   after the design is written — no implementation in the same session.

## Process notes for the new session

- Current `main`: `14b2f0e` (Gate 5 A3 + hardening merged). 137 tests green.
- Credentials/procedures: `scripts_local/` (gitignored) holds the live-run
  wrapper (`a3_run.py`) and the GitHub helpers (`open_gate5_pr.py`,
  `open_followup_pr.py`, `merge_pr.py`, `check_pr_ci.py`, `verify_protection.py`).
- Skills: `leanecon-verified-workflow` (A3 internals + walkthrough record),
  `python-packaging` (venv/uv quirks).
- Governance: protected main, 1 approval, interim relax->merge->restore
  procedure; CTO review gates at every stop point.

**Attribution:** prepared by Hermes Agent (Nous Research) under CTO direction;
the CTO remains the sole semantic approver.
