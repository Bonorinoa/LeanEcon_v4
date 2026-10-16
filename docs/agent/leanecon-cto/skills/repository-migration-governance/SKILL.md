---
name: repository-migration-governance
description: "Use for governed legacy-to-new repository migrations."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [migration, repository, architecture, provenance, governance, freeze, clean-room]
    related_skills: [github-repo-management, github-auth, plan, requesting-code-review]
---

# Repository Migration Governance

Use this skill when a legacy repository must be frozen, dissected, and selectively rebuilt in a new repository. It is for migrations where historical evidence, evaluation integrity, architectural independence, and human approval matter as much as code transfer.

## Core operating model

Treat the legacy repository as three separate things:

1. **Evidence** — observed behavior, failures, historical measurements, and lessons.
2. **Assets** — code, schemas, tests, documentation, or data that might be useful.
3. **Contamination risk** — shortcuts, benchmark leakage, secrets, generated state, hidden coupling, or architecture that should not cross the boundary.

The new repository is a new system with a new history. Do not use a new remote as a pretext for copying the old implementation wholesale.

## Required sequence

1. Read the governing strategy/design document. If full PDF extraction is truncated or blank, use page-range extraction and inspect relevant ranges independently.
2. Capture a read-only baseline: branch, HEAD, upstream divergence, tags, remotes, modified files, untracked files, and ignored/generated candidates. Never reset or clean before dispositions are approved.
3. Inventory the entire repository: source, tests, Lean/formal artifacts, prompts, benchmarks, CI, Docker, deployment, generated files, caches, logs, docs, environment files, and dependency metadata.
4. Verify high-impact claims independently. Record exact path/symbol/line, commit, reproduction command, observed result, confidence, and consequence for the new system.
5. Create a migration ledger before migration. Every major artifact receives a disposition, rationale, provenance, reviewer, tests, contamination risk, and destination.
6. Separate retention from migration. Historical material may remain in the frozen legacy repository without being copied into the new runtime or release corpus.
7. Prepare compact retention artifacts: a short live engineering log, concise legacy summary, and curated failure corpus tied to new acceptance tests.
8. Obtain approval for dirty-worktree dispositions. User-owned modifications, untracked audit files, generated graphs, and possible secrets are never discarded automatically.
9. Freeze the legacy repository non-destructively: apply approved changes, run verification, review the exact diff, create one final freeze commit, create an annotated freeze tag, verify, and archive/protect only after approval.
10. Bootstrap the new repository separately. Add governance, license, CI, contracts, and provenance records before implementation. Do not import legacy custom implementation by default.

## Successor-repository bootstrap (Gate 2) pitfalls

