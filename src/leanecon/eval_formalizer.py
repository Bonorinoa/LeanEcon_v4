"""Deterministic formalizer scorer (v3 Phase 2).

Scores committed fixture JSON (or a live-exported case) with no provider
calls. Definitions: ``docs/v3/METRICS.md`` §3.

``first_try_valid`` = attempt 1 audit-clean (probe is not required).
``draft_complete`` = audit-clean AND probe compiles AND no vacuity AND
no inversion heuristic — the 60–70% predicate. Never claim that number
from the fixture set or from v2-memory.

``sole_author_verified`` is true only when the claim is VERIFIED and the
proof is not reviewer-authored.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from leanecon.formalization import CORE_IDENTIFIER_RE, vacuity_warning


def static_reject_class(problems: list[str] | None) -> str | None:
    """Classify the first audit problem into a histogram bucket."""
    if not problems:
        return None
    blob = " ".join(problems).lower()
    if "sorry" in blob or "admit" in blob:
        return "sorry"
    if "proof body" in blob or "':='" in blob or ":= " in blob:
        return "proof_body"
    if "core mapping" in blob or "fully-qualified" in blob:
        return "d1"
    if "root-namespace" in blob or "scaffolding" in blob:
        return "d4"
    return "other"


#: Fidelity-property mapping (DECISION_LOG 50): every legacy bucket is a
#: *measurement of* one property violation. P1 surface legality,
#: P3 contract (D1/D4/mapping), P4 substance, P5 semantic fidelity.
BUCKET_PROPERTY: dict[str, str] = {
    "sorry": "P1",
    "proof_body": "P1",
    "d1": "P3",
    "d4": "P3",
    "other": "P1",
}

_PROBE_CLASSES: tuple[tuple[str, str], ...] = (
    ("declaration uses `sorry`", "sorry"),
    ("declaration uses 'sorry'", "sorry"),
    ("unknown identifier", "unknown_identifier"),
    ("unknown constant", "unknown_identifier"),
    ("invalid binder annotation", "binder_annotation"),
    ("ambiguous use of", "ambiguity"),
    ("could not synthesize", "instance_synthesis"),
    ("failed to synthesize", "instance_synthesis"),
    ("type mismatch", "type_mismatch"),
    ("application type mismatch", "type_mismatch"),
    ("unknown universe level", "unknown_universe"),
    ("maximum recursion depth", "recursion_depth"),
    ("unexpected token", "syntax"),
)


def classify_probe_failure(stderr_tail: str | None) -> str:
    """Deterministic subclass of a failed compile probe (P2 diagnosis).

    Ordered: identity errors before type mismatches, because an unknown
    Core id also produces follow-on type noise. Empty/None means the
    probe never produced a signal; anything unmatched stays honest as
    ``unclassified`` rather than being forced into a bucket.
    """
    text = (stderr_tail or "").strip().lower()
    if not text:
        return "clean_or_no_signal"
    for needle, klass in _PROBE_CLASSES:
        if needle in text:
            return klass
    return "unclassified"


def _history(case: dict) -> list[dict]:
    return list(case.get("revision_history") or [])


def _attempt_audit_clean(item: dict) -> bool:
    return not list(item.get("static_problems") or [])


def _d1_core_fq(case: dict) -> bool | None:
    report = case.get("mapping_report")
    if not isinstance(report, list) or not report:
        return None
    core_rows = [
        row for row in report if isinstance(row, dict) and row.get("mapping_kind") == "core"
    ]
    if not core_rows:
        return None
    return all(
        bool(CORE_IDENTIFIER_RE.match(row.get("lean_identifier") or "")) for row in core_rows
    )


def _inversion_flag(statement: str | None) -> bool:
    """Cheap heuristic: conclusion restates a hypothesis (same as vacuity)."""
    if not statement:
        return False
    return vacuity_warning(statement) is not None


def _vacuity_flag(case: dict) -> bool:
    warning = case.get("vacuity_warning")
    if warning:
        return True
    return _inversion_flag(case.get("statement_text"))


def _sole_author_verified(case: dict) -> bool:
    if not case.get("verified") and case.get("state") != "VERIFIED":
        return False
    provenance = case.get("provenance") or {}
    if provenance.get("reviewer_authored_formal") or provenance.get("source") == "from_file":
        return False
    if case.get("proof_provenance") == "reviewer":
        return False
    return True


def _attempts_to_valid(history: list[dict]) -> int | None:
    for index, item in enumerate(history, start=1):
        if _attempt_audit_clean(item):
            return index
    return None


def _draft_complete(case: dict, first_clean_item: dict | None) -> bool:
    if first_clean_item is None:
        return False
    statement = case.get("statement_text") or first_clean_item.get("draft") or ""
    if static_reject_class(first_clean_item.get("static_problems")):
        return False
    probe = case.get("statement_probe") or {}
    compiles = bool(probe.get("compiles"))
    if not compiles:
        return False
    if _vacuity_flag(case) or _inversion_flag(statement):
        return False
    return True


def score_case(case: dict) -> dict[str, Any]:
    history = _history(case)
    first = history[0] if history else None
    first_try_valid = bool(first and _attempt_audit_clean(first))
    attempts = _attempts_to_valid(history)
    first_clean = None
    if attempts is not None:
        first_clean = history[attempts - 1]
    reject = None
    if first and not _attempt_audit_clean(first):
        reject = static_reject_class(first.get("static_problems"))
    elif case.get("revision_history"):
        # last failed attempt class if nothing cleaned
        if attempts is None and history:
            reject = static_reject_class(history[-1].get("static_problems"))
    probe = case.get("statement_probe") or {}
    # P-ontology columns (DECISION_LOG 50). fidelity_property labels the
    # violated property when the claim never produced an audit-clean
    # attempt; a clean-then-probed claim that fails only at the kernel
    # signal is a P2 (elaboration) measurement.
    if reject:
        fidelity = BUCKET_PROPERTY.get(reject, "P1")
    elif attempts is not None and not _draft_complete(case, first_clean):
        fidelity = "P2"
    else:
        fidelity = None
    return {
        "claim_id": case.get("claim_id"),
        "state": case.get("state"),
        "artifact_written": bool(case.get("artifact_written")),
        "first_try_valid": first_try_valid,
        "attempts_to_valid": attempts,
        "static_reject_class": reject,
        "fidelity_property": fidelity,
        "probe_compiles": probe.get("compiles") if probe else None,
        "probe_failure_class": (
            classify_probe_failure(probe.get("stderr_tail"))
            if probe and not probe.get("compiles")
            else None
        ),
        "vacuity_flag": _vacuity_flag(case),
        "inversion_flag": _inversion_flag(case.get("statement_text")),
        "d1_core_fq": _d1_core_fq(case),
        "draft_complete": _draft_complete(case, first_clean),
        "sole_author_verified": _sole_author_verified(case),
        "revision_attempts": case.get("revision_attempts") or len(history),
    }


def score_fixture_dir(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    cases: list[dict] = []
    for path in sorted(root.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.setdefault("claim_id", path.stem)
        cases.append(score_case(payload))
    n = len(cases)
    first_try = sum(1 for row in cases if row["first_try_valid"])
    draft = sum(1 for row in cases if row["draft_complete"])
    sole = sum(1 for row in cases if row["sole_author_verified"])
    audit_clean = sum(1 for row in cases if row["attempts_to_valid"] is not None)
    elaborates = sum(1 for row in cases if row["probe_compiles"])
    histogram: dict[str, int] = {}
    for row in cases:
        klass = row["static_reject_class"]
        if klass:
            histogram[klass] = histogram.get(klass, 0) + 1
    # D5: the strict conjunction split into its components, so a partial
    # result (e.g. v4h1: 100% clean, 0% elaborates) is legible without
    # narration. draft_complete stays the earn predicate.
    fidelity_histogram: dict[str, int] = {}
    for row in cases:
        prop = row.get("fidelity_property")
        if prop:
            fidelity_histogram[prop] = fidelity_histogram.get(prop, 0) + 1
    elaboration_histogram: dict[str, int] = {}
    for row in cases:
        klass = row.get("probe_failure_class")
        if klass and klass != "clean_or_no_signal":
            elaboration_histogram[klass] = elaboration_histogram.get(klass, 0) + 1
    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "n": n,
        "provider_calls": 0,
        "first_try_valid_rate": (first_try / n) if n else 0.0,
        "draft_complete_rate": (draft / n) if n else 0.0,
        "audit_clean_rate": (audit_clean / n) if n else 0.0,
        "elaborates_rate": (elaborates / n) if n else 0.0,
        "sole_author_verified_rate": (sole / n) if n else 0.0,
        "static_reject_histogram": histogram,
        "fidelity_histogram": fidelity_histogram,
        "elaboration_histogram": elaboration_histogram,
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score committed formalizer fixtures (no provider)."
    )
    parser.add_argument("--fixtures", required=True, help="directory of fixture JSON files")
    parser.add_argument("--json-out", default="", help="write the report JSON here")
    parser.add_argument("--md-out", default="", help="optional markdown table")
    args = parser.parse_args(argv)
    report = score_fixture_dir(args.fixtures)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.md_out:
        lines = [
            "# Formalizer fixture score (generated)",
            "",
            f"n={report['n']} provider_calls={report['provider_calls']}",
            f"first_try_valid_rate={report['first_try_valid_rate']:.3f}",
            f"draft_complete_rate={report['draft_complete_rate']:.3f} (not a 60–70% claim)",
            f"sole_author_verified_rate={report['sole_author_verified_rate']:.3f}",
            "",
            "| claim_id | first_try_valid | attempts_to_valid | draft_complete | sole_author |",
            "|---|---|---|---|---|",
        ]
        for row in report["cases"]:
            lines.append(
                f"| {row['claim_id']} | {row['first_try_valid']} | {row['attempts_to_valid']} | "
                f"{row['draft_complete']} | {row['sole_author_verified']} |"
            )
        Path(args.md_out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
