# v3.5 Phase 2 — L1 probe-repair diagnosis (2026-08-23)

Session detail for the class-directed repair lever. Authority chain:
experiment card `docs/v3.5/experiments/L1-probe-repair-card.md` →
DECISION_LOG 53 → commits `84bf361` (implementation) + `b78cf9c` (DL
entry) on `v35/intelligence-sprint`. Suite 250 green (239 → 250, 11 new
tests in `tests/test_probe_repair.py`).

## Why the lever exists (measured, Phase 1)

Baseline re-probe with the FIXED verifier (zero provider calls):
model drafts elaborate 4/8; failures exclusively `binder_annotation`×2
+ `syntax`×2. Artifact forensics: v4smk/v4h1 records show the real
probe ALREADY consumed the in-loop budget (3 audit-clean attempts,
probes all False) while the model received only raw stderr — no class,
no position guidance. The lever makes existing spend diagnostic; it
does not add attempts.

## Contract (each clause pinned by a test)

- `diagnose(fb)` returns None iff `static_problems` non-empty OR probe
  is not explicitly False; otherwise
  `DIRECTIVE_FOR_CLASS[classify_probe_failure(stderr)]` plus the
  verbatim `file.lean:L:C` position token when present.
- Directive table TOTAL over the classifier's 11 outputs. `sorry` and
  `clean_or_no_signal` are `""` keys handled by explicit branches — a
  probe failure with EMPTY stderr classifies `clean_or_no_signal` and
  must get the no-signal message, NOT the sorry message (the RED
  totality test caught exactly this conflation pre-commit).
- Runner/library BYTE-PARITY when history has no failed probe (parity
  tests compare `a3_runner._revision_feedback_block` vs
  `probe_repair.revision_feedback_block`); the runner delegates via
  `probe_diagnose(_feedback_as_dict(history[-1]))`.
- Budget: `MAX_REVISION_ATTEMPTS_UNCHANGED == revise_loop.
  MAX_REVISION_ATTEMPTS == 3`.

## Principled vs heuristic (card §mechanism)

Principled: deterministic classification + static Lean-fact directives
(e.g. `[Set α]` is invalid as an instance binder because `Set` is not a
typeclass). Heuristic: prompt wording/order. REJECTED: mechanical
binder rewriting (`[Set α] → …`) — changes binder semantics; sanitizer
scope remains P1/mechanical-P3 only.

## Errors caught during the phase (method lessons)

1. Missing `classify_probe_failure` import — Pyright flagged it AT
   WRITE TIME, I deferred the fix, then ran: 8 red. Fix flagged
   diagnostics before running anything.
2. A patch whose `old_string` was built from memory of a file written
   earlier (not re-read) matched the wrong site and deleted the
   `unknown_identifier` directive. Caught by re-reading the region
   immediately. Rule: read the region before every non-trivial patch,
   especially on files you authored earlier in the same session.
3. Totality hole (above). The RED totality test did its job.

## Pending

G2 optional live smoke — CTO-gated (Labs quota): one fresh claim via
the same-text/new-id technique (v4smk-B text), predictions committed
first; success = FORMALIZED ∧ fresh probe True within ≤3 attempts.

Attribution: Hermes Agent (Nous Research) under CTO direction.
