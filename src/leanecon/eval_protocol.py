"""Sealed evaluation and semantic-review accounting.

The formalizer scorer (``leanecon.eval_formalizer``) measures mechanical
draft hygiene. This module keeps semantic assessment separate: an
evaluator seals a held-out manifest without putting claim text or
expected Lean in the runtime repository, and reviewers record independent
meaning judgments against digested artifacts.

Do not collapse the three facts:

1. draft hygiene — deterministic scorer
2. kernel verification — Lean + 12-check bundle
3. semantic fidelity — reviewer-owned

Protocol id ``formalizer-sealed-1`` is the measurement program for the
*next* held-out set. Spent splits ``v3h`` / ``v3h2`` stay historical.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
PROTOCOL_ID = "formalizer-sealed-1"
SPLITS = frozenset({"development", "held_out"})
SEMANTIC_DECISIONS = frozenset({"faithful", "material_deviation", "insufficient_evidence"})


def canonical_digest(value: Any) -> str:
    """Return a stable SHA-256 digest for protocol material."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def seal_manifest(
    protocol_id: str, cases: list[dict[str, str]], *, split: str = "held_out"
) -> dict[str, Any]:
    """Create a text-free manifest from evaluator-held cases.

    ``cases`` stays outside the repository. Each input needs ``case_id`` and
    ``claim_text``; the returned manifest retains only its digest, preventing
    the application, CI fixtures, and prompt-development loop from reading
    held-out language or gold-shaped targets.
    """
    if split not in SPLITS:
        raise ValueError(f"unsupported split: {split}")
    sealed_cases: list[dict[str, str]] = []
    for case in cases:
        case_id = str(case.get("case_id") or "")
        claim_text = str(case.get("claim_text") or "")
        if not case_id or not claim_text:
            raise ValueError("each sealed case requires case_id and claim_text")
        sealed_cases.append({"case_id": case_id, "claim_digest": canonical_digest(claim_text)})
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": protocol_id,
        "split": split,
        "cases": sealed_cases,
    }
    problems = validate_manifest(manifest)
    if problems:
        raise ValueError("invalid sealed manifest: " + "; ".join(problems))
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return contract violations; held-out manifests must not contain text."""
    problems: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(manifest.get("protocol_id"), str) or not manifest["protocol_id"].strip():
        problems.append("protocol_id is required")
    split = manifest.get("split")
    if split not in SPLITS:
        problems.append(f"split must be one of {sorted(SPLITS)}")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        return problems + ["cases must be a non-empty list"]
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            problems.append("cases must contain objects")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            problems.append("case_id is required")
            continue
        if case_id in seen:
            problems.append(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        digest = case.get("claim_digest")
        if not isinstance(digest, str) or len(digest) != 64:
            problems.append(f"case {case_id}: claim_digest must be a SHA-256 hex digest")
        if split == "held_out" and any(
            key in case for key in ("claim_text", "expected_lean", "gold")
        ):
            problems.append(
                f"case {case_id}: held-out manifests must not contain claim text or gold"
            )
    return problems


def validate_semantic_review(review: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Validate one independent semantic judgment against a sealed manifest."""
    problems: list[str] = []
    case_ids = {case.get("case_id") for case in manifest.get("cases", []) if isinstance(case, dict)}
    for field in ("case_id", "reviewer_id", "reviewed_at", "formal_digest", "rationale"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            problems.append(f"{field} is required")
    if review.get("case_id") not in case_ids:
        problems.append(f"unknown case_id: {review.get('case_id')!r}")
    if review.get("decision") not in SEMANTIC_DECISIONS:
        problems.append(f"decision must be one of {sorted(SEMANTIC_DECISIONS)}")
    formal_digest = review.get("formal_digest")
    if isinstance(formal_digest, str) and len(formal_digest) != 64:
        problems.append("formal_digest must be a SHA-256 hex digest")
    return problems


def score_semantic_reviews(
    manifest: dict[str, Any], reviews: list[dict[str, Any]]
) -> dict[str, Any]:
    """Score independent semantic reviews without inferring their judgments."""
    manifest_problems = validate_manifest(manifest)
    if manifest_problems:
        raise ValueError("invalid manifest: " + "; ".join(manifest_problems))
    all_problems: list[str] = []
    by_case: dict[str, list[dict[str, Any]]] = {}
    for review in reviews:
        problems = validate_semantic_review(review, manifest)
        if problems:
            all_problems.extend(problems)
            continue
        by_case.setdefault(review["case_id"], []).append(review)
    if all_problems:
        raise ValueError("invalid semantic reviews: " + "; ".join(all_problems))

    decisions = Counter(review["decision"] for review in reviews)
    resolved = decisions["faithful"] + decisions["material_deviation"]
    case_ids = [case["case_id"] for case in manifest["cases"]]
    multi_reviewed = sum(len(by_case.get(case_id, [])) >= 2 for case_id in case_ids)
    disagreements = 0
    for case_id in case_ids:
        unique = {item["decision"] for item in by_case.get(case_id, [])}
        if len(unique) > 1:
            disagreements += 1
    return {
        "protocol_id": manifest["protocol_id"],
        "schema_version": SCHEMA_VERSION,
        "split": manifest["split"],
        "case_count": len(case_ids),
        "review_count": len(reviews),
        "cases_with_reviews": sum(bool(by_case.get(case_id)) for case_id in case_ids),
        "cases_with_two_reviews": multi_reviewed,
        "cases_with_disagreement": disagreements,
        "decision_counts": dict(sorted(decisions.items())),
        "semantic_acceptance_rate": decisions["faithful"] / resolved if resolved else None,
        "insufficient_evidence_rate": decisions["insufficient_evidence"] / len(reviews)
        if reviews
        else None,
    }


def load_reviews(directory: Path) -> list[dict[str, Any]]:
    """Load committed or evaluator-provided JSON review records deterministically."""
    reviews: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: review must be a JSON object")
        reviews.append(payload)
    return reviews


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write a validated manifest. Held-out files must stay text-free."""
    problems = validate_manifest(manifest)
    if problems:
        raise ValueError("invalid sealed manifest: " + "; ".join(problems))
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
