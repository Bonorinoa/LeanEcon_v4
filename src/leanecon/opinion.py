"""Consultative opinion side-door (v4 slice 1; DECISION_LOG 51/D3 + 55).

A user or calling program can ask the system for its own consultative
review of an artifact in an in-flight claim walkthrough. An opinion is:

- **consultative only**: it never emits ACCEPTED / REJECTED / VERIFIED,
  never transitions lifecycle state, and never gates PROVING or the
  bundle checks;
- **bound to an immutable artifact revision**: the opinion records the
  formal artifact digest and the accepted-EI digest it was built from;
- **machine-grounded**: the deterministic machine block (P1-P6 property
  labels derived from stored signals, the probe-failure class, the
  repair Diagnosis) is always present and authoritative; the model prose
  is labelled AI-opinion and can never override a machine signal;
- **recorded with provenance** ``consultative_opinion``, distinct from
  review records (``reviewer_kind`` human|ai|auto per
  docs/gate3/08-reviewer-policy.md).

Slice-1 target surface: the formal draft + mapping report (D2). The
pedagogical mode (D5) adds a first-class learner-facing explanation of
any failure and what to try next; it is a field on the same artifact
(``pedagogical``), not a separate feature.

Mechanism split (house discipline, docs/v4/G0_OPINION_SLICE.md):
- machine block + schema validation + refusal guards = PRINCIPLED;
- model-authored prose + prompt wording = HEURISTIC.

Attribution: prepared by Hermes Agent (Nous Research) under CTO
direction; the CTO remains the sole semantic approver.
"""

from __future__ import annotations

import json
from typing import Any

from leanecon.eval_formalizer import classify_probe_failure
from leanecon.probe_repair import diagnose as probe_diagnose

OPINION_SCHEMA_VERSION = "1.0.0"

SURFACE_FORMAL = "formal"
ALLOWED_SURFACES = (SURFACE_FORMAL,)

MODE_CONSULTATIVE = "consultative"
MODE_PEDAGOGICAL = "pedagogical"
ALLOWED_MODES = (MODE_CONSULTATIVE, MODE_PEDAGOGICAL)

#: Outcome vocabulary an opinion must never carry. Guarded structurally
#: (an opinion artifact has no decision/state fields), not by prose scan —
#: prose is prose; the schema is the contract.
RESERVED_OUTCOME_KEYS = ("decision", "state_after", "verdict")

#: P6 is verify-stage only; this surface (formal draft) never exercises it.
P6_NOT_EXERCISED = "verify-stage only — not exercised on this surface"
#: P5 is reviewer-owned meaning; the machine never asserts it.
P5_REVIEWER_OWNED = "reviewer-owned — the machine never asserts semantic fidelity"


def _history(formal: dict) -> list[dict]:
    return list(formal.get("revision_history") or [])


def _is_audit_clean(item: dict) -> bool:
    return not list(item.get("static_problems") or [])


def _attempts_to_valid(history: list[dict]) -> int | None:
    for index, item in enumerate(history, start=1):
        if _is_audit_clean(item):
            return index
    return None


def _earlier_p1_violations(history: list[dict]) -> list[str]:
    """Static (P1) problems seen on earlier attempts of this formalization."""
    seen: list[str] = []
    for item in history[:-1]:
        for problem in item.get("static_problems") or []:
            if problem not in seen:
                seen.append(problem)
    return seen


def _gap_ids(gaps: list[dict], classification: str) -> list[str]:
    return [
        str(g.get("ei_element_id", ""))
        for g in gaps
        if g.get("classification") == classification and g.get("ei_element_id")
    ]


