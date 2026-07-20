from __future__ import annotations

from pathlib import Path
from typing import Any

from reporting.data_product_release_model import (
    file_record,
    json_text,
    write_text,
)


CONFIGURATION_CODES = tuple(
    f"fixture_configuration_{index:02d}"
    for index in range(1, 54)
)
SCOPE_NAMES = tuple(
    f"fixture_scope_{index:02d}"
    for index in range(1, 14)
)


def create_workspace_payload(payload: Path) -> dict[str, Any]:
    write_text(
        payload / "shortlist/configuration-shortlist.html",
        "<!doctype html><title>Fixture shortlist</title>\n",
    )
    write_text(payload / "RELEASE_NOTES.md", "# Fixture release notes\n")

    bundle_root = payload / "comparison-bundle"
    workbook = bundle_root / "configuration-comparison-workbook.xlsx"
    workbook.parent.mkdir(parents=True, exist_ok=True)
    workbook.write_bytes(b"fixture-workbook")

    report_paths = {
        "json": bundle_root / "fixture_scope_01.comparison.json",
        "markdown": bundle_root / "fixture_scope_01.comparison.md",
        "csv": bundle_root / "fixture_scope_01.differences.csv",
        "html": bundle_root / "fixture_scope_01.comparison.html",
    }
    write_text(report_paths["json"], '{"fixture": true}\n')
    write_text(report_paths["markdown"], "# Fixture comparison\n")
    write_text(report_paths["csv"], "field,value\nfixture,true\n")
    write_text(
        report_paths["html"],
        "<!doctype html><title>Fixture comparison</title>\n",
    )

    groups: list[dict[str, Any]] = [
        {
            "scope": SCOPE_NAMES[0],
            "status": "comparable",
            "source_completeness_spec": "fixture_scope_01_completeness.json",
            "source_evidence_spec": "fixture_scope_01_gap_evidence.json",
            "configuration_codes": list(CONFIGURATION_CODES[:41]),
            "pair_count": 820,
            "total_differences": 17,
            "evidence_summary": {},
            "report_as_of": "2026-06-26",
            "files": {
                key: file_record(path, bundle_root)
                for key, path in report_paths.items()
            },
        }
    ]
    for offset, scope in enumerate(SCOPE_NAMES[1:], start=41):
        groups.append(
            {
                "scope": scope,
                "status": "singleton",
                "source_completeness_spec": f"{scope}_completeness.json",
                "source_evidence_spec": f"{scope}_gap_evidence.json",
                "configuration_codes": [CONFIGURATION_CODES[offset]],
                "pair_count": 0,
                "total_differences": 0,
                "files": {},
            }
        )

    bundle = {
        "version": 1,
        "selection_sources": {},
        "selected_configuration_codes": list(CONFIGURATION_CODES),
        "selected_configuration_count": len(CONFIGURATION_CODES),
        "scope_group_count": len(groups),
        "comparable_scope_count": 1,
        "singleton_scope_count": 12,
        "cross_scope_pairs_generated": False,
        "groups": groups,
        "workbook": file_record(workbook, bundle_root),
    }
    write_text(
        bundle_root / "comparison-bundle-manifest.json",
        json_text(bundle),
    )
    return bundle
