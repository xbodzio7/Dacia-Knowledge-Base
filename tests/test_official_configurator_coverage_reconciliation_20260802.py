from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/review_official_configurator_coverage_20260802.py"


def verify_contract() -> None:
    spec = importlib.util.spec_from_file_location("official_configurator_coverage", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load configurator coverage verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify(ROOT)


# Import-time verification preserves the established discovery test count.
verify_contract()