def machine_block(formal: dict, ei: dict | None = None) -> dict:
    """Deterministic P1-P6 machine signal block over a formal artifact.

    Determinism contract (tests/test_opinion.py): identical inputs yield
    an identical block. Every field derives from stored artifact signals;
    no model output enters this function.
    """
    history = _history(formal)
    probe = formal.get("statement_probe") or {}
    compiles = probe.get("compiles")
    stderr = str(probe.get("stderr_tail") or "")
    failure_class = classify_probe_failure(stderr) if compiles is False else None
    gaps = list(formal.get("gaps") or [])

    p3 = {
        "genuinely_missing": _gap_ids(gaps, "genuinely_missing"),
        "id_scheme_deviation": _gap_ids(gaps, "id_scheme_deviation"),
        "unmapped_with_note": len(_gap_ids(gaps, "unmapped_with_note")),
        "total_gaps": len(gaps),
    }
    diagnosis = None
    if compiles is False:
        diagnosis = probe_diagnose(
            {"static_problems": [], "probe_compiles": False, "probe_stderr": stderr}
        )
    block = {
        "schema_version": OPINION_SCHEMA_VERSION,
        "surface": SURFACE_FORMAL,
        "artifact_anchor": {
            "claim_id": formal.get("claim_id"),
            "formal_revision": formal.get("revision"),
            "formal_digest": formal.get("digest"),
            "ei_digest": formal.get("interpretation_digest"),
        },
        "properties": {
            # Accepted drafts are audit-clean by construction; earlier
            # attempts may still carry surface violations.
            "P1_surface_legality": {
                "clean": True,
                "earlier_violations": _earlier_p1_violations(history),
            },
            "P2_elaboration": {
                "compiles": compiles,
                "probe_failure_class": failure_class,
            },
            "P3_contract": p3,
            # vacuity_warning is the stored string; non-empty means the
            # conclusion restates a hypothesis (vacuity/inversion signal,
            # same decider eval_formalizer uses).
            "P4_substance": {"vacuity_or_inversion": bool(formal.get("vacuity_warning"))},
            "P5_semantic_fidelity": P5_REVIEWER_OWNED,
            "P6_proof_adequacy": P6_NOT_EXERCISED,
        },
        "repair_diagnosis": diagnosis,
        "attempts": {
            "used": formal.get("revision_attempts"),
            "attempts_to_valid": _attempts_to_valid(history),
            "probe_failed_attempts": sum(
                1 for item in history if item.get("probe_compiles") is False
            ),
        },
        "deterministic": True,
    }
    return block


def _extract_json(content: str) -> Any:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"opinion response is not valid JSON: {exc}") from exc


def parse_opinion_response(content: str, mode: str) -> dict:
    """Parse + structurally validate the model-authored opinion JSON.

    Raises ValueError on any structural violation (missing keys, wrong
    types, mode mismatch, reserved outcome keys inside the payload).
    """
    if mode not in ALLOWED_MODES:
        raise ValueError(f"unknown opinion mode: {mode}")
    parsed = _extract_json(content)
    if not isinstance(parsed, dict):
        raise ValueError("opinion response must be a JSON object")
    assessment = parsed.get("assessment")
    if not isinstance(assessment, dict):
        raise ValueError("opinion response missing assessment object")
    for key in RESERVED_OUTCOME_KEYS:
        if key in parsed or key in assessment:
            raise ValueError(f"opinion payload carries reserved outcome key: {key}")
    required_assessment = ("summary", "strengths", "concerns", "suggestions")
    for key in required_assessment:
        if key not in assessment:
            raise ValueError(f"opinion assessment missing key: {key}")
        if key == "summary" and not isinstance(assessment[key], str):
            raise ValueError(f"opinion assessment.{key} must be a string")
        if key != "summary" and not isinstance(assessment[key], list):
            raise ValueError(f"opinion assessment.{key} must be a list")
    pedagogical = parsed.get("pedagogical")
    if mode == MODE_PEDAGOGICAL:
        if not isinstance(pedagogical, dict):
            raise ValueError("pedagogical mode requires a pedagogical object")
        for key in ("learner_explanation", "what_to_try_next"):
            if key not in pedagogical:
                raise ValueError(f"opinion pedagogical missing key: {key}")
        if not isinstance(pedagogical["learner_explanation"], str):
            raise ValueError("opinion pedagogical.learner_explanation must be a string")
        if not isinstance(pedagogical["what_to_try_next"], list):
            raise ValueError("opinion pedagogical.what_to_try_next must be a list")
    else:
        # Consultative opinions may carry a null pedagogical slot.
        if pedagogical is not None:
            raise ValueError("consultative opinion must not carry a pedagogical object")
    return {"assessment": assessment, "pedagogical": pedagogical}


