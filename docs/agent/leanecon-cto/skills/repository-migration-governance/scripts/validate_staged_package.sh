#!/usr/bin/env bash
set -euo pipefail

# Validate a staged documentation-only package without reading credential files.
# Usage: ./scripts/validate_staged_package.sh [expected_count] [prefix ...]
expected_count="${1:-18}"
shift || true
prefixes=("docs/gate3/" "references/gate3/")
if (( $# > 0 )); then
  prefixes=("$@")
fi

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

mapfile -t staged < <(git diff --cached --name-only)
mapfile -t unstaged < <(git diff --name-only)
(( ${#staged[@]} == expected_count )) || fail "expected ${expected_count} staged paths, found ${#staged[@]}"
(( ${#unstaged[@]} == 0 )) || fail "unstaged amendments exist"

for path in "${staged[@]}"; do
  allowed=0
  for prefix in "${prefixes[@]}"; do
    [[ "$path" == "$prefix"* ]] && allowed=1
  done
  (( allowed == 1 )) || fail "path outside allowed scope: $path"
done

if git diff --cached --check; then :; else fail "staged whitespace errors"; fi
if git diff --cached --binary | grep -Eiq 'GITHUB_TOKEN|ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|x-access-token:[^[:space:]]+|-----BEGIN (RSA|OPENSSH|EC|DSA|PRIVATE) KEY-----'; then
  fail "credential-like pattern found in staged diff"
fi

if [[ -f references/gate3/ei_schema_draft.json ]]; then
  python3 -m json.tool references/gate3/ei_schema_draft.json >/dev/null
fi

if git diff --cached --name-only | grep -E '(^|/)(src|leanecon_core|lean_workspace)/|\.py$|\.lean$' >/dev/null; then
  fail "implementation-like path entered documentation package"
fi

printf 'staged-files: %d\n' "${#staged[@]}"
printf 'scope: valid\nvalidation: passed\n'
