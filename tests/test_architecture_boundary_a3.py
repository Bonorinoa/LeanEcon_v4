"""A3 architecture-boundary tests (docs/gate3/06 extended to Gate 5 modules).

Static checks prove the controls rather than relying on documentation:
- only leanecon.adapters may import HTTP/provider client libraries;
- no A3 core module references vendor model identifiers;
- no module reads the Mistral credential except the adapter that owns it.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "leanecon"

HTTP_CLIENT_MODULES = {"httpx", "requests", "aiohttp", "urllib3", "mistralai"}
VENDOR_MODEL_IDS = {"mistral-medium-3-5", "labs-leanstral-1-5"}

A3_MODULES = (
    "a3_runner.py",
    "lifecycle.py",
    "claim_store.py",
    "interpretation.py",
    "formalization.py",
    "verifier.py",
    "bundle.py",
    "trace_replay.py",
)


def _a3_files():
    return [SRC / name for name in A3_MODULES]


def test_a3_core_modules_never_import_http_clients():
    violations = []
    for path in _a3_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            bad = [n for n in names if n in HTTP_CLIENT_MODULES]
            if bad:
                violations.append(f"{path.name}: imports {bad}")
    assert violations == [], violations


def test_a3_core_modules_never_reference_vendor_model_ids():
    violations = []
    for path in _a3_files():
        text = path.read_text(encoding="utf-8")
        for model_id in VENDOR_MODEL_IDS:
            if model_id in text:
                violations.append(f"{path.name}: mentions {model_id}")
    assert violations == [], violations


def test_a3_core_modules_never_mention_the_credential():
    violations = []
    for path in _a3_files():
        if "MISTRAL_API_KEY" in path.read_text(encoding="utf-8"):
            violations.append(path.name)
    assert violations == [], violations


def test_a3_runner_keeps_provider_touch_only_in_adapters():
    # a3_runner may import the adapter (composition) but must not contain
    # the HTTP URL or build raw HTTP requests itself.
    text = (SRC / "a3_runner.py").read_text(encoding="utf-8")
    assert "api.mistral.ai" not in text
    assert "httpx" not in text


def test_all_a3_modules_exist():
    for name in A3_MODULES:
        assert (SRC / name).exists(), name
