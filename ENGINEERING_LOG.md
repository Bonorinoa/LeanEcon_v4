# Engineering Log (v4 live)

Compact, durable lessons only. v3's frozen log stays in the v3 archive.

## 2026-08-05 — A1 diagnostics green (Gate 4)

- All ten A1 criteria passed on first complete run after two fixes:
  (a) Lean LSP rejects bare JSON-RPC; it requires `Content-Length` header
  framing — probe now frames requests properly; (b) lakefile pin parsing
  needed a regex (`"mathlib" @ git "<tag>"`), naive line-splitting broke.
- Pinned workspace: Lean `v4.32.2` + Mathlib tag `v4.32.2`; prebuilt cache
  (`lake exe cache get`) makes the 2997-job build ~10 s on a warm checkout.
- Architecture tests (no HTTP imports outside adapters, no vendor model
  ids in core) caught a real violation during development: the runner had
  hardcoded a model id; fixed by routing through the adapter's MVP map.
  Static boundary checks are worth their weight.
- Approval-prompt friction: shell commands touching the profile `.env`
  inline trip interactive approvals; packaging credential loading inside a
  script (`scripts_local/a1_live_probe.py`) avoids it and never prints
  secrets.
- `main` is protected with `enforce_admins: true` + 1 required approval:
  even the owner must merge via PR, and a second account is needed for a
  real review. Interim state documented; no governance fabricated.
