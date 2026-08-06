"""Repo-root discovery tests (installed-run robustness)."""

from pathlib import Path

from leanecon import repopath


def test_finds_repo_root_from_source_tree():
    root = repopath.find_repo_root()
    assert (root / "pyproject.toml").exists()
    assert (root / "lean_workspace").exists()


def test_env_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("LEANECON_REPO_ROOT", str(tmp_path))
    assert repopath.find_repo_root() == tmp_path


def test_falls_back_to_cwd_when_installed(monkeypatch, tmp_path):
    """Installed copy: no repo marker above the module -> cwd fallback."""
    monkeypatch.delenv("LEANECON_REPO_ROOT", raising=False)
    fake_module = tmp_path / "site-packages" / "leanecon" / "repopath.py"
    fake_module.parent.mkdir(parents=True)
    monkeypatch.setattr(repopath, "__file__", str(fake_module))
    monkeypatch.chdir(tmp_path)
    assert repopath.find_repo_root() == tmp_path
