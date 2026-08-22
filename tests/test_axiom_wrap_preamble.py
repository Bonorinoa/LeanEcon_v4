"""RED test: scaffolding ':=' must not block the axiom wrap."""

from __future__ import annotations

from leanecon.verifier import _axiom_wrap_signature

SANITIZED_DRAFT = (
    "import Mathlib\n"
    "\n"
    "open Finset\n"
    "\n"
    "namespace A3Scaffolding.c1\n"
    "def cost (p : ι → ℝ) (x : ι → ℝ) : ℝ := ∑ i, p i * x i\n"
    "end A3Scaffolding.c1\n"
    "\n"
    "open A3Scaffolding.c1\n"
    "\n"
    "theorem t {ι : Type*} [Fintype ι] (p x y : ι → ℝ) : cost p x = cost p y\n"
)


def test_scaffolding_body_does_not_block_wrap():
    """The v4h1 killer: 'def ... :=' in scaffolding triggered the global
    ':=' guard and the theorem was never wrapped. Declaration-aware now."""
    wrapped = _axiom_wrap_signature(SANITIZED_DRAFT)
    assert wrapped != SANITIZED_DRAFT
    assert "axiom t {" in wrapped
    # scaffolding preserved verbatim
    assert "def cost (p : ι → ℝ) (x : ι → ℝ) : ℝ := ∑ i, p i * x i" in wrapped
    # original bare theorem replaced
    assert "\ntheorem t {" not in wrapped


def test_theorem_with_own_body_still_skipped():
    with_body = SANITIZED_DRAFT.replace(
        "theorem t {ι : Type*} [Fintype ι] (p x y : ι → ℝ) : cost p x = cost p y",
        "theorem t {ι : Type*} [Fintype ι] (p x y : ι → ℝ) : cost p x = cost p y := rfl",
    )
    assert _axiom_wrap_signature(with_body) == with_body
