"""Phase 2 red tests — deterministic formalizer scorer (INIT_V3 / METRICS).

The scorer must run on committed fixtures with no live provider.
Hand-edited numbers after this exists are a bug.

Attribution: Hermes Agent (Nous Research) under CTO direction.
"""

from __future__ import annotations

import json
from pathlib import Path

from leanecon.eval_formalizer import (
    score_case,
    score_fixture_dir,
    static_reject_class,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "eval" / "formalizer"


def test_first_try_valid_is_audit_clean_attempt_one():
    case = json.loads((FIXTURES / "first_try_audit_clean.json").read_text())
    row = score_case(case)
    assert row["first_try_valid"] is True
    assert row["attempts_to_valid"] == 1
    assert row["draft_complete"] is False  # probe fails → not 60–70%


def test_attempt_two_valid_records_two():
    case = json.loads((FIXTURES / "attempt_two_clean.json").read_text())
    row = score_case(case)
    assert row["first_try_valid"] is False
    assert row["attempts_to_valid"] == 2


def test_exhausted_budget_is_null_attempts_and_not_valid():
    case = json.loads((FIXTURES / "exhausted_budget.json").read_text())
    row = score_case(case)
    assert row["first_try_valid"] is False
    assert row["attempts_to_valid"] is None
    assert row["state"] == "FAILED"
    assert row["artifact_written"] is False


def test_sorry_contamination_never_draft_complete_even_if_probe_compiles():
    """B2: exit 0 + sorry is not a quality win."""
    case = json.loads((FIXTURES / "b2_sorry_exit0.json").read_text())
    row = score_case(case)
    assert row["first_try_valid"] is False
    assert row["draft_complete"] is False
    assert static_reject_class(case["revision_history"][0]["static_problems"]) == "sorry"


def test_d1_bare_core_classified():
    case = json.loads((FIXTURES / "d1_bare_core.json").read_text())
    row = score_case(case)
    assert row["d1_core_fq"] is False
    assert row["static_reject_class"] == "d1"


def test_vacuity_flag_from_artifact():
    case = json.loads((FIXTURES / "vacuous.json").read_text())
    row = score_case(case)
    assert row["vacuity_flag"] is True
    assert row["draft_complete"] is False


def test_sole_author_verified_zero_unless_model_proof():
    case = json.loads((FIXTURES / "reviewer_verified.json").read_text())
    row = score_case(case)
    assert row["sole_author_verified"] is False


def test_fixture_dir_is_deterministic_and_has_no_live_provider():
    report = score_fixture_dir(FIXTURES)
    assert report["n"] >= 6
    assert report["provider_calls"] == 0
    # Re-run is byte-stable on the JSON payload (ignore generated_at).
    again = score_fixture_dir(FIXTURES)
    a = {k: v for k, v in report.items() if k != "generated_at"}
    b = {k: v for k, v in again.items() if k != "generated_at"}
    assert a == b
    assert report["sole_author_verified_rate"] == 0.0
    # 60–70% is computed but must not be claimed from this fixture set.
    assert "draft_complete_rate" in report


def test_scorer_cli_writes_json(tmp_path):
    from leanecon.eval_formalizer import main

    out = tmp_path / "score.json"
    rc = main(["--fixtures", str(FIXTURES), "--json-out", str(out)])
    assert rc == 0
    payload = json.loads(out.read_text())
    assert payload["n"] >= 6
    assert payload["provider_calls"] == 0
