"""Tests for sanitize_signature_draft (v4 intelligence sprint, Day 2)."""

from __future__ import annotations

from leanecon.formalization import (
    sanitize_signature_draft,
    validate_scaffolding_namespace,
    validate_statement_text,
)


def test_strips_theorem_proof_body():
    draft = (
        "import Mathlib\n\n"
        "theorem t {ι : Type*} [Fintype ι] (f : ι → ℝ) : ∑ i, f i ≥ 0 :=\n"
        "  by\n"
        "    exact le_refl _\n"
    )
    out, notes = sanitize_signature_draft(draft)
    assert ":=" not in out.split("theorem", 1)[1]
    assert "sorry" not in out
    assert any("proof body" in n.lower() for n in notes)
    assert validate_statement_text(out) == []


def test_strips_inline_sorry_body():
    draft = "theorem t (n : ℕ) : n + 0 = n := by sorry\n"
    out, notes = sanitize_signature_draft(draft)
    assert "sorry" not in out
    assert ":=" not in out.split("theorem", 1)[1]
    assert validate_statement_text(out) == []


def test_namespaces_root_scaffolding():
    draft = "abbrev Bundle := Goods → ℝ\n\ntheorem t (b : Bundle) : True\n".replace("Goods", "ι")
    out, notes = sanitize_signature_draft(draft)
    problems = validate_scaffolding_namespace(out)
    assert problems == []
    assert "A3Scaffolding" in out
    assert any("namespace" in n.lower() for n in notes)
    # theorem stays OUTSIDE the scaffolding namespace
    tail = out.rsplit("end", 1)[-1]
    assert "theorem t" in tail


def test_clean_draft_is_untouched():
    draft = (
        "import Mathlib\n"
        "import LeanEcon.Core.Constraints\n\n"
        "namespace A3Scaffolding.c1\n"
        "abbrev Bundle := ι → ℝ\n"
        "end A3Scaffolding.c1\n\n"
        "theorem t (b : Bundle) : True\n"
    )
    out, notes = sanitize_signature_draft(draft)
    assert out == draft
    assert notes == []


def test_wrapped_continuation_body_cut():
    draft = "theorem t\n    (n : ℕ)\n    : n + 0 = n :=\n  rfl\n"
    out, notes = sanitize_signature_draft(draft)
    assert validate_statement_text(out) == []
    assert "rfl" not in out


def test_admit_token_removed():
    draft = "theorem t (n : ℕ) : n + 0 = n := by admit\n"
    out, _notes = sanitize_signature_draft(draft)
    assert "admit" not in out and "sorry" not in out
    assert validate_statement_text(out) == []
