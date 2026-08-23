from __future__ import annotations

from pathlib import Path

from leanecon.release_state import check_release_state

REPO_ROOT = Path(__file__).resolve().parents[1]


def _package_version() -> str:
    import tomllib

    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


def test_current_development_state_is_truthful():
    """The live tree must be self-consistent. On a development version
    (PEP 440 .devN suffix) the check passes as-is with no tag required;
    on a final version HEAD must carry the matching tag (never silently
    pass)."""
    import subprocess

    result = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    tags = {t for t in result.stdout.splitlines() if t}
    errors = check_release_state(REPO_ROOT)
    version = _package_version()
    if version.endswith(".dev0") or ".dev" in version:
        assert errors == []
    elif f"v{version}" in tags:
        assert errors == []
    else:
        assert errors == [f"final version {version} must be tagged v{version} at HEAD"]


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
