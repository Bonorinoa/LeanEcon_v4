# Development truth surface

## Current state

This worktree is a **development build**, not a LeanEcon release.

| Item | Value |
|---|---|
| Package version | `3.0.0.dev0` |
| Builder identity | `leanecon-a3-3.0.0.dev0` |
| Latest supported release | `v2.0.0` on `main` |
| Current development line | v3 Verifiable State Machine (narrowed); v4 = wire intelligence |

`v3.0.0` is deliberately untagged. The original draft-complete target
was missed (combined **2/13 ≈ 15%**). The CTO narrowed the promise to
**Verifiable State Machine** (DECISION_LOG 46). This file still forbids
advertising a final `3.0.0` until the matching tag exists. See
`docs/releases/v3.0.0.md` and `docs/v3/V3_NOT_EARNED.md`.

## Release rule

A final version (for example `3.0.0`) is allowed only when all of the
following are true:

1. the package version and `BUILDER_IDENTITY` agree;
2. the current commit carries the matching annotated `v<version>` tag;
3. the release packet records an earned, approved product promise; and
4. the release-state check and the full verification suite pass.

Development versions must use a PEP 440 prerelease suffix such as
`.devN` and must continue to name the latest supported release in
this document.

`scripts/check_release_state.py` enforces (1), (2), and this file.
It does not authorize a tag.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
