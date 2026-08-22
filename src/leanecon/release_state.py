"""Dependency-free checks for truthful LeanEcon release metadata.

A final version (``X.Y.Z``) is allowed only when HEAD carries ``vX.Y.Z``.
A development version must use a PEP 440 ``.devN`` suffix and name both
the development version and the latest supported release in
``docs/releases/DEVELOPMENT.md``.

This is a truth-surface check, not a tag authorization.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

DEVELOPMENT_VERSION = re.compile(r"^\d+\.\d+\.\d+\.dev\d+$")
FINAL_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def _head_tags(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return {tag for tag in result.stdout.splitlines() if tag}


def check_release_state(root: Path, *, head_tags: set[str] | None = None) -> list[str]:
    """Return release-state violations for ``root`` without mutating it."""
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    runner = (root / "src" / "leanecon" / "a3_runner.py").read_text(encoding="utf-8")
    expected_builder = f'BUILDER_IDENTITY = "leanecon-a3-{version}"'
    errors: list[str] = []

    if expected_builder not in runner:
        errors.append(f"builder identity must equal leanecon-a3-{version}")

    if DEVELOPMENT_VERSION.fullmatch(version):
        truth_surface = root / "docs" / "releases" / "DEVELOPMENT.md"
        if not truth_surface.exists():
            errors.append("development version requires docs/releases/DEVELOPMENT.md")
        else:
            text = truth_surface.read_text(encoding="utf-8")
            if f"`{version}`" not in text:
                errors.append("development truth surface does not name package version")
            if "Latest supported release" not in text:
                errors.append("development truth surface does not identify a supported release")
    elif FINAL_VERSION.fullmatch(version):
        tags = _head_tags(root) if head_tags is None else head_tags
        if f"v{version}" not in tags:
            errors.append(f"final version {version} must be tagged v{version} at HEAD")
    else:
        errors.append(f"unsupported package version form: {version}")
    return errors
