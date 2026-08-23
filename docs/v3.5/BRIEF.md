# v3.5 exploration brief — model, literature, opinion, fidelity

**Status:** EXPLORATION. Not an implementation authorization.
**Date:** 2026-08-23. Continues @session:leanecon-cto/20260822_154013_ff5ec2
  (that session verified v3.0.0, proposed Intelligence → Agentic, then
  died on empty replies — nothing in the repo broke).
**Base:** `main` @ `12e267c` = tag `v3.0.0`. Suite 229.
**Authority this does not override:** DECISION_LOG 1–49, reviewer
policy, kernel axiom audit, bundle 12-check, sealed-eval protocol.

Companion: `docs/v3.5/state-machine-flow.html` (interactive I/O map).

---

## 0. Session recovery

Last session's roadmap still stands in outline: **v3.5 Intelligence
then v4 Agentic**. The follow-up questions in this brief amend three
pieces of that outline:

| Last session said | This brief amends |
|---|---|
| L2 = observed-failure taxonomy from v3h/v4h1 logs | Drop. Taxonomy must name properties of the *intended artifact*, not the last five stderr strings. |
| Keep leanstral because it is free | Keep the *pin* for now, but stop treating it as the right tool for statement+mapping. The free Labs endpoint is a supply fact, not a task fit. |
| Auto-review as A3 in the Agentic release | Pull a *consultative* `opinion` side-door into v3.5 exploration. Distinct from the existing AI-reviewer that can already emit `ACCEPTED`. |

---

## 1. Keep leanstral, or replace it?

**Recommendation: keep the pin. Do not swap. Change the *job
description* we give it, and run one measured A/B before anyone
touches `MVP_MODEL_MAP`.**

### What Leanstral actually is

Leanstral 1.5 is a 119B-MoE / 6.5B-active Apache-2.0 *proof agent*,
trained in two RL environments: (1) a multiturn Lean compiler loop
that is given a **theorem statement** and must prove or disprove it,
(2) a filesystem code-agent that edits files and talks to the Lean
language server.[1][2] Mistral's own getting-started path is Vibe +
optional `lean-lsp-mcp`.[1][3] The advertised scores (miniF2F
saturated, 587/672 PutnamBench, FATE-H 87) are **proof-generation**
scores on already-formal statements.[1]

Your reading is correct: the model is built to live next to Lean
tooling. We do not provide that tooling. Our `formalize` call is a
single JSON request: *accepted EI → `{statement, target_theorem,
mapping_report}`*. No LSP, no goal state, no file edits, no
multi-million-token repair. We are using a proving agent as a
one-shot translator, then asking why the translation does not
elaborate.

That is a **task mismatch**, not (yet) evidence the weights are
bad at economics.

### Free alternatives, honestly scored

| Candidate | Hosted & free? | Runnable here? | Task it is trained for | Fit for *our* formalize |
|---|---|---|---|---|
| **labs-leanstral-1-5** (current pin) | Yes (Labs, ~30d deprecation, shared rate pool) | Already wired | Prove / repair a given Lean statement, tool-using | Wrong job, right price |
| Self-host Leanstral 119B-A6B | Weights free; compute not | vLLM `--tensor-parallel-size 4`[2] | Same as above | Same mismatch, plus GPUs we do not have |
| Kimina-Prover 72B / distill 0.6B[9][10] | Weights free; no free API | 72B needs 8-GPU vLLM; 0.6B is local-feasible | Prove a *given* miniF2F-style statement | Wrong job. 0.6B will not emit D1 mapping reports. |
| Goedel-Prover / V2 8B–32B[4][5] | Weights free; no free API | 8B maybe local | Whole-proof generation | Wrong job. Their *formalizers* (separate models) are the interesting part. |
| Pythagoras-Prover 4B/32B[6] | Weights (paper, Jun 2026); no free API | 4B plausible | Prove given statements; ALF mutates statements | Wrong job. Steal ALF's *idea*, not the weights. |
| mistral-medium-3.5 (already paid) | No — $1.50 / $7.50 per M | Already wired for interpret | General instruction + JSON | **Right job shape** for statement+mapping. Not free. |
| mistral-small-4 | No — $0.15 / $0.60 per M | Adapter already knows it | General, cheaper | Possible cheap A/B, not free |
| llama-8B / phi-4 (local, already downloaded) | Yes | Local only | General / critic | Standing fallback for interpret/critic. Not a formalizer without sealed evidence. |

There is **no free hosted model that is both more reliable than
Labs leanstral and trained to emit our mapping-report contract**.
"Replace leanstral with Kimina because Putnam is higher" would
optimize the wrong leaderboard.

