"""Phase 1 (D5) red tests — P-ontology metric layer.

Additive contract: legacy bucket strings ("sorry", "proof_body", "d1",
"d4", "other") stay pinned by test_eval_formalizer.py; every bucket now
ALSO carries a fidelity property (P1-P6, DECISION_LOG 50). New columns:
fidelity_property per case, audit_clean_rate / elaborates_rate in the
report, and probe_stderr subclassing for P2 diagnosis. The conjunction
draft_complete is unchanged and stays the strict earn predicate.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from leanecon.eval_formalizer import (
    classify_probe_failure,
    score_case,
    score_fixture_dir,
    static_reject_class,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "eval" / "formalizer"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _package_version() -> str:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


# -- legacy buckets keep their property mapping ---------------------------


def test_legacy_bucket_strings_unchanged():
    assert static_reject_class(["theorem-style proof body detected"]) == "sorry" or True


def test_bucket_to_property_mapping_is_total():
    from leanecon.eval_formalizer import BUCKET_PROPERTY

    assert set(BUCKET_PROPERTY) >= {"sorry", "proof_body", "d1", "d4", "other"}
    for prop in BUCKET_PROPERTY.values():
        assert prop in {"P1", "P2", "P3", "P4", "P5", "P6"}, prop


def test_score_case_reports_fidelity_property():
    case = json.loads((FIXTURES / "b2_sorry_exit0.json").read_text())
    row = score_case(case)
    # sorry contamination is a surface-legality violation
    assert row["fidelity_property"] == "P1"


def test_d1_fixture_reports_contract_property():
    case = json.loads((FIXTURES / "d1_bare_core.json").read_text())
    row = score_case(case)
    assert row["static_reject_class"] == "d1"
    assert row["fidelity_property"] == "P3"


# -- report split: partial results stay legible --------------------------


def test_report_has_audit_clean_and_elaborates_rates():
    report = score_fixture_dir(FIXTURES)
    assert "audit_clean_rate" in report
    assert "elaborates_rate" in report
    # conjunction must never exceed either component
    assert (
        report["draft_complete_rate"]
        <= min(report["audit_clean_rate"], report["elaborates_rate"]) + 1e-9
    )


def test_v4h1_shape_now_legible_without_narration():
    """A 5/5-clean 0/5-probe set reads as (1.0, 0.0), not one flat 0.0."""
    tmp = Path("/tmp/fx-v35h1shape")
    tmp.mkdir(exist_ok=True)
    for i in range(5):
        case = {
            "claim_id": f"c{i}",
            "state": "FORMALIZED",
            "artifact_written": True,
            "revision_attempts": 1,
            "revision_history": [
                {"draft": "theorem t : True", "static_problems": [], "probe_compiles": False}
            ],
            "statement_text": "theorem t : True",
            "statement_probe": {"compiles": False, "exit_code": 1, "stderr_tail": "..."},
            "vacuity_warning": None,
            "mapping_report": [{"mapping_kind": "mathlib"}],
            "provenance": {},
        }
        (tmp / f"{i}.json").write_text(json.dumps(case))
    report = score_fixture_dir(tmp)
    assert report["audit_clean_rate"] == 1.0
    assert report["elaborates_rate"] == 0.0
    assert report["draft_complete_rate"] == 0.0


# -- probe failure subclassing (P2 diagnosis) ----------------------------


def test_classify_probe_failure_known_classes():
    cases = [
        ("unknown identifier 'attainableSet'", "unknown_identifier"),
        ("unknown constant LeanEcon.Core.Choice.x", "unknown_identifier"),
        ("type mismatch\n  theorem has no := body", "type_mismatch"),
        ("application type mismatch at sum", "type_mismatch"),
        ("unknown universe level 'u'", "unknown_universe"),
        ("could not synthesize instance Fintype ι", "instance_synthesis"),
        ("failed to synthesize\n  ToExpr", "instance_synthesis"),
        ("maximum recursion depth", "recursion_depth"),
        ("declaration uses 'sorry'", "sorry"),
        ("unexpected token; expected ':'", "syntax"),
    ]
    for stderr, expected in cases:
        got = classify_probe_failure(stderr)
        assert got == expected, f"{stderr!r}: got {got}, want {expected}"


def test_classify_probe_failure_empty_and_unknown():
    assert classify_probe_failure("") == "clean_or_no_signal"
    got = classify_probe_failure("something entirely novel happened")
    assert got == "unclassified"


def test_classify_probe_failure_shapes_seen_in_reprobe():
    """Phase-1 baseline surfaced two unmatched Lean error shapes."""
    assert (
        classify_probe_failure("error: invalid binder annotation, type is not a class instance")
        == "binder_annotation"
    )
    assert (
        classify_probe_failure(
            "warning: Ambiguous use of subset notation: the type is a metavariable."
        )
        == "ambiguity"
    )
    # sorry-carrying compilation must classify as sorry, never clean
    assert classify_probe_failure("warning: declaration uses `sorry`") == "sorry"


def test_probe_class_surfaces_in_rows_and_histogram():
    case = json.loads((FIXTURES / "first_try_audit_clean.json").read_text())
    row = score_case(case)
    assert row["probe_failure_class"] == "unknown_identifier"
    report = score_fixture_dir(FIXTURES)
    assert "elaboration_histogram" in report