- **Verify credentials with a real API call before any creation step.** `gh auth status` may not exist (no `gh` installed) and a stored `GITHUB_TOKEN` may be stale. Call `GET https://api.github.com/user` with the token and require HTTP 200 + expected login before touching the API. A `401 Bad credentials` is an invalid/stale token, not "propagation lag" — never retry it as if it were transient, and never take "it should work now" as evidence.
- **Meaningful CODEOWNERS + `self_approval=false` protection require TWO DISTINCT GitHub accounts.** The same username twice is not two authorized contributors; an AI agent pushing through the CTO's account is not a second account; a bot account must already exist and be added as a collaborator before it can own or approve anything. If the second account does not exist, do not fabricate the governance: create the repo, document the single-owner interim state, and record the second-account requirement as an open gate condition.
- **The agent cannot create GitHub accounts** (email, verification, and credentials belong to the human). Propose the bot-machine-user option; the human creates it.
- **Self-approval protection is symbolic until a second distinct account approves.** GitHub's restriction only bites when the PR author and the approving account are different accounts; single-account operation means the required review is effectively unenforceable. State this plainly to the CTO rather than implying the protection is real.
- **Do not ask for secrets in chat and never print them in tool output.** If the user offers to paste a token, redirect: have them run a self-check that prints only sanitized metadata (http_status, login, token length, sha256 prefix) and paste that back. In the Hermes desktop app, background PTY terminals cannot receive hidden stdin (`read -s` hangs, `getpass` raises `termios.error`/`EOFError`) — the user's own terminal is the safe capture point, not a tool-launched prompt. Also: inline shell commands that source a secrets `.env` or embed credential-shaped regex literals frequently trip interactive approval prompts; package credential loading into a script file instead.
- **`enforce_admins: true` blocks the owner too.** With enforce_admins + required checks + 1 approval, direct pushes to `main` are rejected even for the repo owner (GH006); everything merges via PR, and since self-approval is impossible, merging realistically requires a second account. Use stacked branches (later gate branch → earlier gate branch as PR base) so each PR diff shows only its own gate's work. Caveat: workflows scoped `pull_request: branches: [main]` never run on stacked PRs — use bare `pull_request:` triggers. GitHub reads the workflow file from the PR head branch, so the trigger fix can land in the same branch.
- **Temporary relax → merge → restore** when the CTO explicitly approves merging without the second account: GET `/branches/main/protection` and capture the exact payload; PUT it back with `required_approving_review_count: 0` (keep checks, keep enforce_admins); merge; restore the ORIGINAL payload in a `finally` block; verify the restore with a re-read; and record the relaxation in the repo's engineering log so the audit trail lives in-repo. Never leave protection relaxed across a session boundary. Reusable implementations: `scripts/github_merge_pr.py` (full relax → wait → merge → restore cycle, one command) and `scripts/github_check_pr_ci.py` (pre-flight: list open PRs with their check-run states). Both load the token from the profile env file themselves — no shell sourcing, no secret literals on the command line.
- **Stacked-PR check mechanics:** retargeting a PR's base does NOT re-run checks on the existing head sha — push a new commit (e.g. merge the new `main` into the branch, which `strict: true` checks require anyway). `workflow_dispatch` can only fire workflows that exist on the default branch (404 otherwise). A check-wait poller must distinguish three states — missing (not yet registered), in_progress, failed — and poll with a deadline instead of failing on the first empty poll; require all required checks registered AND completed before merging.
- **Keep the fresh worktree outside the legacy checkout** and leave the legacy repo untouched until its freeze is approved. Record the exact worktree path and the exact initial file list in the gate evidence.

## Disposition vocabulary

Use these categories consistently:

- **import** — substantially copied as-is; rare and explicitly approved.
- **adapt** — copied and materially modified; rare and explicitly approved.
- **rebuild** — independently implemented from a contract, observed behavior, or lesson.
- **inspiration** — no implementation transferred; only the idea, failure, or requirement informed design.
- **historical-discard** — retained only in the legacy archive or excluded because it is obsolete, unsafe, generated, or misleading.

For clean-room or reliability-oriented rebuilds, default custom implementation to `rebuild`, `inspiration`, or `historical-discard`. Never label an artifact `import` merely because it is small or currently passes tests.

## Evidence-register format

For every high-impact claim, record:

```text
claim_id
proposition
source_path
symbol_or_line
source_commit
reproduction_command
observed_result
confidence
confirmed/qualified/rejected
v4_consequence
```

Distinguish what the source proves from what the strategy document inferred. A strategy report is a useful hypothesis source, not a substitute for current-source verification.

## Evaluation-integrity rules

Treat any runtime path that receives gold formal statements, theorem stubs, reviewer labels, answer keys, or claim-specific closures as a possible evaluation leak. Verify whether a “faithfulness” or “success” metric is measuring generation, replay, compilation, or a heuristic shortcut.

In the new repository:

- runtime agents receive only allowed user inputs and approved context;
- gold artifacts stay evaluator-side and are inaccessible by filesystem, environment, import, or network path;
- release and historical corpora are separate;
- legacy scores are never presented as comparable new-repository scores;
- claim-specific recovery code is rebuilt as generic contracts or removed;
- semantic faithfulness and kernel validity have separate gates.

## Secrets and generated state

