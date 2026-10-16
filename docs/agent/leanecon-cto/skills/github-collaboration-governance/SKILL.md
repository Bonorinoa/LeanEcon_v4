---
name: github-collaboration-governance
description: "Use for GitHub ownership and review governance."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [GitHub, governance, CODEOWNERS, branch-protection, collaborators, bots]
    related_skills: [github-auth, github-repo-management, github-code-review]
---

# GitHub Collaboration Governance

Use this skill when bootstrapping a repository or changing its ownership, review, CODEOWNERS, collaborator, or branch-protection model.

## Core rule

Separate the GitHub account that authors or pushes a change from the account that approves it. An AI assistant operating through a user's credentials is not a second GitHub identity and must not be represented as an independent reviewer or CODEOWNER. If a second non-human principal is genuinely required, the repository owner must create and control a dedicated bot or machine-user account first.

## Procedure

1. Identify the authenticated GitHub login with a real API call (`gh api user --jq '.login'` or an equivalent authenticated request). Never infer it from local Git configuration.
2. Collect the exact usernames of the authorized human contributors and, if applicable, the pre-existing bot account. Do not invent placeholders in a production CODEOWNERS file.
3. Keep CODEOWNERS minimal and exact. If the governance requirement is two owners, verify the file contains precisely those two owner lines and no assistant pseudonym, email, or duplicate username.
4. Create and configure repository governance only after the initial branch exists. Require pull requests, at least one approving review, required CI status checks, and disable self-approval where the GitHub setting supports it.
5. Verify effective protection through GitHub's API, not merely through local files or command success. Check required review count, required status contexts, dismissal/stale-review behavior as configured, admin enforcement, and restrictions or bypass rules.
6. Treat a bot owner as automation authority, not semantic authority. Human review remains necessary for economics, formal semantics, security, and release decisions.
7. Add an explicit attribution section to the README when AI-assisted implementation is part of the project history. State that work is performed by an AI assistant under the CTO's direction, that pushes use the CTO's account unless a bot account is explicitly configured, and that the CTO or authorized human remains the semantic reviewer.

## Secure authentication handoff

Prefer `gh auth login` with browser authentication on a desktop. Do not ask the user to paste a token into chat. Do not launch a hidden-input token prompt in a detached or background terminal: such prompts may not have interactive stdin and can hang indefinitely or fail without making the input path clear. If a token must be entered, use a clearly visible foreground terminal with a confirmed interactive TTY, validate it against `/user`, never print it, and avoid persisting it in plaintext when the platform credential store is available.

## Pitfalls

- A local commit author is not a GitHub collaborator or reviewer.
- Listing the same account twice in CODEOWNERS does not create two-person review.
- Under a Hermes profile, the token Hermes loads lives in `$HERMES_HOME/.env`
  (e.g. `~/.hermes/profiles/<profile>/.env`), NOT `~/.hermes/.env`. The default
  home `.env` may hold a stale token: every API call then returns
  `401 Bad credentials` while the user's real token is fine. Diagnose by
  reading `HERMES_HOME`, hashing each candidate `GITHUB_TOKEN`, and testing
  each against `GET /user` until one returns 200. Never print token values.
- Do not infer the GitHub login from `git config user.email`; resolve it via
  `GET /user` (`login` field).
- `enforce_admins: false` may permit an administrator to bypass protection; verify whether that matches the requested policy rather than silently assuming it does.
- A required status check must match the exact check-run context emitted by the workflow (the workflow **job name**, e.g. `scaffold-check`). Verify Actions runs via `GET /repos/<o>/<r>/commits/<sha>/check-runs` — the legacy `/commits/main/status` endpoint shows `pending`/`total_count=0` for Actions and is not authoritative.
- GitHub repository creation may succeed while branch protection fails because `main` does not yet exist; make the minimum governance-only initial commit, then protect the branch.
- Never create implementation code merely to satisfy a branch-protection prerequisite.
- When pushing with a PAT, `git -c http.extraHeader="Authorization: Bearer ..."` fails with `remote: invalid credentials` (header dropped on redirect). Use the one-shot URL form `git push https://x-access-token:$TOKEN@github.com/<owner>/<repo>.git main:main`, then restore the clean remote URL; redact the token from output.
- A CI credential-pattern grep (`ghp_...`) matches the workflow file's own regex text and fails on itself; exclude `.github` from the scan.
- With only one authorized account, `required_approving_review_count=1` is inoperable until a second distinct account (bot or human) is added as a collaborator. Document the reserved slot; don't pretend the rule is live.

## Verification checklist

Record actual outputs for:

- authenticated login;
- repository URL, owner, visibility, and license;
- exact CODEOWNERS contents;
- branch-protection JSON or equivalent effective settings;
- clean-clone CI result;
- remote branch and commit state;
- absence of implementation and credentials in the initial tree.

Session-specific authentication and terminal failure notes are in `references/secure-auth-handoff.md`.
