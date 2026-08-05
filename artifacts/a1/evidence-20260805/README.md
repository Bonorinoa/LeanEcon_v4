# Gate 4 — A1 Diagnostics Evidence Packet

**Run date:** 2026-08-05 · **Environment:** macOS 26.5.2 (arm64), Python 3.11.15 (venv), Lean 4.32.2 via elan 4.2.0 · **Branch:** `gate4/a1-diagnostics`

**Scope:** A1 diagnostics only (CTO authorization, Gate 3 closure). No A3 workflow, no LeanEcon Core, no production `VERIFIED` claims.

## Result: all ten criteria GREEN

Run `a1-33345b32d37e` (live) and `a1-b9dd5c1d97d6` (offline). Machine-readable summaries and full event traces are committed in this directory.

| # | Criterion (plan) | Status | Evidence |
|---|---|---|---|
| 1 | Pinned Lean and Mathlib build successfully | ✅ HEALTHY | `scripts/a1_lean_build.sh`: `lake update` exit 0, `lake exe cache get` exit 0, `lake build LeanEcon.A1` — 2997 jobs built. Pin: `lean-toolchain` = `leanprover/lean4:v4.32.2`, Mathlib = git tag `v4.32.2` (lakefile). |
| 2 | Lean compiler probe succeeds | ✅ HEALTHY | `lake env lean --version` → `Lean (version 4.32.2, arm64-apple-darwin24.6.0, commit f3b06c70…)`; `LeanEcon.A1` probe theorem kernel-checked. |
| 3 | LSP responds or explicitly reports UNAVAILABLE | ✅ HEALTHY | `lean --server` JSON-RPC `initialize` (Content-Length framed) returned capabilities; probe emits `LSP_UNAVAILABLE` explicitly when absent — no silent fallback. |
| 4 | Formalization model returns valid structured output (live) | ✅ HEALTHY | `labs-leanstral-1-5` via Mistral adapter, synthetic PUBLIC probe, structured JSON returned. See `live-summary-redacted.json` C4. |
| 5 | Interpretation model returns schema-valid interpretation (live) | ✅ HEALTHY | `mistral-medium-3-5` via Mistral adapter, synthetic micro claim, JSON interpretation returned. See C5. |
| 6 | Provider metadata: model, request id, latency, tokens | ✅ HEALTHY | Every live response carried `model`, `request_id`, `latency_ms`, `token_metadata` (prompt/completion tokens). See C6. |
| 7 | Every diagnostic emits a machine-readable event | ✅ HEALTHY | Append-only JSONL per run (`live-run-events.jsonl`): one `DIAGNOSTIC_RESULT` per criterion plus `HEALTH_CHECK`; runner validates every event before append. |
| 8 | Runtime cannot access v3 gold/labels/release artifacts | ✅ HEALTHY | Structural scan: no `benchmark_baselines`, `evals`, `gold*`, `sealed_corpus`, `.codebase-memory`, `leanecon_v3`, release paths; no gold env pointers; policy denies gold markers even in PROJECT payloads (test-enforced). |
| 9 | Invalid Lean input produces a typed failure | ✅ HEALTHY | `def broken : Nat := ` → exit ≠ 0, typed `LEAN_SYNTAX_ERROR`, recorded as criterion C9. |
| 10 | Provider outage/malformed output produces typed provider failure | ✅ HEALTHY | Malformed response → `ProviderFailure(PROVIDER_INVALID_OUTPUT)`; outage/retry-exhaustion → `PROVIDER_UNAVAILABLE`; no silent fallback (architecture + mocked tests). |

## Verification commands (recorded per plan)

| Command | Result |
|---|---|
| `bash scripts/a1_lean_build.sh` (lean_workspace) | exit 0; `build-exit=0`; `✔ [2997/2997] Built LeanEcon.A1` |
| `.venv/bin/python -m pytest -q` | **44 passed** (events, data policy, provider boundary, architecture boundary, lean probes, gold isolation) |
| `.venv/bin/python -m leanecon.a1_runner` (offline) | exit 0; C1–C3, C7–C10 HEALTHY; C4–C6 UNAVAILABLE (skipped, requires `--live`) |
| `.venv/bin/python scripts_local/a1_live_probe.py` | exit 0; **all_green=true**; summary written redacted |

**Limitations:** live probes are point-in-time samples (one request per model), not availability statistics; CI runs tests without a Lean toolchain, so workspace-dependent tests skip there and are proven locally; the live-probe helper (`scripts_local/a1_live_probe.py`) stays local-only because it reads the profile credential path.

## Clean-checkout reproduction

1. `git clone` + `git checkout gate4/a1-diagnostics`
2. `uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]"`
3. `.venv/bin/python -m pytest -q` → 44 passed
4. With elan/lake: `bash scripts/a1_lean_build.sh` → builds pinned workspace
5. `.venv/bin/python -m leanecon.a1_runner` → offline diagnostics
6. With `MISTRAL_API_KEY`: `.venv/bin/python -m leanecon.a1_runner --live` → criteria 4–6

## Boundaries respected

- Provider egress only through `leanecon/adapters/mistral.py` (architecture tests enforce: no HTTP client imports outside adapters, no vendor model ids or credential names in core).
- No v3 implementation copied; `LeanEcon/A1.lean` is a new kernel-probe module with no economics content (Core is Gate 6).
- Live payloads were synthetic, PUBLIC-classified, and policy-checked; secrets redacted from all committed evidence (secret-pattern scan clean).

**Attribution:** Prepared by Hermes Agent (Nous Research) under direction of the CTO (@Bonorinoa), who remains the sole semantic approver.
