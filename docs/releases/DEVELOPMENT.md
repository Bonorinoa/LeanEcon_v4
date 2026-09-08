# Development truth surface

## Current state

This worktree is the **v4 agentic development line** (dev version; the
latest supported release is v3.5.0 Measured Elaboration).

| Item | Value |
|---|---|
| Package version | `4.0.0.dev0` |
| Builder identity | `leanecon-a3-4.0.0.dev0` |
| Latest supported release | `v3.5.0` |
| Next development line | v4 agentic — consultative opinion side-door first (DL 51/D3; `docs/v4/INIT_V4_AGENTIC.md`, `docs/v4/G0_OPINION_SLICE.md`) |

The v3.5.0 earn (sealed holdout `formalizer-v35h1` draft_complete 2/3 ≥
0.60) stands on the tag. v4 opens the agentic line: the consultative
opinion surface (never ACCEPTED/REJECTED, never a lifecycle transition),
with the D4 model A/B held by the CTO (keep `labs-leanstral-1-5` until
retirement forces the decision — reported Labs retirement 2026-09-30).

## Release rule

A final version (for example `4.0.0`) is allowed only when all of the
following are true:

1. the package version and `BUILDER_IDENTITY` agree;
2. the current commit carries the matching annotated `v<version>` tag;
3. the release packet records an earned, approved product promise; and
4. the release-state check and the full verification suite pass.

Development versions must use a PEP 440 prerelease suffix such as
`.devN` and must continue to name the latest supported release in
this document. This file reverted to `4.0.0.dev0` at the first commit
of the v4 development line.

`scripts/check_release_state.py` enforces (1), (2), and this file.
It does not authorize a tag.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
