"""v3 Phase 1 red tests — wire revise_loop into live formalize_claim.

TDD per docs/v3/PLAN.md and INIT_V3 D1–D5. Watch these fail on the
single-shot formalize_claim, then implement the minimal wiring.

The three non-negotiables:

1. CONTAMINATION: a sorry / theorem-body ``:=`` draft is still FAILED
   after the loop; no formal artifact; audit wins even if a naive probe
   would report compiles.
2. BUDGET: a draft that never cleans yields exactly MAX_REVISION_ATTEMPTS
   provider drafts, then FAILED; no silent 4th.
3. ATTEMPT-2 SUCCESS: dirty attempt 1 + audit-clean attempt 2 is
   FORMALIZED with ``revision_attempts == 2`` on the written candidate.

``--from-file`` is not these tests (existing suite). Probe is a signal
(D2): audit-clean + probe-fail is still FORMALIZED.

Attribution: Hermes Agent (Nous Research) under CTO direction; CTO
remains the sole semantic approver.
"""

from __future__ import annotations

import json

import pytest

from leanecon import a3_runner
from leanecon.claim_store import ArtifactStore, ClaimRecord
from leanecon.events import EventLog
from leanecon.revise_loop import MAX_REVISION_ATTEMPTS
from tests.conftest import (
    WORKSPACE,
    FakeAdapter,
    formalize_output,
    valid_ei,
)

C1_THEOREM = "leanecon_c1_attainable_monotone"


@pytest.fixture(autouse=True)
def _fast_probe(monkeypatch):
    """Keep mocked formalize runs fast and CI-deterministic: the live loop now
    calls the real compile probe, which is a `lake env lean` call. Unit tests
    patch it; the probe itself has a dedicated real-workspace test."""
    monkeypatch.setattr(
        a3_runner,
        "probe_statement_compiles",
        lambda *a, **k: {"compiles": True, "exit_code": 0, "stderr_tail": ""},
    )
    yield


def _accepted_claim(
    tmp_path, claim_id: str
) -> tuple[ArtifactStore, ClaimRecord, object, str, EventLog]:
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id=claim_id, revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei(claim_id, valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs(claim_id)[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    return store, claim, events_dir, run_id, log


def _sequence_factory(outputs):
    """formalize_factory that yields ``outputs`` then repeats the last."""
    it = iter(outputs)
    last = outputs[-1]

    def factory():
        return next(it, last)

    return factory


def _state_events(events_dir):
    records = [
        json.loads(line)
        for path in events_dir.glob("*.jsonl")
        for line in path.read_text().splitlines()
        if line.strip()
    ]
    return [r for r in records if r.get("event_type") == "CLAIM_STATE_CHANGED"]


def test_a3_runner_imports_revise_loop():
    """library ≠ product flips when the live path actually calls the loop."""
    from pathlib import Path

    source = Path(a3_runner.__file__).read_text(encoding="utf-8")
    assert "from leanecon.revise_loop import" in source
    assert "revise_statement_draft" in source


def test_contaminated_draft_still_fails_after_loop_and_writes_no_artifact(tmp_path, monkeypatch):
    """B2 / D2: sorry-carrying draft is rejected by audit even if probe compiles.

    Single-shot today already fails on the first sorry and never retries.
    After wiring, three contaminated drafts still FAIL with no artifact.
    """
    monkeypatch.setattr(
        a3_runner,
        "probe_statement_compiles",
        lambda *a, **k: {"compiles": True, "exit_code": 0, "stderr_tail": ""},
    )
    store, claim, events_dir, run_id, log = _accepted_claim(tmp_path, "c-loop-sorry")
    dirty = formalize_output(f"theorem {C1_THEOREM} : True := by sorry", C1_THEOREM)
    adapter = FakeAdapter(formalize_factory=_sequence_factory([dirty, dirty, dirty, dirty]))

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)

    assert state == "FAILED"
    assert candidate is None
    assert store.formal_revs("c-loop-sorry") == []
    assert len(adapter.requests_seen) == MAX_REVISION_ATTEMPTS
    failed = [e for e in _state_events(events_dir) if e.get("state_after") == "FAILED"]
    assert failed
    detail = failed[-1].get("detail") or {}
    assert detail.get("attempts_used") == MAX_REVISION_ATTEMPTS
    assert detail.get("revision_history")
    assert any(
        "sorry" in str(p) for p in (detail["revision_history"][0].get("static_problems") or [])
    )


def test_attempt_budget_is_enforced_no_silent_fourth_provider_call(tmp_path):
    """A draft that never cleans consumes exactly MAX_REVISION_ATTEMPTS requests."""
    store, claim, events_dir, run_id, log = _accepted_claim(tmp_path, "c-loop-budget")
    dirty = formalize_output("theorem t : True := by sorry", "t")
    fourth = formalize_output("theorem t : True", "t")  # would be valid if a 4th ran
    adapter = FakeAdapter(formalize_factory=_sequence_factory([dirty, dirty, dirty, fourth]))

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)

    assert state == "FAILED"
    assert candidate is None
    assert store.formal_revs("c-loop-budget") == []
    assert len(adapter.requests_seen) == MAX_REVISION_ATTEMPTS
    # The 4th (clean) draft must never have been requested.
    payloads = [r["payload"] for r in adapter.requests_seen]
    assert len(payloads) == MAX_REVISION_ATTEMPTS


