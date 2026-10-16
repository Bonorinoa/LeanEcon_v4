# Secure Authentication Handoff — session notes (LeanEcon v4 Gate 2, 2026-08)

Working notes from bootstrapping `Bonorinoa/LeanEcon_v4`. Every item below was
hit for real; keep these as the checklist when the same class of failure
reappears.

## 1. Which `.env` is the real one (root cause of ~30 min of false 401s)

Hermes runs under a profile. The token Hermes actually loads lives in:

- `$HERMES_HOME/.env`, e.g. `~/.hermes/profiles/<profile>/.env` (the profile's
  own env file), NOT `~/.hermes/.env`.

Symptom: every API call returns `401 Bad credentials` even though the user
"updated the token". Cause: the skill fallback read `~/.hermes/.env` (default
home, stale token) while the valid token sat in the profile `.env`.

Diagnosis that worked:

```python
import hashlib, os
from pathlib import Path
print("HERMES_HOME=" + os.environ.get("HERMES_HOME", "<unset>"))
for p in [Path.home()/".hermes/.env",
          Path.home()/".hermes/profiles/leanecon-cto/.env"]:
    if p.exists():
        tok = ""
        for line in p.read_text(errors="replace").splitlines():
            if line.startswith("GITHUB_TOKEN="):
                tok = line.split("=",1)[1].strip(); break
        print(p, "len="+str(len(tok)), "sha="+hashlib.sha256(tok.encode()).hexdigest()[:12])
```

Then test EACH candidate token against `GET https://api.github.com/user` until
one returns 200. Print metadata (length, sha256 prefix, login), never the value.

The stale `~/.hermes/.env` token returned 401; the profile token returned
`200 login=Bonorinoa`. The user's key was correct the whole time — the lookup
was wrong.

## 2. Do not infer the GitHub login from git config

`git config user.email` (`agonz439@asu.edu`) does not imply the GitHub handle
(`Bonorinoa`). Always resolve the login via an authenticated API call
(`GET /user` → `login`).

## 3. Hidden-input token prompts hang in detached/background terminals

`read -r -s` in a background terminal without interactive stdin hangs forever
(`zsh: read:1: -p: no coprocess` / Python `getpass` EOFError). Do not use
background PTY prompts for secrets.

Working pattern: write a self-check script that prints ONLY sanitized metadata
plus a final `RESULT: OK` / `RESULT: FAILED` line, have the user run it in
their own visible terminal, and paste the output back. Never ask for the raw
token in chat.

## 4. Git push with a PAT: use the URL form, not `http.extraHeader`

`git -c http.extraHeader="Authorization: Bearer $TOKEN" push` fails with
`remote: invalid credentials` — the header is dropped on GitHub's redirect.
Working one-shot form (token stays out of `.git/config`):

```bash
git push https://x-access-token:$TOKEN@github.com/<owner>/<repo>.git main:main
git remote set-url origin https://github.com/<owner>/<repo>.git   # restore clean URL
```

Redact the token from command output with `| sed "s/$TOKEN/***REDACTED***/g"`.

## 5. Actions uses check-runs, not legacy commit statuses

`GET /repos/<o>/<r>/commits/main/status` returns `state=pending, total_count=0`
for Actions runs — the legacy status API is not populated. The authoritative
check is:

```bash
GET /repos/<o>/<r>/commits/<sha>/check-runs
# look for: name=<context> status=completed conclusion=success app=github-actions
```

Required-check contexts in branch protection must match the workflow **job
name** (e.g. job `scaffold-check` → context `scaffold-check`).

## 6. CI credential-scan self-match

A `grep -rInE '(ghp_[A-Za-z0-9]{20,}|...)' --exclude-dir=.git .` scan matches
the workflow file's own regex text and fails on itself. Fix: also exclude
`.github` from the scan (`--exclude-dir=.github`), or store the pattern in a
file excluded from the scan.

## 7. Branch protection payload that worked (Gate 2)

```json
{
  "required_status_checks": {"strict": true, "contexts": ["scaffold-check"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false
}
```

`PUT /repos/<o>/<r>/branches/main/protection` → 200. Self-approval is disabled
by GitHub's platform rule (PR authors cannot approve their own PRs) — there is
no API flag; it holds whenever `required_pull_request_reviews` is enabled.

## 8. One-approval rule is inoperable with a single account

With only one authorized account (`@Bonorinoa`), `required_approving_review_count=1`
cannot be satisfied — no second account exists to approve. It becomes operable
the moment the bot/second account is added as a collaborator. Document the
reserved CODEOWNERS slot rather than pretending the rule works today.
