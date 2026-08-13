# Clean-clone reproduction — v1.0.0 (2026-08-08)

**Status:** ✅ COMPLETE — full reproduction green (P1 from `docs/audit/post-v1-audit.md`)
**Clone:** `/tmp/leanecon-v1-clean` (11 GB with build artifacts)
**Source:** `main @ 49d7d7c` (v1.0.0 + PR #14 bot-activation)
**Runner:** `scripts_local/clean_clone_check.sh` (P5 recipe)
**Predictions recorded BEFORE the run:** `artifacts/local/clean-clone-2026-08-08-expectations.md`

## Predictions vs actuals (7/7)

| # | Prediction | Confidence | Actual | Verdict |
|---|---|---|---|---|
| 1 | Fresh clone at 49d7d7c | 0.95 | `49d7d7c Merge pull request #14…` | ✅ |
| 2 | `lake build LeanEcon.Core.*` OK | 0.9 | `lake build OK` | ✅ |
| 3 | `lake build Mathlib -- -j4` OK, no OOM | 0.75 | `lake build OK` (8174 modules, `-j4` tail) | ✅ |
| 4 | `uv venv --python 3.11` + install OK | 0.95 | clean (step 3/4 no error) | ✅ |
| 5 | pytest 168 green in clean clone | 0.85 | **168 passed in 32.78s** | ✅ |
| 6 | Wall time < 90 min | 0.7 | **~60 min** (15:39:07 → 16:39:13) | ✅ |
| 7 | No `12_core_pin` / D2 surprises | 0.9 | bundle tests green incl. `12_core_pin` | ✅ |

**Score: 7/7 ✅** (baseline: fwt1 7/7, Gate 7 9/9, OOS 12✅/3⚠️)

## What this proves

- v1.0.0 is **reproducible from a cold start**: fresh clone → mathlib from
  source → venv → pytest green, no hidden local state.
- The pinned workspace identity (Lean v4.32.2 + Mathlib v4.32.2) and the
  D2/Core contracts hold in a clean environment.
- The `clean_clone_check.sh` recipe is still valid post-ship (P5 lesson:
  python-3.11 venv baseline, `-j4` memory cap, full Mathlib for the probe).
- Closes the **P1 reproducibility item** from `docs/audit/post-v1-audit.md`
  (deferred at v1.0.0 exit).

## Cost / notes

- ~60 min wall, dominated by mathlib-from-source (no `lake exe cache` on
  this machine). Memory-capped tail (`-j4`) avoided OOM on 24 GB RAM.
- Disk: ~11 GB for the clean clone with build artifacts (gitignored; safe
  to delete when done: `rm -rf /tmp/leanecon-v1-clean`).
- Not predicted (informational): exact mathlib compile time, disk usage.

**Attribution:** Hermes Agent under CTO direction.