def test_attempt_two_success_records_revision_attempts_equals_two(tmp_path):
    """Dirty attempt 1, audit-clean attempt 2 → FORMALIZED + revision_attempts=2."""
    store, claim, events_dir, run_id, log = _accepted_claim(tmp_path, "c-loop-ok2")
    dirty = formalize_output("theorem t : True := by sorry", "t")
    clean = formalize_output("theorem t : True", "t")
    adapter = FakeAdapter(formalize_factory=_sequence_factory([dirty, clean]))

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)

    assert state == "FORMALIZED"
    assert candidate is not None
    assert candidate["revision_attempts"] == 2
    assert candidate["target_theorem"] == "t"
    assert len(candidate["revision_history"]) == 2
    assert candidate["revision_history"][0]["static_problems"]
    formal = store.read_formal("c-loop-ok2", store.formal_revs("c-loop-ok2")[-1])
    assert formal["revision_attempts"] == 2
    assert len(adapter.requests_seen) == 2
    # Second request must have been given prior feedback (kernel/static).
    second_prompt = adapter.requests_seen[1]["payload"]["prompt"]
    assert "sorry" in second_prompt.lower() or "static" in second_prompt.lower()


def test_audit_clean_probe_fail_retries_then_keeps_formalized(tmp_path, monkeypatch):
    """D2: probe-fail does not FAIL the claim. Leftover budget may chase compile."""
    probes = iter(
        [
            {"compiles": False, "exit_code": 1, "stderr_tail": "unknown identifier"},
            {"compiles": True, "exit_code": 0, "stderr_tail": ""},
        ]
    )
    monkeypatch.setattr(
        a3_runner,
        "probe_statement_compiles",
        lambda *a, **k: next(probes),
    )
    store, claim, events_dir, run_id, log = _accepted_claim(tmp_path, "c-loop-probe")
    clean = formalize_output("theorem t : True", "t")
    adapter = FakeAdapter(formalize_factory=_sequence_factory([clean, clean]))

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)

    assert state == "FORMALIZED"
    assert candidate is not None
    assert candidate["revision_attempts"] == 2
    assert candidate["statement_probe"]["compiles"] is True
    assert len(adapter.requests_seen) == 2
    second_prompt = adapter.requests_seen[1]["payload"]["prompt"]
    assert "unknown identifier" in second_prompt


def test_three_audit_clean_probe_fails_still_formalized(tmp_path, monkeypatch):
    monkeypatch.setattr(
        a3_runner,
        "probe_statement_compiles",
        lambda *a, **k: {"compiles": False, "exit_code": 1, "stderr_tail": "boom"},
    )
    store, claim, events_dir, run_id, log = _accepted_claim(tmp_path, "c-loop-p3")
    clean = formalize_output("theorem t : True", "t")
    adapter = FakeAdapter(formalize_factory=_sequence_factory([clean, clean, clean, clean]))

    state, candidate = a3_runner.formalize_claim(claim, store, log, run_id, adapter, WORKSPACE)

    assert state == "FORMALIZED"
    assert candidate is not None
    assert candidate["revision_attempts"] == 3
    assert candidate["statement_probe"]["compiles"] is False
    assert len(adapter.requests_seen) == 3
