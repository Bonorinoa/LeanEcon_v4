"""v3 Phase 3 red tests — skeleton CLI + verify gate.

INIT_V3 Phase 3: first allowed additive CLI. Unresolved ``-- GAP:``
never reaches verify. Measurement uses committed fixtures (no live
model skeleton on v3p1).

Attribution: Hermes Agent (Nous Research) under CTO direction.
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from leanecon import a3_runner
from leanecon.claim_store import ArtifactStore, ClaimRecord
from leanecon.skeleton import skeleton_edit_distance, validate_skeleton
from tests.conftest import formalize_output, valid_ei, WORKSPACE

SKELETON = """theorem t : True := by
  have h1 : True := by
    -- GAP: close True
    sorry
"""


def _args(tmp_path, **kwargs) -> Namespace:
    base = {
        "events_dir": str(tmp_path / "events"),
        "reviewer_kind": "",
        "from_file": "",
        "statement_file": "",
        "mapping_file": "",
        "target_theorem": "",
        "force": False,
        "skeleton": "",
        "file": "",
        "proof": "",
        "timeout": 120,
        "notes": "",
        "reviewer": "cto",
    }
    base.update(kwargs)
    return Namespace(**base)


def _formalized(tmp_path, claim_id: str = "c-skel"):
    store = ArtifactStore(tmp_path)
    claim = ClaimRecord(claim_id=claim_id, revision=1, source_text="claim", data_class="PROJECT")
    store.save_claim(claim)
    store.write_ei(claim_id, valid_ei(), status="accepted")
    claim.state = "ACCEPTED"
    claim.accepted_ei_rev = store.ei_revs(claim_id)[-1]
    store.save_claim(claim)
    events_dir = tmp_path / "events"
    run_id, log = a3_runner._new_run(events_dir)
    from tests.conftest import FakeAdapter

    state, _ = a3_runner.formalize_claim(
        claim, store, log, run_id,
        FakeAdapter(formalize_factory=lambda: formalize_output("theorem t : True", "t")),
        WORKSPACE,
    )
    claim.state = state
    claim.formal_rev = store.formal_revs(claim_id)[-1]
    store.save_claim(claim)
    return store, claim


def test_a3_runner_imports_skeleton():
    source = Path(a3_runner.__file__).read_text(encoding="utf-8")
    assert "from leanecon.skeleton import" in source
    assert "cmd_skeleton" in source


def test_skeleton_subcommand_stores_drafting_artifact(tmp_path):
    store, claim = _formalized(tmp_path)
    path = tmp_path / "skel.lean"
    path.write_text(SKELETON, encoding="utf-8")
    rc = a3_runner.cmd_skeleton(
        _args(tmp_path, claim_id=claim.claim_id, file=str(path)), store
    )
    assert rc == 0
    assert store.skeleton_revs(claim.claim_id) == [1]
    artifact = store.read_skeleton(claim.claim_id)
    assert artifact["has_unresolved_gaps"] is True
    assert artifact["text"] == SKELETON
    # claim state unchanged
    assert store.load_claim(claim.claim_id).state == "FORMALIZED"


def test_unresolved_skeleton_blocks_verify(tmp_path):
    store, claim = _formalized(tmp_path)
    path = tmp_path / "skel.lean"
    path.write_text(SKELETON, encoding="utf-8")
    a3_runner.cmd_skeleton(_args(tmp_path, claim_id=claim.claim_id, file=str(path)), store)
    with pytest.raises(SystemExit, match="unresolved skeleton gaps"):
        a3_runner.cmd_verify(
            _args(tmp_path, claim_id=claim.claim_id, proof=str(path)), store
        )


def test_no_skeleton_does_not_change_verify_gap_guard(tmp_path):
    """Absent skeleton is not a new refuse reason (existing gap/formal guards stay)."""
    store, claim = _formalized(tmp_path)
    assert store.skeleton_revs(claim.claim_id) == []
    # proof missing still the old error, not the skeleton error
    with pytest.raises(SystemExit, match="proof file not found"):
        a3_runner.cmd_verify(
            _args(tmp_path, claim_id=claim.claim_id, proof=str(tmp_path / "missing.lean")),
            store,
        )


def test_edit_distance_measurement_is_deterministic():
    skel = validate_skeleton(SKELETON)
    assert skel.has_unresolved_gaps
    refined = "theorem t : True := by\n  trivial\n"
    d = skeleton_edit_distance(SKELETON, refined)
    assert d > 0
    assert skeleton_edit_distance(SKELETON, SKELETON) == 0
