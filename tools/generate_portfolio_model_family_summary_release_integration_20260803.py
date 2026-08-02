#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "project/state.json"
PACKAGE_PATH = (
    ROOT
    / "project/packages/portfolio-model-family-summary-release-integration-20260803.md"
)
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
PACKAGE_ID = "portfolio_model_family_summary_release_integration_001"
NEXT_PACKAGE_ID = "data_products_v1_12_0_accelerated_release_preparation_001"
CHANGELOG_ENTRY = (
    "* Integrated the source-preserving portfolio model-family JSON, Markdown and "
    "standalone HTML summary into every newly built versioned data-product archive, "
    "verified download entry points and offline workspace navigation while preserving "
    "all existing scope, ranking and non-inference boundaries."
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_state() -> dict[str, Any]:
    state = read_json(STATE_PATH)
    state["updated_on"] = "2026-08-03"
    state["phase"] = "Portfolio Model Family Summary Release Integration"
    state["reference_delivery"] = {
        "name": "Portfolio Model Family Summary",
        "pull_request": 477,
        "head_sha": "cbcbb352b3387a01c74994697dd27d0b46e4fc8c",
        "quality_run": 30773174873,
    }
    state["baseline"]["tests"] = 1860
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "reporting_release_integration",
        "name": "Portfolio Model Family Summary Release Integration",
        "status": "complete",
        "goal": (
            "Add the verified model-family JSON, Markdown and HTML summary to the "
            "versioned data-product archive, download verification and offline "
            "workspace navigation without changing source data or comparison semantics."
        ),
        "manifest_paths": [
            "tools/reporting/data_product_release.py",
            "tools/reporting/data_product_release_download.py",
            "tools/reporting/data_product_workspace_index.py",
            "tools/data_product_release_download.py",
            "tests/test_data_product_release.py",
            "tests/test_portfolio_model_family_summary_release_integration.py",
            "tools/generate_portfolio_model_family_summary_release_integration_20260803.py",
            "project/packages/portfolio-model-family-summary-release-integration-20260803.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
        ],
    }
    state["next_package"] = {
        "package_id": NEXT_PACKAGE_ID,
        "kind": "accelerated_release_preparation",
        "name": "Data Products v1.12.0 Accelerated Release Preparation",
        "status": "planned",
        "goal": (
            "Prepare immutable data-products-v1.12.0 assets containing the verified "
            "portfolio model-family summary, prove exact-source double-build byte "
            "identity and publish only after complete Quality and post-merge verification."
        ),
        "manifest_paths": [],
    }
    return state


def package_text() -> str:
    return """# Portfolio Model Family Summary Release Integration

Date: 2026-08-03

Package ID: `portfolio_model_family_summary_release_integration_001`

Status: **complete**

## Goal

Integrate the verified portfolio model-family summary into every newly generated versioned data-product release and its offline consumer workspace without altering source data or comparison semantics.

## Integrated release members

- `model-families/portfolio-model-family-summary.json`;
- `model-families/portfolio-model-family-summary.md`;
- `model-families/portfolio-model-family-summary.html`.

## Release contract

A newly built release declares the model-family summary in its manifest, contains all three deterministic members and preserves the existing 81 configurations, 22 reporting scopes and 130 within-scope pairs. The family summary retains 33 unique provenance sources, 251 source-to-configuration relationships and zero configurations without provenance.

## Consumer contract

Verified release download exposes the family HTML as an optional backward-compatible entry point. New workspaces show a dedicated **Model family summary** card. Older immutable releases without this member remain valid and continue to download normally.

## Non-inference boundary

The integration does not create cross-scope pairs, rankings, recommendations or inferred values. It does not change master data, source relationships or an already published release.

## Next package

`data_products_v1_12_0_accelerated_release_preparation_001` prepares the first immutable release containing the integrated family summary.

## Verification

```bash
python tools/generate_portfolio_model_family_summary_release_integration_20260803.py --verify
python -m unittest tests.test_portfolio_model_family_summary_release_integration
python -m unittest tests.test_data_product_release tests.test_data_product_release_download
python tools/dkb.py project-state --check
```
"""


def update_changelog() -> None:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY in text:
        return
    marker = "### Added\n"
    if marker not in text:
        raise RuntimeError("CHANGELOG Added section not found")
    CHANGELOG_PATH.write_text(
        text.replace(marker, marker + "\n" + CHANGELOG_ENTRY + "\n", 1),
        encoding="utf-8",
    )


def verify_code_contract() -> None:
    release = (ROOT / "tools/reporting/data_product_release.py").read_text(
        encoding="utf-8"
    )
    download = (
        ROOT / "tools/reporting/data_product_release_download.py"
    ).read_text(encoding="utf-8")
    workspace = (
        ROOT / "tools/reporting/data_product_workspace_index.py"
    ).read_text(encoding="utf-8")
    cli = (ROOT / "tools/data_product_release_download.py").read_text(
        encoding="utf-8"
    )
    release_test = (ROOT / "tests/test_data_product_release.py").read_text(
        encoding="utf-8"
    )
    required_release = (
        "collect_portfolio_model_family_summary",
        "render_portfolio_model_family_json",
        "render_portfolio_model_family_markdown",
        "render_portfolio_model_family_html",
        "model-families/portfolio-model-family-summary",
        '"model_family_summary_generated": True',
        '"model_family_summary_source_count"',
        '"model_family_summary_relationship_count"',
    )
    for marker in required_release:
        if marker not in release:
            raise RuntimeError(f"release integration marker missing: {marker}")
    if (
        '"model_family_summary_html": '
        '"model-families/portfolio-model-family-summary.html"'
    ) not in download:
        raise RuntimeError("download entry point is missing")
    for marker in (
        "MODEL_FAMILY_HTML_MEMBER",
        '"title": "Model family summary"',
    ):
        if marker not in workspace:
            raise RuntimeError(f"workspace integration marker missing: {marker}")
    for marker in (
        '"model_family_summary_html": "Model family summary"',
        'keys.append("model_family_summary_html")',
    ):
        if marker not in cli:
            raise RuntimeError(f"download CLI integration marker missing: {marker}")
    if "self.assertEqual(len(names), 96)" not in release_test:
        raise RuntimeError("release archive inventory baseline was not updated")


def apply() -> None:
    verify_code_contract()
    PACKAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_PATH.write_text(package_text(), encoding="utf-8")
    STATE_PATH.write_text(
        json.dumps(expected_state(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    update_changelog()


def verify() -> None:
    verify_code_contract()
    if not PACKAGE_PATH.exists():
        raise RuntimeError("package receipt is missing")
    if PACKAGE_PATH.read_text(encoding="utf-8") != package_text():
        raise RuntimeError("package receipt differs")
    state = read_json(STATE_PATH)
    expected = expected_state()
    if state["phase"] != expected["phase"]:
        raise RuntimeError("project phase differs")
    if state["baseline"]["tests"] != 1860:
        raise RuntimeError("test baseline differs")
    for section in ("current_package", "next_package"):
        for key in ("package_id", "kind", "name", "status", "goal"):
            if state[section][key] != expected[section][key]:
                raise RuntimeError(f"project state differs for {section}.{key}")
    required_manifest = set(expected["current_package"]["manifest_paths"])
    if not required_manifest.issubset(
        set(state["current_package"]["manifest_paths"])
    ):
        raise RuntimeError("package manifest is incomplete")
    if CHANGELOG_ENTRY not in CHANGELOG_PATH.read_text(encoding="utf-8"):
        raise RuntimeError("CHANGELOG receipt is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    verify()
    print("Portfolio model-family release integration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
