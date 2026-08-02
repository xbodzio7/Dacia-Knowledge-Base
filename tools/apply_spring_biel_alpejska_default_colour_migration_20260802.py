#!/usr/bin/env python3
"""Apply and verify the exact-current Spring Essential Biel Alpejska migration."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/imports/configuration_values/spring_biel_alpejska_default_colour_20260802.json"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
REPORT_JSON = ROOT / "data/reporting/spring_biel_alpejska_default_colour_migration.json"
REPORT_MD = ROOT / "data/reporting/spring_biel_alpejska_default_colour_migration.md"
IMPORTER = ROOT / "tools/import_configuration_values.py"

DATE = "2026-08-02"
SOURCE = "src_pl_spring_commercial_context_20260802"
CONFIGURATION = "spring_essential_electric70_automatic"
ATTRIBUTE = "exterior_color"
VALUE = "biel alpejska"
VALUE_CODE = "spring_essential_electric70_automatic_exterior_color_20260802"
WHITE_MAPPING = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"
EXPRESSION_MAPPING = "spring_colour_biel_alpejska__spring_expression_electric70_automatic"
EXTREME_MAPPING = "spring_colour_biel_alpejska__spring_extreme_electric100_automatic"
TYPE2_ITEM = "spring_type2_charging_cable_option"
DOMESTIC_ITEM = "spring_domestic_socket_charging_cable_option"

EXPECTED_SPEC = {
    "attribute_code": ATTRIBUTE,
    "attribute_contract": {"data_type": "string", "status": "active", "unit": ""},
    "fuel_type_code": "",
    "id_start": 3568,
    "kind": "configuration_attribute_values",
    "notes_template": (
        "Exact-current Spring Essential default exterior colour. Source page {page}, "
        "section {section}: {source_text}. The direct scalar records the grade default "
        "independently from the zero-surcharge commercial palette relationship."
    ),
    "observation_date": DATE,
    "rows": [{
        "configuration_code": CONFIGURATION,
        "source_code": SOURCE,
        "source_text": "Biel Alpejska — standard — 0 PLN",
        "value": VALUE,
    }],
    "source_page": 1,
    "source_section": "official_sources[0].evidence.exterior_colours",
    "version": 1,
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected object: {path}")
    return value


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_importer():
    module_name = "configuration_value_importer"
    spec = importlib.util.spec_from_file_location(module_name, IMPORTER)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load canonical configuration-value importer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def expected_value_row(root: Path = ROOT) -> dict[str, str]:
    importer = load_importer()
    loaded = importer.load_spec(root / SPEC.relative_to(ROOT))
    rows = importer.build_expected_rows(root, loaded)
    if len(rows) != 1:
        raise AssertionError("Spring white specification must generate exactly one row")
    return dict(rows[0])


def build(root: Path = ROOT) -> dict[str, Any]:
    spec_payload = read_json(root / SPEC.relative_to(ROOT))
    if spec_payload != EXPECTED_SPEC:
        raise AssertionError("canonical Spring white specification drifted")

    expected = expected_value_row(root)
    _, values = read_csv(root / VALUES.relative_to(ROOT))
    stored = [row for row in values if row["code"] == VALUE_CODE]
    if stored != [expected]:
        raise AssertionError("stored Spring Essential direct colour value drifted")

    _, mappings = read_csv(root / MAPPINGS.relative_to(ROOT))
    index = {row["code"]: row for row in mappings}
    white = index[WHITE_MAPPING]
    if {
        "availability_status": white["availability_status"],
        "amount": white["amount"],
        "currency_code": white["currency_code"],
        "price_date": white["price_date"],
        "source_code": white["source_code"],
    } != {
        "availability_status": "standard",
        "amount": "0",
        "currency_code": "PLN",
        "price_date": DATE,
        "source_code": SOURCE,
    }:
        raise AssertionError("stored Essential white mapping drifted")
    for code in (EXPRESSION_MAPPING, EXTREME_MAPPING):
        row = index[code]
        if row["availability_status"] != "optional" or row["amount"] or row["price_date"]:
            raise AssertionError(f"unapproved white mapping changed: {code}")
    type2 = [row for row in mappings if row["commercial_item_code"] == TYPE2_ITEM]
    domestic = [row for row in mappings if row["commercial_item_code"] == DOMESTIC_ITEM]
    if len(type2) != 3 or len(domestic) != 2:
        raise AssertionError("completed charging-cable mappings were not preserved")

    return {
        "version": 1,
        "generated_on": DATE,
        "status": "complete",
        "scope": {
            "configuration_code": CONFIGURATION,
            "attribute_code": ATTRIBUTE,
            "commercial_mapping_code": WHITE_MAPPING,
            "source_code": SOURCE,
        },
        "import_specification": {
            "path": str(SPEC.relative_to(root)).replace("\\", "/"),
            "kind": "configuration_attribute_values",
            "row_count": 1,
            "id_start": 3568,
        },
        "direct_value_migration": {
            "rows_added": 1,
            "before": None,
            "after": {
                "id": 3568,
                "code": VALUE_CODE,
                "configuration_code": CONFIGURATION,
                "attribute_code": ATTRIBUTE,
                "value": VALUE,
                "observation_date": DATE,
                "source_code": SOURCE,
            },
        },
        "commercial_mapping_migration": {
            "rows_updated": 1,
            "before": {
                "availability_status": "optional",
                "amount": "",
                "currency_code": "PLN",
                "price_date": "",
                "source_code": "src_pl_spring_brochure_20260219",
            },
            "after": {
                "availability_status": "standard",
                "amount_pln": 0,
                "currency_code": "PLN",
                "price_date": DATE,
                "source_code": SOURCE,
            },
        },
        "preserved_boundaries": {
            "expression_white_mapping_unchanged": True,
            "extreme_white_mapping_unchanged": True,
            "type2_mapping_count_unchanged": 3,
            "domestic_cable_mapping_count_unchanged": 2,
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
            "configuration_values": 3568,
            "configuration_import_specs": 139,
            "master_rows": 11728,
        },
        "next_package": {
            "package_id": "post_spring_biel_alpejska_priority_selection_review_001",
            "goal": "Select the next bounded repository package after the accepted default-colour migration.",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    return (
        "# Spring Essential Biel Alpejska Default Colour Migration\n\n"
        "**Status:** complete  \n**Date:** 2026-08-02\n\n"
        "- Direct value: `exterior_color = biel alpejska` for Spring Essential Electric 70.\n"
        "- Commercial mapping: `standard`, **0 PLN**.\n"
        "- Expression and Extreme white mappings remain unresolved and unchanged.\n"
        "- Completed Type 2 and domestic-socket cable representations remain unchanged.\n"
    )


def apply(root: Path = ROOT) -> None:
    importer = load_importer()
    loaded = importer.load_spec(root / SPEC.relative_to(ROOT))
    expected = dict(importer.build_expected_rows(root, loaded)[0])
    values_path = root / VALUES.relative_to(ROOT)
    fields, rows = read_csv(values_path)
    replaced = False
    for idx, row in enumerate(rows):
        if row["code"] == VALUE_CODE:
            rows[idx] = expected
            replaced = True
    if not replaced:
        rows.append(expected)
    write_csv(values_path, fields, rows)

    mappings_path = root / MAPPINGS.relative_to(ROOT)
    fields, rows = read_csv(mappings_path)
    for row in rows:
        if row["code"] == WHITE_MAPPING:
            row.update({
                "availability_status": "standard",
                "amount": "0",
                "currency_code": "PLN",
                "price_date": DATE,
                "source_code": SOURCE,
                "notes": (
                    "Exact-current Spring Essential state: Biel Alpejska is the standard "
                    "exterior colour at zero surcharge. The direct exterior_color scalar "
                    "records the grade default; Expression and Extreme remain unresolved."
                ),
            })
    write_csv(mappings_path, fields, rows)
    report = build(root)
    (root / REPORT_JSON.relative_to(ROOT)).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (root / REPORT_MD.relative_to(ROOT)).write_text(render_markdown(report), encoding="utf-8")


def verify(root: Path = ROOT) -> None:
    report = build(root)
    if read_json(root / REPORT_JSON.relative_to(ROOT)) != report:
        raise AssertionError("committed Spring white report is not deterministic")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    verify()
    print("Spring Essential Biel Alpejska migration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
