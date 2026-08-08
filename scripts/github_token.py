"""Load GitHub tokens for LeanEcon ops scripts (CTO + hermessinho bot).

Used by scripts_local helpers. Never prints token values.
Prefer LEANECON_BOT_TOKEN for bot-authored push/PR; GITHUB_TOKEN for
CTO/admin flows (branch protection relax/restore).
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_FILE = Path.home() / ".hermes/profiles/leanecon-cto/.env"
BOT_ENV_FILE = Path.home() / ".hermes/profiles/leanecon-cto/.env.bot"


def load_token(token_name: str = "GITHUB_TOKEN") -> str:
    env_val = os.environ.get(token_name)
    if env_val:
        return env_val.strip().strip('"').strip("'")

    if token_name == "LEANECON_BOT_TOKEN" and BOT_ENV_FILE.exists():
        try:
            for line in BOT_ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{token_name}="):
                    return line.partition("=")[2].strip().strip('"').strip("'")
        except OSError:
            pass

    if ENV_FILE.exists():
        try:
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{token_name}="):
                    return line.partition("=")[2].strip().strip('"').strip("'")
        except OSError:
            pass
    return ""


def load_bot_token() -> str:
    """Bot token first, then CTO token fallback."""
    return load_token("LEANECON_BOT_TOKEN") or load_token("GITHUB_TOKEN")


def load_cto_token() -> str:
    """CTO token (protection / admin flows)."""
    return load_token("GITHUB_TOKEN")
