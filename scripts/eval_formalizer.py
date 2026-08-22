#!/usr/bin/env python3
"""CLI wrapper: PYTHONPATH=src python scripts/eval_formalizer.py --fixtures ..."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from leanecon.eval_formalizer import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
