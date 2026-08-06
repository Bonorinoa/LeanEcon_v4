"""Interpretation service (docs/gate5/a3-design.md §3).

Produces and validates EconomicInterpretation candidates against the draft
schema (references/gate3/ei_schema_draft.json), enforces the locked
``none_noted`` reviewer-acknowledgement rule (EI design decision 2), and
finalizes an accepted revision immutably.

The EI candidate is a meaning hypothesis, never a proof and never a
hidden answer key. ``semantic_triage`` may flag; only a human reviewer may
set ``review.decision`` to APPROVED (enforced by the runner + finalize).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from leanecon.data_policy import canonical_digest

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "references" / "gate3" / "ei_schema_draft.json"

REVIEW_PENDING = "PENDING"
REVIEW_APPROVED = "APPROVED"
REVIEW_REJECTED = "REJECTED"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _business_rule_problems(candidate: dict) -> list[str]:
    """Schema-independent semantic rules on top of jsonschema validation."""
    problems: list[str] = []

    review = candidate.get("review") or {}
    if review.get("decision") != REVIEW_PENDING:
        problems.append("review.decision must be PENDING at production time")

    assumptions = candidate.get("assumptions") or {}
    if assumptions.get("accepted"):
        problems.append("assumptions.accepted must be empty until a reviewer accepts them")

    ambiguities = candidate.get("ambiguities") or []
    none_noted = candidate.get("none_noted", False)
    if not ambiguities and not none_noted:
        problems.append("empty ambiguities requires none_noted: true (locked EI decision 2)")
    if ambiguities and none_noted:
        problems.append("none_noted must be false when ambiguities are listed")

    conclusion = candidate.get("conclusion") or {}
    if not conclusion.get("text"):
        problems.append("conclusion.text is required")

    objects = candidate.get("objects") or []
    ids = [o.get("id") for o in objects]
    if len(ids) != len(set(ids)):
        problems.append("object ids must be unique")

    confidence = candidate.get("confidence")
    if confidence is not None and not (0.0 <= confidence <= 1.0):
        problems.append("confidence must be within [0, 1]")

    classification = candidate.get("data_classification")
    if classification not in ("PUBLIC", "PROJECT", "RESTRICTED"):
        problems.append(f"data_classification must be PUBLIC/PROJECT/RESTRICTED, got {classification!r}")

    return problems


def validate_ei_candidate(candidate: dict, schema: dict | None = None) -> list[str]:
    """Return a list of problems (empty when the candidate is valid)."""
    schema = schema or load_schema()
    problems: list[str] = []
    try:
        import jsonschema

        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(candidate), key=lambda e: list(e.path)):
            problems.append(f"schema: {'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}")
    except Exception as exc:  # pragma: no cover - dependency failure must be visible
        problems.append(f"jsonschema unavailable: {exc}")
    problems.extend(_business_rule_problems(candidate))
    return problems


def interpret_prompt(claim_text: str) -> str:
    """Prompt for the interpret capability (MVP model per adapter config).

    Instructs schema-shaped JSON output; the response is parsed and
    validated downstream — the model never self-certifies.
    """
    return (
        "You are the interpretation service of a kernel-checked economics "
        "formalization system. Produce an EconomicInterpretation for the given "
        "economic claim. It is a meaning hypothesis for human review — do NOT "
        "prove anything, do NOT write Lean code, do NOT invent facts beyond the claim.\n\n"
        "Return ONLY a JSON object with exactly these fields:\n"
        "  schema_version: \"1.0.0\"\n"
        "  claim: {canonical_text: normalized claim, source_text: original text}\n"
        "  context: {domain_tags: [str], definitions: [{id, text}], ontology_refs: [str]}\n"
        "  objects: [{id, kind, role}]  (economic objects/agents/markets)\n"
        "  assumptions: {proposed: [str], accepted: []}\n"
        "  quantifiers: [str]  (controlled English quantifier/scope statements)\n"
        "  conclusion: {text: str, solution_or_equilibrium_concept: str|null}\n"
        "  ambiguities: [{issue: str, alternatives: [str]}]  OR empty\n"
        "  none_noted: true iff ambiguities is empty\n"
        "  provenance: {source_span: str, mapping_method: str, references: [str]}\n"
        "  confidence: number 0..1 (process confidence, not truth)\n"
        "  degradation_flags: [str]\n"
        "  review: {decision: \"PENDING\", reviewer: null, event_ref: null}\n"
        "  data_classification: \"PROJECT\"\n\n"
        "Claim:\n"
        f"{claim_text}"
    )


def parse_interpret_response(content: str) -> dict:
    """Parse model content into a dict; strip code fences if present."""
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"interpret response is not valid JSON: {exc}") from exc


def finalize_ei(
    candidate: dict,
    reviewer: str,
    event_ref: str,
    acknowledges_none_noted: bool = False,
    notes: str = "",
) -> dict:
    """Produce the immutable accepted revision of an EI candidate.

    Enforces the none_noted rule: approving an interpretation that found no
    ambiguity requires explicit reviewer acknowledgement.
    """
    if candidate.get("review", {}).get("decision") not in (REVIEW_PENDING, REVIEW_APPROVED):
        raise ValueError("only a PENDING candidate may be finalized")
    none_noted = bool(candidate.get("none_noted", False))
    if none_noted and not acknowledges_none_noted:
        raise ValueError("none_noted interpretation requires reviewer acknowledgement (acknowledges_none_noted)")
    finalized = dict(candidate)
    finalized["review"] = {
        "decision": REVIEW_APPROVED,
        "reviewer": reviewer,
        "notes": notes,
        "event_ref": event_ref,
        "acknowledges_none_noted": acknowledges_none_noted,
    }
    finalized["digest"] = canonical_digest({k: v for k, v in finalized.items() if k != "digest"})
    return finalized
