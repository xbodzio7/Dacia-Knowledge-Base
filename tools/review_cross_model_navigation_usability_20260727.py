#!/usr/bin/env python3
"""Verify the Cross-Model Navigation Usability Review decision."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "cross_model_navigation_usability_review.json"
AUDIT = ROOT / "data" / "reporting" / "data_products_v1_8_1_publication_audit.json"
WORKSPACE_INDEX = ROOT / "tools" / "reporting" / "data_product_workspace_index.py"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.cross_model_comparison_view import collect_view, render_html  # noqa: E402


class ReviewError(RuntimeError):
    """Raised when the usability review contract drifts."""


class HrefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def verify_report(report: Mapping[str, Any]) -> None:
    ensure(report.get("version") == 1, "review version differs")
    ensure(report.get("kind") == "cross_model_navigation_usability_review", "review kind differs")
    ensure(report.get("reviewed_on") == "2026-07-27", "review date differs")
    ensure(report.get("status") == "complete", "review is not complete")
    source = report.get("source_release", {})
    ensure(source.get("release_id") == 360138130, "source release ID differs")
    ensure(source.get("publication_record_commit") == "3b7709b41dca39f1822d20bb9a20fd61144f5443", "source publication record differs")
    ensure(source.get("archive_member_count") == 85, "source archive count differs")
    ensure(source.get("workspace_local_link_count") == 83, "source workspace link count differs")

    workspace = report.get("current_discoverability", {}).get("workspace_index", {})
    ensure(workspace.get("primary_card_count") == 4, "current primary card count differs")
    ensure(workspace.get("scope_report_link_count") == 76, "current scope link count differs")
    ensure(workspace.get("asset_link_count") == 3, "current asset link count differs")
    ensure(workspace.get("total_local_link_count") == 83, "current local link count differs")
    ensure(workspace.get("cross_model_entry_point_count") == 0, "current cross-model entry point differs")

    candidates = report.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "candidate set differs")
    ensure([item.get("rank") for item in candidates] == [1, 2, 3, 4, 5], "candidate ranks differ")
    ensure(candidates[0].get("code") == "conditional_primary_cross_model_card", "selected candidate differs")
    ensure(candidates[0].get("weighted_score") == 100, "selected score differs")

    selection = report.get("selection", {})
    ensure(selection.get("workspace_path") == "contents/cross-model/cross-model-comparison-view.html", "selected path differs")
    contract = report.get("implementation_contract", {})
    ensure(contract.get("member_absent_primary_card_count") == 4, "absent-member card count differs")
    ensure(contract.get("member_present_primary_card_count") == 5, "present-member card count differs")
    ensure(contract.get("v1_8_1_expected_local_link_count") == 84, "planned local link count differs")
    ensure(contract.get("older_release_behavior_unchanged") is True, "older release compatibility differs")
    ensure(contract.get("release_republication_required") is False, "review requires republication")
    ensure(all(value is False for value in report.get("semantic_boundaries", {}).values()), "semantic boundary differs")


def verify_repository_evidence() -> None:
    audit = load_json(AUDIT)
    ensure(audit.get("status") == "PASS", "public audit did not pass")
    workspace = audit.get("workspace", {})
    ensure(workspace.get("content_file_count") == 85, "audited content count differs")
    ensure(workspace.get("index_local_link_count") == 83, "audited index link count differs")
    cross_model = audit.get("cross_model", {})
    ensure(cross_model.get("model_family_count") == 5, "audited model count differs")
    ensure(cross_model.get("reporting_scope_count") == 19, "audited scope count differs")
    ensure(cross_model.get("html_local_file_link_count") == 57, "audited cross-model link count differs")

    source = WORKSPACE_INDEX.read_text(encoding="utf-8")
    for title in (
        "Configuration shortlist",
        "Comparison workbook",
        "Comparison bundle manifest",
        "Release notes",
    ):
        ensure(title in source, f"current primary product missing: {title}")
    member = "cross-model/cross-model-comparison-view.html"
    if member in source:
        ensure(
            "if CROSS_MODEL_HTML_MEMBER in release_members:" in source,
            "implemented cross-model entry point is not conditional",
        )
        ensure(
            '"title": "Models and comparison scopes"' in source,
            "implemented cross-model entry point title differs",
        )

    view = collect_view(ROOT)
    summary = view.get("summary", {})
    ensure(summary.get("model_family_count") == 5, "generated model count differs")
    ensure(summary.get("reporting_scope_count") == 20, "generated scope count differs")
    ensure(summary.get("active_configuration_count") == 78, "generated configuration count differs")
    ensure(summary.get("within_scope_pair_count") == 129, "generated pair count differs")
    rendered = render_html(view)
    ensure("<script" not in rendered.lower(), "cross-model HTML uses JavaScript")
    parser = HrefParser()
    parser.feed(rendered)
    local_files = [href for href in parser.hrefs if not href.startswith(("http://", "https://", "#"))]
    ensure(len(local_files) == 60, "generated cross-model local file link count differs")


def verify_state() -> None:
    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package", {})
    ensure(isinstance(current.get("name"), str) and bool(current["name"]), "current package is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current package status differs")
    next_package = state.get("next_package", {})
    ensure(isinstance(next_package.get("name"), str) and bool(next_package["name"]), "next package is missing")
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 1062, "test baseline regressed")
    ensure(baseline.get("csv_files") == 46, "CSV baseline changed")
    ensure(baseline.get("rows") == 9688, "row baseline changed")
    ensure(baseline.get("availability_records") == 4754, "availability baseline changed")
    ensure(baseline.get("attributes") == 385, "attribute baseline changed")


def verify() -> None:
    verify_report(load_json(REPORT))
    verify_repository_evidence()
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the review contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Cross-Model Navigation Usability Review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
