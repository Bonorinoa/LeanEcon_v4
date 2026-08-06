"""Verification bundle (docs/gate5/a3-design.md §6, gate3/05).

``VERIFIED`` is a trust claim: the bundle must let the reviewer identify
exactly what was interpreted, approved, checked, and under which
environment. The validator implements the eleven required checks; a
VERIFIED result requires every check to pass. The proven or failed input
statement is always retained, with sanity-check metadata describing the
state in which it was evaluated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from leanecon.claim_store import ArtifactStore
from leanecon.data_policy import canonical_digest
from leanecon.lean_probe import read_workspace_identity

BUNDLE_SCHEMA_VERSION = "1.0.0"

MANIFEST_FIELDS = (
    "bundle_schema_version",
    "bundle_id",
    "claim_id",
    "claim_revision",
    "claim_digest",
    "interpretation_digest",
    "formal_statement_digest",
    "proof_artifact_digest",
    "workspace_identity",
    "axiom_audit",
    "axiom_approval_ref",
    "dependency_audit",
    "trace_refs",
    "capability_snapshots",
    "sanity_checks",
    "result",
    "failure_reasons",
    "reproducibility",
    "created_at",
    "builder_identity",
    "retention_policy",
)


def build_bundle(
    store: ArtifactStore,
    claim,
    ei_artifact: dict,
    formal_artifact: dict,
    proof_source: str,
    verification: dict,
    approval_record: dict,
    axiom_record: Optional[dict],
    trace_refs: list[str],
    capability_snapshots: dict,
    workspace_root: Path,
    commands: list[str],
    builder_identity: str = "leanecon-a3-0.1.0",
    retention_policy: str = "payloads kept; raw provider responses not retained",
) -> tuple[str, Path]:
    """Assemble a bundle directory and return (bundle_id, path)."""
    import uuid

    bundle_id = f"bundle-{claim.claim_id}-r{claim.revision}-{uuid.uuid4().hex[:6]}"
    identity = read_workspace_identity(workspace_root)
    from leanecon.claim_store import _now

    manifest = {
        "bundle_schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "claim_id": claim.claim_id,
        "claim_revision": claim.revision,
        "claim_digest": canonical_digest(
            {"claim_id": claim.claim_id, "revision": claim.revision, "source_text": claim.source_text}
        ),
        "interpretation_digest": ei_artifact.get("digest"),
        "formal_statement_digest": canonical_digest({"statement": formal_artifact.get("statement_text", "")}),
        "proof_artifact_digest": canonical_digest({"proof": proof_source}),
        "workspace_identity": {
            "toolchain": identity.lean_toolchain,
            "mathlib": identity.mathlib_revision,
            "pinned": identity.pinned,
            "workspace_root": str(workspace_root),
        },
        "axiom_audit": {
            "axioms_used": verification.get("axiom_list", []),
            "sorryAx_present": "sorryAx" in verification.get("axiom_list", []),
            "static_sorry_ok": verification.get("static_sorry_ok"),
        },
        "axiom_approval_ref": (axiom_record or {}).get("record_ref"),
        "dependency_audit": {
            "imports": formal_artifact.get("imports", []),
            "mathlib_revision": identity.mathlib_revision,
        },
        "trace_refs": trace_refs,
        "capability_snapshots": capability_snapshots,
        "sanity_checks": {
            "workspace_pinned": identity.pinned,
            "compile_ok": verification.get("compile_ok"),
            "exit_code": verification.get("exit_code"),
            "timed_out": verification.get("timed_out"),
            "elapsed_ms": verification.get("elapsed_ms"),
            "stderr_tail": verification.get("stderr_tail"),
            "lean_toolchain": identity.lean_toolchain,
        },
        "result": verification.get("outcome"),
        "failure_reasons": [verification.get("reason_code")] if verification.get("reason_code") else [],
        "reproducibility": {
            "commands": commands,
            "builder_identity": builder_identity,
            "created_at": _now(),
        },
        "created_at": _now(),
        "builder_identity": builder_identity,
        "retention_policy": retention_policy,
    }

    files = {
        "claim.json": {
            "claim_id": claim.claim_id,
            "revision": claim.revision,
            "source_text": claim.source_text,
            "data_class": claim.data_class,
        },
        "ei_accepted.json": ei_artifact,
        "formal_candidate.json": formal_artifact,
        "proof_input.lean": proof_source,
        "verification.json": verification,
        "approval_record.json": approval_record,
        "axiom_record.json": axiom_record if axiom_record is not None else {},
    }
    path = store.write_bundle(bundle_id, manifest, files)
    return bundle_id, path


def validate_bundle(store: ArtifactStore, bundle_id: str, claim) -> list[tuple[str, bool, str]]:
    """Eleven checks (docs/gate3/05 §checklist). Returns (item, ok, detail)."""
    checks: list[tuple[str, bool, str]] = []
    manifest = store.read_bundle_manifest(bundle_id)
    bundle_dir = store.bundle_path(bundle_id)

    def read(name: str) -> Any:
        path = bundle_dir / name
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    claim_json = read("claim.json")
    ei = read("ei_accepted.json")
    formal = read("formal_candidate.json")
    verification = read("verification.json")
    approval = read("approval_record.json")
    axiom_rec = read("axiom_record.json")
    proof = read("proof_input.lean")

    claim_payload = claim_json if isinstance(claim_json, dict) else {}
    ei_dict = ei if isinstance(ei, dict) else {}
    formal_dict = formal if isinstance(formal, dict) else {}
    ver_dict = verification if isinstance(verification, dict) else {}
    approval_dict = approval if isinstance(approval, dict) else {}
    axiom_dict = axiom_rec if isinstance(axiom_rec, dict) else {}

    # 1 exact user claim
    ok = bool(claim_payload) and manifest.get("claim_digest") == canonical_digest(
        {
            "claim_id": claim_payload.get("claim_id"),
            "revision": claim_payload.get("revision"),
            "source_text": claim_payload.get("source_text"),
        }
    )
    checks.append(("1_exact_claim", ok, "claim_digest matches claim artifact"))

    # 2 accepted interpretation immutable + approved
    ei_ok = ei_dict.get("status") == "accepted"
    ei_ok = ei_ok and ei_dict.get("review", {}).get("decision") == "APPROVED"
    ei_ok = ei_ok and manifest.get("interpretation_digest") == ei_dict.get("digest")
    if not ei_ok:
        checks.append(("2_accepted_interpretation", False, f"EI status={ei_dict.get('status')} review={ei_dict.get('review')}"))
    else:
        checks.append(("2_accepted_interpretation", True, "immutable accepted EI digest + APPROVED review"))

    # 3 accepted formal statement linked
    formal_ok = bool(formal_dict.get("statement_text"))
    formal_ok = formal_ok and manifest.get("formal_statement_digest") == canonical_digest(
        {"statement": formal_dict.get("statement_text", "")}
    )
    checks.append(("3_formal_statement", formal_ok, "statement linked + digest matches"))

    # 4 kernel check
    checks.append(("4_kernel_check", bool(ver_dict.get("compile_ok")), "lake env lean accepted the candidate"))

    # 5 no incomplete proof (static + kernel)
    sorry_ok = bool(ver_dict.get("static_sorry_ok")) and not (
        "sorryAx" in (ver_dict.get("axiom_list") or [])
    )
    checks.append(("5_no_sorry", sorry_ok, "static scan + sorryAx absent from axiom audit"))

    # 6 axiom/dependency audit vs approval record
    approved = set(axiom_dict.get("approved_axioms", []))
    used = set(ver_dict.get("axiom_list", []))
    # A zero-axiom theorem needs no approval record (vacuous); otherwise the
    # per-run reviewer record must cover every used axiom.
    audit_ok = (not used) or (bool(axiom_dict) and used <= approved)
    checks.append(("6_axiom_audit", audit_ok, f"axioms {sorted(used)} within approved {sorted(approved)}"))

    # 7 pinned workspace identity
    ws = manifest.get("workspace_identity", {})
    checks.append(("7_pinned_workspace", bool(ws.get("pinned")), "toolchain + mathlib pin recorded"))

    # 8 content digests present
    digests = [manifest.get(k) for k in ("claim_digest", "interpretation_digest", "formal_statement_digest", "proof_artifact_digest", "manifest_digest")]
    checks.append(("8_digests", all(digests), "all five digests present"))

    # 9 trace links
    checks.append(("9_trace_links", bool(manifest.get("trace_refs")) and bool(approval_dict.get("event_ref")), "approval + verification refs present"))

    # 10 state-dependent metadata
    meta_ok = bool(manifest.get("capability_snapshots")) and bool(manifest.get("sanity_checks"))
    checks.append(("10_state_metadata", meta_ok, "capability snapshots + sanity checks present"))

    # 11 reproducible manifest
    repro = manifest.get("reproducibility", {})
    checks.append(("11_reproducibility", bool(repro.get("commands")) and bool(repro.get("created_at")), "commands + timestamps present"))

    return checks


def bundle_result(checks: list[tuple[str, bool, str]]) -> str:
    return "VERIFIED" if all(ok for _, ok, _ in checks) else "INVALID"
