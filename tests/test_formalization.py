"""Formalization contract tests (docs/gate5/a3-design.md §4)."""

from leanecon.formalization import (
    formalize_prompt,
    material_element_ids,
    parse_formalize_response,
    validate_mapping_report,
)
from tests.conftest import complete_mapping_report, valid_ei


def test_material_element_ids_cover_the_frame():
    ei = valid_ei()
    ids = dict(material_element_ids(ei))
    assert ids["consumer"] == "object"
    assert ids["assumption:0"] == "assumption"
    assert ids["quantifier:0"] == "quantifier"
    assert ids["conclusion"] == "conclusion"
    assert "definition:0" not in ids  # no definitions in this EI


def test_complete_mapping_report_has_no_gaps():
    ei = valid_ei()
    problems, gaps = validate_mapping_report(complete_mapping_report(), ei)
    assert problems == []
    assert gaps == []


def test_missing_row_is_a_gap():
    ei = valid_ei()
    report = [row for row in complete_mapping_report() if row["ei_element_id"] != "conclusion"]
    problems, gaps = validate_mapping_report(report, ei)
    assert any(g["ei_element_id"] == "conclusion" and g["ei_element_kind"] == "conclusion" for g in gaps)


def test_unmapped_material_element_is_a_visible_gap():
    ei = valid_ei()
    report = complete_mapping_report()
    report[0] = {**report[0], "status": "unmapped", "note": "no Mathlib identifier for consumer"}
    problems, gaps = validate_mapping_report(report, ei)
    assert any(g["ei_element_id"] == "consumer" for g in gaps)


def test_material_element_cannot_be_deferred():
    ei = valid_ei()
    report = complete_mapping_report()
    report[-1] = {**report[-1], "status": "deferred"}
    problems, gaps = validate_mapping_report(report, ei)
    assert any("deferred" in p for p in problems)


def test_invalid_status_rejected():
    ei = valid_ei()
    report = complete_mapping_report()
    report[0] = {**report[0], "status": "mystery"}
    problems, gaps = validate_mapping_report(report, ei)
    assert any("invalid status" in p for p in problems)


def test_parse_formalize_response_requires_keys():
    import json

    parsed = parse_formalize_response(json.dumps(
        {"statement": "theorem t : True", "target_theorem": "t", "mapping_report": []}
    ))
    assert parsed["target_theorem"] == "t"
    for bad in (
        json.dumps({"statement": "x"}),
        json.dumps({"statement": "x", "target_theorem": "t", "mapping_report": "nope"}),
        "not json",
    ):
        try:
            parse_formalize_response(bad)
            raise AssertionError("expected ValueError")
        except ValueError:
            pass


def test_formalize_prompt_contains_accepted_ei_not_gold():
    prompt = formalize_prompt(valid_ei())
    assert "mapping_report" in prompt
    assert "never invent a definition" in prompt
    assert "gold" not in prompt.lower() or "hidden" not in prompt.lower()


def test_formalize_prompt_has_hardened_rules():
    """Walkthrough hardening: the prompt now states the failure modes the
    live formalizer exhibited (proof body, invalid binders, tautology)."""
    prompt = formalize_prompt(valid_ei())
    assert "NO `:=`" in prompt
    assert "[Set α]" in prompt  # named as the invalid-binder counter-example
    assert "tautologies" in prompt
    assert "never 'object:u'" in prompt


def test_validate_statement_text_rejects_contract_violations():
    from leanecon.formalization import validate_statement_text

    assert validate_statement_text("theorem t : True") == []
    assert any("sorry" in p for p in validate_statement_text("theorem t : P := by sorry"))
    assert any("admit" in p for p in validate_statement_text("theorem t : P := by admit"))
    assert any("proof body" in p for p in validate_statement_text("theorem t (h : P) : P := h"))


def test_vacuity_warning_detects_tautology():
    from leanecon.formalization import vacuity_warning

    assert vacuity_warning("theorem t (h : P) : P") is not None
    assert vacuity_warning("theorem t (h : P) : P ∧ Q") is None


def test_classify_gaps_distinguishes_id_deviation():
    from leanecon.formalization import classify_gaps

    report = [
        {"ei_element_id": "object:u", "ei_element_kind": "object", "status": "mapped",
         "lean_identifier": "u", "mapping_kind": "mathlib", "provenance": "t", "note": ""},
        {"ei_element_id": "conclusion", "ei_element_kind": "conclusion", "status": "mapped",
         "lean_identifier": "P", "mapping_kind": "mathlib", "provenance": "t", "note": ""},
    ]
    gaps = [
        {"ei_element_id": "u", "ei_element_kind": "object", "reason": "missing mapping row"},
        {"ei_element_id": "x", "ei_element_kind": "object", "reason": "missing mapping row"},
    ]
    classified = classify_gaps(gaps, report)
    by_id = {g["ei_element_id"]: g for g in classified}
    assert by_id["u"]["classification"] == "id_scheme_deviation"   # 'object:u' covers 'u'
    assert by_id["x"]["classification"] == "genuinely_missing"     # no row mentions 'x'
