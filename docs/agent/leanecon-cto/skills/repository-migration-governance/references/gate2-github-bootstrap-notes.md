# Gate 2 GitHub bootstrap — session notes (LeanEcon v4, 2026-08-04)

Session-specific detail behind the "Successor-repository bootstrap (Gate 2)
pitfalls" section in SKILL.md. Reuse the patterns; do not treat the specific
transcript as a template.

## What happened

- Goal: create `Bonorinoa/LeanEcon_v4` (public, Apache-2.0, clean-room scaffold,
  CODEOWNERS with two authorized contributors, protected `main`, one CI check).
- The stored `GITHUB_TOKEN` in `~/.hermes/.env` returned HTTP 401
  (`Bad credentials`) on `GET /api/github.com/user` even after the user
  "updated" it — the token was 40 chars with no `ghp_` prefix (classic PAT
  shape) and was rejected every time. A 401 is not propagation lag.
- No `gh` CLI installed → curl + token path only.
- Attempts to capture a fresh token via a hidden prompt failed:
  - `read -r -s` inside `terminal(background=true, pty=true)` hung with
    `zsh:read:1: -p: no coprocess` and later never received input even with
    the terminal pane focused (`process poll` showed prompt still waiting).
  - `python3 getpass` in a PTY failed with `termios.error: (19, ...)` /
    `EOFError` (no controllable echo, no real TTY).
- User confirmed by eye; `process poll` showed the prompt never received
  input. Lesson: trust the tool state, not the claim — re-verify with the API.

## Working patterns

1. **Verify-before-store**: never write a token to `~/.hermes/.env` unless
   `GET /user` returns 200 with the expected `login`. Sanity-check length and
   prefix (`ghp_` / `github_pat_` for fine-grained; 40-hex for classic).
2. **User-side secure self-check**: write a small script that reads the token,
   validates it, and prints ONLY sanitized metadata (http_status, login,
   token length, sha256 prefix). The user runs it in their own terminal and
   pastes the output back. Token never crosses chat or tool output.
   See `templates/token_selfcheck.py` for the exact script.
3. **Best fix for the user**: `brew install gh && gh auth login` (browser
   flow) — credential lands in macOS Keychain, not a plaintext env file, and
   `gh` handles repo/API calls with correct scopes (`repo`, `workflow`).

## Governance facts discovered

- CODEOWNERS with the CTO's account twice is NOT two authorized contributors.
- An AI assistant has no separate GitHub identity; it pushes/reviews through
  the CTO's token. A bot account (`leanecon-bot` style) must be created by a
  human, then added as a collaborator, before it can be a real second
  CODEOWNER / approving reviewer.
- With one account, `required_approving_review_count=1` +
  `dismiss_stale_reviews` + `require_code_owner_reviews` is symbolic:
  self-approval can only be blocked when author and approver differ.

## Interim posture when the second account is missing

Create the repo with `@<cto>` as the only CODEOWNER, document the
single-owner interim state in the gate report, and record
"second distinct GitHub account must be added as collaborator + listed in
CODEOWNERS" as an explicit open gate condition before any implementation
merge. Do not fake a second identity to satisfy the letter of the rule.