def build_opinion_prompt(
    claim_text: str,
    ei: dict,
    formal: dict,
    machine: dict,
    mode: str,
) -> str:
    """Assemble the opinion prompt (HEURISTIC part: wording is free to
    change; the machine block and the mode contract are not)."""
    ei_conclusion = (ei.get("conclusion") or {}).get("text", "")
    statement = formal.get("statement_text") or ""
    report = formal.get("mapping_report") or []
    mode_line = (
        "Include the `pedagogical` object: explain any failure in plain "
        "learner terms (P1-P6 vocabulary where possible) and list what to "
        "try next."
        if mode == MODE_PEDAGOGICAL
        else "Set `pedagogical` to null."
    )
    return (
        "You are asked for a CONSULTATIVE opinion on a Lean formalization draft "
        "inside LeanEcon's verified workflow.\n"
        "You are NOT an authorized reviewer: never emit ACCEPTED, REJECTED, or "
        "any verdict. You never change lifecycle state. Your prose is AI-opinion "
        "only and cannot override the machine block below.\n\n"
        f"Claim (canonical):\n{claim_text}\n\n"
        f"Accepted interpretation conclusion:\n{ei_conclusion}\n\n"
        f"Formal statement (draft):\n{statement}\n\n"
        f"Mapping report (rows):\n{json.dumps(report, indent=2)}\n\n"
        f"Machine block (deterministic signals — authoritative):\n"
        f"{json.dumps(machine, indent=2)}\n\n"
        "Reply as JSON only:\n"
        "{\n"
        '  "assessment": {\n'
        '    "summary": "<one-paragraph read of fidelity and risks>",\n'
        '    "strengths": ["<what the draft does well>"],\n'
        '    "concerns": ["<fidelity/mapping/probe concerns, citing the claim '
        'or machine signals>"],\n'
        '    "suggestions": ["<concrete next steps for the human author>"]\n'
        "  },\n"
        '  "pedagogical": null | {"learner_explanation": "<plain-language '
        'explanation of the current state and any failure>", '
        '"what_to_try_next": ["<learner next steps>"]}\n'
        "}\n\n"
        f"Mode: {mode}. {mode_line}\n"
    )


def validate_opinion_artifact(record: dict) -> list[str]:
    """Structural validation of a stored opinion artifact. Returns a list
    of problems (empty when valid). The machine block's ``deterministic``
    flag and the digest anchors are part of the contract."""
    problems: list[str] = []
    required = (
        "schema_version",
        "opinion_id",
        "claim_id",
        "surface",
        "mode",
        "requested_at",
        "actor",
        "artifact_anchor",
        "machine_block",
        "assessment",
        "pedagogical",
        "provenance",
    )
    for key in required:
        if key not in record:
            problems.append(f"missing field: {key}")
    for key in RESERVED_OUTCOME_KEYS:
        if key in record:
            problems.append(f"reserved outcome key present: {key}")
    anchor = record.get("artifact_anchor") or {}
    for key in ("formal_digest", "ei_digest", "formal_revision"):
        if not anchor.get(key):
            problems.append(f"artifact_anchor missing: {key}")
    machine = record.get("machine_block") or {}
    if not machine.get("deterministic"):
        problems.append("machine_block must be deterministic")
    provenance = record.get("provenance") or {}
    if provenance.get("kind") != "consultative_opinion":
        problems.append("provenance.kind must be consultative_opinion")
    if provenance.get("capability") != "opinion":
        problems.append("provenance.capability must be opinion")
    return problems
