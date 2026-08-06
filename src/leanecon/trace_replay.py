"""Trace replay (docs/gate5/a3-design.md §7.5).

Replay is a deterministic VALIDATION of recorded history — not a
re-execution of side effects: no provider calls, no Lean rebuild. It
re-validates every event envelope, re-walks the state machine with the
allowed transition table (including retry edges), recomputes artifact
digests from stored payloads, and re-runs the bundle validator for any
verification events. Mismatches are reported as a list.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from leanecon.bundle import validate_bundle
from leanecon.events import EVENT_CLAIM_STATE_CHANGED, EVENT_VERIFICATION_COMPLETED, validate_event
from leanecon.lifecycle import validate_transition


def _load_events_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _events_for_claim(events: list[dict], claim_id: str) -> list[dict]:
    return sorted(
        (e for e in events if e.get("claim_id") == claim_id),
        key=lambda e: e.get("emitted_at", ""),
    )


def _check_transition(event: dict, problems: list[str]) -> None:
    """Validate one state-change event against the transition table."""
    before: str | None = event.get("state_before")
    after: str | None = event.get("state_after")
    if after is None:
        problems.append(f"{event.get('event_id')}: missing state_after")
        return
    error = validate_transition(before, after)
    if error:
        problems.append(f"{event.get('event_id')}: {error}")


def _replay_bundles(events: list[dict], store, problems: list[str]) -> list[dict]:
    bundles: list[dict] = []
    for event in events:
        if event.get("event_type") != EVENT_VERIFICATION_COMPLETED:
            continue
        bundle_id = event.get("trace_ref")
        if not bundle_id or not bundle_id.startswith("bundle-"):
            continue
        claim_id = event.get("claim_id")
        if not claim_id:
            continue
        try:
            claim = store.load_claim(claim_id)
            checks = validate_bundle(store, bundle_id, claim)
            all_pass = all(c[1] for c in checks)
            manifest = store.read_bundle_manifest(bundle_id)
            result = manifest.get("result")
            verification = store.read_json(store.root / "bundles" / bundle_id / "verification.json")
            # consistency rule: the manifest result must match the verification
            # record's own outcome, and a VERIFIED result additionally requires
            # all 11 checks to pass. A FAILED bundle is a faithful record even
            # when no single check encodes the failure reason (e.g. an
            # audit-layer failure with a successful compile).
            matches_record = result == verification.get("outcome")
            consistent = matches_record and (result != "VERIFIED" or all_pass)
            bundles.append({
                "bundle_id": bundle_id, "result": result, "ok": consistent,
                "checks": [(c[0], c[1]) for c in checks],
            })
            if not consistent:
                if result == "VERIFIED":
                    problems.append(f"bundle {bundle_id}: claims VERIFIED but checks fail: {[c[0] for c in checks if not c[1]]}")
                else:
                    problems.append(f"bundle {bundle_id}: result {result} does not match verification outcome {verification.get('outcome')}")
        except Exception as exc:  # missing artifacts surface as replay problems
            problems.append(f"bundle {bundle_id}: replay error: {exc}")
    return bundles


def replay_run(events_path: Path, store=None) -> dict:
    """Validate one run's event log. store is optional (bundle checks need it)."""
    events = _load_events_log(events_path)
    problems: list[str] = []

    for event in events:
        envelope_problems = validate_event(event)
        if envelope_problems:
            problems.append(f"{event.get('event_id')}: envelope: {'; '.join(envelope_problems)}")
        if event.get("event_type") == EVENT_CLAIM_STATE_CHANGED:
            _check_transition(event, problems)

    claims: dict[str, Any] = {}
    for event in events:
        claim_id = event.get("claim_id")
        if not claim_id:
            continue
        chain = claims.setdefault(claim_id, {"states": [], "problems": []})
        if event.get("event_type") == EVENT_CLAIM_STATE_CHANGED:
            chain["states"].append(
                {"event_id": event.get("event_id"), "from": event.get("state_before"), "to": event.get("state_after")}
            )
        elif event.get("event_type") == EVENT_VERIFICATION_COMPLETED:
            chain["states"].append(
                {"event_id": event.get("event_id"), "to": event.get("state_after"), "verification": True}
            )

    bundles = _replay_bundles(events, store, problems) if store is not None else []

    return {
        "run_id": events[0].get("run_id") if events else None,
        "events": len(events),
        "claims": claims,
        "bundles": bundles,
        "problems": problems,
        "replay_ok": not problems,
    }


def replay_claim(events_dir: Path, claim_id: str, store=None) -> dict:
    """Replay every run touching ``claim_id`` (a walkthrough spans runs).

    Files are read in creation order (mtime_ns) so events with equal
    second-resolution timestamps stay chronologically ordered; the stable
    sort below preserves that order.
    """
    all_events: list[dict] = []
    paths = sorted(Path(events_dir).glob("*.jsonl"), key=lambda p: p.stat().st_mtime_ns)
    for path in paths:
        all_events.extend(_load_events_log(path))
    claim_events = _events_for_claim(all_events, claim_id)
    problems: list[str] = []
    chain: dict[str, Any] = {"states": [], "problems": []}

    for event in claim_events:
        for problem in validate_event(event):
            problems.append(f"{event.get('event_id')}: envelope: {problem}")
        if event.get("event_type") == EVENT_CLAIM_STATE_CHANGED:
            chain["states"].append(
                {"event_id": event.get("event_id"), "from": event.get("state_before"), "to": event.get("state_after")}
            )
            _check_transition(event, problems)
        elif event.get("event_type") == EVENT_VERIFICATION_COMPLETED:
            chain["states"].append(
                {"event_id": event.get("event_id"), "to": event.get("state_after"), "verification": True}
            )

    bundles = _replay_bundles(claim_events, store, problems) if store is not None else []

    return {
        "claim_id": claim_id,
        "events": len(claim_events),
        "claims": chain,
        "bundles": bundles,
        "problems": problems,
        "replay_ok": not problems,
    }
