#!/usr/bin/env python3
"""Apply the exact-current Spring Essential Biel Alpejska default colour."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/imports/spring_biel_alpejska_default_colour_20260802.csv"
VALUES_PATH = ROOT / "data/master/configuration_attribute_values.csv"
MAPPINGS_PATH = ROOT / "data/master/commercial_item_configurations.csv"
ITEMS_PATH = ROOT / "data/master/commercial_items.csv"
SOURCES_PATH = ROOT / "data/master/sources.csv"
REPRESENTATION_REVIEW_PATH = ROOT / "data/reporting/spring_standard_equipment_representation_review.json"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_biel_alpejska_default_colour_migration.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_biel_alpejska_default_colour_migration.md"

DATE = "2026-08-02"
SOURCE_CODE = "src_pl_spring_commercial_context_20260802"
CONFIGURATION_CODE = "spring_essential_electric70_automatic"
ATTRIBUTE_CODE = "exterior_color"
VALUE = "biel alpejska"
VALUE_CODE = "spring_essential_electric70_automatic_exterior_color_20260802"
MAPPING_CODE = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"
EXPRESSION_MAPPING = "spring_colour_biel_alpejska__spring_expression_electric70_automatic"
EXTREME_MAPPING = "spring_colour_biel_alpejska__spring_extreme_electric100_automatic"
TYPE2_ITEM = "spring_type2_charging_cable_option"
HOME_CABLE_ITEM = "spring_home_charging_cable_option"
OLD_SOURCE_CODE = "src_pl_spring_brochure_20260219"

SPEC_FIELDS = [
    "record_type",
    "configuration_code",
    "attribute_code",
    "value",
    "availability_status",
    "source_code",
    "source_page",
    "source_section",
    "source_text",
    "normalization_notes",
]
VALUE_FIELDS = [
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "gear_number",
    "value",
    "observation_date",
    "source_code",
    "notes",
]
MAPPING_FIELDS = [
    "id",
    "code",
    "commercial_item_code",
    "configuration_code",
    "availability_status",
    "amount",
    "currency_code",
    "price_date",
    "source_code",
    "notes",
]
EXPECTED_SPEC = {
    "record_type": "value",
    "configuration_code": CONFIGURATION_CODE,
    "attribute_code": ATTRIBUTE_CODE,
    "value": VALUE,
    "availability_status": "",
    "source_code": SOURCE_CODE,
    "source_page": "",
    "source_section": "Kolor",
    "source_text": "Biel Alpejska 0 zł",
    "normalization_notes": (
        "Exact-current Essential default paint at zero surcharge; stores the normalized "
        "direct scalar independently from the commercial palette relationship."
    ),
}
EXPECTED_VALUE = {
    "code": VALUE_CODE,
    "configuration_code": CONFIGURATION_CODE,
    "attribute_code": ATTRIBUTE_CODE,
    "fuel_type_code": "",
    "gear_number": "",
    "value": VALUE,
    "observation_date": DATE,
    "source_code": SOURCE_CODE,
    "notes": (
        "Exact-current Spring Essential default exterior colour. The direct scalar "
        "records the grade default independently from the zero-surcharge commercial "
        "palette relationship."
    ),
}
EXPECTED_MAPPING_BEFORE = {
    "availability_status": "optional",
    "amount": "",
    "currency_code": "PLN",
    "price_date": "",
    "source_code": OLD_SOURCE_CODE,
}
EXPECTED_MAPPING_AFTER = {
    "availability_status": "standard",
    "amount": "0",
    "currency_code": "PLN",
    "price_date": DATE,
    "source_code": SOURCE_CODE,
}


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def render_table(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def assert_subset(row: Mapping[str, str], expected: Mapping[str, str], label: str) -> None:
    actual = {field: row.get(field, "") for field in expected}
    if actual != dict(expected):
        raise RuntimeError(f"{label} drifted: {actual!r}")


def value_row(row_id: int) -> dict[str, str]:
    return {"id": str(row_id), **EXPECTED_VALUE}


def mapping_after(row: Mapping[str, str]) -> dict[str, str]:
    updated = dict(row)
    updated.update(EXPECTED_MAPPING_AFTER)
    updated["notes"] = (
        "Exact-current Spring Essential state: Biel Alpejska is the standard exterior "
        "colour at zero surcharge. The direct exterior_color scalar records the grade "
        "default; Expression and Extreme palette relationships remain unresolved."
    )
    return updated


def build_expected(
    spec_fields: list[str],
    spec_rows: list[dict[str, str]],
    value_fields: list[str],
    value_rows: list[dict[str, str]],
    mapping_fields: list[str],
    mapping_rows: list[dict[str, str]],
    item_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    representation_review: Mapping[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    if spec_fields != SPEC_FIELDS or spec_rows != [EXPECTED_SPEC]:
        raise RuntimeError("Biel Alpejska import specification drifted")
    if value_fields != VALUE_FIELDS:
        raise RuntimeError("configuration value schema drifted")
    if mapping_fields != MAPPING_FIELDS:
        raise RuntimeError("commercial mapping schema drifted")

    decisions = {
        row["concept"]: row for row in representation_review.get("decisions", [])
    }
    colour_decision = decisions.get("Essential Biel Alpejska default colour")
    if not colour_decision or colour_decision.get("classification") != "existing_pattern_available":
        raise RuntimeError("representation review no longer approves the colour pattern")
    approved = colour_decision["approved_representation"]
    if approved.get("direct_value_attribute") != ATTRIBUTE_CODE:
        raise RuntimeError("approved direct colour attribute drifted")
    commercial = approved.get("commercial_mapping", {})
    if commercial.get("mapping_code") != MAPPING_CODE:
        raise RuntimeError("approved commercial mapping drifted")
    if commercial.get("target_availability_status") != "standard":
        raise RuntimeError("approved commercial status drifted")
    if commercial.get("target_amount_pln") != 0:
        raise RuntimeError("approved commercial amount drifted")

    source_index = {row["code"]: row for row in source_rows}
    if SOURCE_CODE not in source_index or source_index[SOURCE_CODE]["status"] != "active":
        raise RuntimeError("exact-current Spring source is not registered and active")

    next_values = [dict(row) for row in value_rows]
    target_values = [row for row in next_values if row["code"] == VALUE_CODE]
    spring_colour_values = [
        row for row in next_values
        if row["configuration_code"].startswith("spring_")
        and row["attribute_code"] == ATTRIBUTE_CODE
    ]
    if target_values:
        if len(target_values) != 1:
            raise RuntimeError("duplicate Spring Essential colour value")
        assert_subset(target_values[0], EXPECTED_VALUE, "Spring Essential colour value")
        if spring_colour_values != target_values:
            raise RuntimeError("an unapproved additional Spring exterior colour value exists")
    else:
        if spring_colour_values:
            raise RuntimeError("unexpected pre-existing Spring exterior colour value")
        next_id = max(int(row["id"]) for row in next_values) + 1
        if next_id != 3568:
            raise RuntimeError(f"unexpected next configuration value id: {next_id}")
        next_values.append(value_row(next_id))

    mapping_index = {row["code"]: row for row in mapping_rows}
    if MAPPING_CODE not in mapping_index:
        raise RuntimeError("Essential Biel Alpejska mapping is missing")
    target_mapping = mapping_index[MAPPING_CODE]
    before = {field: target_mapping[field] for field in EXPECTED_MAPPING_BEFORE}
    after = {field: target_mapping[field] for field in EXPECTED_MAPPING_AFTER}
    if before == EXPECTED_MAPPING_BEFORE:
        replacement = mapping_after(target_mapping)
        next_mappings = [
            replacement if row["code"] == MAPPING_CODE else dict(row)
            for row in mapping_rows
        ]
    elif after == EXPECTED_MAPPING_AFTER:
        next_mappings = [dict(row) for row in mapping_rows]
        expected_notes = mapping_after(target_mapping)["notes"]
        if target_mapping["notes"] != expected_notes:
            raise RuntimeError("Essential Biel Alpejska mapping notes drifted")
    else:
        raise RuntimeError("Essential Biel Alpejska mapping is outside the approved transition")

    unchanged_index = {row["code"]: row for row in next_mappings}
    for code in (EXPRESSION_MAPPING, EXTREME_MAPPING):
        assert_subset(
            unchanged_index[code],
            {
                "availability_status": "optional",
                "amount": "",
                "currency_code": "PLN",
                "price_date": "",
                "source_code": OLD_SOURCE_CODE,
            },
            f"preserved mapping {code}",
        )

    type2 = [
        row for row in next_mappings
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(type2) != 3 or any(row["availability_status"] != "optional" for row in type2):
        raise RuntimeError("charging-cable boundary changed")
    item_codes = {row["code"] for row in item_rows}
    if HOME_CABLE_ITEM in item_codes:
        raise RuntimeError("home charging cable must remain unmodelled")

    final_value = next(row for row in next_values if row["code"] == VALUE_CODE)
    final_mapping = next(row for row in next_mappings if row["code"] == MAPPING_CODE)
    report = {
        "version": 1,
        "generated_on": DATE,
        "status": "complete",
        "scope": {
            "configuration_code": CONFIGURATION_CODE,
            "attribute_code": ATTRIBUTE_CODE,
            "commercial_mapping_code": MAPPING_CODE,
            "source_code": SOURCE_CODE,
        },
        "import_specification": {
            "path": "data/imports/spring_biel_alpejska_default_colour_20260802.csv",
            "row_count": 1,
            "record_type": "value",
        },
        "direct_value_migration": {
            "rows_added": 1,
            "before": None,
            "after": {
                "id": int(final_value["id"]),
                "code": final_value["code"],
                "configuration_code": final_value["configuration_code"],
                "attribute_code": final_value["attribute_code"],
                "value": final_value["value"],
                "observation_date": final_value["observation_date"],
                "source_code": final_value["source_code"],
            },
        },
        "commercial_mapping_migration": {
            "rows_updated": 1,
            "before": dict(EXPECTED_MAPPING_BEFORE),
            "after": {
                "availability_status": final_mapping["availability_status"],
                "amount_pln": int(final_mapping["amount"]),
                "currency_code": final_mapping["currency_code"],
                "price_date": final_mapping["price_date"],
                "source_code": final_mapping["source_code"],
            },
        },
        "preserved_boundaries": {
            "expression_white_mapping_unchanged": True,
            "extreme_white_mapping_unchanged": True,
            "type2_mapping_count_unchanged": 3,
            "home_cable_items_added": 0,
            "charging_attributes_added": 0,
        },
        "master_data_delta": {
            "configuration_value_rows_added": 1,
            "commercial_mapping_rows_updated": 1,
            "commercial_mapping_rows_added": 0,
            "source_rows_added": 0,
            "attributes_added": 0,
            "commercial_items_added": 0,
            "net_master_row_increase": 1,
        },
        "verified_after_counts": {
            "configuration_values": len(next_values),
            "configuration_import_specs": 139,
            "master_rows": 11715,
        },
        "next_package": {
            "package_id": "spring_supplied_charging_cable_model_decision_001",
            "goal": (
                "Record an explicit architecture decision for independently supplied Type 2 "
                "and home charging cables before creating attributes or commercial mappings."
            ),
        },
    }
    if report["verified_after_counts"]["configuration_values"] != 3568:
        raise RuntimeError("unexpected configuration-value count after migration")
    return next_values, next_mappings, report


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    value = report["direct_value_migration"]["after"]
    mapping = report["commercial_mapping_migration"]["after"]
    return f"""# Spring Essential Biel Alpejska Default Colour Migration

