#!/usr/bin/env python3
"""Score independent semantic-review records against a sealed manifest.

Does not call a provider. Does not infer meaning. Publishes counts.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from leanecon.eval_protocol import load_reviews, score_semantic_reviews


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score LeanEcon semantic-review records")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reviews-dir", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = score_semantic_reviews(manifest, load_reviews(args.reviews_dir))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
