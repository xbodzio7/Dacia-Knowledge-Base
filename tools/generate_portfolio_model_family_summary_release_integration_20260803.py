#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "project/state.json"
PACKAGE_PATH = ROOT / "project/packages/portfolio-model-family-summary-release-integration-20260803.md"
PACKAGE_ID = "portfolio_model_family_summary_release_integration_001"
NEXT_PACKAGE_ID = "data_products_v1_12_0_accelerated_release_preparation_001"
BASELINE_TESTS = 1859


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def package_text() -> str:
    return """# Portfolio Model Family Summary Release Integration

Date: 2026-08-03

Package ID: `portfolio_model_family_summary_release_integration_001`

Status: **complete**

## Goal

Integrate the verified portfolio model-family summary into every newly generated versioned data-product release and its offline consumer workspace without altering source data or comparison semantics.

## Integrated release members

- `model-families/portfolio_model_family_summary.json`;
- `model-families/portfolio_model_family_summary.md`;
- `model-families/portfolio_model_family_summary.html`.

## Release contract

The release CLI first performs the canonical data-product build, verifies it, copies the three committed family-summary outputs byte-for-byte, adds one relative offline link from the existing cross-model page, deterministically rebuilds the archive and rewrites the external manifest and checksums.

The integrated manifest records the product directory and formats. The family JSON contract preserves 81 configurations, six families, 22 reporting scopes, 251 explicit source relationships and zero configurations without provenance.

## Consumer contract

Verified download extracts every manifest member, including all family-summary files. The existing offline workspace links to the cross-model page, which now contains a relative link to the family-summary HTML. Older immutable releases remain valid because verification does not require the new optional manifest fields.

## Non-inference boundary

The integration creates no cross-scope pairs, rankings, recommendations or inferred values and changes no source or master data.

## Next package

`data_products_v1_12_0_accelerated_release_preparation_001` prepares the first immutable release containing the integrated family summary.
"""


def verify_code_contract() -> None:
    module = (ROOT / "tools/reporting/portfolio_model_family_release_integration.py").read_text(encoding="utf-8")
    cli = (ROOT / "tools/data_product_release.py").read_text(encoding="utf-8")
    test = (ROOT / "tests/test_portfolio_model_family_release_integration.py").read_text(encoding="utf-8")
    required_module = (
        "base_release.create_release_assets",
        "portfolio_model_family_summary_generated",
        "write_deterministic_zip",
        "FAMILY_HTML_HREF",
        "source_configuration_relationship_count",
        "configurations_without_provenance_count",
    )
    for marker in required_module:
        if marker not in module:
            raise RuntimeError(f"integration marker missing: {marker}")
    if "reporting.portfolio_model_family_release_integration" not in cli:
        raise RuntimeError("release CLI does not use the integration layer")
    if test.count("    def test_") != 7:
        raise RuntimeError("release integration test count differs")


def verify_state() -> None:
    state = read_json(STATE_PATH)
    if state["phase"] != "Portfolio Model Family Summary Release Integration":
        raise RuntimeError("project phase differs")
    if state["baseline"]["tests"] != BASELINE_TESTS:
        raise RuntimeError("test baseline differs")
    if state["current_package"]["package_id"] != PACKAGE_ID:
        raise RuntimeError("current package differs")
    if state["current_package"]["status"] != "complete":
        raise RuntimeError("current package is not complete")
    if state["next_package"]["package_id"] != NEXT_PACKAGE_ID:
        raise RuntimeError("next package differs")
    required = {
        "tools/reporting/portfolio_model_family_release_integration.py",
        "tools/data_product_release.py",
        "tests/test_portfolio_model_family_release_integration.py",
        "tools/generate_portfolio_model_family_summary_release_integration_20260803.py",
        "project/packages/portfolio-model-family-summary-release-integration-20260803.md",
        "project/state.json",
        "project/STATE_SUMMARY.md",
        "README.md",
        "CHANGELOG.md",
        "project/ROADMAP.md",
        "project/SESSION_STATE.md",
    }
    if not required.issubset(set(state["current_package"]["manifest_paths"])):
        raise RuntimeError("package manifest is incomplete")


def verify() -> None:
    verify_code_contract()
    verify_state()
    if not PACKAGE_PATH.is_file():
        raise RuntimeError("package receipt is missing")
    if PACKAGE_PATH.read_text(encoding="utf-8") != package_text():
        raise RuntimeError("package receipt differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required")
    verify()
    print("Portfolio model-family release integration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
