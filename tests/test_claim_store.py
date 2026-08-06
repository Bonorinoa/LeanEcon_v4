"""Claim/artifact store tests (docs/gate5/a3-design.md §2)."""

from pathlib import Path

from leanecon.claim_store import (
    ArtifactStore,
    ClaimRecord,
    FORMAL_STATUS_CURRENT,
    FORMAL_STATUS_SUPERSEDED,
    sanitize_module_part,
)
from leanecon.data_policy import canonical_digest


def _claim(claim_id="c1") -> ClaimRecord:
    return ClaimRecord(claim_id=claim_id, revision=1, source_text="some claim", data_class="PROJECT")


def test_claim_round_trip(tmp_path):
    store = ArtifactStore(tmp_path)
    store.save_claim(_claim())
    loaded = store.load_claim("c1")
    assert loaded.source_text == "some claim"
    assert loaded.state == "DRAFT"


def test_ei_revisions_are_immutable_and_digest_anchored(tmp_path):
    store = ArtifactStore(tmp_path)
    ei = {"claim": {"canonical_text": "x"}, "revision": None}
    first = store.write_ei("c1", ei, status="draft")
    second = store.write_ei("c1", {"claim": {"canonical_text": "y"}}, status="draft")
    assert first["revision"] == 1 and second["revision"] == 2
    assert first["digest"] != second["digest"]
    # reading does not mutate
    reread = store.read_ei("c1", 1)
    assert reread["digest"] == first["digest"]


def test_supersede_formals_on_ei_change(tmp_path):
    store = ArtifactStore(tmp_path)
    ei1 = store.write_ei("c1", {"claim": {"canonical_text": "x"}}, status="accepted")
    ei2 = store.write_ei("c1", {"claim": {"canonical_text": "z"}}, status="accepted")
    store.write_formal("c1", {"statement_text": "s1", "interpretation_digest": ei1["digest"]}, status="current")
    store.write_formal("c1", {"statement_text": "s2", "interpretation_digest": ei2["digest"]}, status="current")
    store.supersede_formals_for("c1", ei2["digest"])
    rev1 = store.read_formal("c1", 1)
    rev2 = store.read_formal("c1", 2)
    assert rev1["status"] == FORMAL_STATUS_SUPERSEDED  # built on the old EI digest
    assert rev2["status"] == FORMAL_STATUS_CURRENT


def test_review_records_are_numbered(tmp_path):
    store = ArtifactStore(tmp_path)
    store.write_review_record("c1", "axiom", {"approved_axioms": ["propext"]})
    store.write_review_record("c1", "axiom", {"approved_axioms": ["propext", "Classical.choice"]})
    records = store.list_review_records("c1", "axiom")
    assert len(records) == 2
    assert records[0]["record_index"] == 1
    assert records[1]["approved_axioms"] == ["propext", "Classical.choice"]


def test_claim_digest_changes_with_content(tmp_path):
    store = ArtifactStore(tmp_path)
    store.save_claim(_claim("a"))
    d1 = store.read_json(store.claim_path("a"))["digest"]
    claim = _claim("a")
    claim.source_text = "changed"
    store.save_claim(claim)
    d2 = store.read_json(store.claim_path("a"))["digest"]
    assert d1 != d2


def test_digest_matches_canonical_sha256(tmp_path):
    store = ArtifactStore(tmp_path)
    record = _claim("b")
    store.save_claim(record)
    stored = store.read_json(store.claim_path("b"))
    assert stored["digest"] == canonical_digest({k: v for k, v in stored.items() if k != "digest"})


def test_sanitize_module_part():
    assert sanitize_module_part("claim-c1!") == "claim_c1_"
