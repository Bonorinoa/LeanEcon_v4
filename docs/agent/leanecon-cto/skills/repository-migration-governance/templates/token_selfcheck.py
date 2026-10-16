#!/usr/bin/env python3
"""Safe self-check for a GitHub token stored in ~/.hermes/.env.

Prints ONLY sanitized metadata (never the token) so the output is safe to
paste back into chat. The user runs this in THEIR OWN terminal — do not
launch hidden-input prompts from Hermes background PTYs (read -s hangs,
getpass fails without a real TTY).

Usage:
    python3 token_selfcheck.py [path-to-env-file]

Exit code 0 only when the token validates (HTTP 200) against
GET https://api.github.com/user. Adjust the expected login below.
"""
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

EXPECTED_LOGIN = "agon439"  # set to the GitHub account that must own the token

p = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / ".hermes/.env")
tok = ""
if p.exists():
    for line in p.read_text(errors="replace").splitlines():
        if line.startswith("GITHUB_TOKEN="):
            tok = line.split("=", 1)[1].strip()
            break

print("=== GitHub token self-check (no secrets printed) ===")
print("env_exists=" + str(p.exists()))
if not tok:
    print("entry_found=false")
    print("RESULT: FAILED - no GITHUB_TOKEN entry found")
    sys.exit(1)

print("entry_found=true")
print("token_length=" + str(len(tok)))
print("token_sha256_prefix=" + hashlib.sha256(tok.encode()).hexdigest()[:12])

req = urllib.request.Request(
    "https://api.github.com/user",
    headers={
        "Authorization": "Bearer " + tok,
        "Accept": "application/vnd.github+json",
        "User-Agent": "leanecon-token-selfcheck",
    },
)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        status = r.status
        data = json.loads(r.read())
except urllib.error.HTTPError as e:
    status = e.code
    try:
        data = json.loads(e.read())
    except Exception:
        data = {}

print("http_status=" + str(status))
print("login=" + str(data.get("login")))
print("message=" + str(data.get("message", "")))
if status == 200 and data.get("login") == EXPECTED_LOGIN:
    print("RESULT: OK - token valid for " + str(data.get("login")))
    sys.exit(0)
print("RESULT: FAILED - token rejected by GitHub or wrong account")
sys.exit(1)
