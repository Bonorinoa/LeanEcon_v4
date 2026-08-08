"""Reviewer policy tests (docs/gate3/08-reviewer-policy.md)."""

import pytest

from leanecon.reviewer_policy import (
    infer_reviewer_kind,
    normalize_reviewer_kind,
    resolve_reviewer,
)


def test_infer_human_by_default():
    assert infer_reviewer_kind("Bonorinoa") == "human"
    assert infer_reviewer_kind("cto") == "human"
    assert infer_reviewer_kind("alice") == "human"


def test_infer_ai_identities():
    for rid in ("ai", "AI", "hermes", "hermes-agent", "leanecon-ai", "leanecon-ai:v1", "ai:oos"):
        assert infer_reviewer_kind(rid) == "ai", rid


def test_explicit_kind_overrides_inference():
    assert normalize_reviewer_kind("ai", "Bonorinoa") == "ai"
    assert normalize_reviewer_kind("human", "hermes") == "human"
    assert normalize_reviewer_kind("auto", "hermes") == "ai"
    assert normalize_reviewer_kind(None, "Bonorinoa") == "human"


def test_invalid_kind_rejected():
    with pytest.raises(ValueError):
        normalize_reviewer_kind("robot", "x")


def test_resolve_requires_identity():
    with pytest.raises(ValueError):
        resolve_reviewer("")
    with pytest.raises(ValueError):
        resolve_reviewer(None)
    assert resolve_reviewer("hermes") == ("hermes", "ai")
    assert resolve_reviewer("Bonorinoa", "human") == ("Bonorinoa", "human")
