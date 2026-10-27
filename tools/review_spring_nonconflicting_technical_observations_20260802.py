#!/usr/bin/env python3
"""Review fully assimilated Spring technical evidence against current master."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
VALUES_PATH = ROOT / "data/master/configuration_attribute_values.csv"
ATTRIBUTES_PATH = ROOT / "data/master/attributes.csv"
ENUM_REGISTRY_PATH = ROOT / "data/master/attribute_enum_domains.csv"
SOURCES_PATH = ROOT / "data/master/sources.csv"
SOURCE_CONFIGURATIONS_PATH = ROOT / "data/master/source_configurations.csv"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_nonconflicting_technical_observations_review.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_nonconflicting_technical_observations_review.md"

BROCHURE_CODE = "src_pl_spring_brochure_20260219"
PRICE_LIST_CODE = "src_pl_spring_price_my25_stock_20260708"
CONFIGURATIONS = (
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
)

SAFE_COMMON_VALUES = {
    "electric_motor_type": "permanent_magnet_synchronous",
    "traction_battery_type": "lithium_iron_phosphate",
    "steering_type": "Elektryczne wspomaganie układu kierowniczego",
    "overall_height": "1489",
    "front_track": "1385",
    "overall_width": "1583",
    "overall_width_with_mirrors": "1767",
    "rear_track": "1365",
    "front_overhang": "683",
    "wheelbase": "2423",
    "rear_overhang": "595",
    "overall_length": "3701",
}

EXPECTED_SOURCE_HASHES = {
    BROCHURE_CODE: "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d",
    PRICE_LIST_CODE: "809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def source_record(rows: list[dict[str, str]], code: str) -> dict[str, str]:
    selected = [row for row in rows if row["code"] == code]
    if len(selected) != 1:
        raise RuntimeError(f"expected one source row for {code}")
    return selected[0]


def build(root: Path = ROOT) -> dict[str, Any]:
    attributes = read_rows(root / ATTRIBUTES_PATH.relative_to(ROOT))
    values = read_rows(root / VALUES_PATH.relative_to(ROOT))
    registry = read_rows(root / ENUM_REGISTRY_PATH.relative_to(ROOT))
    sources = read_rows(root / SOURCES_PATH.relative_to(ROOT))
    source_configurations = read_rows(
        root / SOURCE_CONFIGURATIONS_PATH.relative_to(ROOT)
    )

    attribute_index = {row["code"]: row for row in attributes}
    spring_values = [
        row for row in values if row["configuration_code"] in CONFIGURATIONS
    ]
    present_pairs = {
        (row["configuration_code"], row["attribute_code"])
        for row in spring_values
    }

    for code, expected in {
        "electric_motor_type": ("enum", ""),
        "traction_battery_type": ("enum", ""),
        "steering_type": ("string", ""),
        "overall_height": ("integer", "mm"),
        "front_track": ("integer", "mm"),
        "overall_width": ("integer", "mm"),
        "overall_width_with_mirrors": ("integer", "mm"),
        "rear_track": ("integer", "mm"),
        "front_overhang": ("integer", "mm"),
        "wheelbase": ("integer", "mm"),
        "rear_overhang": ("integer", "mm"),
        "overall_length": ("integer", "mm"),
    }.items():
        row = attribute_index.get(code)
        if row is None:
            raise RuntimeError(f"missing canonical attribute: {code}")
        if (row["data_type"], row["unit"]) != expected:
            raise RuntimeError(f"attribute contract drifted for {code}")
        if row["status"] != "active":
            raise RuntimeError(f"inactive canonical attribute: {code}")

    source_receipts: list[dict[str, Any]] = []
    for code in (BROCHURE_CODE, PRICE_LIST_CODE):
        source = source_record(sources, code)
        expected_hash = EXPECTED_SOURCE_HASHES[code]
        if source["sha256"] != expected_hash:
            raise RuntimeError(f"registered source hash drifted for {code}")
        path = root / source["file_path"]
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError(f"source bytes drifted for {code}")
        source_receipts.append(
            {
                "source_code": code,
                "repository_path": source["file_path"],
                "sha256": expected_hash,
                "source_date": source["document_date"],
            }
        )

    brochure_configurations = {
        row["configuration_code"]
        for row in source_configurations
        if row["source_code"] == BROCHURE_CODE
    }
    if not set(CONFIGURATIONS).issubset(brochure_configurations):
        raise RuntimeError("brochure-to-Spring configuration coverage drifted")

    safe_observations = [
        {
            "configuration_code": configuration,
            "attribute_code": attribute,
            "value": value,
            "observation_date": "2026-02-19",
            "source_code": BROCHURE_CODE,
            "source_page": 18 if attribute in {
                "electric_motor_type",
                "traction_battery_type",
                "steering_type",
            } else 21,
        }
        for configuration in CONFIGURATIONS
        for attribute, value in SAFE_COMMON_VALUES.items()
    ]
    already_present = [
        row
        for row in safe_observations
        if (row["configuration_code"], row["attribute_code"]) in present_pairs
    ]
    if already_present:
        raise RuntimeError(
            "approved Spring non-conflicting observations unexpectedly already exist"
        )

    registry_index = {row["attribute_code"]: row for row in registry}
    enum_representation = {
        "electric_motor_type": {
            "registry_status": (
                "present" if "electric_motor_type" in registry_index else "missing"
            ),
            "required_domain_file": "electric_motor_types.csv",
            "required_value": "permanent_magnet_synchronous",
        },
        "traction_battery_type": {
            "registry_status": (
                "present" if "traction_battery_type" in registry_index else "missing"
            ),
            "required_domain_file": "battery_chemistries.csv",
            "required_value": "lithium_iron_phosphate",
        },
    }

    return {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "scope": {
            "source_codes": [BROCHURE_CODE, PRICE_LIST_CODE],
            "configuration_codes": list(CONFIGURATIONS),
            "reviewed_areas": [
                "battery",
                "charging_times",
                "performance",
                "dimensions",
                "luggage",
            ],
            "master_data_mutation_authorized": False,
        },
        "source_receipts": source_receipts,
        "master_snapshot": {
            "spring_scalar_observations": len(spring_values),
            "approved_pairs_already_present": len(already_present),
            "approved_attribute_count": len(SAFE_COMMON_VALUES),
            "approved_observation_count": len(safe_observations),
        },
        "approved_migration": {
            "classification": "context_safe_nonconflicting",
            "source_code": BROCHURE_CODE,
            "source_pages": [18, 21],
            "observation_date": "2026-02-19",
            "configuration_count": len(CONFIGURATIONS),
            "attribute_values": SAFE_COMMON_VALUES,
            "observation_count": len(safe_observations),
            "observations": safe_observations,
            "enum_representation": enum_representation,
            "boundaries": [
                "Only facts printed as common to Electric 70 and Electric 100 or shown as model-wide body dimensions are approved.",
                "No value is transferred from the MY2025 stock-only price list into the current Spring configuration set.",
                "The 146 mm ground-clearance value is excluded because the source limits it to 15-inch wheels.",
                "No charging-time, range, maximum-speed or grade-specific value is included.",
            ],
        },
        "classifications": [
            {
                "fact": "traction battery chemistry",
                "source_value": "Litowo–żelazowo–fosforanowy",
                "classification": "approved_migration",
                "reason": "The brochure states one common chemistry for both represented powertrains, exact grade footnotes cover all three configurations, and no later source conflicts with it.",
            },
            {
                "fact": "electric motor technology",
                "source_value": "Silnik synchroniczny ze stałymi magnesami",
                "classification": "approved_migration",
                "reason": "The brochure states one common motor technology for Electric 70 and Electric 100 and the canonical enum attribute already exists.",
            },
            {
                "fact": "steering assistance type",
                "source_value": "Elektryczne wspomaganie układu kierowniczego",
                "classification": "approved_migration",
                "reason": "The brochure states one common steering system and the canonical string attribute already has the same source-faithful representation pattern in other models.",
            },
            {
                "fact": "common body dimensions",
                "source_value": SAFE_COMMON_VALUES,
                "classification": "approved_migration",
                "reason": "Nine arrow-bounded dimensions are unambiguous in the fully reviewed page-21 visual and are not wheel-, grade- or powertrain-qualified.",
            },
            {
                "fact": "traction battery mass",
                "source_value": "204 kg",
                "classification": "deferred_model_year_bound",
                "reason": "The value exists only in the July price list explicitly limited to MY2025 dealer stock; no brochure or later exact-current source proves model-year independence.",
            },
            {
                "fact": "traction battery nominal voltage",
                "source_value": "354 V",
                "classification": "deferred_model_year_bound",
                "reason": "The value exists only in the MY2025 stock technical table and must not be projected onto the current configuration set.",
            },
            {
                "fact": "traction battery capacity",
                "source_value": "24.3 kWh",
                "classification": "deferred_measurement_basis",
                "reason": "The sources do not qualify the value as gross or net while the canonical traction-battery capacity attributes require that distinction.",
            },
            {
                "fact": "charging times",
                "classification": "deferred_contextual",
                "reason": "SOC endpoints, charger power, option/package state and dated source context must remain explicit; automatic migration is prohibited for this package.",
            },
            {
                "fact": "performance and range",
                "classification": "represented_or_deferred",
                "reason": "Power, 0-50, 0-100, maximum speed and mixed range are already represented; torque retains a source-unit conflict and no later values are imported.",
            },
            {
                "fact": "luggage volumes",
                "classification": "already_represented",
                "reason": "The 308 L minimum and 1004 L folded values already exist for all three configurations with ISO 3832 context.",
            },
            {
                "fact": "wheel-qualified ground clearance",
                "source_value": "146 mm",
                "classification": "deferred_configuration_dependent",
                "reason": "The page-21 footnote limits the value to 15-inch wheels, so it is excluded from the common migration.",
            },
        ],
        "summary": {
            "approved_attributes": len(SAFE_COMMON_VALUES),
            "approved_observations": len(safe_observations),
            "approved_enum_attributes": 2,
            "deferred_facts": 5,
            "already_represented_fact_groups": 2,
            "master_rows_changed": 0,
        },
        "next_package": {
            "package_id": "spring_nonconflicting_common_technical_observations_migration_001",
            "goal": "Materialize the 36 approved brochure observations, add only the two required enum-domain mappings and controlled values, and preserve every deferred MY2025, charging, range and wheel-qualified boundary.",
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    approved = report["approved_migration"]
    summary = report["summary"]
    return f"""# Spring Non-conflicting Technical Observations Review

