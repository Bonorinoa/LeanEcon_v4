# P4 — A3 contract deltas D1/D2/D4: CTO review package

> Status: **ready for CTO review** — Gate 6 P4 per
> `docs/gate6/IMPLEMENTATION_PLAN.md` §5. All deltas are additive to the
> existing contracts; the 137-test baseline stays green (156 passed with
> the 19 new tests). No commit yet — approval first, then commit/PR per the
> established flow.
>
> Authority: design + plan approved (DECISION_LOG items 15–18); P1 merged
> (PR #7); P2 batch approved (item 20, PR #8); P3 registry v1 approved and
> merged (PR #9).

## 0. Deltas at a glance

| Delta | Change | Home | Tests | Status |
|---|---|---|---|---|
| D1 | `mapping_kind` enum gains `core`; `core` rows REQUIRE a fully-qualified `LeanEcon.Core.<Area>.<name>` identifier; bare/invalid ids flagged | `formalization.py` (enum + `CORE_IDENTIFIER_RE` + validator + prompt) | 6 new unit tests | ✅ implemented |
| D2 | Bundle gains `workspace_identity.core_revision` (digest of the merged Core tree) + `dependency_audit.core_imports`; validator check `12_core_pin` fails when Core imports exist without the pin (and on stale pins) | `lean_probe.py` (digest) + `bundle.py` (manifest + check 12) | 7 new unit tests | ✅ implemented |
| D4 | A3-local scaffolding must be namespace-scoped; root-namespace declarations in the candidate are rejected pre-store | `formalization.py` (`validate_scaffolding_namespace` + prompt) + `a3_runner.py` (hook at formalize) | 2 unit + 2 end-to-end (mocked provider) + 1 regression | ✅ implemented |
| D3 | Collision check as a documented review item in the ontology-record template | `core-glossary-detail.md` (registry v1.1.0 template + change log) | docs only; CI-grep proposal below (§1.3) | ✅ docs |

**Surfaced finding (fixed as root cause):** the walkthrough-era proof-body
check (`re.search(r"\s:=", ...)`) false-positived on legitimate scaffolding
definitions (`abbrev Bundle := ℝ`). D4's namespaced scaffolding made the
old regex untenable — the check now rejects `:=` only on theorem-style
declarations (`theorem`/`lemma`/`example`/`axiom`), with a regression test
(`test_validate_statement_text_allows_definitional_body`). The original
hardening intent (no proof bodies) is preserved.

## 1. Per-delta detail

### 1.1 D1 — `core` mapping kind + fully-qualified identifiers

- `MAPPING_KINDS` gains `"core"` (a3-core-design.md §4 target contract).
- New `CORE_IDENTIFIER_RE = ^LeanEcon\.Core\.[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$`
  — the `LeanEcon.Core.` prefix plus **at least two dotted components**
  (`<Area>.<name>`), because the namespace skeleton (design §1.3) requires
  declarations to live under an Area. `LeanEcon.Core.attainableSet` (no
  Area) is flagged, as is any bare name or non-Core id.
- `validate_mapping_report` rejects mapped `core` rows whose
  `lean_identifier` does not match: problem list → `PROVIDER_INVALID_OUTPUT`
  at formalize, candidate never reaches the store.
- `formalize_prompt` now instructs the model: `core` rows must carry the
  FQ id (`LeanEcon.Core.Choice.attainableSet`), never a bare name; the row
  must resolve as written.

### 1.2 D2 — Core pin in the bundle

- `lean_probe.compute_core_revision(workspace_root)` — SHA-256 over the
  sorted (relative path, content) pairs of every `LeanEcon/Core/**/*.lean`
  module. **Content-based** (the "manifest digest of the Core module tree"
  option in design §1.4): the pin tracks actual Core content, not
  unrelated commits. `None` when no Core tree exists (pre-Core claims).
- `WorkspaceIdentity` gains `core_revision` (frozen dataclass, default
  `None` — backward compatible).
- `build_bundle`: `workspace_identity.core_revision` recorded;
  `dependency_audit.core_imports` = union of Core imports across the
  formal statement **and the proof input** (the kernel compiles the proof;
  an import there must be pinned too).
- Validator check **`12_core_pin`** (new, additive — the eleven original
  checks are untouched and still numbered 1–11):
  - Core imports present without a pin → **fail** (the plan's required
    behavior);
  - pin present and workspace available → recompute and compare
    (**stale-pin detection**, data-flow-model.md §8: "Stale Core pin |
    bundle validator rejects"); mismatch → fail;
  - workspace not available/unreadable → presence verified, environment
    noted (honest fallback for offline validation);
  - no Core imports → vacuous pass (historical c1–c4/fwt1 bundles
    re-validate unchanged).
- `schema_version` policy proposal: **keep `1.0.0`** — the fields are
  additive, the validator is the only consumer, and historical bundles
  without the fields must still validate (presence-based check handles
  both shapes). Matches the EI-schema freeze precedent (additions folded
  into 1.0.0, no released consumers). See decision D2 below.
- Wording: "eleven required checks" references in code updated to reflect
  the additive 12th check (`cmd_bundle` prints the actual count).

### 1.3 D3 — collision check (docs) + CI-grep proposal

- The ontology-record template (registry v1.1.0) gains the
  `collision_check` review item (design §7 criterion 4): the FQ name must
  not collide with any imported dependency's namespace, and unqualified
  use in candidates must not shadow imported Mathlib identifiers —
  recorded per declaration at promotion. Additive; no entry meaning
  changed; no downstream re-review (change-log row added).
- **Proposed (not implemented) mechanical aid:** a promotion-time grep
  that extracts root-level declaration names from
  `lean_workspace/LeanEcon/Core/*.lean` (`^(def|abbrev|structure|class|theorem|instance) `)
  and compiles a `#check <name>` probe under `import Mathlib` in the
  pinned workspace — a Mathlib root identifier with the same name
  resolves to the Mathlib one and the probe output is verbatim kernel
  evidence (same culture as the P2 check-file). Batch-sized (~one lake
  invocation per declaration); run at promotion, not per-commit. If the
  CTO wants it in CI (scaffold-check), it becomes a separate small
  delta — deliberately not in this batch.

### 1.4 D4 — namespace-scoped A3-local scaffolding

- **Home proposed and implemented: `formalization.py`** (static input
  contract on the candidate statement, sibling of
  `validate_statement_text`), not the verifier. Rationale: the candidate
  STATEMENT is the formalizer's output and the prompt can require the
  rule; the verifier compiles reviewer-authored PROOF fixtures, which are
  human artifacts and were reviewed at root in the past — hard-failing
  the kernel path would reject approved inputs. A verify-side soft signal
  for proof scaffolding is proposed separately (decision D6).
- `validate_scaffolding_namespace(statement)`: lexical namespace-depth
  tracking (`namespace`/`end`); any `abbrev|def|structure|class|inductive|instance`
  at depth 0 is flagged. `theorem` is deliberately NOT scaffolding and
  never flagged. Tolerates `noncomputable`/`@[attr]` prefixes.
- Hooked into `formalize_claim` after the sorry/`:=` check: root
  scaffolding → `PROVIDER_INVALID_OUTPUT`, candidate never reaches the
  store (same class as the Track B static rejections).
- `formalize_prompt` instructs `namespace A3Scaffolding.<claim_id> ... end`.
- **Surfaced finding:** the `:=` proof-body check had to become
  declaration-aware (see §0) — this is the fix-the-class item; the old
  regex would have rejected every D4-compliant namespaced scaffolding
  statement.

## 2. Doc-code consistency (a3-core-design.md §4)

| Design states (§4) | Implementation | Consistent? |
|---|---|---|
| `mapping_kind`: `mathlib \| core \| glossary_term \| local_definition` — "`none` is dropped (Open Q2)" | enum = `mathlib, core, local_definition, glossary_term, none`; prompt instructs the target contract (no `none`) | ⚠️ `none` retained in the enum for historical tolerance — deliberate exclusion (decision D7); prompt aligned to the target contract |
| D1: "`core` rows carry the fully qualified identifier (e.g. `LeanEcon.Core.Choice.attainableSet`, never bare `attainableSet`) — the row must resolve as written" | `CORE_IDENTIFIER_RE` + validator + prompt | ✅ |
| D4: "scaffolding must be namespace-scoped (`namespace A3Scaffolding.<claim>`), never root-namespace" | `validate_scaffolding_namespace` + prompt + formalize hook | ✅ |
| D2 (§1.4): "`workspace_identity.core_revision` (commit sha or manifest digest of the Core module tree) and `dependency_audit` records Core imports" | content digest + `core_imports` + check 12 | ✅ |

## 3. Decisions requested from the CTO

| # | Decision | Proposal | Alternatives |
|---|---|---|---|
| D1 | Core FQ pattern: require `LeanEcon.Core.<Area>.<name>` (≥2 components after the prefix) | Yes — matches the namespace skeleton (design §1.3) | allow 1 component (`LeanEcon.Core.X`) |
| D2 | Manifest `schema_version` policy: **keep 1.0.0** (additive fields; validator-only consumer; historical bundles must re-validate) | Keep | bump 1.1.0 (churn; no released consumers) |
| D3 | Check numbering: new distinct check `12_core_pin` | Separate item — auditable failure reason | fold into check 7 (muddies the pin-failure semantics) |
| D4 | Stale-pin comparison (manifest vs workspace) included in check 12 when the workspace is available | Include — completes data-flow §8's failure flow | presence-only |
| D5 | D4 semantics: hard rejection at formalize (PROVIDER_INVALID_OUTPUT, no artifact) | Hard — same class as sorry/`:=`; the prompt requires the rule | soft warning only |
| D6 | Verify-side proof scaffolding: **no check in this batch**; proposed as a soft recorded signal later | Defer — proofs are reviewer-owned; hard-failing would reject approved fixtures | soft signal now |
| D7 | `mapping_kind: none` stays in the enum (historical tolerance); the prompt already instructs the target contract | Keep for now; remove in a later delta (Open Q2, already resolved in design) | remove now |
| D8 | D3 CI grep: proposal only (§1.3) | Proposal only | implement in scaffold-check now |

## 4. What is deliberately NOT in this batch

- **No verify-side scaffolding check** (D6 above) — reviewer-authored proof
  fixtures at root (c1–c4, fwt1) remain valid inputs; the D4 contract
  governs candidates.
- **No removal of `mapping_kind: none`** (D7) — Open Q2's drop is recorded
  in the design; landing it now would touch the enum contract beyond the
  plan's P4 table.
- **No D1 reverse check** (a non-core row citing a `LeanEcon.Core.*`
  identifier is not yet flagged as mislabeled) — proposed, not
  implemented; the required direction (core ⇒ FQ) is the plan's ask.
- **No Core-importing claim run** — Core is not yet used by any claim
  (risk-register rule: D2 lands BEFORE any claim imports Core; a live
  Core-import verification is P5/evidence work).
- **No equilibrium declarations, no demand/choice correspondences, no v3
  material** (unchanged from the plan's §8).

## 5. Process notes

- Files touched: `src/leanecon/{formalization,a3_runner,bundle,lean_probe,trace_replay}.py`,
  `tests/test_{formalization,bundle,a3_runner}.py`,
  `docs/gate6/references/core-glossary-detail.md` (registry v1.1.0).
- Verification: **156 passed** (137 baseline + 19 new; real output
  above). The D4 end-to-end tests use the mocked-provider pattern with
  the autouse `probe_statement_compiles` patch (test_a3_runner.py). No
  Lean builds needed — no Lean source changed.
- After approval: DECISION_LOG items 22–24 (P3 registry merged PR #9;
  P4 batch approved; commit pending) + this package, then commit/PR per
  the established flow (docs+code; scaffold-check gate; merge quirks per
  the skill).

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver. This package
authorizes nothing; the P4 commit follows only after CTO approval.
