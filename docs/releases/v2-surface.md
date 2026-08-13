# v2.0.0 surface (Phoenix)

v2 is **additive and sharpening**; it changes nothing in the v1 frozen
surface (breaking changes would require a major version bump — the bump
to 2.0.0 reflects the promise sharpening + assist foundation, not a
CLI/schema break).

## Unchanged from v1 (still frozen)

- CLI (`leanecon-a3`): all v1 subcommands, signatures, and semantics —
  `ingest`, `interpret`, `review`, `formalize` (live + `--from-file`),
  `gap-ack`, `axiom-approve`, `verify`, `bundle`, `replay`, `status`.
- EI schema 1.0.0; bundle schema 1.0.0 (12 checks incl. `12_core_pin`).
- Core P2 + G7 (9 decls + 3 theorem boundaries); no Core declarations
  added, changed, or removed in v2.
- Lean v4.32.2 / Mathlib v4.32.2; reviewer policy (human | ai); CTO as
  accountable semantic authority.

## Added in v2 (library modules — NOT CLI surface)

| Module | Role | Gating |
|---|---|---|
| `leanecon.revise_loop` | bounded (2–3 attempt) kernel-feedback revision of formal-statement drafts; audit gate authoritative over naive compile; contamination gate (sorry-carrying draft = FAILED even if probe reports compiles) | harness with injected `audit`/`probe`; no lifecycle/`TRANSITIONS` edits; never the pass gate |
| `leanecon.skeleton` | proof-skeleton drafting contract: explicit `-- GAP:` annotations enforced (empty notes rejected), unannotated placeholders flagged, unmarked auto-tactic bodies flagged as B2 smuggling risk; `refined_proof_ok` is a **static** sorry/admit mirror, NOT the kernel audit; `skeleton_edit_distance` measures reviewer delta | a skeleton with unresolved gaps never enters `verify` (by design — it would fail the sorryAx audit); no bypass added |

## Provider capabilities (unchanged map, honest use)

| Capability | Model | v2 status |
|---|---|---|
| `interpret` | mistral-medium-3-5 | live — every interpret |
| `formalize` | labs-leanstral-1-5 | live draft + `--from-file` recovery |
| `prove_or_repair` | labs-leanstral-1-5 | enum only — unused |
| `diagnostic_probe` | mistral-medium-3-5 | A1 |

## v2 measurement surface

- `docs/eval/formalizer-scorecard.md` v2 section (live v2p1 attempts:
  first-try valid 0/3, static-reject catch 6/6, contamination caught
  1/1, sole-author of VERIFIED 0%).
- `docs/eval/interpreter-scorecard.md` (unchanged rates; v2p1-A/B/C
  revisions recorded in the Phase 1 record).
- Phase 3 edit-distance / time-to-VERIFIED measurement: **deferred**
  (CTO directive 2026-08-09); v3 candidate, not part of this tag.
- B2 spike tracked at `spikes/001-bounded-search/` (2/8 false greens).

## Honest bounds (repeat of the promise's teeth)

- The kernel axiom audit (`#print axioms` / `sorryAx` absent) remains the
  ONLY pass gate for anything reaching the kernel.
- A bare compile exit 0 is NOT a pass (B2 spike: `apply?`/`simp`
  fabricated `sorry` bodies with exit 0 on 2/8 targets).
- Nothing in v2 bypasses the reviewer or the audit; no auto-applied
  tactics; no unattended `VERIFIED`.
- Auto-formalize of NL/LaTeX into richer IRs (graphs, embeddings) is the
  **v3 direction**, not a v2 claim.

**Attribution:** Hermes Agent (Nous Research) under CTO direction; CTO
remains the accountable semantic authority.
