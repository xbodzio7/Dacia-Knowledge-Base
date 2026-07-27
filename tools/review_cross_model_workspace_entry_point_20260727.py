#!/usr/bin/env python3
"""Verify the Cross-Model Workspace Entry Point implementation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/cross_model_workspace_entry_point.json"
REVIEW = ROOT / "data/reporting/cross_model_navigation_usability_review.json"
AUDIT = ROOT / "data/reporting/data_products_v1_8_1_publication_audit.json"
INDEX = ROOT / "tools/reporting/data_product_workspace_index.py"
WORKFLOW = ROOT / ".github/workflows/data-product-release-download.yml"
STATE = ROOT / "project/state.json"


class EntryPointError(RuntimeError):
    """Raised when the workspace entry-point contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise EntryPointError(message)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def verify() -> None:
    report = load(REPORT)
    ensure(report.get("version") == 1, "report version differs")
    ensure(
        report.get("kind") == "cross_model_workspace_entry_point",
        "report kind differs",
    )
    ensure(
        report.get("implemented_on") == "2026-07-27",
        "implementation date differs",
    )
    ensure(
        report.get("status") == "complete",
        "implementation is not complete",
    )
    ensure(
        report.get("selected_by")
        == "cross_model_navigation_usability_review.json",
        "selection source differs",
    )
    review = load(REVIEW)
    ensure(
        review.get("selection", {}).get("code")
        == "conditional_primary_cross_model_card",
        "review selection differs",
    )

    implementation = report.get("implementation", {})
    ensure(
        implementation.get("release_member")
        == "cross-model/cross-model-comparison-view.html",
        "member differs",
    )
    ensure(
        implementation.get("workspace_path")
        == "contents/cross-model/cross-model-comparison-view.html",
        "workspace path differs",
    )
    ensure(
        implementation.get("member_absent_primary_card_count") == 4,
        "absent card count differs",
    )
    ensure(
        implementation.get("member_present_primary_card_count") == 5,
        "present card count differs",
    )
    ensure(
        implementation.get("public_v1_8_1_local_link_count") == 84,
        "public link count differs",
    )
    ensure(
        implementation.get("conditional_on_verified_manifest_membership")
        is True,
        "manifest condition differs",
    )
    ensure(
        implementation.get("requires_local_file") is True,
        "local file requirement differs",
    )
    ensure(
        implementation.get("parses_cross_model_json") is False,
        "JSON parsing boundary differs",
    )

    source = INDEX.read_text(encoding="utf-8")
    ensure(
        'CROSS_MODEL_HTML_MEMBER = '
        '"cross-model/cross-model-comparison-view.html"' in source,
        "member constant missing",
    )
    ensure(
        "if CROSS_MODEL_HTML_MEMBER in release_members:" in source,
        "conditional card missing",
    )
    ensure(
        '"title": "Models and comparison scopes"' in source,
        "card title missing",
    )
    ensure(
        '"description": '
        '"Browse model families and open only existing scope reports."'
        in source,
        "card description missing",
    )
    ensure("_verified_content_path(" in source, "verified path helper missing")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    ensure("--version 1.8.1" in workflow, "public smoke version differs")
    ensure(
        "0b7009fd1950693e347638a6b96756aeefb43b8a" in workflow,
        "public smoke commit differs",
    )
    ensure("len(local)==84" in workflow, "public smoke link count missing")
    ensure(
        "Models and comparison scopes" in workflow,
        "public smoke card check missing",
    )
    ensure(
        "compare-workspace-index" in workflow,
        "byte parity job missing",
    )

    audit = load(AUDIT)
    ensure(
        audit.get("workspace", {}).get("index_local_link_count") == 83,
        "historical audit was rewritten",
    )
    ensure(
        all(
            value is False
            for value in report.get("semantic_boundaries", {}).values()
        ),
        "semantic boundary differs",
    )

    state = load(STATE)
    ensure(
        state.get("phase") == "Cross-Model Workspace Entry Point",
        "project phase differs",
    )
    ensure(
        state.get("current_package", {}).get("name")
        == "Cross-Model Workspace Entry Point",
        "current package differs",
    )
    ensure(
        state.get("current_package", {}).get("status") == "complete",
        "current package is not complete",
    )
    ensure(
        state.get("next_package", {}).get("name")
        == "Post-Cross-Model Workspace Priority Selection Review",
        "next package differs",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests") == 1070, "test baseline differs")
    ensure(baseline.get("csv_files") == 46, "CSV baseline changed")
    ensure(baseline.get("rows") == 9688, "row baseline changed")
    ensure(
        baseline.get("availability_records") == 4754,
        "availability baseline changed",
    )
    ensure(baseline.get("attributes") == 385, "attribute baseline changed")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the implementation contract.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, EntryPointError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Cross-Model Workspace Entry Point")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
