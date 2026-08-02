#!/usr/bin/env python3
"""Review existing repository representations for current Spring equipment."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES_PATH = ROOT / "data/master/attributes.csv"
VALUES_PATH = ROOT / "data/master/configuration_attribute_values.csv"
AVAILABILITY_PATH = ROOT / "data/master/configuration_attribute_availability.csv"
ITEMS_PATH = ROOT / "data/master/commercial_items.csv"
MEMBERSHIPS_PATH = ROOT / "data/master/commercial_item_attributes.csv"
MAPPINGS_PATH = ROOT / "data/master/commercial_item_configurations.csv"
SEMANTIC_REVIEW_PATH = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.json"
KHaki_APPLY_PATH = ROOT / "data/reporting/spring_essential_khaki_price_apply.json"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_standard_equipment_representation_review.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_standard_equipment_representation_review.md"

ESSENTIAL = "spring_essential_electric70_automatic"
EXTREME = "spring_extreme_electric100_automatic"
EXPRESSION = "spring_expression_electric70_automatic"
TYPE2_ITEM = "spring_type2_charging_cable_option"
HOME_CABLE_ITEM = "spring_home_charging_cable_option"
WHITE_MAPPING = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def is_cable_attribute(row: Mapping[str, str]) -> bool:
    text = " ".join(
        row.get(field, "").lower()
        for field in ("code", "name", "description")
    )
    terms = ("charging cable", "charge cable", "charging cord", "cable supplied")
    return any(term in text for term in terms)


def build(root: Path = ROOT) -> dict[str, Any]:
    attributes = read_rows(root / ATTRIBUTES_PATH.relative_to(ROOT))
    values = read_rows(root / VALUES_PATH.relative_to(ROOT))
    availability = read_rows(root / AVAILABILITY_PATH.relative_to(ROOT))
    items = read_rows(root / ITEMS_PATH.relative_to(ROOT))
    memberships = read_rows(root / MEMBERSHIPS_PATH.relative_to(ROOT))
    mappings = read_rows(root / MAPPINGS_PATH.relative_to(ROOT))
    semantic = read_object(root / SEMANTIC_REVIEW_PATH.relative_to(ROOT))
    khaki = read_object(root / KHaki_APPLY_PATH.relative_to(ROOT))

    attribute_index = {row["code"]: row for row in attributes}
    item_index = {row["code"]: row for row in items}
    mapping_index = {row["code"]: row for row in mappings}

    if attribute_index["exterior_color"]["data_type"] != "string":
        raise RuntimeError("exterior_color representation drifted")
    if attribute_index["charging_connector_type"]["description"] != "Charging connector standard":
        raise RuntimeError("charging_connector_type semantics drifted")

    exterior_values = [row for row in values if row["attribute_code"] == "exterior_color"]
    spring_exterior_values = [
        row for row in exterior_values
        if row["configuration_code"].startswith("spring_")
    ]
    connector_values = [
        row for row in values
        if row["attribute_code"] == "charging_connector_type"
    ]
    standard_availability = [
        row for row in availability
        if row["availability_status"] == "standard"
    ]
    cable_attributes = [row["code"] for row in attributes if is_cable_attribute(row)]

    type2_memberships = [
        row for row in memberships
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    type2_mappings = [
        row for row in mappings
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    standard_commercial = [
        row for row in mappings
        if row["availability_status"] == "standard"
    ]
    grade_standard_commercial = [
        row for row in standard_commercial
        if "exact_stock" not in row["source_code"]
    ]

    if len(exterior_values) < 1:
        raise RuntimeError("repository lost the direct exterior_color pattern")
    spring_colour_before = not spring_exterior_values
    spring_colour_after = (
        len(spring_exterior_values) == 1
        and spring_exterior_values[0]["code"]
        == "spring_essential_electric70_automatic_exterior_color_20260802"
        and spring_exterior_values[0]["configuration_code"] == ESSENTIAL
        and spring_exterior_values[0]["attribute_code"] == "exterior_color"
        and spring_exterior_values[0]["value"] == "biel alpejska"
        and spring_exterior_values[0]["observation_date"] == "2026-08-02"
        and spring_exterior_values[0]["source_code"]
        == "src_pl_spring_commercial_context_20260802"
    )
    if not (spring_colour_before or spring_colour_after):
        raise RuntimeError("Spring exterior_color is outside the reviewed transition")
    if connector_values:
        raise RuntimeError("unexpected unconditional charging_connector_type scalar")
    if cable_attributes:
        raise RuntimeError("a dedicated supplied charging-cable attribute already exists")
    if item_index[TYPE2_ITEM]["item_type"] != "option":
        raise RuntimeError("Type 2 commercial item type drifted")
    if len(type2_memberships) != 1:
        raise RuntimeError("expected one Type 2 commercial membership")
    if type2_memberships[0]["attribute_code"] != "charging_connector_type":
        raise RuntimeError("Type 2 membership boundary drifted")
    if len(type2_mappings) != 3 or {
        row["configuration_code"] for row in type2_mappings
    } != {ESSENTIAL, EXPRESSION, EXTREME}:
        raise RuntimeError("Type 2 mapping scope drifted")
    if HOME_CABLE_ITEM in item_index:
        raise RuntimeError("home charging cable unexpectedly already exists")
    white = mapping_index[WHITE_MAPPING]
    white_before = (
        white["availability_status"] == "optional"
        and not white["amount"]
        and not white["price_date"]
        and white["source_code"] == "src_pl_spring_brochure_20260219"
    )
    white_after = (
        white["availability_status"] == "standard"
        and white["amount"] == "0"
        and white["currency_code"] == "PLN"
        and white["price_date"] == "2026-08-02"
        and white["source_code"]
        == "src_pl_spring_commercial_context_20260802"
    )
    if not (white_before or white_after):
        raise RuntimeError("Essential white mapping is outside the reviewed transition")
    if semantic["classification_summary"]["semantic_migration_required"] != 3:
        raise RuntimeError("semantic review boundary drifted")
    if khaki["mapping_update"]["after"]["amount"] != 2300:
        raise RuntimeError("preceding Khaki apply boundary drifted")

    return {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "scope": {
            "reviewed_concepts": [
                "Essential default exterior colour",
                "Type 2 supplied charging cable",
                "Home charging cable",
            ],
            "master_data_mutation_authorized": False,
            "source_reports": [
                "data/reporting/spring_exact_current_semantic_migration_review.json",
                "data/reporting/spring_essential_khaki_price_apply.json",
            ],
        },
        "repository_patterns": {
            "direct_scalar_default_colour": {
                "attribute_code": "exterior_color",
                "data_type": "string",
                "existing_value_rows": 7,
                "spring_value_rows": 0,
                "pattern_status": "available",
                "meaning": "A source-stated default exterior colour is stored as a direct configuration value, independently of commercial palette options.",
            },
            "boolean_equipment_availability": {
                "standard_rows": len(standard_availability),
                "pattern_status": "available_when_a_compatible_boolean_attribute_exists",
                "meaning": "Standard equipment is represented directly in configuration_attribute_availability for a compatible canonical equipment attribute.",
            },
            "commercial_standard_relationship": {
                "standard_mapping_rows": 4,
                "non_stock_grade_standard_rows": 0,
                "pattern_status": "not_a_grade_standard_precedent",
                "meaning": "Existing standard commercial mappings preserve selected equipment in exact stock vehicles; they do not establish a trim-level factory-standard representation.",
            },
            "charging_connector_scalar": {
                "attribute_code": "charging_connector_type",
                "existing_value_rows": len(connector_values),
                "pattern_status": "not_compatible_with_supplied_cable",
                "meaning": "The attribute describes the vehicle charging connector standard, not a cable supplied with the vehicle.",
            },
            "supplied_charging_cable_attribute": {
                "compatible_attribute_codes": cable_attributes,
                "pattern_status": "missing",
            },
        },
        "decisions": [
            {
                "concept": "Essential Biel Alpejska default colour",
                "classification": "existing_pattern_available",
                "approved_representation": {
                    "direct_value_attribute": "exterior_color",
                    "configuration_code": ESSENTIAL,
                    "value": "biel alpejska",
                    "observation_date": "2026-08-02",
                    "source_code": "src_pl_spring_commercial_context_20260802",
                    "commercial_mapping": {
                        "mapping_code": WHITE_MAPPING,
                        "target_availability_status": "standard",
                        "target_amount_pln": 0,
                        "reason": "Preserve the current commercial relationship while the direct scalar records the grade default.",
                    },
                },
                "new_attribute_required": False,
            },
            {
                "concept": "Type 2 supplied charging cable",
                "classification": "new_representation_decision_required",
                "current_problem": {
                    "commercial_item_code": TYPE2_ITEM,
                    "linked_attribute": "charging_connector_type",
                    "exact_current_state": {
                        ESSENTIAL: "standard",
                        EXPRESSION: "unresolved",
                        EXTREME: "standard",
                    },
                },
                "rejected_shortcut": "Changing only the commercial mapping to standard would retain an attribute membership that describes the vehicle connector rather than the supplied cable.",
                "minimum_model_requirement": "A dedicated independently available supplied-cable concept that can be standard for Essential and Extreme without asserting an Expression state.",
                "new_attribute_required": True,
            },
            {
                "concept": "Home charging cable",
                "classification": "new_representation_decision_required",
                "current_problem": {
                    "commercial_item_code": None,
                    "compatible_attribute_code": None,
                    "exact_current_state": {
                        ESSENTIAL: "optional_1500_pln",
                        EXPRESSION: "unresolved",
                        EXTREME: "optional_1500_pln",
                    },
                },
                "rejected_shortcut": "Reusing charging_connector_type would conflate vehicle connector standard with a separately supplied cable and would not allow Type 2 and home cables to coexist.",
                "minimum_model_requirement": "A second independently available supplied-cable concept because the home cable can coexist with the Type 2 cable and has its own commercial status and price.",
                "new_attribute_required": True,
            },
        ],
        "summary": {
            "existing_pattern_migrations": 1,
            "new_representation_decisions": 2,
            "master_rows_changed": 0,
            "attributes_added": 0,
            "commercial_items_added": 0,
        },
        "next_package": {
            "package_id": "spring_biel_alpejska_default_colour_migration_001",
            "goal": "Add the exact-current Essential Biel Alpejska direct exterior_color value and convert only its existing commercial mapping to standard at zero surcharge, leaving all charging-cable decisions untouched.",
        },
        "architecture_boundary": {
            "status": "decision_required_before_cable_mutation",
            "decision_question": "Choose the canonical representation for independently supplied charging cables before adding Type 2 or home-cable attributes and mappings.",
            "review_recommendation": "Use separate boolean equipment concepts for the Type 2 cable and home charging cable because both can coexist and have independent standard/optional states.",
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    patterns = report["repository_patterns"]
    return f"""# Spring Standard Equipment Representation Review

