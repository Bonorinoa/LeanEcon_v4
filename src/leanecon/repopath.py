"""Repository-root discovery shared by the runners.

Source-tree runs resolve ``__file__`` upward to the repo marker
(pyproject.toml + lean_workspace). Installed runs (site-packages) fall
back to the ``LEANECON_REPO_ROOT`` environment variable or the current
working directory (the documented invocation is from the repo root).

Both a1_runner and a3_runner must use this instead of deriving the root
from ``Path(__file__).parents[n]`` — the depth changes when the package
is installed into site-packages.
"""

from __future__ import annotations

import os
from pathlib import Path


def find_repo_root() -> Path:
    override = os.environ.get("LEANECON_REPO_ROOT")
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists() and (parent / "lean_workspace").exists():
            return parent
    return Path.cwd()