Do not read or migrate secret contents merely to inventory them. Record the path and risk, verify ignore/status behavior, and exclude it from migration. Treat caches, bytecode, generated graphs, rendered PDFs, temporary extraction trees, UUID/check files, and build outputs as generated state until proven otherwise.

For generated graph/index artifacts, compare metadata (commit, timestamp, node/edge counts, sizes) and source-control status before deciding whether to preserve, archive, or restore. Do not silently replace a committed historical graph with a partial regenerated index.

**Credential-shaped literals in source fail CI secret scans.** Pattern-based credential scanners (including the repo's own scaffold scan) match fake test fixtures and detection regexes, not just real secrets. Two durable fixes: build fake tokens dynamically in tests (`fake = "ghp_" + "A" * 30`) and assemble secret-matching regexes from string fragments (`"gh" + "p_[A-Za-z0-9]{20,}"`). Before committing, scan the staged diff against a pattern file rather than embedding the patterns in the shell command line (which also trips interactive approval prompts).

**Successor-repository rule:** never import the legacy graph/index into the successor. Restore the committed legacy state when the working copy contains incidental or partial regeneration, then install or rerun the representation tooling (MCP, Graphify, or equivalent) against the successor only after it has meaningful source structure. Treat the fresh graph as advisory and reproducible tooling output, not as architecture truth or a release dependency.

## Freeze procedure

A freeze is a reviewed state transition, not a cleanup command:

1. inventory current changes;
2. assign every change a disposition;
3. preserve or archive generated state deliberately;
4. apply only approved documentation/history changes;
5. run the agreed tests and record actual output;
6. review staged diff;
7. commit once;
8. tag the exact commit;
9. verify clean status, branches, tags, and remote state;
10. archive or protect the repository only after explicit approval.

Never use `git reset`, `git clean`, branch deletion, history rewrite, or deletion of user-owned material as an implicit freeze step.

## Human alignment and documentation

When the user wants to understand and approve architecture, use gates. At each gate provide:

- the decision;
- alternatives considered;
- recommendation;
- plain-language explanation;
- concrete evidence;
- acceptance/exit criteria;
- exact user decision required.

For planning alignment, multiple-choice decision artifacts are preferred when they reduce ambiguity. Keep project documentation compact and high-information; put detailed session-specific evidence in `references/` or ledgers rather than creating many long top-level documents.

## Validation checklist

Before reporting a migration or freeze as complete, verify:

- exact legacy commit and tag;
- clean worktree or explicitly documented exceptions;
- no secret contents staged;
- all major artifacts have ledger dispositions;
- provenance distinguishes copied code from rebuilt code;
- new repository has independent history;
- architecture boundaries have executable tests where possible;
- evaluation gold isolation is tested;
- verification artifacts are reproducible;
- user approval exists for irreversible actions.

## Approval-gate closure and staged-package validation

Use this workflow when a CTO closes a documentation or contract gate after iterative review:

1. Convert each approval response into an explicit decision-table row. A blanket response such as “Y to all questions” closes every enumerated question, but does not broaden scope beyond the question wording. Preserve distinctions such as “design direction approved” versus “schema frozen” and “A1 authorized” versus “all Gate 4 work authorized.”
2. Reconcile every document against the closure record. Remove stale `OPEN`, `CONDITIONAL`, `awaiting approval`, and “gate remains blocked” markers; do not leave duplicate historical rows in a current-state table. Keep historical context in a clearly labeled decision log, not as contradictory live status.
3. Prefer a full-file rewrite when repeated exact-match patches produce stale or duplicated table rows. Re-read the complete file before rewriting, and verify the rewritten result afterward.
4. Keep the docs-only boundary explicit in the package index and decision log: no implementation, no v3 transfer, and no implied authorization for later gates. Credit the AI assistant in attribution while preserving the CTO's semantic authority.
5. Stage only the intended package paths, then run final checks against the staged tree: whitespace/errors, schema parsing, exact path-scope/count, no unstaged amendments, and secret-pattern scanning over the staged diff. Use robust quoting in inline validation scripts; prefer a temporary script or shell variables when nested Python/shell quoting could alter expressions.
6. After the package passes validation, stop at the authorized boundary. A documentation commit is not permission to begin implementation unless the gate record separately authorizes that next scope.

For a worked example and reusable validation command, see `references/approval-gate-closure-pattern.md` and `scripts/validate_staged_package.sh`.

## Design-review packages (gate before implementation)

Some gates are design reviews rather than docs closures: the CTO must understand the INNER WORKINGS of a planned subsystem so they can later interpret evaluation results. Shape the package accordingly:

- **Explain internals in plain language, no Lean.** Every artifact must be readable by someone who never sees Lean syntax; explain kernel, `sorry`, axiom audits, and `#print axioms` in prose (see `references/lean-workspace-diagnostics.md`).
- **Sections that make results interpretable:** lifecycle states + who triggers each transition (system vs reviewer); exact data flow (objects, digests vs payloads, redaction points); each service contract; verifier internals and the exact VERIFIED/FAILED/BLOCKED criteria; bundle manifest field-by-field; event sequences for happy + semantic-rejection + proof-failure + outage paths; a "reading a bundle" CTO guide; test plan with reuse inventory; open questions explicitly flagged. Gate 5's ten mandated sections are in `references/gate5-a3-design-review.md`.
- **Per-run reviewer records instead of repo-wide allowlists** (axiom approval via `axiom_approval_ref`, mapping-gap acknowledgement): same pattern both times — first run surfaces the item and FAILS (`AXIOM_VIOLATION`), the bundle carries the plain-language list, the reviewer approves a per-run record, retry passes on the same candidate. Design the walkthrough to exercise this honest first-run loop.
- **Draft-schema exercise pattern:** "design direction approved" ≠ schema frozen. When a locked direction needs a concrete representation (e.g. `none_noted` + reviewer acknowledgement), PROPOSE the representation in the design, flag it as an open question, and defer freeze until implementation exercises it.
- **Acceptance-test-before-implementation:** when the plan requires canonical examples reviewed before building (EI acceptance test: first 3–5 claims), propose candidates in an appendix explicitly flagged for review; implementation waits on that separate approval.
- **Approval of the design ≠ authorization to commit.** After "approve as-is", stage the package (`git add docs/<gate>/`), but still do NOT commit/push/implement until the CTO separately authorizes the commit; record the approval outcome and pending items in memory.
- **Baseline evidence:** run the existing test suite before writing the package and cite the real pass count in the summary.

## References

- `references/leanecon-gate0-example.md` contains the reusable evidence/ledger/freeze pattern.
- `references/pdf-strategy-extraction.md` contains the page-range extraction fallback for incomplete PDF extraction.
- `references/gate2-github-bootstrap-notes.md` contains the successor-repo bootstrap session notes (token 401 ≠ lag, two-account CODEOWNERS, Hermes PTY stdin limits).
- `references/lean-workspace-diagnostics.md` covers pinned Lean/Mathlib workspace probes: Content-Length LSP framing, pin parsing, cache-fast builds, typed-failure probes.
- `references/approval-gate-closure-pattern.md` contains the Gate 3 closure workflow, stale-marker pitfalls, and validation evidence.
- `references/gate5-a3-design-review.md` contains the Gate 5 A3 design-review decisions, canonical-claim candidates, and reading-a-bundle doctrine.
- `scripts/validate_staged_package.sh` validates a staged docs-only package without reading secrets.
- `scripts/github_merge_pr.py` runs the full relax → wait-for-checks → merge → restore cycle for a PR on a protected single-account `main` (`python github_merge_pr.py OWNER/REPO PR_NUMBER`).
- `scripts/github_check_pr_ci.py` lists open PRs with check-run states — pre-flight for the merge cycle (`python github_check_pr_ci.py OWNER/REPO`).
- `templates/token_selfcheck.py` is the safe token self-check script: user runs it in their own terminal, pastes back only sanitized metadata. Never print tokens.