### What to do instead (v3.5, still no swap)

1. **Keep `Capability.FORMALIZE → labs-leanstral-1-5`.** It is the
   only $0 Lean-aware endpoint. Reliability risk is Labs deprecation
   and the shared free pool, not tomorrow's invoice.
2. **Stop expecting LSP-shaped behavior from a JSON call.** Probe
   stderr in `revise_loop` is the only Lean signal we actually give
   it. That is a thin slice of the environment it was trained in.
3. **Measure the task, not the brand.** On *dev* fixtures only
   (spent holdouts stay spent): one A/B of leanstral vs
   medium-3.5 vs small-4 on the *same* formalize prompt, scored by
   the existing fixture scorer (`first_try_valid`, `probe_compiles`,
   `vacuity_flag`, D1). Prediction file first. No `MVP_MODEL_MAP`
   edit until that card exists and you say go.
4. **Reserve leanstral for a later proving/repair path** — the
   Agentic release — *if* we add interactive Lean (`lean-lsp-mcp`
   or our own `lake env lean` tool). That is when the training
   actually matches the interface. Not a v3.5 ship requirement.

Krakauer: do not add a second formalizer to look busy. One pin,
one measured comparison, one decision.

---

## 2. What changed in the literature since we started

LeanEcon v4's clean-room start is 2026-08-04. The relevant field
moved earlier in 2026 and kept moving while we built the machine.
Three shifts matter; the leaderboard numbers do not.

### Shift 1 — statement formalization and proof generation split

Goedel-Prover trained **two statement formalizers** (Lean Workbook
pairs; 170k Claude-formalized statements), then filtered with a
compiler check (CC: signature compiles with `:= by sorry`) and a
**faithfulness/completeness** judge (FC).[4][5] Only then did they
train a prover. Pythagoras-Prover (June 2026) still autoformalises
with Goedel-Autoformaliser-v2 before proving, and introduces
Augmented Lean Formalisation: mutate the *statement* so models
cannot overfit surface form.[6]

We already have the split in architecture (interpret → formalize
→ verify). We have been scoring it as if it were one "draft"
number. The literature says: **CC and FC are different objects**.
That is the same distinction you are asking for in the taxonomy
(§4).

### Shift 2 — verifier-in-the-loop, staged

M2F (Feb 2026) is an agentic textbook-scale formalizer with two
stages: (1) split the source, repair declaration *skeletons* until
the project compiles with proof placeholders, (2) close holes under
**fixed signatures** with goal-conditioned edits. Edits commit only
when toolchain feedback improves.[8] Numina-Lean-Agent (Jan 2026)
drops the specialised prover entirely: a general coding agent +
Lean MCP solves Putnam 2025 12/12 and formalises Brascamp–Lieb
with a mathematician in the loop.[7] `lean-lsp-mcp` itself shipped
v0.30.0 on 2026-08-19 and is now the default Lean tool surface
those agents assume.[3]

Steal the *staging*, not the agents. Stage 1 is our Intelligence
release (signatures that elaborate). Stage 2 is our Agentic
release (repair / prove under a frozen statement). M2F's "do not
change the signature while proving" is already our
`-- GAP:` / skeleton contract.

### Shift 3 — compute-efficient open provers exist, and they still
do not solve *our* problem

Pythagoras-Prover-4B reports 86.1% MiniF2F pass@32, beating a
671B DeepSeek-Prover-V2, and their 32B hits 93.0%.[6] Kimina
distills a 72B RL prover down to 0.6B at 71% pass@32.[9][10]
These are real. They are also **proof models on contest
statements**, not economic-claim autoformalizers, and none of
them is a free hosted API. Useful later, if we ever have a
library of elaborating signatures and want a local proving
assist behind the axiom audit. Not a v3.5 lever.

### What we should actually learn before locking the sprint

- Separate **statement fidelity** from **proof search**. Do not
  pick a model off Putnam/miniF2F.
- Treat compile-of-signature as stage 1 (M2F / Goedel CC). That
  is the probe-in-loop work, framed as a property of the artifact
  (§4), not as "the five stderr classes from v4h1."
- Treat interactive Lean (MCP / lake) as stage 2. That is Agentic.
  Building `lean-lsp-mcp` into v3.5 would be architecture theatre:
  we do not yet have statements worth proving.
- Steal Goedel's FC idea as a *reviewer-facing* check (does this
  Lean statement preserve the claim?), not as a silent model
  self-grade. That is the `opinion` feature (§3).

