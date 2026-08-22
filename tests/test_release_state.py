from __future__ import annotations

from pathlib import Path

from leanecon.release_state import check_release_state

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_current_development_state_is_truthful():
    """The live tree must be self-consistent. On a tagged release HEAD the
    check passes as-is; on an untagged tree it must report exactly the
    missing-tag error (never silently pass)."""
    import subprocess

    result = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    tags = {t for t in result.stdout.splitlines() if t}
    errors = check_release_state(REPO_ROOT)
    if "v3.0.0" in tags:
        assert errors == []
    else:
        assert errors == ["final version 3.0.0 must be tagged v3.0.0 at HEAD"]


def test_final_release_requires_matching_head_tag(tmp_path):
    (tmp_path / "docs/releases").mkdir(parents=True)
    (tmp_path / "src/leanecon").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.2.3"\n')
    (tmp_path / "src/leanecon/a3_runner.py").write_text('BUILDER_IDENTITY = "leanecon-a3-1.2.3"\n')
    assert check_release_state(tmp_path, head_tags=set()) == [
        "final version 1.2.3 must be tagged v1.2.3 at HEAD"
    ]
    assert check_release_state(tmp_path, head_tags={"v1.2.3"}) == []


def test_builder_must_match_package_version(tmp_path):
    (tmp_path / "docs/releases").mkdir(parents=True)
    (tmp_path / "src/leanecon").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "3.0.0.dev0"\n')
    (tmp_path / "src/leanecon/a3_runner.py").write_text('BUILDER_IDENTITY = "leanecon-a3-3.0.0"\n')
    (tmp_path / "docs/releases/DEVELOPMENT.md").write_text(
        "Latest supported release\n`3.0.0.dev0`\n"
    )
    assert check_release_state(tmp_path, head_tags=set()) == [
        "builder identity must equal leanecon-a3-3.0.0.dev0"
    ]


def test_development_version_requires_truth_surface(tmp_path):
    (tmp_path / "src/leanecon").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "3.0.0.dev0"\n')
    (tmp_path / "src/leanecon/a3_runner.py").write_text(
        'BUILDER_IDENTITY = "leanecon-a3-3.0.0.dev0"\n'
    )
    assert check_release_state(tmp_path, head_tags=set()) == [
        "development version requires docs/releases/DEVELOPMENT.md"
    ]
