# v2 Phase 3 (skeleton contract) + Phase 4 (release prep) — 2026-08-09

Continuation of the v2 plan (`docs/v2/INIT_V2.md`). Phase 1+2 were already
shipped (see `v2-phase1-walkthrough-2026-08-09.md` + the Phase 2 record).
This file covers: the Phase 3 contract slice, its one real test-found bug,
the Phase 4 release packet, and the gate/authorization patterns exercised.

## Phase 3 — proof-skeleton drafting assist (contract slice)

CTO directive 2026-08-09: "push your work and start phase 4" — this
halted Phase 3 at the CONTRACT slice (the INIT_V2 §Phase 3 gate offers
promote / halt-with-record; measurement deferred).

Shipped (PR #16, 2 commits, bot flow):
- `src/leanecon/skeleton.py` — skeleton contract + measurement layer:
  - `validate_skeleton` — parses a have-chain (`have h : P := by ...`),
    enforces EXPLICIT gap annotation: every placeholder step needs
    `-- GAP: <note>` (empty note rejected); unannotated
    sorry/admit/metavar placeholders flagged; a complete-looking
    auto-tactic body (aesop/simp/trivial/exact?/omega/...) with NO gap
    marker flagged as B2 smuggling risk (fabricated sorry bodies, exit 0
    — the spike lesson applied at skeleton level).
  - `refined_proof_ok` — STATIC sorry/admit scan, mirror of the
    verifier's contamination gate; docstring must state it is NOT the
    kernel audit (the kernel `sorryAx` audit at verify stays the only
    pass gate).
  - `skeleton_edit_distance` — line-based SequenceMatcher diff (model
    skeleton vs reviewer-refined proof), for the edit-distance /
    time-to-VERIFIED measurement.
- `tests/test_skeleton_contract.py` — 5 Red-first tests (structure/gaps,
  annotated-gap enforcement, B2 smuggling flag, audit-contract-unchanged,
  edit-distance ordering). Suite 168 → 176.
- Design rule (same as `revise_loop.py`): standalone harness, injected
  boundaries → NO lifecycle/`TRANSITIONS` edits (F1), no runner changes,
  `replay_ok` untouched. Skeleton with unresolved gaps NEVER enters
  `verify` — by design, it would fail the sorryAx audit.

### Real bug found by the tests (Python regex, generalizable)

`_GAP_NOTE_RE = re.compile(r"--\s*GAP\s*:(.*)$")` failed in two ways on
multi-line have-step bodies:

1. `$` without `re.MULTILINE` never matches at end-of-line inside a
   multi-line string → the annotation was never detected.
2. After adding `re.MULTILINE`, the greedy `\s*` after the colon
   CROSSED the newline and swallowed the next line's `sorry` as a
   "non-empty note" → empty-note rejection never fired.

Fix: `re.compile(r"--\s*GAP\s*:[^\S\n]*(.*)$", re.MULTILINE)` —
non-newline horizontal whitespace only, and MULTILINE so `$` binds at
each line end. Lesson: when matching an end-of-line token in a
multi-line body, use `[^\S\n]*` after the separator, never bare `\s*`.

### Measurement: DEFERRED, recorded honestly

Edit-distance / time-to-VERIFIED on the frozen v2p1-A/B/C proofs was NOT
run (CTO chose Phase 4). Recorded as a Phase 4.x follow-up candidate,
NOT as a v2 promise. The scorecard v2 section says "contract shipped,
measurement deferred" — no fabricated measurement rows.

## Phase 4 — v2.0.0 release prep (docs-only packet; tag = CTO gate)

Earn rule holds: tag `v2.0.0` only after CTO approves the release packet.
Packet deliverables (all docs):
- `docs/releases/v2.0.0.md` — sharpened promise (model drafts 60–70% on
  simple claims; reviewer closes; kernel axiom audit = ONLY pass gate),
  Phases 1–3 status table, surface freeze (unchanged from v1: EI 1.0.0,
  bundle 1.0.0/12 checks, CLI, Core P2+G7; new modules are LIBRARY, not
  CLI surface), exit-criteria checklist, v2 non-claims, verify commands.
- `docs/releases/v2-surface.md` — frozen vs added; honest bounds repeated.
- `pyproject.toml` → 2.0.0 + README v2 section + DECISION_LOG items —
  applied only WITH the tag after approval.

### Release evidence pattern (verified this session)

`scripts_local/a3_run.py bundle --claim-id <id>` is READ-ONLY
revalidation of an existing bundle — the acceptance criterion "every v2
claim's bundle revalidates" is proven by running it on each claim and
reading the 12-check output (esp. `12_core_pin` with the Core digest
matching the workspace, `650f98eb4fe0…`). All three v2p1 claims
revalidated 12/12. This is the evidence-first pattern: never assert
"bundles revalidate" in a release doc without running it.

### Open items handed to the CTO gate

- Track `spikes/` (untracked!) — `spikes/001-bounded-search/` (B2 spike,
  2/8 false greens) is load-bearing evidence for the no-bare-compile
  doctrine; recommended to track with the release.
- `merge_pr.py 16` + `verify_protection.py` after CTO merges PR #16.

## Authorization / gating patterns exercised

- **Out-of-band directive authorizes commit+push.** A `clarify` returned
  empty, then an explicit OOB user message ("push your work and start
  phase 4") was treated as per-action authorization for commit+push+PR
  (bot flow `open_pr.py --bot`), while MERGE stayed CTO-only. The OOB
  message also selected the phase option (hold-Phase-3 → Phase 4) that
  the clarify had offered.
- **Branch stacking:** `v2/phase3-skeleton` was first branched off the
  Phase 2 branch (before PR #15 merged) → carried Phase 2 commits. After
  the merge, `git switch main && git merge --ff-only origin/main` then
  `git switch v2/phase3-skeleton && git rebase origin/main` gave a clean
  2-commit PR diff. Standard stacked-branch hygiene; note the rebase in
  the PR body so the merge history is legible.
- **Merge verification:** after the CTO says "merged", confirm via
  `git fetch origin` + `git log origin/main` showing the merge commit
  (e.g. `18beaa9 Merge pull request #15 ...`) before proceeding, and
  `verify_protection.py` to confirm protection restored
  (enforce_admins: True, checks ['scaffold-check'] strict, 1 approval).

## Collaboration preference (user correction, 2026-08-09)

The CTO pushed back on the "references are hallucinating" boilerplate
that recurred when MoA reference contexts disagreed with tool output.
Durable rule: **verify against the repo/tool output and engage with the
substance; briefly note what is stale or wrong in a reference when it
matters, then move on — never relitigate or narrate the discrepancy at
length.** The failure mode to name is "unshared grounding", not
"hallucination". Subagent dispatch was offered as a remedy and deferred
("keep subagents in mind for future tasks").