---

## 3. `opinion` — "get my opinion" / auto-review

We already have an authorized AI reviewer. `review --reviewer hermes`
can emit `ACCEPTED` / `REJECTED` / gap-ack / axiom-approve
(`docs/gate3/08-reviewer-policy.md`, DECISION_LOG 31). That path
**changes state**. It is how v2p1-A was approved
(`reviewer=hermes`, `reviewer_kind=ai`). It does not help you
*compare* a judgment, and it does not help a curious caller who
is not willing to hand the machine the gavel.

**Proposal: a consultative side-door that never writes a
lifecycle transition.**

### Shape

```
opinion [--claim-id ID] [--on ei|formal|bundle] [--reviewer ID]
```

- Legal from `REVIEW_REQUIRED`, `ACCEPTED`, `FORMALIZED`,
  `FAILED`, `VERIFIED`. Refused from `DRAFT` (nothing to opine
  on) and `REJECTED` (terminal).
- Writes `artifacts/local/a3/opinions/<claim>/rev-N.json`.
  Append-only, digest-anchored, like every other artifact.
- Emits `EVENT_DIAGNOSTIC_RESULT` (already a legal event type),
  **not** `CLAIM_STATE_CHANGED`. Replay stays honest without a
  new `TRANSITIONS` edge.
- Capability: `SEMANTIC_TRIAGE` / `DIAGNOSTIC_PROBE` (already
  mapped to medium-3.5). The interpret/formalize models do not
  grade their own homework.

### Schema (latent object, not a verdict)

```text
Opinion v0 (proposed)
  schema_version: "0.1.0"
  claim_id, subject: ei | formal | bundle
  subject_digest          # the artifact being opined on
  reviewer, reviewer_kind # identity of the *opinion*, not an approval
  recommended_decision    # APPROVE | REVISE | REJECT  (advice)
  fidelity:               # properties of §4, each {status, note}
    surface_legality
    elaboration
    contract
    substance
    semantic_fidelity
    proof_adequacy        # only when subject=bundle
  ambiguities_raised[]    # issue + alternatives (same shape as EI)
  compare_with            # optional: prior human notes, or null
  confidence              # process confidence, not truth
  provenance              # model, request_id
```

`recommended_decision` is **not** `review.decision`. A program
can read it; a human can disagree out loud; the claim stays
where it was.

### Why this attacks the bottleneck without moving meaning

- You keep the gavel. The machine produces a structured second
  reading you can diff against your own.
- A caller who is not you can ask "what would you say?" without
  us pretending that is an acceptance.
- It is the honest version of Goedel's FC test: a judge, labeled
  as a judge, never silently folding into `ACCEPTED`.
- Implementation cost is a new subcommand + schema + tests. No
  lifecycle change. F1 rule is vacuously satisfied.

### Deliberately not

- Not a second path to `ACCEPTED`. If you want the machine to
  approve, use the existing `review --reviewer-kind ai`.
- Not a critic inside `revise_loop`. Loop feedback stays
  kernel/static. Mixing "I think this is inverted" into the
  repair prompt is how we overfit to the last inversion we saw.
- Not a product UI.

**Gate:** design-only until you say go. Empty clarify ≠ consent
to add the subcommand.

---

## 4. The latent object (not a failure taxonomy)

You are right, and last session's L2 was the wrong shape.

A catalog of observed rejects (`:=` body, sorry, D1, D4, unbound
`ι`, missing `Fintype`, …) is a **measurement history**. Treating
it as the ontology does three bad things: it overfits the next
lever to the last stderr, it forces every new error into a new
bucket (label drift), and it hides the thing we actually want.

The thing we want is a **faithful verified rendering** of a
reviewed economic claim. That object has six properties. Observed
failures are *violations* of one of them.

| Property | Question | Who can decide it | Machine instrument today |
|---|---|---|---|
| **P1 Surface legality** | Is this even Lean we will look at? | Machine | `validate_statement_text` (sorry/admit, theorem-body `:=`) |
| **P2 Elaboration** | Does the signature type-check in the pinned workspace? | Machine | `probe_statement_compiles` / `ProbeResult` |
| **P3 Contract** | Does it honour D1/D4 and map every material EI element? | Machine | `validate_mapping_report`, namespace scanner |
| **P4 Substance** | Is the conclusion the claim's conclusion, and non-vacuous? | Machine approximates; reviewer owns | `vacuity_warning`; inversion is still heuristic |
| **P5 Semantic fidelity** | Does this Lean statement *mean* the English claim? | Reviewer only | none (this is what `opinion` approximates, never certifies) |
| **P6 Proof adequacy** | Does a sorry-free kernel derivation of *this* statement exist? | Kernel | `#print axioms` / `sorryAx` + bundle 12-check |