**Status:** complete  
**Date:** {report['generated_on']}  
**Master-data mutations:** 0

## Existing repository patterns

- Direct default colour: `exterior_color` already has **{patterns['direct_scalar_default_colour']['existing_value_rows']}** configuration values and is the established scalar representation for a source-stated grade colour.
- Standard equipment: `configuration_attribute_availability` contains **{patterns['boolean_equipment_availability']['standard_rows']}** standard rows where a compatible canonical equipment attribute exists.
- Commercial `standard` mappings: **{patterns['commercial_standard_relationship']['standard_mapping_rows']}** rows exist, but **{patterns['commercial_standard_relationship']['non_stock_grade_standard_rows']}** are non-stock grade-standard precedents; current rows preserve selected equipment in exact stock vehicles.
- `charging_connector_type` has **{patterns['charging_connector_scalar']['existing_value_rows']}** direct values and describes the vehicle connector standard, not a supplied cable.
- No compatible supplied-charging-cable attribute exists.

## Decisions

### Biel Alpejska — existing pattern available

For Spring Essential, add the exact-current direct value:

- `attribute_code`: `exterior_color`
- `value`: `biel alpejska`
- `observation_date`: `2026-08-02`
- `source_code`: `src_pl_spring_commercial_context_20260802`

Then convert only `spring_colour_biel_alpejska__spring_essential_electric70_automatic` to `standard` at **0 PLN**. The scalar records the grade default; the commercial relationship preserves the zero-surcharge palette state.

### Type 2 cable — new representation decision required

Changing the existing commercial mapping from optional to standard is insufficient because its only membership is `charging_connector_type`, whose meaning is the vehicle connector standard. Essential and Extreme are exact-current standard; Expression remains unresolved.

### Home charging cable — new representation decision required

No compatible item or attribute exists. Reusing `charging_connector_type` would conflate the vehicle connector with a separately supplied cable and could not represent Type 2 and home cables simultaneously.

## Architecture boundary

Before either cable is mutated, choose a canonical supplied-cable representation. The review recommends two independent boolean equipment concepts because the cables can coexist and have independent standard/optional states.

## Next package

`{report['next_package']['package_id']}` will migrate only the exact-current Essential Biel Alpejska default and will leave all charging-cable records untouched.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def apply(root: Path = ROOT) -> None:
    report = build(root)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    expected = build(root)
    if read_object(root / REPORT_JSON_PATH.relative_to(ROOT)) != expected:
        raise RuntimeError("Spring representation review JSON is stale")
    if (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != render_markdown(expected):
        raise RuntimeError("Spring representation review Markdown is stale")


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