**Status:** complete  
**Date:** {report['generated_on']}  
**Master-data mutations:** 0

## Result

The fully assimilated Spring brochure and MY2025 stock price list were compared with current master data across battery, charging, performance, dimensions and luggage evidence.

Exactly **{summary['approved_attributes']}** canonical attributes and **{summary['approved_observations']}** dated observations are approved for a bounded follow-up migration:

- LFP traction-battery chemistry;
- permanent-magnet synchronous traction-motor technology;
- electric power steering;
- nine common body dimensions from the rendered page-21 diagram.

All approved values come from `src_pl_spring_brochure_20260219`, apply identically to Electric 70 and Electric 100, and are not qualified by grade, wheel size or model year. The migration needs controlled enum representation for `traction_battery_type` and `electric_motor_type`, but no new canonical attribute.

## Deliberate non-migrations

- **204 kg battery mass** and **354 V nominal voltage** remain deferred because their only source is the MY2025 stock price list; they are not projected into current Spring configurations.
- **24.3 kWh** remains deferred because the source does not identify gross versus net capacity.
- Charging times, range and maximum speed are not migrated.
- The **146 mm** ground-clearance value remains deferred because it is explicitly limited to 15-inch wheels.
- Existing 308 L and 1004 L ISO 3832 luggage observations remain unchanged.

## Next package

`{report['next_package']['package_id']}` will materialize only the **{approved['observation_count']}** approved brochure observations and the minimum controlled enum-domain support required by the existing attributes.
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
    actual = read_object(root / REPORT_JSON_PATH.relative_to(ROOT))
    if actual != expected:
        raise RuntimeError("Spring technical review JSON is stale")
    markdown = (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8")
    if markdown != render_markdown(expected):
        raise RuntimeError("Spring technical review Markdown is stale")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
