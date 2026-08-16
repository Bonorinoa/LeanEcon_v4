# Development truth surface

## Current state

This worktree is a **development build**, not a LeanEcon release.

| Item | Value |
|---|---|
| Package version | `3.0.0.dev0` |
| Builder identity | `leanecon-a3-3.0.0.dev0` |
| Latest supported release | `v2.0.0` on `main` |
| Current development line | constrained auto-formalization (loop + scorer + skeleton) |

`v3.0.0` is deliberately untagged. Its original draft-complete target
was missed on the frozen evaluation splits (2/8 = 25%), so no
document, package metadata, or verification bundle may present this
development line as an earned release. See `docs/v3/V3_NOT_EARNED.md`
and `docs/eval/v3-claim-split.md`.

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
