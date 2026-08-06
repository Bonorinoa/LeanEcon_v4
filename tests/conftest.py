"""Shared A3 test helpers: fake provider adapter, valid EI, mapping reports."""

from __future__ import annotations

from pathlib import Path

import pytest

from leanecon.adapters.mistral import MistralAdapter
from leanecon.events import CapabilityStatus
from leanecon.providers import (
    Capability,
    ProviderFailure,
    ProviderFailureKind,
    ProviderMetadata,
    ProviderResponse,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "lean"

WORKSPACE = Path(__file__).resolve().parents[1] / "lean_workspace"

ELAN_PATH = Path.home() / ".elan" / "bin"


def valid_ei(none_noted: bool = False, claim_text: str = "test claim") -> dict:
    return {
        "schema_version": "1.0.0",
        "claim": {"canonical_text": claim_text, "source_text": claim_text},
        "context": {"domain_tags": ["micro"], "definitions": [], "ontology_refs": []},
        "objects": [{"id": "consumer", "kind": "agent", "role": "decision-maker"}],
        "assumptions": {"proposed": ["budget expansion"], "accepted": []},
        "quantifiers": ["for every consumer"],
        "conclusion": {"text": "attainable set does not shrink", "solution_or_equilibrium_concept": None},
        "ambiguities": [] if none_noted else [{"issue": "meaning of attainable", "alternatives": ["feasible", "chosen"]}],
        "none_noted": none_noted or False,
        "provenance": {"source_span": "s", "mapping_method": "test"},
        "confidence": 0.5,
        "degradation_flags": [],
        "review": {"decision": "PENDING", "reviewer": None, "event_ref": None},
        "data_classification": "PROJECT",
    }


def complete_mapping_report() -> list[dict]:
    return [
        {"ei_element_id": "consumer", "ei_element_kind": "object", "lean_identifier": "Bundle",
         "mapping_kind": "local_definition", "status": "mapped", "provenance": "test", "note": ""},
        {"ei_element_id": "assumption:0", "ei_element_kind": "assumption", "lean_identifier": "Bold ⊆ Bnew",
         "mapping_kind": "mathlib", "status": "mapped", "provenance": "test", "note": ""},
        {"ei_element_id": "quantifier:0", "ei_element_kind": "quantifier", "lean_identifier": "∀ Bold Bnew",
         "mapping_kind": "mathlib", "status": "mapped", "provenance": "test", "note": ""},
        {"ei_element_id": "conclusion", "ei_element_kind": "conclusion",
         "lean_identifier": "Attainable Bold ⊆ Attainable Bnew",
         "mapping_kind": "local_definition", "status": "mapped", "provenance": "test", "note": ""},
    ]


def formalize_output(statement: str, target: str, report: list[dict] | None = None) -> dict:
    return {"statement": statement, "target_theorem": target, "mapping_report": report or complete_mapping_report()}


class FakeAdapter(MistralAdapter):
    """Deterministic in-memory adapter. Interprets via ``ei_factory`` and
    formalizes via ``formalize_factory``; no network, no credentials."""

    def __init__(self, ei_factory=valid_ei, formalize_factory=None, interpret_failure=None, formalize_failure=None):
        super().__init__(transport=lambda *a, **k: {"choices": [{"message": {"content": ""}}]})
        self._api_key_env = "MISTRAL_TEST_KEY"
        self._ei_factory = ei_factory
        self._formalize_factory = formalize_factory
        self._interpret_failure = interpret_failure
        self._formalize_failure = formalize_failure
        self.requests_seen: list[dict] = []

    def _invoke(self, capability, model, payload, decision, run_id) -> ProviderResponse:
        self.requests_seen.append({"capability": capability, "model": model, "payload": payload})
        metadata = ProviderMetadata(provider="mistral", model=model, request_id="req-mock", latency_ms=5,
                                    token_metadata={"prompt_tokens": 10, "completion_tokens": 5})

        if capability is Capability.INTERPRET:
            failure = self._interpret_failure
            if failure is not None:
                raise ProviderFailure(failure, "mock interpret failure", provider="mistral")
            ei = self._ei_factory()
            import json
            return ProviderResponse(capability=capability, status=CapabilityStatus.HEALTHY,
                                    output={"content": json.dumps(ei)}, metadata=metadata)

        if capability is Capability.FORMALIZE:
            failure = self._formalize_failure
            if failure is not None:
                raise ProviderFailure(failure, "mock formalize failure", provider="mistral")
            if self._formalize_factory is None:
                raise AssertionError("FakeAdapter.formalize_factory not configured")
            import json
            output = self._formalize_factory()
            return ProviderResponse(capability=capability, status=CapabilityStatus.HEALTHY,
                                    output={"content": json.dumps(output)}, metadata=metadata)

        raise AssertionError(f"unexpected capability: {capability}")


@pytest.fixture
def elan_on_path(monkeypatch):
    """Put the elan toolchain dir on PATH for real-workspace tests."""
    monkeypatch.setenv("PATH", f"{ELAN_PATH}:{__import__('os').environ.get('PATH', '')}")
    return ELAN_PATH


@pytest.fixture
def workspace_ready() -> bool:
    return (WORKSPACE / "lean-toolchain").exists() and (WORKSPACE / "lakefile.lean").exists()
