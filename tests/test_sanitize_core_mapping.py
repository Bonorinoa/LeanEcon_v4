"""Tests for sanitize_core_mapping_rows (v4 lever extension, Day 3)."""

from __future__ import annotations

from leanecon.formalization import sanitize_core_mapping_rows


def test_trims_application_suffix_from_core_row():
    report = [
        {
            "ei_element_id": "budget_set",
            "ei_element_kind": "definition",
            "lean_identifier": "attainableSet p e",
            "mapping_kind": "core",
            "status": "mapped",
            "provenance": "",
            "note": "",
        }
    ]
    out, notes = sanitize_core_mapping_rows(report)
    assert out[0]["mapping_kind"] == "core"
    assert out[0]["lean_identifier"] == "LeanEcon.Core.Choice.attainableSet"
    assert notes


def test_bare_core_name_downgrades_to_local_definition():
    """A core row whose identifier cannot become a valid FQ Core id is
    downgraded to local_definition (honest: not Core vocabulary)."""
    report = [
        {
            "ei_element_id": "strictly_increasing_utility",
            "ei_element_kind": "assumption",
            "lean_identifier": "StrictMono u",
            "mapping_kind": "core",
            "status": "mapped",
            "provenance": "",
            "note": "",
        }
    ]
    out, notes = sanitize_core_mapping_rows(report)
    assert out[0]["mapping_kind"] == "local_definition"
    assert any("downgraded" in n for n in notes)


def test_valid_fq_core_row_untouched():
    good = {
        "ei_element_id": "conclusion",
        "ei_element_kind": "conclusion",
        "lean_identifier": "LeanEcon.Core.Choice.attainableSet",
        "mapping_kind": "core",
        "status": "mapped",
        "provenance": "",
        "note": "",
    }
    out, notes = sanitize_core_mapping_rows([good])
    assert out == [good]
    assert notes == []


def test_non_core_rows_untouched():
    rows = [
        {
            "ei_element_id": "x",
            "ei_element_kind": "object",
            "lean_identifier": "f x",
            "mapping_kind": "mathlib",
            "status": "mapped",
            "provenance": "",
            "note": "",
        },
        {
            "ei_element_id": "y",
            "ei_element_kind": "object",
            "lean_identifier": "hu",
            "mapping_kind": "local_definition",
            "status": "mapped",
            "provenance": "",
            "note": "",
        },
    ]
    out, notes = sanitize_core_mapping_rows(rows)
    assert out == rows
    assert notes == []


def test_known_core_names_get_fq_prefix():
    """'attainableSet' alone (no application args) is promoted to the FQ
    LeanEcon.Core id when the bare name matches a known Core declaration."""
    report = [
        {
            "ei_element_id": "budget_set",
            "ei_element_kind": "definition",
            "lean_identifier": "attainableSet",
            "mapping_kind": "core",
            "status": "mapped",
            "provenance": "",
            "note": "",
        }
    ]
    out, notes = sanitize_core_mapping_rows(report)
    assert out[0]["lean_identifier"] == "LeanEcon.Core.Choice.attainableSet"
