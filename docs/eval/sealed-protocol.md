# Sealed formalizer evaluation protocol

**Status:** measurement plumbing on the v3 development line. Not a
product version. Not a new held-out set. Not a tag.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.

## Purpose

This protocol distinguishes three facts that must never be collapsed:

1. **Draft hygiene** — `leanecon.eval_formalizer` checks structure,
   elaboration signal, vacuity, and audit contamination. CI runs this
   on committed fixtures with `provider_calls == 0`.
2. **Kernel verification** — Lean plus the 12-item bundle validator
   decides whether a submitted proof is acceptable. Compile exit 0 is
   not a pass (B2).
3. **Semantic fidelity** — independent reviewers decide whether a
   formal statement preserves the English claim's material meaning.
   `leanecon.eval_protocol` records those judgments; it does not
   infer them.

Neither compilation nor a reviewer-authored `VERIFIED` proof is
evidence that a model formalized the claim faithfully.

## Split discipline

Development cases may be committed and used for prompt/model
iteration (`tests/fixtures/eval/formalizer/`).

Held-out cases are authored and retained by an evaluation owner.
The owner uses `leanecon.eval_protocol.seal_manifest` to commit only
`case_id` and a SHA-256 digest of each claim. Claim text, intended
Lean, and proof patterns must remain out of the runtime tree, CI
fixtures, prompts, and release packets.

The `v3h` and `v3h2` sets are **spent**. They are historical evidence
only and must not be rerun to claim progress. See
`docs/eval/v3-claim-split.md`.

Protocol id: `formalizer-sealed-1`. This is the program for the
*next* CTO-approved held-out set. It is not `v4` and does not
authorize a v4 tag.

## Run procedure

1. Freeze development prompts/model/configuration and record their
   digests.
2. Write predictions (`artifacts/local/<run>-expectations.md`)
   **before** any live run.
3. An evaluation owner creates a fresh held-out set and a text-free
   manifest. Freshness: no verbatim overlap with existing
   `source_text`.
4. Run every held-out claim **once** with the bounded formalization
   loop via `.venv/bin/python scripts_local/a3_run.py`. Preserve raw
   artifacts outside the repository.
5. Score draft hygiene with `scripts/eval_formalizer.py`; the scorer
   must make zero provider calls.
6. Give each English claim and its formal artifact to two independent
   semantic reviewers. They record `faithful`, `material_deviation`,
   or `insufficient_evidence`, with a rationale and formal-artifact
   digest.
7. Run `scripts/eval_semantic_reviews.py` over the sealed manifest
   and review directory. Publish counts, including disagreements.
   Do not invent an aggregate quality score that hides disagreement.

## Release evidence

For a future model-quality claim, publish at minimum: the sealed
manifest, the deterministic draft score report, the semantic-review
report, the number of cases with two reviews, disagreement counts,
model/configuration digest, and an explicit statement that semantic
fidelity remains reviewer-judged.

No release is earned by this protocol alone. It adds a reproducible
measurement gate. The kernel and bundle audit remain the sole
`VERIFIED` pass gate. The 60–70% draft-complete target stays
**MISSED** (2/8 = 25% on spent splits) until a new frozen set is
scored under this protocol.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
