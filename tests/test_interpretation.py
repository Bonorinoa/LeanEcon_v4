"""Interpretation service tests (docs/gate5/a3-design.md §3)."""

import json

import pytest

from leanecon.interpretation import (
    finalize_ei,
    interpret_prompt,
    load_schema,
    parse_interpret_response,
    validate_ei_candidate,
)
from tests.conftest import valid_ei


def test_valid_candidate_passes():
    assert validate_ei_candidate(valid_ei()) == []


def test_valid_none_noted_candidate_passes():
    assert validate_ei_candidate(valid_ei(none_noted=True)) == []


def test_empty_ambiguities_without_none_noted_fails():
    candidate = valid_ei()
    candidate["ambiguities"] = []
    problems = validate_ei_candidate(candidate)
    assert any("none_noted" in p for p in problems)


def test_none_noted_with_ambiguities_fails():
    candidate = valid_ei(none_noted=True)
    candidate["ambiguities"] = [{"issue": "x", "alternatives": ["a", "b"]}]
    problems = validate_ei_candidate(candidate)
    assert any("none_noted" in p for p in problems)


def test_production_candidate_must_be_pending():
    candidate = valid_ei()
    candidate["review"] = {"decision": "APPROVED", "reviewer": "cto", "event_ref": "evt-1"}
    problems = validate_ei_candidate(candidate)
    assert any("PENDING" in p for p in problems)


def test_accepted_assumptions_must_be_empty_at_production():
    candidate = valid_ei()
    candidate["assumptions"]["accepted"] = ["something"]
    problems = validate_ei_candidate(candidate)
    assert any("accepted" in p for p in problems)


def test_unknown_field_rejected_by_schema():
    candidate = valid_ei()
    candidate["made_up_field"] = True
    assert validate_ei_candidate(candidate) != []


def test_schema_additive_none_noted_exercise():
    # the draft-schema exercise (Q1) added none_noted as an optional field
    schema = load_schema()
    assert "none_noted" in schema["properties"]
    assert "acknowledges_none_noted" in schema["properties"]["review"]["properties"]


def test_finalize_requires_acknowledgement_for_none_noted():
    with pytest.raises(ValueError):
        finalize_ei(valid_ei(none_noted=True), reviewer="cto", event_ref="evt-1")
    finalized = finalize_ei(valid_ei(none_noted=True), reviewer="cto", event_ref="evt-1",
                            acknowledges_none_noted=True)
    assert finalized["review"]["decision"] == "APPROVED"
    assert finalized["review"]["acknowledges_none_noted"] is True
    assert finalized["digest"]


def test_finalize_sets_review_fields():
    finalized = finalize_ei(valid_ei(), reviewer="cto", event_ref="evt-9", notes="ok")
    assert finalized["review"]["reviewer"] == "cto"
    assert finalized["review"]["event_ref"] == "evt-9"


def test_parse_response_strips_code_fences():
    candidate = valid_ei()
    content = f"```json\n{json.dumps(candidate)}\n```"
    assert parse_interpret_response(content) == candidate
    with pytest.raises(ValueError):
        parse_interpret_response("not json at all")


def test_interpret_prompt_mentions_schema_shape_and_no_proof():
    prompt = interpret_prompt("some claim")
    assert "EconomicInterpretation" in prompt
    assert "none_noted" in prompt
    assert "do NOT write Lean code" in prompt
    assert "theorem" not in prompt
    assert "sorry" not in prompt
