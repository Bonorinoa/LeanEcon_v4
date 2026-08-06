"""Formalization service (docs/gate5/a3-design.md §4).

Turns the ACCEPTED interpretation into a candidate Lean statement plus a
mapping report (EI element -> Mathlib identifier or A3-local scaffolding
definition). The mapping report is required before PROVING (locked EI
decision 3): material elements must be mapped or explicitly flagged as
unmapped gaps; unacknowledged gaps block PROVING entry.

No LeanEcon Core exists yet (Gate 6): economics vocabulary maps to
Mathlib structure or to clearly-labeled A3-local scaffolding definitions
inside the candidate file. Nothing here invents definitions silently.
"""

from __future__ import annotations

import json
import re
from typing import Any

#: Element kinds that must be mapped (or flagged unmapped) before PROVING.
MATERIAL_KINDS = {"object", "assumption", "quantifier", "conclusion", "solution", "definition"}
#: Expository kinds may be deferred with a note.
DEFERRABLE_KINDS = {"context", "note"}

MAPPING_STATUSES = ("mapped", "unmapped", "deferred")
MAPPING_KINDS = ("mathlib", "local_definition", "glossary_term", "none")


def material_element_ids(ei: dict) -> list[tuple[str, str]]:
    """Return [(element_id, kind)] for every material element of the EI.

    Element ids are stable: objects use their ``id``; other elements use
    ``kind:index`` references. The formalizer is instructed to use these.
    """
    elements: list[tuple[str, str]] = []
    for obj in ei.get("objects", []) or []:
        elements.append((obj.get("id", "?"), "object"))
    for i, _ in enumerate(ei.get("assumptions", {}).get("proposed", []) or []):
        elements.append((f"assumption:{i}", "assumption"))
    for i, _ in enumerate(ei.get("quantifiers", []) or []):
        elements.append((f"quantifier:{i}", "quantifier"))
    elements.append(("conclusion", "conclusion"))
    if (ei.get("conclusion") or {}).get("solution_or_equilibrium_concept"):
        elements.append(("solution_concept", "solution"))
    for i, _ in enumerate(ei.get("context", {}).get("definitions", []) or []):
        elements.append((f"definition:{i}", "definition"))
    return elements


def validate_mapping_report(report: list[dict], ei: dict) -> tuple[list[str], list[dict]]:
    """Validate report shape; return (problems, gaps).

    A gap is a material element with status ``unmapped`` (or a missing row).
    Deferred rows are allowed only for non-material kinds.
    """
    problems: list[str] = []
    if not isinstance(report, list):
        return ["mapping_report must be a list"], []

    by_id = {row.get("ei_element_id"): row for row in report if isinstance(row, dict)}
    for row in report:
        if not isinstance(row, dict):
            problems.append("mapping report rows must be objects")
            continue
        if row.get("status") not in MAPPING_STATUSES:
            problems.append(f"row {row.get('ei_element_id')}: invalid status {row.get('status')!r}")
        if row.get("status") == "mapped" and row.get("mapping_kind") not in MAPPING_KINDS:
            problems.append(f"row {row.get('ei_element_id')}: invalid mapping_kind {row.get('mapping_kind')!r}")
        if row.get("status") == "deferred" and row.get("ei_element_kind") not in DEFERRABLE_KINDS:
            problems.append(f"row {row.get('ei_element_id')}: material element may not be deferred")

    gaps: list[dict] = []
    for element_id, kind in material_element_ids(ei):
        row = by_id.get(element_id)
        if row is None:
            gaps.append({"ei_element_id": element_id, "ei_element_kind": kind, "reason": "missing mapping row"})
        elif row.get("status") == "unmapped":
            gaps.append({"ei_element_id": element_id, "ei_element_kind": kind, "reason": row.get("note") or "unmapped"})
        elif row.get("status") not in ("mapped",):
            problems.append(f"row {element_id}: material {kind} must be mapped or unmapped, got {row.get('status')!r}")
    return problems, gaps


def formalize_prompt(ei: dict) -> str:
    """Prompt for the formalize capability (MVP model per adapter config)."""
    return (
        "You are the formalization service of a kernel-checked economics system. "
        "Given the ACCEPTED interpretation below (JSON), write a Lean 4 formal "
        "statement in the pinned Mathlib workspace.\n\n"
        "Rules:\n"
        "- Output ONLY a JSON object: {\"statement\": <theorem signature as Lean text, "
        "e.g. 'theorem name (args) : proposition' — WITHOUT proof body>, "
        "\"target_theorem\": <theorem name>, \"mapping_report\": [...]}.\n"
        "- Do not write a proof body. Do not use sorry/admit.\n"
        "- The statement may define small A3-local scaffolding definitions first "
        "(clearly commented 'A3-local scaffolding, not LeanEcon Core').\n"
        "- The mapping_report must contain one row per material EI element with "
        "fields: ei_element_id, ei_element_kind, lean_identifier, mapping_kind "
        "(mathlib|local_definition|glossary_term|none), status (mapped|unmapped|deferred), "
        "provenance, note. Element ids: object ids from the interpretation, "
        "'assumption:<i>', 'quantifier:<i>', 'conclusion', 'solution_concept', 'definition:<i>'.\n"
        "- If an element cannot be mapped, mark it unmapped with a note — never "
        "invent a definition to hide the gap.\n\n"
        "Accepted interpretation (JSON):\n"
        f"{json.dumps(ei, indent=1, sort_keys=True)}"
    )


def parse_formalize_response(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"formalize response is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("formalize response must be a JSON object")
    for key in ("statement", "target_theorem", "mapping_report"):
        if key not in parsed:
            raise ValueError(f"formalize response missing key: {key}")
    if not isinstance(parsed["mapping_report"], list):
        raise ValueError("formalize mapping_report must be a list")
    return parsed
