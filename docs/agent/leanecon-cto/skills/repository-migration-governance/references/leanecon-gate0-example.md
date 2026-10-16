# Gate 0 Example: Evidence, Ledger, Freeze

This condensed pattern comes from a LeanEcon v3→v4 migration review.

## Baseline

Capture read-only:

- branch, HEAD, upstream divergence, tags, remotes;
- tracked and untracked counts;
- modified paths and generated paths;
- secret-risk filenames without opening secret contents.

Example baseline fields:

```text
branch=main
head=<commit>
upstream=<commit>
tags=[]
modified=.codebase-memory/*
untracked=.hermes/,tmp/
```

## Evidence register example

| ID | Claim | Source | Finding | Confidence |
|---|---|---|---|---|
| E1 | A supplied theorem stub bypasses statement generation | `src/formalizer/formalizer.py:<range>` | Stub is compiled directly and perfect faithfulness metadata is assigned | High |
| E2 | Runtime evaluation receives theorem stubs | `evals/local_gate.py:<range>` | Runner reads and passes `claim["theorem_stub"]` | High |
| E3 | Policy is concentrated in a prover execution module | `src/prover/execution.py` | Large module mixes proving, recovery, retrieval, fallbacks, and events | High |
| E4 | State transitions can be hidden | `docs/PROVER_STATE_MACHINE.md:<range>` | Invalid edges may be suppressed; lifecycle has rough edges | High |

The exact paths and line ranges must be refreshed against the current commit; never reuse these as proof without checking.

## Ledger example

```csv
source_artifact,source_commit,artifact_class,disposition,rationale,v4_destination,reviewer,required_tests,contamination_risk
src/prover/execution.py,<sha>,python_service,rebuild,"Mixed policy and claim-specific recovery",src/leanecon/orchestrator.py,CTO+agent,state-boundary tests,high
lean_workspace/LeanEcon/Preamble/,<sha>,lean_module,rebuild,"First-principles Core",leanecon_core/,CTO,Lean build + axiom audit,high
benchmark_baselines/,<sha>,benchmark,historical-discard,"Historical evidence only",--,CTO,gold isolation,high
```

## Freeze checklist

1. Review every modified/untracked path with the owner.
2. Decide whether generated graph/index state is preserved, archived, or restored.
3. Apply only approved documentation changes.
4. Run agreed verification and record actual results.
5. Review staged diff.
6. Create one freeze commit.
7. Annotate a freeze tag pointing at that exact commit.
8. Verify clean status, tag, branch tips, and remote state.
9. Archive/protect only after explicit approval.

Never silently run `git reset`, `git clean`, branch deletion, or history rewrite as part of freezing.