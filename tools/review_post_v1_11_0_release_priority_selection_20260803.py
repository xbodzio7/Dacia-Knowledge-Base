#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from catalog_completion_history import DUSTER_HYBRIDG150_CONFIGURATION_CODES


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/post_v1_11_0_release_priority_selection_review.json"
REPORT_MD = ROOT / "data/reporting/post_v1_11_0_release_priority_selection_review.md"
PACKAGE_DOC = ROOT / "project/packages/post-v1.11.0-release-priority-selection-review-20260803.md"
STATE_PATH = ROOT / "project/state.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
PACKAGE_ID = "post_v1_11_0_release_priority_selection_review_001"
NEXT_PACKAGE_ID = "portfolio_model_family_summary_001"
CHANGELOG_ENTRY = (
    "* Added a deterministic post-v1.11.0 priority review that confirms zero "
    "eligible source-backed completeness candidates, preserves all exhausted "
    "source boundaries and selects a scope-preserving portfolio model-family "
    "summary as the next reporting package without ranking or inferred values."
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def source_registry_summary() -> dict[str, Any]:
    rows = [
        row for row in read_csv(ROOT / "data/master/sources.csv")
        if not row.get("document_date") or row.get("document_date") <= "2026-08-03"
    ]
    fields = tuple(rows[0]) if rows else ()
    type_field = next(
        (name for name in ("source_type", "type", "kind") if name in fields),
        None,
    )
    status_field = next(
        (name for name in ("status", "lifecycle_status") if name in fields),
        None,
    )
    return {
        "source_count": len(rows),
        "source_type_counts": (
            dict(sorted(Counter(row[type_field] for row in rows).items()))
            if type_field
            else {}
        ),
        "source_status_counts": (
            dict(sorted(Counter(row[status_field] for row in rows).items()))
            if status_field
            else {}
        ),
    }


def historical_completeness_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Preserve the 2026-08-03 review denominator after later catalog additions."""
    summary = dict(payload["summary"])
    later_rows = [
        item
        for item in payload.get("configurations", [])
        if item.get("configuration_code") in DUSTER_HYBRIDG150_CONFIGURATION_CODES
    ]
    if not later_rows:
        return summary
    if {
        item.get("configuration_code") for item in later_rows
    } != DUSTER_HYBRIDG150_CONFIGURATION_CODES:
        raise RuntimeError("later Duster hybrid-G 150 completeness scope differs")
    if any(
        item.get("scope_file") != "duster_hybridg150_4x4_completeness.json"
        or item.get("expected_technical") != 0
        or item.get("expected_equipment") != 0
        for item in later_rows
    ):
        raise RuntimeError("later Duster identity-only completeness boundary differs")
    summary["active_configuration_count"] -= len(later_rows)
    summary["completeness_scope_count"] -= 1
    return summary


def build_report() -> dict[str, Any]:
    publication = read_json(
        ROOT / "data/reporting/data_products_v1_11_0_publication.json"
    )
    completeness = read_json(
        ROOT / "data/reporting/existing_configuration_missing_data_analysis.json"
    )
    roadmap = (ROOT / "project/ROADMAP.md").read_text(encoding="utf-8")
    summary = historical_completeness_summary(completeness)

    if publication["status"] != "complete":
        raise RuntimeError("v1.11.0 publication is not complete")
    if publication["tag"] != "data-products-v1.11.0":
        raise RuntimeError("unexpected publication tag")
    if summary["eligible_candidate_count"] != 0:
        raise RuntimeError("source-backed candidate selection must remain source-led")
    if summary["exhausted_source_candidate_count"] != summary["candidate_count"]:
        raise RuntimeError("not every current source candidate is exhausted")

    roadmap_contract = (
        "wybór najwyżej wartościowego kolejnego pakietu raportowego",
        "porównania modeli i wersji wykraczające poza bieżące konfiguracje",
        "dalsze stabilne formaty raportów dla użytkowników zewnętrznych",
    )
    missing_roadmap = [item for item in roadmap_contract if item not in roadmap]
    if missing_roadmap:
        raise RuntimeError(f"roadmap reporting contract missing: {missing_roadmap}")

    return {
        "version": 1,
        "as_of": "2026-08-03",
        "kind": "post_v1_11_0_release_priority_selection_review",
        "status": "complete",
        "publication": {
            "tag": publication["tag"],
            "source_commit": publication["source_commit"],
            "double_build_byte_identity": publication["double_build_byte_identity"],
            "offline_workspace_verification": publication[
                "offline_workspace_verification"
            ],
        },
        "source_registry": source_registry_summary(),
        "completeness": {
            "active_configuration_count": summary["active_configuration_count"],
            "completeness_scope_count": summary["completeness_scope_count"],
            "missing_technical_count": summary["missing_technical_count"],
            "missing_equipment_count": summary["missing_equipment_count"],
            "candidate_count": summary["candidate_count"],
            "exhausted_source_candidate_count": summary[
                "exhausted_source_candidate_count"
            ],
            "eligible_candidate_count": summary["eligible_candidate_count"],
        },
        "roadmap_reporting_contract": list(roadmap_contract),
        "selection": {
            "package_id": NEXT_PACKAGE_ID,
            "kind": "reporting_product",
            "name": "Portfolio Model Family Summary",
            "status": "planned",
            "goal": (
                "Create deterministic JSON, Markdown and HTML summaries for each "
                "model family from current source-backed active configurations, "
                "preserving independent reporting scopes and exact provenance "
                "without cross-scope pairs, ranking, recommendations or inferred values."
            ),
            "rationale": [
                "the immutable v1.11.0 release is complete and verified",
                "all seven source-backed completeness candidates are exhausted",
                "the roadmap explicitly prioritizes the next high-value reporting package",
                "the existing 81-configuration portfolio supports a bounded family-level view",
                "the package extends stable external reporting without changing master data",
            ],
        },
        "preserved_boundaries": [
            "no exhausted source candidate is reopened",
            "no missing value is converted to zero or not_available",
            "no cross-scope configuration pair is generated",
            "no ranking or recommendation is generated",
            "no source-backed value is inferred or transferred between configurations",
            "no new source, model or architecture scope is introduced",
        ],
        "rejected_alternatives": [
            {
                "kind": "source_backed_import",
                "reason": "eligible_candidate_count is zero",
            },
            {
                "kind": "new_source_or_model_expansion",
                "reason": "would require a new scope decision or external source intake",
            },
            {
                "kind": "cross_scope_ranking",
                "reason": "would violate current comparison and non-inference semantics",
            },
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    completeness = report["completeness"]
    selection = report["selection"]
    source_registry = report["source_registry"]
    lines = [
        "# Post-v1.11.0 Release Priority Selection Review",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Canonical evidence",
        "",
        f"- published release: `{report['publication']['tag']}` from `{report['publication']['source_commit']}`;",
        f"- registered sources: {source_registry['source_count']};",
        f"- active configurations: {completeness['active_configuration_count']};",
        f"- completeness scopes: {completeness['completeness_scope_count']};",
        f"- missing technical slots: {completeness['missing_technical_count']};",
        f"- missing equipment slots: {completeness['missing_equipment_count']};",
        f"- source candidates: {completeness['candidate_count']};",
        f"- exhausted candidates: {completeness['exhausted_source_candidate_count']};",
        f"- eligible candidates: {completeness['eligible_candidate_count']}.",
        "",
        "## Selected package",
        "",
        f"**{selection['name']}** — `{selection['package_id']}`",
        "",
        selection["goal"],
        "",
        "### Rationale",
        "",
    ]
    lines.extend(f"- {item};" for item in selection["rationale"])
    lines.extend(["", "## Preserved boundaries", ""])
    lines.extend(f"- {item};" for item in report["preserved_boundaries"])
    lines.extend(["", "## Rejected alternatives", ""])
    lines.extend(
        f"- `{item['kind']}` — {item['reason']};"
        for item in report["rejected_alternatives"]
    )
    return "\n".join(lines) + "\n"


def render_package(report: dict[str, Any]) -> str:
    selection = report["selection"]
    return f"""# Post-v1.11.0 Release Priority Selection Review

Date: 2026-08-03

Package ID: `{PACKAGE_ID}`

Status: **complete**

## Result

The canonical release receipt, source registry, completeness analysis and roadmap were reviewed after immutable `data-products-v1.11.0` publication.

The completeness queue contains {report['completeness']['candidate_count']} source candidates and all are exhausted; the eligible count is zero. No source-backed import can therefore be selected without new evidence or a new scope decision.

The roadmap explicitly asks for the highest-value next reporting package, cross-model/version views beyond the current configuration surfaces and stable external formats. The selected package is:

`{selection['package_id']}` — **{selection['name']}**

{selection['goal']}

## Non-inference boundary

The selection does not reopen exhausted candidates, introduce a new source or model, create cross-scope pairs, rank configurations or infer missing values.

## Verification

```bash
python tools/review_post_v1_11_0_release_priority_selection_20260803.py --verify
python -m unittest tests.test_post_v1_11_0_release_priority_selection_20260803
python tools/dkb.py project-state --check
```
"""


def expected_state(report: dict[str, Any]) -> dict[str, Any]:
    state = read_json(STATE_PATH)
    state["updated_on"] = "2026-08-03"
    state["phase"] = "Post-v1.11.0 Release Priority Selection Review"
    state["baseline"]["tests"] = 1842
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "priority_selection_review",
        "name": "Post-v1.11.0 Release Priority Selection Review",
        "status": "complete",
        "goal": (
            "Inspect canonical release, source, completeness and roadmap evidence "
            "and select one bounded next package without reopening closed evidence."
        ),
        "manifest_paths": [
            "tools/review_post_v1_11_0_release_priority_selection_20260803.py",
            "data/reporting/post_v1_11_0_release_priority_selection_review.json",
            "data/reporting/post_v1_11_0_release_priority_selection_review.md",
            "project/packages/post-v1.11.0-release-priority-selection-review-20260803.md",
            "tests/test_post_v1_11_0_release_priority_selection_20260803.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
        ],
    }
    state["next_package"] = {
        "package_id": report["selection"]["package_id"],
        "kind": report["selection"]["kind"],
        "name": report["selection"]["name"],
        "status": report["selection"]["status"],
        "goal": report["selection"]["goal"],
        "manifest_paths": [],
    }
    return state


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


def apply() -> None:
    report = build_report()
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_DOC.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    PACKAGE_DOC.write_text(render_package(report), encoding="utf-8")
    STATE_PATH.write_text(
        json.dumps(expected_state(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    update_changelog()


def verify() -> None:
    report = build_report()
    expected_files = {
        REPORT_JSON: json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        REPORT_MD: render_markdown(report),
        PACKAGE_DOC: render_package(report),
    }
    for path, expected in expected_files.items():
        if not path.exists():
            raise RuntimeError(f"missing generated output: {path.relative_to(ROOT)}")
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            raise RuntimeError(f"generated output differs: {path.relative_to(ROOT)}")
    state = read_json(STATE_PATH)
    expected = expected_state(report)
    if state["current_package"]["package_id"] == PACKAGE_ID:
        if state["phase"] != expected["phase"]:
            raise RuntimeError("canonical project phase differs")
        if state["baseline"]["tests"] != expected["baseline"]["tests"]:
            raise RuntimeError("canonical test baseline differs")
        for section in ("current_package", "next_package"):
            for key in ("package_id", "kind", "name", "status", "goal"):
                if state[section][key] != expected[section][key]:
                    raise RuntimeError(
                        f"canonical project state differs for {section}.{key}"
                    )
        required_manifest = set(
            expected["current_package"]["manifest_paths"]
        )
        actual_manifest = set(
            state["current_package"]["manifest_paths"]
        )
        if not required_manifest.issubset(actual_manifest):
            raise RuntimeError("canonical package manifest is incomplete")
    else:
        if state["baseline"]["tests"] < 1842:
            raise RuntimeError("canonical test baseline regressed")
        if report["selection"]["package_id"] != NEXT_PACKAGE_ID:
            raise RuntimeError("durable selected package differs")
        if not PACKAGE_DOC.exists():
            raise RuntimeError("durable package receipt is missing")
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
    print("Post-v1.11.0 priority selection review: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
