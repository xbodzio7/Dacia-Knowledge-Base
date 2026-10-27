#!/usr/bin/env python3
"""Build and verify the bounded Spring commercial-context review package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "project/sources/dacia-pl-spring-commercial-context-20260802.json"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_commercial_context_resolution.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_commercial_context_resolution.md"


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def build_report(source: Mapping[str, Any]) -> dict[str, Any]:
    decisions = source["decisions"]
    type2 = decisions["type2_charging_cable"]
    paint = decisions["paint_context"]
    stock = decisions["stock_context"]
    conclusion = source["package_conclusion"]

    exact_type2 = [
        item for item in type2
        if item["review_resolution"] == "exact_current_standard"
    ]
    unresolved_type2 = [
        item for item in type2
        if item["review_resolution"] != "exact_current_standard"
    ]
    exact_paints = paint["exact_current_my26"]

    return {
        "version": 1,
        "generated_on": source["observed_on"],
        "status": "complete",
        "source_code": source["source_code"],
        "scope": {
            "model_code": source["model_code"],
            "market": source["market"],
            "official_source_count": len(source["official_sources"]),
            "master_data_mutation_authorized": source["scope"][
                "master_data_mutation_authorized"
            ],
        },
        "type2_resolution": {
            "reviewed_configuration_count": len(type2),
            "exact_current_standard_count": len(exact_type2),
            "exact_current_standard_configurations": [
                item["configuration_code"] for item in exact_type2
            ],
            "current_grade_unresolved_count": len(unresolved_type2),
            "current_grade_unresolved_configurations": [
                item["configuration_code"] for item in unresolved_type2
            ],
            "master_action": "defer_semantic_migration",
            "reason": (
                "The current exact Essential and Extreme states classify the Type 2 "
                "cable as standard. The existing commercial item is option-shaped, so "
                "the review does not write a fabricated zero-price option row."
            ),
        },
        "paint_resolution": {
            "exact_current_my26_rows": exact_paints,
            "exact_current_my26_count": len(exact_paints),
            "my2025_price_promotions": conclusion["my2025_prices_promoted_to_my26"],
            "legacy_palette_global_removals": 0,
            "master_action": paint["master_action"],
            "reason": (
                "Only the exact Essential MY26 palette is current and configuration-"
                "specific. MY2025 stock prices and absence from one grade palette are "
                "not transferred to uncaptured current grades."
            ),
        },
        "stock_resolution": {
            "classification": stock["review_resolution"],
            "stock_totals_decomposed": conclusion["stock_totals_decomposed"],
            "master_action": stock["master_action"],
            "reason": stock["reason"],
        },
        "mutation_summary": {
            "master_rows_changed": conclusion["master_rows_changed"],
            "prices_imported": 0,
            "availability_states_changed": 0,
            "models_or_domains_added": 0,
        },
        "findings": [
            "Current exact MY26 evidence resolves the Type 2 cable as standard for Essential electric 70 and Extreme electric 100.",
            "Expression electric 70 remains unresolved for current MY26 because the exact official matrix captured in this review is MY2025 stock-only.",
            "Essential MY26 has exact current paint states: Biel alpejska is standard at 0 PLN and Khaki lichen is optional at 2300 PLN.",
            "The 2300 PLN MY2025 paint class is not promoted to current Expression or Extreme mappings.",
            "Whole-vehicle stock totals are not decomposed into reusable standalone option or paint prices.",
        ],
        "next_package": {
            "package_id": conclusion["next_package"],
            "goal": (
                "Capture exact current official Expression and Extreme grade states, "
                "including their paint palettes and charging-equipment semantics, "
                "before any bounded master-data migration."
            ),
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    type2 = report["type2_resolution"]
    paint = report["paint_resolution"]
    stock = report["stock_resolution"]
    paints = "\n".join(
        f"- `{item['configuration_code']}` / `{item['commercial_item_code']}`: "
        f"**{item['availability_status']}**, {item['price_pln']} PLN"
        for item in paint["exact_current_my26_rows"]
    )
    findings = "\n".join(f"- {item}" for item in report["findings"])
    return f"""# Spring Commercial Context Resolution

**Status:** complete  
**Date:** {report['generated_on']}  
**Master-data mutations:** 0

## Type 2 charging cable

Current exact official MY26 evidence resolves the cable as **standard equipment** for:

- `spring_essential_electric70_automatic`,
- `spring_extreme_electric100_automatic`.

`spring_expression_electric70_automatic` remains unresolved for the current model year. The exact official matrix available in this review is explicitly limited to MY2025 dealer stock, so its standard state is not promoted to MY26.

The existing commercial item is option-shaped. This package therefore records the conflict resolution but does not create a zero-price option or silently change availability semantics.

## Paint context

Exact current MY26 observations:

{paints}

The official 2300 PLN paint class for Expression and Extreme belongs to the MY2025 stock-only price list. It remains historical/contextual evidence and is not transferred to current MY26 mappings. Legacy colours absent from the captured Essential palette are not globally removed because current Expression and Extreme palettes were not captured exactly.

## Stock context

Classification: `{stock['classification']}`.

{stock['reason']}

## Findings

{findings}

## Data boundary

- master rows changed: **0**,
- prices imported: **0**,
- availability states changed: **0**,
- models or domains added: **0**.

## Next package

`{report['next_package']['package_id']}` will capture exact current Expression and Extreme grade states before any bounded commercial migration.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def verify(root: Path = ROOT) -> None:
    source = read_object(root / SOURCE_PATH.relative_to(ROOT))
    expected = build_report(source)
    actual = read_object(root / REPORT_JSON_PATH.relative_to(ROOT))
    if actual != expected:
        raise RuntimeError("Spring commercial context JSON report is stale")
    expected_markdown = render_markdown(expected)
    actual_markdown = (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(
        encoding="utf-8"
    )
    if actual_markdown != expected_markdown:
        raise RuntimeError("Spring commercial context Markdown report is stale")


def apply(root: Path = ROOT) -> None:
    source = read_object(root / SOURCE_PATH.relative_to(ROOT))
    report = build_report(source)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    if arguments.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
