"""Architecture boundary tests (docs/gate3/06): single provider boundary.

Static checks prove the control rather than relying on documentation:
- only leanecon.adapters may import HTTP/provider client libraries;
- no core module references vendor model identifiers;
- no module reads credentials except the adapter that owns them.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "leanecon"

HTTP_CLIENT_MODULES = {"httpx", "requests", "aiohttp", "urllib3", "mistralai"}
VENDOR_MODEL_IDS = {"mistral-medium-3-5", "labs-leanstral-1-5"}


def _python_files():
    return sorted(SRC.rglob("*.py"))


def _in_adapters(path: Path) -> bool:
    try:
        path.relative_to(SRC / "adapters")
        return True
    except ValueError:
        return False


def test_only_adapters_import_http_clients():
    violations = []
    for path in _python_files():
        if _in_adapters(path):
            continue
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
                violations.append(f"{path.relative_to(SRC)}: imports {bad}")
    assert violations == [], violations


def test_core_never_references_vendor_model_ids():
    violations = []
    for path in _python_files():
        if _in_adapters(path):
            continue
        text = path.read_text(encoding="utf-8")
        for model_id in VENDOR_MODEL_IDS:
            if model_id in text:
                violations.append(f"{path.relative_to(SRC)}: mentions {model_id}")
    assert violations == [], violations


def test_only_mistral_adapter_reads_the_mistral_credential():
    violations = []
    for path in _python_files():
        if path == SRC / "adapters" / "mistral.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "MISTRAL_API_KEY" in text:
            violations.append(str(path.relative_to(SRC)))
    assert violations == [], violations


def test_single_boundary_module_exists():
    assert (SRC / "adapters" / "mistral.py").exists()
