#!/bin/bash
# A1 criteria 1/2: pinned Lean/Mathlib workspace build.
#
# Reproducible from a clean checkout:
#   cd lean_workspace && ../scripts/a1_lean_build.sh
#
# Requirements: elan + lake on PATH (toolchain pinned by lean-toolchain),
# network access to GitHub (mathlib v4.32.2 and its dependencies).
# Expected: lake-update-exit=0, cache-get-exit=0, build-exit=0, DONE.
set -x
export PATH="$HOME/.elan/bin:$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/../lean_workspace" || exit 1
echo "STEP=lake-update"; lake update 2>&1; echo "lake-update-exit=$?"
echo "STEP=cache-get"; lake exe cache get 2>&1; echo "cache-get-exit=$?"
echo "STEP=build"; lake build LeanEcon.A1 2>&1; echo "build-exit=$?"
echo "DONE"
