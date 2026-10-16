#!/usr/bin/env python3
"""Check CI status of all open PRs in a repository.

Reads the token from the profile env file itself (never prints it) and
lists each open PR with mergeable_state and every registered check run
(name, status, conclusion). Useful before running the merge
orchestration to confirm a PR's checks exist and are green.

Usage:
    python github_check_pr_ci.py <OWNER/REPO>
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".hermes/profiles/leanecon-cto/.env"
API = "https://api.github.com"


def load_token() -> str:
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GITHUB_TOKEN="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    return ""


def api(token: str, path: str):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: github_check_pr_ci.py <OWNER/REPO>", file=sys.stderr)
        return 2
    repo = sys.argv[1]
    token = load_token()
    if not token:
        print("GITHUB_TOKEN not found in profile env", file=sys.stderr)
        return 2
    pulls = api(token, f"/repos/{repo}/pulls?state=open")
    for pr in pulls:
        print(f"PR #{pr['number']}: {pr['title']}")
        print(f"  mergeable_state: {pr.get('mergeable_state')}")
        sha = pr["head"]["sha"]
        checks = api(token, f"/repos/{repo}/commits/{sha}/check-runs")
        for check in checks.get("check_runs", []):
            print(f"  check: {check['name']} | {check['status']} | {check.get('conclusion')}")
        if checks.get("total_count") == 0:
            print("  (no checks registered yet)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
