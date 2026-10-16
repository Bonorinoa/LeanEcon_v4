# v4 direction + how to tag a final release (2026-08-16)

## v3 / v4 lock

- v3 promise **narrowed** to Verifiable State Machine (DECLOG 46).
  Packet: `docs/releases/v3.0.0.md`. 60–70% draft-complete is **not**
  a v3 claim (combined **2/13 ≈ 15%**; all of v3h / v3h2 / v3h3 spent).
- v4 = wire intelligence into that machine (`docs/v4/INIT_V4.md`,
  DECLOG 47). Sprint: `docs/v4/SPRINT.md`. Default first lever:
  deterministic formalize sanitizer (strip theorem `:=`/`sorry`,
  refuse root-level Core redefs), not a model swap.
- No v4 code until v3 is on `main` and the CTO says go on Day 1.
- Sealed-holdout procedure: `references/v3h3-sealed-holdout-2026-08-16.md`.

## Do not bump a final version on a PR branch

`scripts/check_release_state.py` requires `vX.Y.Z` at HEAD for a
final package version. GitHub Actions `pull_request` checkout is a
merge-ref and will not see that tag → CI red. Sequence: merge the
branch as `X.Y.Z.devN`, then on `main` bump + annotated tag in the
same commit. `merge_pr.py` uses `merge_method=merge` (not squash).

## Token check before protection ops

`load_cto_token()` prefers `os.environ["GITHUB_TOKEN"]` over the
profile `.env`. Before `merge_pr.py` / `verify_protection.py`, GET
`/user` and print **login only**. Expect `@Bonorinoa`. `hermessinho`
can push/PR (`open_pr.py --bot`) but cannot relax protection or merge
its own PR.

Predictions for live evals belong in tracked `docs/eval/`, not only
gitignored `.hermes/plans` or `artifacts/local`.

**Attribution:** Hermes under CTO direction.
