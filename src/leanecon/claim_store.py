"""Claim records and the A3 artifact store (docs/gate5/a3-design.md §2).

Artifacts live under ``artifacts/local/a3/`` (gitignored; local run data,
reviewed evidence is exported separately). Every artifact JSON is
revisioned and digest-anchored; accepted artifacts are immutable by
digest and downstream references record the digest they were built from.

Digests use ``data_policy.canonical_digest`` (SHA-256 over canonical
JSON) so the same digest primitive is shared across the trust boundary.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from leanecon.data_policy import canonical_digest

DEFAULT_ROOT = Path("artifacts/local/a3")

EI_STATUS_DRAFT = "draft"
EI_STATUS_ACCEPTED = "accepted"
FORMAL_STATUS_CURRENT = "current"
FORMAL_STATUS_SUPERSEDED = "superseded"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _without_digest(payload: dict) -> dict:
    out = dict(payload)
    out.pop("digest", None)
    return out


@dataclass
class ClaimRecord:
    claim_id: str
    revision: int
    source_text: str
    data_class: str
    state: str = "DRAFT"
    accepted_ei_rev: Optional[int] = None
    formal_rev: Optional[int] = None
    current_bundle: Optional[str] = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ClaimRecord":
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)


class ArtifactStore:
    """JSON artifact store with revisioning and digest anchoring."""

    def __init__(self, root: Path | str = DEFAULT_ROOT):
        self.root = Path(root)

    # -- low-level -----------------------------------------------------
    def _path(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write_json(self, rel_path: Path, payload: dict) -> dict:
        payload = dict(payload)
        payload["digest"] = canonical_digest(_without_digest(payload))
        rel_path.parent.mkdir(parents=True, exist_ok=True)
        rel_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload

    def read_json(self, rel_path: Path) -> dict:
        if not rel_path.exists():
            raise FileNotFoundError(str(rel_path))
        return json.loads(rel_path.read_text(encoding="utf-8"))

    # -- claims --------------------------------------------------------
    def claim_path(self, claim_id: str) -> Path:
        return self.root / "claims" / f"{claim_id}.json"

    def load_claim(self, claim_id: str) -> ClaimRecord:
        return ClaimRecord.from_dict(self.read_json(self.claim_path(claim_id)))

    def save_claim(self, record: ClaimRecord) -> ClaimRecord:
        record.updated_at = _now()
        self.write_json(self.claim_path(record.claim_id), record.to_dict())
        return record

    def list_claims(self) -> list[str]:
        claims_dir = self.root / "claims"
        if not claims_dir.exists():
            return []
        return sorted(p.stem for p in claims_dir.glob("*.json"))

    # -- EI revisions --------------------------------------------------
    def _ei_dir(self, claim_id: str) -> Path:
        return self.root / "eis" / claim_id

    def ei_revs(self, claim_id: str) -> list[int]:
        d = self._ei_dir(claim_id)
        if not d.exists():
            return []
        return sorted(int(p.stem.split("-")[1]) for p in d.glob("rev-*.json"))

    def write_ei(self, claim_id: str, ei: dict, status: str) -> dict:
        rev = (self.ei_revs(claim_id) or [0])[-1] + 1
        payload = dict(ei)
        payload["revision"] = rev
        payload["status"] = status
        payload["claim_id"] = claim_id
        payload["stored_at"] = _now()
        return self.write_json(self._ei_dir(claim_id) / f"rev-{rev}.json", payload)

    def read_ei(self, claim_id: str, rev: int | None = None) -> dict:
        revs = self.ei_revs(claim_id)
        if not revs:
            raise FileNotFoundError(f"no EI for {claim_id}")
        return self.read_json(self._ei_dir(claim_id) / f"rev-{(rev or revs[-1])}.json")

    # -- formalization revisions ----------------------------------------
    def _formal_dir(self, claim_id: str) -> Path:
        return self.root / "formal" / claim_id

    def formal_revs(self, claim_id: str) -> list[int]:
        d = self._formal_dir(claim_id)
        if not d.exists():
            return []
        return sorted(int(p.stem.split("-")[1]) for p in d.glob("rev-*.json"))

    def write_formal(self, claim_id: str, candidate: dict, status: str) -> dict:
        rev = (self.formal_revs(claim_id) or [0])[-1] + 1
        payload = dict(candidate)
        payload["revision"] = rev
        payload["status"] = status
        payload["claim_id"] = claim_id
        payload["stored_at"] = _now()
        return self.write_json(self._formal_dir(claim_id) / f"rev-{rev}.json", payload)

    def read_formal(self, claim_id: str, rev: int | None = None) -> dict:
        revs = self.formal_revs(claim_id)
        if not revs:
            raise FileNotFoundError(f"no formalization for {claim_id}")
        return self.read_json(self._formal_dir(claim_id) / f"rev-{(rev or revs[-1])}.json")

    def supersede_formals_for(self, claim_id: str, ei_digest: str) -> None:
        """Mark every formalization not built on ``ei_digest`` as superseded
        (changed accepted interpretation invalidates downstream artifacts)."""
        for rev in self.formal_revs(claim_id):
            artifact = self.read_formal(claim_id, rev)
            if artifact.get("interpretation_digest") != ei_digest and artifact.get("status") == FORMAL_STATUS_CURRENT:
                artifact["status"] = FORMAL_STATUS_SUPERSEDED
                artifact["superseded_at"] = _now()
                self.write_json(self._formal_dir(claim_id) / f"rev-{rev}.json", artifact)

    # -- review records -------------------------------------------------
    def _review_dir(self, claim_id: str) -> Path:
        return self.root / "reviews" / claim_id

    def write_review_record(self, claim_id: str, kind: str, record: dict) -> dict:
        records = self.list_review_records(claim_id, kind)
        n = len(records) + 1
        payload = dict(record)
        payload["kind"] = kind
        payload["claim_id"] = claim_id
        payload["record_index"] = n
        payload["stored_at"] = _now()
        return self.write_json(self._review_dir(claim_id) / f"{kind}-{n}.json", payload)

    def list_review_records(self, claim_id: str, kind: str | None = None) -> list[dict]:
        d = self._review_dir(claim_id)
        if not d.exists():
            return []
        records = []
        for p in sorted(d.glob("*.json")):
            record = json.loads(p.read_text(encoding="utf-8"))
            if kind is None or record.get("kind") == kind:
                records.append(record)
        return records

    # -- bundles ---------------------------------------------------------
    def write_bundle(self, bundle_id: str, manifest: dict, files: dict[str, str | dict]) -> Path:
        bundle_dir = self.root / "bundles" / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            if isinstance(content, dict):
                (bundle_dir / name).write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            else:
                (bundle_dir / name).write_text(content, encoding="utf-8")
        manifest = dict(manifest)
        manifest["manifest_digest"] = canonical_digest(_without_digest(manifest))
        (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return bundle_dir

    def read_bundle_manifest(self, bundle_id: str) -> dict:
        return self.read_json(self.root / "bundles" / bundle_id / "manifest.json")

    def bundle_path(self, bundle_id: str) -> Path:
        return self.root / "bundles" / bundle_id


def new_run_id(prefix: str = "a3") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def sanitize_module_part(value: str) -> str:
    """Claim id -> safe module name fragment for generated Lean files."""
    return re.sub(r"[^A-Za-z0-9_]", "_", value) or "claim"
