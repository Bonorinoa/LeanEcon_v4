# Approval-Gate Closure Pattern

## Purpose

Reusable procedure for closing a governed documentation/contract gate after iterative CTO review without accidentally broadening authorization or leaving contradictory status text.

## Closure mapping

When the CTO gives a blanket response such as “Y to all questions,” enumerate the questions first and map each one to a decision record. Preserve scope distinctions:

- lifecycle semantics approved does not authorize lifecycle implementation;
- a design direction approved does not freeze the schema;
- A1 diagnostics authorized does not authorize A3, Core, or production verification;
- a docs-only commit authorized does not authorize later implementation.

Record the mapping in both a decision log and a concise decisions-required table. Mark closed rows `LOCKED` or `AUTHORIZED`; mark deferred design explicitly rather than leaving it `OPEN`.

## Reconciliation pass

Search the entire package for stale status markers such as `OPEN`, `CONDITIONAL`, `awaiting`, `remains blocked`, and `Required`. Inspect every hit: some may be legitimate future-work language, but no current-state table should retain superseded duplicate rows. A repeated patch can leave a ghost row—for example, an old outbound-policy row surviving beside its newly locked replacement.

If targeted replacements fail twice or table edits begin duplicating rows, read the whole file and rewrite the enclosing table or file once. Do not keep applying stale exact-match patches.

## Validation pattern

For a staged docs-only package, verify:

1. `git diff --cached --check` passes.
2. JSON schemas parse with `python3 -m json.tool` (or an equivalent validator).
3. Every staged path is in the intended package prefixes and the expected file count matches.
4. `git diff --name-only` is empty, so no staged file has an unstaged amendment.
5. The staged binary diff is scanned for credential patterns without printing secrets.
6. No implementation directories or files entered the staged scope.

Use robust shell quoting. Nested single quotes in a `python3 -c` expression can turn a string literal such as `"valid"` into an identifier and produce `NameError: name 'valid' is not defined`. Prefer a temporary script, environment variables, or careful outer quoting.

## Evidence and stopping boundary

Report the exact staged file list, stat, validation results, and commit hash. Preserve attribution to the AI assistant while stating that the CTO remains semantic authority. After a docs-only commit, stop unless a separate approval explicitly authorizes the next implementation scope.

This pattern was derived from LeanEcon v4 Gate 3 closure; the names and paths are illustrative and should be adapted to the next governed migration gate.
