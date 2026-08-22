#!/usr/bin/env python3
"""Fail closed on inconsistent LeanEcon release metadata.

This check is intentionally runnable before the application is installed
(CI inserts ``src`` on ``sys.path``). A final package version must be
tagged at HEAD; development versions must carry a PEP 440 development
suffix and declare the supported release truth surface.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from leanecon.release_state import check_release_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate LeanEcon release metadata")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = check_release_state(args.root.resolve())
    if errors:
        for error in errors:
            print(f"release-state error: {error}")
        return 1
    print("release-state OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
