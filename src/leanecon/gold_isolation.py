"""Gold isolation rules (Gate 4, A1 criterion 8).

Runtime must have no access path — filesystem, environment, or package
import — to v3 gold statements, reviewer labels, or release artifacts.
Shared by the isolation tests and the A1 runner so both enforce the
same list.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Paths that must never exist in the v4 runtime tree.
FORBIDDEN_PATHS = (
    "benchmark_baselines",
    "evals",
    "gold",
    "gold_statements",
    "sealed_corpus",
    ".codebase-memory",
    "leanecon_v3",
)

FORBIDDEN_ENV_VARS = (
    "LEANECON_GOLD_PATH",
    "GOLD_STATEMENTS",
    "HIDDEN_LABELS_PATH",
)

RELEASE_ARTIFACT_PATHS = ("artifacts/release", "release_corpus", "mvp_bundle")


def scan_forbidden_paths(repo_root: Path, skip_parts=(".lake", ".venv", ".git")) -> list:
    found = []
    for name in FORBIDDEN_PATHS:
        hits = [p for p in Path(repo_root).rglob(name) if not any(part in skip_parts for part in p.parts)]
        found.extend(str(h.relative_to(repo_root)) for h in hits)
    return found


def scan_forbidden_env() -> list:
    return [name for name in FORBIDDEN_ENV_VARS if os.environ.get(name)]


def scan_release_artifacts(repo_root: Path) -> list:
    return [name for name in RELEASE_ARTIFACT_PATHS if (Path(repo_root) / name).exists()]
