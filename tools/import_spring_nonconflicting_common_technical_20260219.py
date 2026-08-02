#!/usr/bin/env python3
"""Materialize the reviewed common Spring technical observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "spring_nonconflicting_common_technical_20260219.csv"
REVIEW = ROOT / "data" / "reporting" / "spring_nonconflicting_technical_observations_review.json"
REPORT_JSON = ROOT / "data" / "reporting" / "spring_nonconflicting_common_technical_migration.json"
REPORT_MD = ROOT / "data" / "reporting" / "spring_nonconflicting_common_technical_migration.md"
COMPLETENESS_FILES = {
    "spring_electric70_automatic": ROOT / "data" / "reporting" / "spring_electric70_automatic_completeness.json",
    "spring_electric100_automatic": ROOT / "data" / "reporting" / "spring_electric100_automatic_completeness.json",
}
SOURCE_CODE = "src_pl_spring_brochure_20260219"
SOURCE_FILE = ROOT / "PDF" / "Broszury" / "DACIA SPRING broszura 20260219.pdf"
SOURCE_SHA256 = "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d"
OBSERVATION_DATE = "2026-02-19"
CONFIGURATIONS = (
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
)
SPEC_FIELDS = (
    "configuration_code",
    "attribute_code",
    "value",
    "source_page",
    "source_label",
    "normalization_notes",
)
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "gear_number", "value", "observation_date", "source_code", "notes",
)
DOMAIN_FIELDS = ("code", "name", "description", "status")
REGISTRY_FIELDS = ("attribute_code", "domain_file", "status")
EXPECTED_FIRST_ID = 3569
EXPECTED_LAST_ID = 3604
ATTRIBUTE_CONTRACTS = {
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
}
ENUM_RULES = {
    "electric_motor_type": ("electric_motor_types.csv", "permanent_magnet_synchronous"),
    "traction_battery_type": ("battery_chemistries.csv", "lithium_iron_phosphate"),
}
COMMON_TECHNICAL_SLOTS = (
    "electric_motor_type",
    "traction_battery_type",
    "steering_type",
    "overall_height",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
)
EXPECTED_SCOPE_SLOT_COUNTS = {
    "spring_electric70_automatic": 31,
    "spring_electric100_automatic": 12,
}
EXPECTED_SCOPE_CONFIGURATIONS = {
    "spring_electric70_automatic": {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
    },
    "spring_electric100_automatic": {"spring_extreme_electric100_automatic"},
}
EXPECTED_VALUES = {
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
ENUM_ROWS = {
    "battery_chemistries.csv": {
        "code": "lithium_iron_phosphate",
        "name": "Lithium iron phosphate (LFP)",
        "description": "Lithium iron phosphate traction-battery chemistry",
        "status": "active",
    },
    "electric_motor_types.csv": {
        "code": "permanent_magnet_synchronous",
        "name": "Permanent-magnet synchronous",
        "description": "Permanent-magnet synchronous electric traction motor",
        "status": "active",
    },
}


class ContractError(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def write_rows_atomic(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec() -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    ensure(len(rows) == 36, f"expected 36 specification rows, found {len(rows)}")
    identities = {(row["configuration_code"], row["attribute_code"]) for row in rows}
    ensure(len(identities) == 36, "duplicate specification identity")
    ensure(Counter(row["configuration_code"] for row in rows) == Counter({code: 12 for code in CONFIGURATIONS}), "per-configuration count differs")
    ensure(Counter(row["attribute_code"] for row in rows) == Counter({code: 3 for code in EXPECTED_VALUES}), "per-attribute count differs")
    for row in rows:
        ensure(row["configuration_code"] in CONFIGURATIONS, f"unexpected configuration: {row['configuration_code']}")
        attribute = row["attribute_code"]
        ensure(attribute in EXPECTED_VALUES, f"unexpected attribute: {attribute}")
        ensure(row["value"] == EXPECTED_VALUES[attribute], f"unexpected value: {attribute}")
        ensure(row["source_page"] == ("18" if attribute in {"electric_motor_type", "traction_battery_type", "steering_type"} else "21"), f"unexpected source page: {attribute}")
        ensure(row["source_label"].strip() and row["normalization_notes"].strip(), f"missing evidence text: {attribute}")
    return rows


def generated_rows(spec_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for index, row in enumerate(spec_rows, start=EXPECTED_FIRST_ID):
        result.append({
            "id": str(index),
            "code": f"{row['configuration_code']}_{row['attribute_code']}_20260219",
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "fuel_type_code": "",
            "gear_number": "",
            "value": row["value"],
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": f"Source page {row['source_page']}: {row['source_label']}. {row['normalization_notes']}",
        })
    return result


def verify_contracts(spec_rows: list[dict[str, str]]) -> None:
    ensure(SOURCE_FILE.is_file() and sha256(SOURCE_FILE) == SOURCE_SHA256, "Spring brochure SHA-256 differs")
    sources = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    source = sources.get(SOURCE_CODE)
    ensure(source is not None and source.get("sha256") == SOURCE_SHA256 and source.get("status") == "active", "source registry differs")
    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    for code in CONFIGURATIONS:
        ensure(configurations.get(code, {}).get("status") == "active", f"missing active configuration: {code}")
    links = {(row["source_code"], row["configuration_code"]) for row in read_rows(MASTER / "source_configurations.csv")}
    for code in CONFIGURATIONS:
        ensure((SOURCE_CODE, code) in links, f"source/configuration link missing: {code}")
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code, (data_type, unit) in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None and row.get("status") == "active", f"missing active attribute: {code}")
        ensure((row.get("data_type"), row.get("unit")) == (data_type, unit), f"attribute contract differs: {code}")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    ensure(review.get("status") == "complete", "review is not complete")
    approved = review.get("approved_migration", {}).get("observations", [])
    reviewed = {(row["configuration_code"], row["attribute_code"], row["value"], str(row["source_page"])) for row in approved}
    specified = {(row["configuration_code"], row["attribute_code"], row["value"], row["source_page"]) for row in spec_rows}
    ensure(reviewed == specified, "specification differs from approved review observations")


def apply_enum_support() -> None:
    registry_path = MASTER / "attribute_enum_domains.csv"
    require_header(registry_path, REGISTRY_FIELDS)
    registry = read_rows(registry_path)
    by_attribute = {row["attribute_code"]: row for row in registry}
    for attribute, (domain_file, _) in ENUM_RULES.items():
        expected = {"attribute_code": attribute, "domain_file": domain_file, "status": "active"}
        if attribute in by_attribute:
            ensure(by_attribute[attribute] == expected, f"enum registry conflict: {attribute}")
        else:
            registry.append(expected)
    registry.sort(key=lambda row: row["attribute_code"])
    write_rows_atomic(registry_path, REGISTRY_FIELDS, registry)

    for domain_file, expected in ENUM_ROWS.items():
        path = MASTER / "enums" / domain_file
        if path.exists():
            require_header(path, DOMAIN_FIELDS)
            rows = read_rows(path)
        else:
            rows = []
        by_code = {row["code"]: row for row in rows}
        if expected["code"] in by_code:
            ensure(by_code[expected["code"]] == expected, f"enum value conflict: {expected['code']}")
        else:
            rows.append(expected)
        rows.sort(key=lambda row: row["code"])
        write_rows_atomic(path, DOMAIN_FIELDS, rows)


def apply_values(spec_rows: list[dict[str, str]]) -> None:
    path = MASTER / "configuration_attribute_values.csv"
    require_header(path, VALUE_FIELDS)
    current = read_rows(path)
    generated = generated_rows(spec_rows)
    generated_codes = {row["code"] for row in generated}
    existing = [row for row in current if row["code"] in generated_codes]
    if existing:
        ensure(existing == generated, "partial or conflicting migration rows already exist")
        return
    ensure(max(int(row["id"]) for row in current) == EXPECTED_FIRST_ID - 1, "configuration value ID suffix moved")
    write_rows_atomic(path, VALUE_FIELDS, [*current, *generated])


def apply_completeness_specs() -> None:
    for scope, path in COMPLETENESS_FILES.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        configurations = {
            row["configuration_code"] for row in payload.get("configurations", [])
        }
        ensure(
            configurations == EXPECTED_SCOPE_CONFIGURATIONS[scope],
            f"completeness configuration scope differs: {scope}",
        )
        slots = payload.get("technical_slots")
        ensure(isinstance(slots, list), f"technical slots missing: {scope}")
        identities = [
            (row.get("attribute_code", ""), row.get("fuel_type_code", ""))
            for row in slots
        ]
        ensure(len(identities) == len(set(identities)), f"duplicate technical slot: {scope}")
        existing = set(identities)
        for attribute in COMMON_TECHNICAL_SLOTS:
            identity = (attribute, "")
            if identity not in existing:
                slots.append({"attribute_code": attribute, "fuel_type_code": ""})
                existing.add(identity)
        ensure(
            len(slots) == EXPECTED_SCOPE_SLOT_COUNTS[scope],
            f"unexpected technical-slot count after migration: {scope}",
        )
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def verify_completeness_specs() -> None:
    required = {(attribute, "") for attribute in COMMON_TECHNICAL_SLOTS}
    for scope, path in COMPLETENESS_FILES.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        configurations = {
            row["configuration_code"] for row in payload.get("configurations", [])
        }
        ensure(
            configurations == EXPECTED_SCOPE_CONFIGURATIONS[scope],
            f"completeness configuration scope differs: {scope}",
        )
        identities = [
            (row.get("attribute_code", ""), row.get("fuel_type_code", ""))
            for row in payload.get("technical_slots", [])
        ]
        ensure(len(identities) == len(set(identities)), f"duplicate technical slot: {scope}")
        ensure(required.issubset(set(identities)), f"common technical slots missing: {scope}")
        ensure(
            len(identities) == EXPECTED_SCOPE_SLOT_COUNTS[scope],
            f"unexpected technical-slot count: {scope}",
        )


def build_report() -> dict[str, object]:
    return {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "source_code": SOURCE_CODE,
        "observation_date": OBSERVATION_DATE,
        "configuration_count": 3,
        "attribute_count": 12,
        "observation_count": 36,
        "value_id_range": [EXPECTED_FIRST_ID, EXPECTED_LAST_ID],
        "enum_domains_added": {
            "electric_motor_type": "electric_motor_types.csv",
            "traction_battery_type": "battery_chemistries.csv",
        },
        "enum_values_added": {
            "electric_motor_type": "permanent_magnet_synchronous",
            "traction_battery_type": "lithium_iron_phosphate",
        },
        "completeness_specs_updated": {
            scope: EXPECTED_SCOPE_SLOT_COUNTS[scope]
            for scope in sorted(EXPECTED_SCOPE_SLOT_COUNTS)
        },
        "preserved_deferrals": [
            "battery_mass_204_kg_my2025_stock_only",
            "battery_voltage_354_v_my2025_stock_only",
            "battery_capacity_24_3_kwh_measurement_basis_unqualified",
            "charging_times_context_dependent",
            "ground_clearance_15_inch_wheel_only",
            "range_and_maximum_speed_not_reimported",
        ],
        "next_package": "spring_legacy_pdf_assimilation_closure_001",
    }


def write_reports() -> None:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Spring non-conflicting common technical migration\n\n"
        "Status: **complete**\n\n"
        "The package materializes 36 exact brochure observations: 12 common attributes for each of the three active Spring configurations. It adds controlled domains only for permanent-magnet synchronous motor technology and LFP traction-battery chemistry.\n\n"
        "## Imported\n\n"
        "- permanent-magnet synchronous electric motor;\n"
        "- LFP traction-battery chemistry;\n"
        "- electric power steering;\n"
        "- overall height, front and rear track, body width, width with mirrors, front and rear overhang, wheelbase and overall length;\n"
        "- Spring Electric 70 and Electric 100 completeness specifications extended by the same twelve common technical slots.\n\n"
        "## Preserved boundaries\n\n"
        "Battery mass 204 kg and voltage 354 V remain MY2025-stock-only evidence. The unqualified 24.3 kWh capacity, charging times, range, maximum speed and 15-inch-wheel ground clearance are not promoted by this package.\n\n"
        "## Verification\n\n"
        "The deterministic importer validates the exact source SHA-256, the completed review contract, the 36-row declarative specification, controlled enum domains and the contiguous configuration-value suffix 3569-3604.\n",
        encoding="utf-8",
    )


def verify_materialized() -> None:
    spec_rows = load_spec()
    verify_contracts(spec_rows)
    registry = {row["attribute_code"]: row for row in read_rows(MASTER / "attribute_enum_domains.csv")}
    for attribute, (domain_file, enum_code) in ENUM_RULES.items():
        ensure(registry.get(attribute) == {"attribute_code": attribute, "domain_file": domain_file, "status": "active"}, f"enum registry missing: {attribute}")
        values = {row["code"]: row for row in read_rows(MASTER / "enums" / domain_file)}
        ensure(values.get(enum_code) == ENUM_ROWS[domain_file], f"enum value missing: {enum_code}")
    verify_completeness_specs()
    expected = generated_rows(spec_rows)
    expected_codes = {row["code"] for row in expected}
    actual = [row for row in read_rows(MASTER / "configuration_attribute_values.csv") if row["code"] in expected_codes]
    ensure(actual == expected, "stored migration rows differ")
    ensure([int(row["id"]) for row in actual] == list(range(EXPECTED_FIRST_ID, EXPECTED_LAST_ID + 1)), "migration IDs differ")
    ensure(json.loads(REPORT_JSON.read_text(encoding="utf-8")) == build_report(), "JSON report differs")
    ensure("204 kg" in REPORT_MD.read_text(encoding="utf-8"), "Markdown deferral boundary missing")
    print("Spring common technical migration: PASS (36 values; IDs 3569-3604)")


def apply() -> None:
    spec_rows = load_spec()
    verify_contracts(spec_rows)
    apply_enum_support()
    apply_values(spec_rows)
    apply_completeness_specs()
    write_reports()
    verify_materialized()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    else:
        verify_materialized()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
