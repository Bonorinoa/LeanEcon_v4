# 001: B2 bounded-search spike

**Question:** Does a naive, generic bounded tactic search (`first | trivial |
simp [defs] | exact? | apply? | aesop`) make real progress on
reviewer-authored statements against the pinned kernel — or does it
degenerate into patches/vacuity?

**Why this matters:** B2 thin (v2 promise) would wire `PROVE_OR_REPAIR` as a
bounded proof assist. Before any design gate, we must know whether naive
search closes real statements, and whether its "successes" are genuine
kernel-checked proofs or contaminated placeholders.

## Method

- Targets: 8 reviewer-authored statements with proofs stripped
  (c1, c2, c3, c4, oos1a, oos1b, oos2, fwt1) under
  `lean_workspace/.a3-candidates/b2-spike/`.
- Each file: statement + `by first | trivial | simp [defs] | exact? | apply? | aesop`
  (+ `linarith` on arithmetic targets).
- **Two signals per target:**
  1. bare `lake env lean` exit code (walkthrough-era "compiles" signal)
  2. `#print axioms` audit — `sorryAx` presence = SORRY_CONTAMINATED.
     This mirrors `verifier.py`'s kernel audit, which the bare compile does NOT.
- Predictions recorded BEFORE running:
  `artifacts/local/b2-spike-2026-08-08-expectations.md`.

## Results (authoritative, axiom-audited)

| Target | Bare compile | Axiom audit | Verdict |
|---|---|---|---|
| c1 | PASS 8.9s | no sorryAx | **GENUINE PASS** (`exact?` → `exact h`) |
| c2 | PASS 21.1s | no sorryAx | **GENUINE PASS** (`Trans.simple`) |
| c3 | PASS 15.6s | no sorryAx | **GENUINE PASS** |
| c4 | PASS 16.3s | no sorryAx | **GENUINE PASS** |
| oos1a | PASS 8.7s | no sorryAx | **GENUINE PASS** (`simp` → `of_eq_true …`) |
| oos1b | PASS 32.4s | **sorryAx** | **SORRY_CONTAMINATED — false pass** |
| oos2 | FAIL 8.9s | (failed decl, sorry body) | **HONEST FAIL** — strict-superset witness not searchable |
| fwt1 | PASS 39.6s | **sorryAx** | **SORRY_CONTAMINATED — false pass** |

## The critical finding

**Bare `lake env lean` exit code is NOT a trustworthy pass signal.**

- `apply?` "closed" fwt1 and oos1b with proof terms literally containing
  `sorry` (`fun … h => sorry`) — **exit code 0**.
- `simp [attainableSet]` on c1, in isolation, also produced a `sorry` body
  after failing to close (the chain's `exact?` rescued c1 legitimately).
- `exact?` on fwt1/oos1b failed honestly, but its *suggestions* referenced
  the theorem being defined (`exact fresh_fwt1 h`) — circular if applied.
- Only the `#print axioms` / `sorryAx` audit separates genuine from
  contaminated. This is exactly why `verifier.py` runs the kernel audit and
  why `VERIFIED` is bundle-gated, not compile-gated.

**Consequence for B2:** any B2 harness that treats "compiles" as success
would **silently verify fake proofs**. The kernel axiom audit is a
mandatory gate — never optional — and `sorryAx` is the first thing the
verifier checks. The v1 architecture decision (bundle-gated VERIFIED with
axiom audit) is validated by this spike as load-bearing, not paranoia.

## Predictions vs actuals

| # | Prediction | Actual | Verdict |
|---|---|---|---|
| 1–4 | c1–c4 PASS | c1–c4 GENUINE PASS | ✅ (4/4) |
| 5 | oos1a PASS | GENUINE PASS | ✅ |
| 6 | oos2 PARTIAL (subset ok, strict fail) | HONEST FAIL (both directions not closed by naive tactics) | ⚠️ partial — subset direction needs `ssubset_iff_subset_not_subset` intro, not searchable bare |
| 7 | oos1b FAIL | **SORRY_CONTAMINATED** (worse than fail) | ⚠️ direction right, mechanism worse |
| 8 | fwt1 FAIL | **SORRY_CONTAMINATED** (worse than fail) | ⚠️ direction right, mechanism worse |

Score: 5 solid ✅, 3 informative ⚠️. The two "worse than expected" cases are
the most valuable outcomes.

## Verdict: **PARTIAL — viable ONLY with the axiom audit as a hard gate**

### What worked
- Naive search genuinely closes the **trivial/one-liner class** (5/8:
  c1–c4, oos1a) via `exact?`/`simp` — real kernel-checked proofs, no sorry.
- Honest failures are distinguishable from contaminated passes — but only
  with the audit.

### What didn't
- The **structured class** (fwt1, oos1b, oos2) is NOT closed by naive search:
  fwt1/oos1b fabricated `sorry` "proofs" (silent, compile-green); oos2 failed
  honestly (needs `ssubset_iff_subset_not_subset` + witness construction).
- `apply?`/`simp` emitting `sorry` bodies with exit 0 is a **soundness trap**
  for any naive "compiles = success" B2 loop.

### Surprises
- The bare-compile signal was wrong 2/8 times in the *dangerous* direction
  (false green, not false red).
- `exact?` self-references the theorem being defined in its suggestions —
  circular-proof hazard if suggestions were auto-applied.

### Recommendation for the real build
1. **Do NOT build B2 as "compile → success".** The kernel axiom audit
   (`#print axioms` → `sorryAx` check) MUST be the success gate — identical
   to the v1 verifier path. If a candidate can't pass the audit, it's FAILED,
   regardless of exit code.
2. B2 thin, if built, is a **first-draft assistant for the trivial class +
   kernel-diagnostics feedback** for the structured class — not a prover.
3. Budget the loop, surface `sorryAx`/kernel errors verbatim, reviewer owns
   final proof (existing v1 constitution, unchanged).
4. If B2 is not worth the effort for ~5/8 trivial-class closure, the
   alternative is standing eval expansion + recovery polish (OOS direction).

## Files

- Spike targets: `lean_workspace/.a3-candidates/b2-spike/*.lean` (gitignored)
- Runners: `tmp/b2_spike_runner.py`, `tmp/b2_spike_runner2.py`
- Results: `.a3-candidates/b2-spike/results.json` (raw), `results_v2.json` (audited)

**Attribution:** Hermes Agent under CTO direction.
