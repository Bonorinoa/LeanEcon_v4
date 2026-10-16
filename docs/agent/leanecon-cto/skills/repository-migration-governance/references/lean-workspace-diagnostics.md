# Lean Workspace Diagnostics (A1-style probes)

Field notes from probing a pinned Lean 4 + Mathlib workspace for health
diagnostics. Applies to any gate that must prove "the pinned workspace
builds and the toolchain responds" before formal work begins.

## Pin layout (verification-bundle identity)

- `lean-toolchain`: one line, e.g. `leanprover/lean4:v4.32.2`.
- `lakefile.lean` requires Mathlib by git tag:
  `require "leanprover-community" / "mathlib" @ git "v4.32.2"`.
- `lake-manifest.json` (commit it) locks every dependency to an exact
  revision: `inputRev` = the tag, `rev` = the sha. The workspace identity
  for the verification bundle = toolchain + Mathlib tag + manifest revs.

**Pin parsing pitfall:** extract the Mathlib tag with a regex —
`re.search(r'"mathlib"\s*@\s*git\s+"([^"]+)"', lakefile_text)`. Naive
`line.split("@")[-1]` returns `git "v4.32.2`, not the tag.

## Build sequence

```bash
export PATH="$HOME/.elan/bin:$PATH"   # elan is often not on PATH in fresh shells
lake update          # resolves manifest against the pins
lake exe cache get   # downloads prebuilt oleans
lake build <Target>  # e.g. a kernel-probe module
```

`lake exe cache get` is the difference between minutes and seconds: a
~3000-job Mathlib build completes in ~10s on a warm cache. First-time
fetch of the cache is several minutes — run it as a background process
with completion notification, and do other work meanwhile.

A "kernel probe" module is a tiny `.lean` file importing
`Mathlib.Data.Real.Basic` + `Mathlib.Tactic` with one trivial theorem
(`by simp`) — it proves the kernel checks declarations against the
pinned workspace without carrying any domain content.

## LSP probe: Content-Length framing is mandatory

`lean --server` rejects bare JSON-RPC with
`Watchdog error: Cannot read LSP request: Invalid header field`. The
initialize request must be LSP-framed:

```
Content-Length: <len(body)>\r\n\r\n{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"processId":null,"rootUri":null,"capabilities":{}}}
```

A healthy response contains `"capabilities"` on stdout, framed the same
way. The server exits non-zero when stdin closes ("Stream was closed") —
that stderr line after a successful initialize is normal, not a failure.
Per contract, the probe reports `HEALTHY` or explicitly `UNAVAILABLE`
with `LSP_UNAVAILABLE` — never silent fallback.

## Typed-failure probes

- Invalid input: write a broken snippet (e.g. `def broken : Nat := `) to a
  scratch file, run `lean <file>`; the probe is healthy iff the exit code
  is non-zero and the failure is recorded with a reason code
  (`LEAN_SYNTAX_ERROR`). An unexpected zero exit is itself a defect.
- Unpinned workspace (missing toolchain or lakefile pin) →
  `WORKSPACE_UNPINNED`, `UNAVAILABLE` — never a silent default.
- `sorry`/`admit` detection is a text scan on candidate sources
  (`SORRY_FOUND`); it supports the VERIFIED bar but is not a substitute
  for kernel checking.

## CI note

Workspace-dependent tests should skip gracefully when the toolchain or a
built workspace is absent (CI runners), while pure-logic tests (pin
parsing, sorry scan, policy) always run. Keep the probe's scratch
directory out of tracked paths and gitignore `.lake/`.
