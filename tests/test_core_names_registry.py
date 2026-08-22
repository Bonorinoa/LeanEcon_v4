"""Tests: core-names registry derives from the pinned workspace."""

from __future__ import annotations

from pathlib import Path

from leanecon.formalization import core_names_from_workspace


def test_derived_from_pinned_workspace():
    names = core_names_from_workspace()
    # spot-check against the known Core layout
    assert names.get("attainableSet") == "LeanEcon.Core.Choice.attainableSet"
    assert names.get("budgetSetEndowment") == "LeanEcon.Core.Constraints.budgetSetEndowment"
    assert names.get("marketClearing") == "LeanEcon.Core.Equilibrium.marketClearing"
    # theorems are included too
    assert any(v.endswith(".competitiveEquilibrium_paretoEfficient") for v in names.values())


def test_scan_picks_up_new_declaration(tmp_path: Path):
    """A new Core declaration is found automatically — no table to update."""
    core = tmp_path / "lean_workspace" / "LeanEcon" / "Core"
    core.mkdir(parents=True)
    (core / "NewArea.lean").write_text(
        "def shinyNewThing (n : ℕ) : ℕ := n + 1\ntheorem shinyFact : True\n",
        encoding="utf-8",
    )
    names = core_names_from_workspace(tmp_path)
    assert names["shinyNewThing"] == "LeanEcon.Core.NewArea.shinyNewThing"
    assert "shinyFact" in names
    assert names["shinyFact"] == "LeanEcon.Core.NewArea.shinyFact"


def test_fallback_when_no_workspace(tmp_path: Path):
    empty = tmp_path / "nowhere"
    empty.mkdir()
    names = core_names_from_workspace(empty)
    assert names  # static fallback still provides the known vocabulary