**Status:** complete  
**Date:** {report['generated_on']}

## Direct default-colour value

- Configuration: `{value['configuration_code']}`
- Attribute: `{value['attribute_code']}`
- Value: **{value['value']}**
- Observation date: `{value['observation_date']}`
- Source: `{value['source_code']}`

The direct scalar records the exact-current grade default independently from the commercial palette relationship.

## Commercial relationship

`{report['scope']['commercial_mapping_code']}` is now:

- availability: `{mapping['availability_status']}`
- surcharge: **{mapping['amount_pln']} {mapping['currency_code']}**
- price date: `{mapping['price_date']}`
- source: `{mapping['source_code']}`

## Preserved boundaries

- Expression Biel Alpejska remains an unresolved optional palette relationship;
- Extreme Biel Alpejska remains an unresolved optional palette relationship;
- all three Type 2 mappings remain unchanged;
- no home-cable item, charging attribute or cable mapping is added.

## Master-data delta

- configuration values added: 1;
- commercial mappings updated: 1;
- net master-row increase: 1;
- attributes and commercial items added: 0.

## Next package

`{report['next_package']['package_id']}` must record the supplied-cable architecture decision before any charging-cable mutation.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def build(root: Path = ROOT) -> tuple[str, str, dict[str, Any]]:
    spec_fields, spec_rows = read_table(root / SPEC_PATH.relative_to(ROOT))
    value_fields, value_rows = read_table(root / VALUES_PATH.relative_to(ROOT))
    mapping_fields, mapping_rows = read_table(root / MAPPINGS_PATH.relative_to(ROOT))
    _, item_rows = read_table(root / ITEMS_PATH.relative_to(ROOT))
    _, source_rows = read_table(root / SOURCES_PATH.relative_to(ROOT))
    review = read_object(root / REPRESENTATION_REVIEW_PATH.relative_to(ROOT))
    next_values, next_mappings, report = build_expected(
        spec_fields,
        spec_rows,
        value_fields,
        value_rows,
        mapping_fields,
        mapping_rows,
        item_rows,
        source_rows,
        review,
    )
    return (
        render_table(value_fields, next_values),
        render_table(mapping_fields, next_mappings),
        report,
    )


def apply(root: Path = ROOT) -> None:
    values_content, mappings_content, report = build(root)
    write_atomic(root / VALUES_PATH.relative_to(ROOT), values_content)
    write_atomic(root / MAPPINGS_PATH.relative_to(ROOT), mappings_content)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    values_content, mappings_content, report = build(root)
    if (root / VALUES_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != values_content:
        raise RuntimeError("configuration_attribute_values.csv is not in the approved state")
    if (root / MAPPINGS_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != mappings_content:
        raise RuntimeError("commercial_item_configurations.csv is not in the approved state")
    if read_object(root / REPORT_JSON_PATH.relative_to(ROOT)) != report:
        raise RuntimeError("Biel Alpejska migration JSON is stale")
    if (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("Biel Alpejska migration Markdown is stale")


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
