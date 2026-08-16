from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

from leanecon.eval_protocol import (
    PROTOCOL_ID,
    canonical_digest,
    score_semantic_reviews,
    seal_manifest,
    validate_manifest,
    validate_semantic_review,
    write_manifest,
)

# Synthetic only — not a live economics claim and not a spent holdout.
SYNTHETIC_CLAIM = "Synthetic fixture claim used only to exercise the sealed-manifest scorer."
SYNTHETIC_FORMAL = "theorem syn_fixture : True"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _synthetic_manifest():
    return seal_manifest(PROTOCOL_ID, [{"case_id": "syn-1", "claim_text": SYNTHETIC_CLAIM}])


def _review(decision: str, reviewer_id: str) -> dict:
    return {
        "case_id": "syn-1",
        "reviewer_id": reviewer_id,
        "reviewed_at": "2026-08-16T00:00:00Z",
        "formal_digest": canonical_digest(SYNTHETIC_FORMAL),
        "decision": decision,
        "rationale": "Fixture rationale; not a semantic judgment of a real claim.",
    }


def test_sealed_manifest_keeps_heldout_text_out_of_the_result():
    manifest = _synthetic_manifest()
    assert manifest["split"] == "held_out"
    assert manifest["protocol_id"] == PROTOCOL_ID
    assert manifest["cases"] == [
        {"case_id": "syn-1", "claim_digest": canonical_digest(SYNTHETIC_CLAIM)}
    ]
    assert "claim_text" not in manifest["cases"][0]
    assert validate_manifest(manifest) == []


def test_heldout_manifest_rejects_text_and_gold():
    manifest = _synthetic_manifest()
    manifest["cases"][0]["expected_lean"] = "theorem leaked : True"
    assert (
        "case syn-1: held-out manifests must not contain claim text or gold"
        in validate_manifest(manifest)
    )


def test_write_manifest_refuses_leaked_gold(tmp_path):
    manifest = _synthetic_manifest()
    manifest["cases"][0]["gold"] = "leaked"
    with pytest.raises(ValueError, match="held-out manifests must not contain"):
        write_manifest(tmp_path / "manifest.json", manifest)


def test_semantic_review_scoring_requires_complete_independent_records():
    manifest = _synthetic_manifest()
    review = _review("faithful", "reviewer-a")
    assert validate_semantic_review(review, manifest) == []
    report = score_semantic_reviews(manifest, [review])
    assert report["semantic_acceptance_rate"] == 1.0
    assert report["cases_with_two_reviews"] == 0
    assert report["cases_with_disagreement"] == 0


def test_two_reviewers_disagreement_is_counted_not_adjudicated():
    manifest = _synthetic_manifest()
    report = score_semantic_reviews(
        manifest,
        [_review("faithful", "reviewer-a"), _review("material_deviation", "reviewer-b")],
    )
    assert report["cases_with_two_reviews"] == 1
    assert report["cases_with_disagreement"] == 1
    assert report["decision_counts"] == {"faithful": 1, "material_deviation": 1}
    assert report["semantic_acceptance_rate"] == 0.5


def test_invalid_semantic_review_is_rejected():
    manifest = _synthetic_manifest()
    with pytest.raises(ValueError, match="unknown case_id"):
        score_semantic_reviews(
            manifest,
            [
                {
                    "case_id": "unknown",
                    "reviewer_id": "reviewer-a",
                    "reviewed_at": "2026-08-16T00:00:00Z",
                    "formal_digest": "0" * 64,
                    "decision": "faithful",
                    "rationale": "No basis.",
                }
            ],
        )


def test_cli_scores_sealed_tmp_fixture(tmp_path):
    manifest = _synthetic_manifest()
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    write_manifest(tmp_path / "manifest.json", manifest)
    (reviews_dir / "a.json").write_text(json.dumps(_review("faithful", "reviewer-a")))
    (reviews_dir / "b.json").write_text(json.dumps(_review("faithful", "reviewer-b")))

    ns = runpy.run_path(
        str(REPO_ROOT / "scripts" / "eval_semantic_reviews.py"), run_name="not_main"
    )
    out = tmp_path / "report.json"
    rc = ns["main"](
        [
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--reviews-dir",
            str(reviews_dir),
            "--json-out",
            str(out),
        ]
    )
    assert rc == 0
    report = json.loads(out.read_text())
    assert report["case_count"] == 1
    assert report["cases_with_two_reviews"] == 1
    assert report["semantic_acceptance_rate"] == 1.0
    assert report["cases_with_disagreement"] == 0
    assert "claim_text" not in json.loads((tmp_path / "manifest.json").read_text())["cases"][0]
