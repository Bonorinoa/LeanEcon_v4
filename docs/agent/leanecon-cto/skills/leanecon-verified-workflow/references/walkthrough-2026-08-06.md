# Live walkthrough record — 2026-08-06 (Gate 5, first four canonical claims)

Context: claims c1–c4 approved as proposed by the CTO; live interpretation
and formalization (mistral-medium-3-5 / labs-leanstral-1-5); reviewer
identity "Bonorinoa". Result: all four claims VERIFIED with valid bundles;
trace replay green for all four.

## Formalizer (labs-leanstral-1-5) evaluation — per claim

| Claim | Statement compiles? | Substantive? | Finding |
|---|---|---|---|
| c1 budget expansion | yes | NO | Vacuous tautology: conclusion `budget_set ⊆ attainable_set` IS its own hypothesis; `preferences` param unused; mapping row cites a hypothesis absent from the statement |
| c2 preference transitivity | NO | NO | Invalid binder `[Set α]` ("type is not a class instance"); also vacuous (conclusion = `h_trans`) |
| c3 strictly increasing utility | — | NO | Proof body literally `sorry` (contract violation; kernel audit would catch `sorryAx`); missing the strict-monotonicity hypothesis (unprovable as stated) |
| c4 monotone order | yes | YES | Correct `∀ x y, x ≤ y → f x ≤ f y` statement with valid inline proof — only faithful one |

Systemic: mapping reports do not reliably use the canonical EI element ids
(`definition:<i>`, object ids as-is). Observed instead: definitions under
titles, objects as `object:u`/`object:x`. The strict completeness check
correctly surfaced these as gaps; reviewer gap-acks recorded the
non-compliance as an evaluation signal.

Verdict: the reviewer-in-the-loop design is load-bearing; do not trust
formalizer statements un-reviewed. Kernel + bundle remain the arbiters.

## Three product bugs the walkthrough surfaced (all fixed + regression-tested)

1. **`#print axioms` empty-format not parsed** — zero-axiom theorems print
   "'name' does not depend on any axioms", a different sentence; the parser
   missed it, so c1 (no axioms) FAILED with LEAN_SYNTAX_ERROR despite a
   successful compile.
2. **Bundle check 6 demanded an axiom record even for zero-axiom theorems**
   — fixed to pass vacuously when `used` is empty.
3. **Static sorry scan false-positived on a fixture comment** mentioning the
   word "sorry" (documenting the formalizer's placeholder) — fixed by
   stripping Lean comments before the scan; kernel audit stays authoritative.

## Two design hardenings

- `VERIFIED` state is gated on the BUNDLE VALIDATOR, not the verifier record
  (kernel-verified + invalid bundle => state FAILED, manifest rebuilt with
  `bundle_validation_failed`).
- Replay consistency rule: manifest.result must equal the verification
  record's outcome (VERIFIED additionally requires all 11 checks) — a FAILED
  bundle with all checks passing is a faithful record when the failure was
  audit-layer.

## Track B — formalizer improvement (implemented same session)

All findings above are now caught or surfaced EARLIER in the formalize step:

- **Prompt hardening** (`formalize_prompt`): explicit HARD rules — no `:=`
  proof body, no `[Set α]`-style invalid binders, no tautologies/vacuous
  theorems, every hypothesis must appear in the signature, every parameter
  used, mapping ids EXACTLY as given ("never 'object:u'").
- **Static validation** (`validate_statement_text`): sorry/admit/`:=` in the
  statement => hard `PROVIDER_INVALID_OUTPUT`; no formal artifact is written.
- **Compile probe** (`verifier.probe_statement_compiles`): runs the statement
  through `lake env lean` in the pinned workspace at formalize time;
  `statement_probe.{compiles,exit_code,stderr_tail}` recorded in the formal
  artifact and printed. Evaluation signal, NOT a blocker — a non-compiling
  statement is still reviewable; the kernel arbitrates at verify.
- **Vacuity heuristic** (`vacuity_warning`): flags conclusions that restate
  a hypothesis (normalized substring check). Warning only.
- **Gap classification** (`classify_gaps`): missing rows are labeled
  `id_scheme_deviation` (a row id like `object:u` covers canonical `u`) vs
  `genuinely_missing`; unmapped-status gaps are `unmapped_with_note`.
- **`formalize --force`**: re-formalization attempt on an already-FORMALIZED
  claim — new formal revision supersedes the old candidate
  (FORMALIZED -> FORMALIZED lifecycle edge). Use this instead of re-ingesting
  when the formalizer produced a bad statement.
- **Test pattern**: mocked runner tests autouse-patch
  `a3_runner.probe_statement_compiles` to a fast fake (real probe is a
  ~10–20 s Mathlib compile); the probe itself has a `@requires_workspace`
  real test (compile-ok statement => True; the walkthrough's `[Set α]`
  statement => False).

## Track B live verification (c1r2 run) — the decisive result

Same canonical text as c1, ingested under a new claim id (`c1r2`) to compare
the hardened pipeline without disturbing the VERIFIED c1 record. Fresh EI
reviewed and approved by the CTO, then formalized live with the hardened
prompt:

- Attempt 1: model output rejected — `statement carries a proof body
  ('... :=')` => `FAILED`/`PROVIDER_INVALID_OUTPUT`, no artifact written.
- Attempt 2 (retry, `FAILED -> FORMALIZED` edge): IDENTICAL rejection.

**Verdict: prompt hardening alone does NOT fix labs-leanstral's compliance.**
The model attaches `:=` proof bodies even against an explicit "NO `:=`"
rule (2/2). The new static validation is therefore load-bearing — it stops
non-compliant statements before they reach the store and the trace records
every rejection. Posture: the formalizer is a DRAFTING AID; the
reviewer-authored proof fixture is the load-bearing artifact. Do not loop
live retries after two identical rejections — record and move to
reviewer-authored input.

Also surfaced by the run: a rejected candidate writes no formal artifact, so
`cmd_formalize` must guard `formal_revs()[-1]` (IndexError) — fixed, keeps
the previous `formal_rev` reference, and the `FAILED -> FORMALIZED` retry
edge keeps recovery clean.

## Draft-schema exercises exercised live

- `none_noted` marker + mandatory `--acknowledge-none-noted` (none of the
  four live EIs hit it — all had real ambiguities).
- Nullable `review.reviewer`/`review.event_ref` while PENDING.

## Review flow notes

- Gap acknowledgments and axiom approvals are per-run reviewer records
  (`gap-ack`, `axiom-approve`), recorded under the reviewer identity.
- Zero-axiom claims (c1, c2) needed no axiom record; c3/c4 needed the
  Mathlib baseline `propext,Classical.choice,Quot.sound`.
- Revisions: `VERIFIED`/`REJECTED` are terminal; a changed claim re-enters
  via `ingest` (revision+1). `formalize --force` is the exception — it adds
  a formal revision without re-ingesting.