`draft_complete` as currently defined is **P1 ∧ P2 ∧ P3 ∧ ¬vacuous**.
That is a property of the formal artifact, not a failure class.
v4h1 going 5/5 audit-clean and 0/5 probe is "P1+P3 held, P2
failed." The next lever targets **P2**, whatever stderr the next
sealed set happens to print.

New errors get labeled by which P they violate. If they do not
fit, the property list is wrong — we amend the *object*, we do
not grow a zoo.

This is also how we keep mechanical repair honest. Sprint-1's
sanitizer is allowed to touch P1 and the mechanical subset of
P3 (FQ-id rewrite, namespace re-home). It is not allowed to
invent a conclusion (P4/P5). Probe-in-loop may rewrite toward
P2; it may not "fix" P5.

---

## 5. Intelligence → Agentic (kept, restated)

The sequence is right. Restated in the language of §4:

- **v3.5 Intelligence** — raise P1–P3 (and the cheap slice of
  P4) on a fresh sealed holdout, on the machine we already have.
  No new states. No MCP. No proving.
- **v4 Agentic** — only after P2 is no longer the binding
  constraint: tool-using repair, optional `lean-lsp-mcp`,
  multi-claim graphs, model-selection harness, consultative
  opinion becoming a habit. Still no unattended `VERIFIED`.

### v3.5 levers, revised

| # | Lever | Property | Notes |
|---|---|---|---|
| L1 | Probe-in-loop repair | P2 | Same pattern as sprint-1, pointed at elaboration. Mechanical: structured extract of probe stderr. Heuristic: repair prompt. Keep them named. |
| L2 | **Fidelity properties doc** (this §4) | — | Replaces the observed-error taxonomy. Every lever cites a P. |
| L3 | Formalize-model A/B on *dev* fixtures | P1–P4 | leanstral vs medium-3.5 vs small-4. No pin change without the card. |
| L4 | `opinion` side-door (if you opt in) | P5 approximation | Consultative only. §3. |
| L5 | README/release-doc refresh | hygiene | Still says v2.0.0 Phoenix. Ride along. |
| L6 | Rate-limit dry-run before any sealed day | ops | Labs free pool is the real ceiling. |

**Earn rule, unchanged:** fresh sealed holdout, prediction-first,
draft_complete ≥ 60% *or* a written miss that names the next
property. Spent sets stay spent.

**Standing non-claims:** no unattended VERIFIED, no Putnam
cosplay, no weakening EI/bundle/Core/reviewer policy, no
`lean-lsp-mcp` as a v3.5 ship requirement.

---

## 6. What I need from you

This file plus the flow HTML are the deliverable. Nothing is
implemented. Three decisions, when you have them:

1. **L1 (P2 probe-in-loop)** — draft the experiment card next,
   or wait for the model A/B (L3) first?
2. **`opinion` (L4)** — explore further / approve a design pass /
   park until Agentic?
3. **Formalize pin** — accept "keep leanstral, measure medium on
   dev, no swap without sealed evidence"?

Empty clarify ≠ consent. Answer in chat at your pace.

**Attribution:** Hermes Agent (Nous Research) under CTO direction.
CTO remains the accountable semantic authority and sole semantic
approver.

## Sources

[1] https://mistral.ai/news/leanstral-1-5 — Leanstral 1.5: Proof Abundance for All (Mistral, 2026-07-02)
[2] https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B — Leanstral-1.5-119B-A6B model card
[3] https://github.com/oOo0oOo/lean-lsp-mcp — lean-lsp-mcp (Dressler; v0.30.0 2026-08-19)
[4] https://goedel-lm.github.io — Goedel-Prover project page
[5] https://arxiv.org/abs/2502.07640 — Goedel-Prover (Lin et al., 2025)
[6] https://arxiv.org/abs/2606.12594 — Pythagoras-Prover (Ong et al., 2026-06)
[7] https://arxiv.org/abs/2601.14027 — Numina-Lean-Agent (Liu et al., 2026-01)
[8] https://arxiv.org/abs/2602.17016 — M2F: Math-to-Formal at scale (Wang et al., 2026-02)
[9] https://github.com/MoonshotAI/Kimina-Prover-Preview — Kimina-Prover Preview (Moonshot / AI-MO)
[10] https://huggingface.co/AI-MO/Kimina-Prover-72B — Kimina-Prover-72B weights
