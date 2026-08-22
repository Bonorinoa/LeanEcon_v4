# Development truth surface

## Current state

This worktree is the **v3.0.0 release** (Verifiable State Machine).

| Item | Value |
|---|---|
| Package version | `3.0.0` |
| Builder identity | `leanecon-a3-3.0.0` |
| Release | `v3.0.0` (tagged on main) |
| Next development line | v4 intelligence (elaboration-class lever; `docs/v4/INIT_V4.md`) |

The original draft-complete target was missed (2/13 ≈ 15%) and was
narrowed out of the v3 promise (DECISION_LOG 46). v4h1 measured
audit-clean 5/5 after the mechanical repair lever (DECISION_LOG 48);
probe/elaboration rate is to be re-measured on a fresh sealed set
(v4h1 is spent; its probe numbers were invalidated by a wrap bug,
fixed in `verifier.py` 2026-08-17).

## Release rule

A final version (for example `3.0.0`) is allowed only when all of the
following are true:

1. the package version and `BUILDER_IDENTITY` agree;
2. the current commit carries the matching annotated `v<version>` tag;
3. the release packet records an earned, approved product promise; and
4. the release-state check and the full verification suite pass.

Development versions must use a PEP 440 prerelease suffix such as
`.devN` and must continue to name the latest supported release in
this document. The next line of development (v4) must revert this
file to `3.0.1.dev0` or similar before its first commit.

`scripts/check_release_state.py` enforces (1), (2), and this file.
It does not authorize a tag.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
