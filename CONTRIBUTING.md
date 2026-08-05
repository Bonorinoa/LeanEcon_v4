# Contributing to LeanEcon v4

LeanEcon v4 is a governed, clean-room rebuild. Contributions are welcome, but
the review bar is deliberate.

## Review policy

- **Branch protection:** `main` is protected. All changes land via pull
  request; direct pushes are blocked.
- **Required review:** every PR needs at least one approving review from an
  authorized contributor, and the author cannot approve their own PR.
- **Required CI:** the scaffold CI check must pass before merge.
- **Semantic approval:** the CTO (or an authorized human reviewer) owns
  interpretation and semantic approval. Automated agents never approve meaning.
- **No v3 import:** do not copy v3 code, prompts, schemas, tests, or
  `.codebase-memory`. Every relationship to a v3 artifact is recorded in the
  migration ledger with a disposition.

## Process

1. Fork or branch from `main`.
2. Make a small, single-purpose change.
3. Open a pull request describing the change, its motivation, and its
   disposition with respect to v3 (`import` / `adapt` / `rebuild` /
   `inspiration` / `historical-discard`).
4. Wait for CI and an approving review; address review feedback.
5. Never merge your own PR.

## What is accepted

- Governance, documentation, contracts, tests, and first-principles
  implementation that respects the gate sequence and trust boundaries.
- Anything that improves auditable provenance or verification honesty.

## What is rejected

- Wholesale copying from v3 (or anywhere else) without a ledger disposition.
- Claim-specific closures, hidden benchmark answers, or gold artifacts in
  runtime code.
- Committed credentials or provider payloads.
- Labeling results `VERIFIED` without the complete verification bundle.
