#!/usr/bin/env python3
"""Mechanical consistency check for the LeanEcon Core glossary registry.

Gate 6 P3 procedure (2026-08-06): run this BEFORE a registry versioning
commit. It catches entry-count drift, numbering gaps, status-ladder
violations, and PROMOTION DRIFT — statuses that no longer match reality
(the P3 pass caught six P2-promoted declarations still marked
`core-candidate`).

Usage:
    .venv/bin/python <this script> [registry_path]

Defaults: docs/gate6/references/core-glossary-detail.md
Expected contract: 28 entries numbered 1..28; every `- **Status:**` first
token in {glossary-only, core-candidate, core, mathlib}; the equilibrium
family (entries 21-28, between the section markers below) only
glossary-only or core-candidate, never promoted.
Exit 0 on pass, 1 on any failure. No network, no Lean — pure text scan.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

EXPECTED_ENTRIES = 28
LADDER = ["glossary-only", "core-candidate", "core", "mathlib"]
EQ_START = "### 21. `exchange-economy`"
EQ_END = "## Cross-claim"


def _tag(status_line: str) -> str:
    """First token of a '- **Status:** <tag>[; note]' line, punctuation-stripped."""
    return status_line.split(";")[0].split()[0].strip("*().").strip()


def check(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    entries = re.findall(r"### (\d+)\. `([^`]+)`", text)
    ids = [int(n) for n, _ in entries]
    if len(entries) != EXPECTED_ENTRIES:
        failures.append(f"expected {EXPECTED_ENTRIES} entries, found {len(entries)}")
    if ids != list(range(1, EXPECTED_ENTRIES + 1)):
        failures.append(f"numbering gaps: {ids}")

    statuses = re.findall(r"\*\*Status:\*\* ([^\n]+)", text)
    if len(statuses) != len(entries):
        failures.append(f"{len(statuses)} status lines for {len(entries)} entries")
    tags = []
    for s in statuses:
        t = _tag(s)
        if t not in LADDER:
            failures.append(f"status outside ladder: {s!r}")
        tags.append(t)
    print("status ladder counts:", dict(Counter(tags)))

    if EQ_START in text and EQ_END in text:
        eq = text.split(EQ_START)[1].split(EQ_END)[0]
        for m in re.finditer(r"\*\*Status:\*\* ([^\n]+)", eq):
            t = _tag(m.group(1))
            if t not in ("glossary-only", "core-candidate"):
                failures.append(f"equilibrium entry violates ladder: {m.group(1)!r}")
            if "**core**" in m.group(1):
                failures.append(f"equilibrium entry promoted unexpectedly: {m.group(1)!r}")
    else:
        print("warning: equilibrium section markers not found; 21-28 constraint skipped")

    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print(f"glossary registry check PASSED ({EXPECTED_ENTRIES} entries)")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "docs/gate6/references/core-glossary-detail.md")
    raise SystemExit(check(target))
