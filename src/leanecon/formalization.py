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
from typing import Any, Optional

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
    """Prompt for the formalize capability (MVP model per adapter config).

    Hardened after the 2026-08-06 walkthrough: the live formalizer produced
    vacuous tautologies (c1), an invalid `[Set α]` binder (c2), a `sorry`
    proof body (c3), and non-canonical mapping ids. The rules below make each
    failure mode an explicit instruction; the static validator
    (validate_statement_text) and the compile probe back it up.
    """
    return (
        "You are the formalization service of a kernel-checked economics system. "
        "Given the ACCEPTED interpretation below (JSON), write a Lean 4 formal "
        "statement in the pinned Mathlib workspace.\n\n"
        "Rules:\n"
        "- Output ONLY a JSON object: {\"statement\": <theorem signature as Lean text, "
        "e.g. 'theorem name (args) : proposition' — signature ONLY, no proof body>, "
        "\"target_theorem\": <theorem name>, \"mapping_report\": [...]}.\n"
        "- HARD: the statement must be a SIGNATURE ONLY. It must end at the "
        "conclusion: `... : <conclusion>` with NO `:=` and NO `by ...` — do not "
        "attach a proof body. Do not use sorry/admit anywhere.\n"
        "- HARD: the statement must be well-formed Lean that compiles under "
        "`import Mathlib`. Typeclass binders like `[Set α]` are INVALID — use "
        "`[Fintype α]`, `[LinearOrder α]` etc. only for genuine typeclasses.\n"
        "- HARD: no tautologies and no vacuous theorems. The conclusion must be "
        "a substantive proposition about the claim, NOT identical to any "
        "hypothesis, and not derivable from a hypothesis alone. If the claim "
        "is a property claim (e.g. 'weak preference is transitive'), state the "
        "property as the conclusion with the objects as parameters.\n"
        "- Every hypothesis you list in the signature must actually appear in "
        "the signature, and every parameter must be USED in the statement. Do "
        "not reference hypotheses that are absent.\n"
        "- The statement may define small A3-local scaffolding definitions first "
        "(clearly commented 'A3-local scaffolding, not LeanEcon Core').\n"
        "- The mapping_report must contain one row per material EI element with "
        "fields: ei_element_id, ei_element_kind, lean_identifier, mapping_kind "
        "(mathlib|local_definition|glossary_term|none), status (mapped|unmapped|deferred), "
        "provenance, note. Element ids MUST be used EXACTLY as given: object ids "
        "from the interpretation (e.g. 'u', 'x', 'preferences' — never 'object:u'), "
        "'assumption:<i>', 'quantifier:<i>', 'conclusion', 'solution_concept', "
        "'definition:<i>'. Do not rename or prefix them.\n"
        "- If an element cannot be mapped, mark it unmapped with a note — never "
        "invent a definition to hide the gap.\n\n"
        "Accepted interpretation (JSON):\n"
        f"{json.dumps(ei, indent=1, sort_keys=True)}"
    )


_SORRY_TOKENS = ("sorry", "admit")


def validate_statement_text(statement: str) -> list[str]:
    """Static contract checks on the candidate statement. Returns problems.

    Hard failures (the run is rejected with PROVIDER_INVALID_OUTPUT):
    - sorry/admit anywhere in the statement;
    - a proof body attached with ``:=`` (the prompt requires a bare signature).

    These mirror the walkthrough's c2/c3 failure modes. The kernel compile
    probe (verifier.probe_statement_compiles) additionally records whether the
    statement compiles — an evaluation signal, not a blocker.
    """
    problems: list[str] = []
    lowered = statement.lower()
    for token in _SORRY_TOKENS:
        if token in lowered:
            problems.append(f"statement contains '{token}' (contract violation)")
    if re.search(r"\s:=", statement) or statement.rstrip().endswith(":="):
        problems.append("statement carries a proof body ('... :='); output the signature only")
    return problems


def vacuity_warning(statement: str) -> Optional[str]:
    """Heuristic: does the conclusion restate a hypothesis (vacuous/tautological)?

    Extracts the text after the LAST ``:`` (the conclusion) and checks whether
    a normalized form of it also appears in the hypothesis region. A warning
    only — the reviewer decides; the kernel arbitrates.
    """
    colon = statement.rfind(":")
    if colon == -1:
        return None
    conclusion = statement[colon + 1 :].strip().rstrip(".")
    if not conclusion:
        return None
    hypothesis_region = statement[:colon]
    norm = lambda s: re.sub(r"\s+", "", s)
    if norm(conclusion) in norm(hypothesis_region):
        return f"conclusion restates a hypothesis (potential vacuity): '{conclusion[:80]}'"
    return None


def classify_gaps(gaps: list[dict], report: list[dict]) -> list[dict]:
    """Annotate missing-row gaps: id-scheme deviation vs genuinely missing.

    The live formalizer sometimes prefixed canonical ids ('object:u' instead
    of 'u'). A row whose id is '<anything>:<canonical>' (or '<kind>:<canonical>')
    demonstrably covers the element under a non-compliant id — an evaluation
    signal about id discipline, not a coverage gap. Anything else is
    genuinely missing. Unmapped-status gaps keep their reason unchanged.
    """
    row_ids = {str(row.get("ei_element_id", "")) for row in report if isinstance(row, dict)}
    classified: list[dict] = []
    for gap in gaps:
        gap = dict(gap)
        cid = str(gap["ei_element_id"])
        if gap.get("reason") == "missing mapping row":
            deviation = any(
                rid != cid and (rid.endswith(":" + cid) or rid == f"{gap['ei_element_kind']}:{cid}")
                for rid in row_ids
            )
            gap["classification"] = "id_scheme_deviation" if deviation else "genuinely_missing"
        else:
            gap["classification"] = "unmapped_with_note"
        classified.append(gap)
    return classified


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
