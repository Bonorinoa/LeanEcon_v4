"""Gold isolation tests (Gate 4, A1 criterion 8).

The runtime must have no access path — filesystem, environment, or
package import — to v3 gold statements, reviewer labels, or release
artifacts. The sealed corpora do not live in this repository at all in
MVP; these checks prove it structurally.
"""

from pathlib import Path

from leanecon import data_policy, gold_isolation

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_no_gold_or_v3_material_in_repository():
    found = gold_isolation.scan_forbidden_paths(REPO_ROOT)
    assert found == [], f"forbidden paths present: {found}"


def test_no_gold_env_pointers_in_runtime_environment():
    present = gold_isolation.scan_forbidden_env()
    assert present == [], f"gold-pointing env vars set: {present}"


def test_runtime_policy_denies_gold_even_when_project_classified():
    # Belt and braces: even if gold content were somehow staged into a
    # request, the policy denies it before any egress.
    decision = data_policy.evaluate({"gold_statement": "..."}, "PROJECT")
    assert decision.allowed is False


def test_release_artifact_paths_absent():
    present = gold_isolation.scan_release_artifacts(REPO_ROOT)
    assert present == []
