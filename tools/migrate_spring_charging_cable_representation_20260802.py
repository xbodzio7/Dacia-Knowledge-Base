#!/usr/bin/env python3
"""Apply or verify the bounded Spring charging-cable representation migration."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/imports/configuration_attribute_availability/spring_charging_cable_representation_20260802.json"
ATTRIBUTES = ROOT / "data/master/attributes.csv"
AVAILABILITY = ROOT / "data/master/configuration_attribute_availability.csv"
CONFIGURATIONS = ROOT / "data/master/configurations.csv"
SOURCES = ROOT / "data/master/sources.csv"
STATUSES = ROOT / "data/master/enums/equipment_availability_statuses.csv"
STATE = ROOT / "project/state.json"
STATE_SUMMARY = ROOT / "project/STATE_SUMMARY.md"
SNAPSHOT = ROOT / "project/sources/dacia-pl-spring-saved-configurations-20260802.json"
DECISION = ROOT / "project/decisions/spring-charging-cable-representation-20260802.md"
REPORT_JSON = ROOT / "data/reporting/spring_charging_cable_representation_migration.json"
REPORT_MD = ROOT / "data/reporting/spring_charging_cable_representation_migration.md"
PACKAGE_DOC = ROOT / "project/packages/spring-charging-cable-representation-migration-20260802.md"

ATTRIBUTE_FIELDS = (
    "id",
    "code",
    "category",
    "name",
    "data_type",
    "unit",
    "description",
    "status",
)
AVAILABILITY_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "availability_status",
    "observation_date",
    "source_code",
    "notes",
)
PACKAGE_ID = "spring_charging_cable_representation_migration_001"
NEXT_PACKAGE_ID = "spring_charging_cable_commercial_semantics_review_001"


class MigrationError(RuntimeError):
    """Raised when the migration contract is not satisfied."""


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MigrationError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise MigrationError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def append_csv_rows(
    path: Path,
    fields: tuple[str, ...],
    rows: list[dict[str, str]],
) -> None:
    if not rows:
        return
    existing_fields, _ = read_csv(path)
    if existing_fields != list(fields):
        raise MigrationError(
            f"unexpected header for {path}: {existing_fields!r}"
        )
    needs_newline = path.stat().st_size > 0 and path.read_bytes()[-1:] not in {
        b"\n",
        b"\r",
    }
    with path.open("a", encoding="utf-8", newline="") as handle:
        if needs_newline:
            handle.write("\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fields),
            lineterminator="\n",
        )
        writer.writerows(rows)


def next_numeric_id(rows: list[dict[str, str]]) -> int:
    values: list[int] = []
    for row in rows:
        raw = (row.get("id") or "").strip()
        if not raw.isdigit():
            raise MigrationError(f"non-numeric id encountered: {raw!r}")
        values.append(int(raw))
    return max(values, default=0) + 1


def row_without_id(row: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in row.items() if key != "id"}


def require_exact_existing(
    actual: dict[str, str],
    expected_without_id: dict[str, str],
    *,
    label: str,
) -> None:
    if row_without_id(actual) != expected_without_id:
        raise MigrationError(
            f"existing {label} differs from migration specification: "
            f"{row_without_id(actual)!r} != {expected_without_id!r}"
        )


def master_row_count(root: Path) -> int:
    count = 0
    for path in sorted((root / "data/master").rglob("*.csv")):
        _, rows = read_csv(path)
        count += len(rows)
    return count


def source_codes(root: Path) -> set[str]:
    _, rows = read_csv(root / SOURCES.relative_to(ROOT))
    return {row["code"] for row in rows}


def configuration_codes(root: Path) -> set[str]:
    _, rows = read_csv(root / CONFIGURATIONS.relative_to(ROOT))
    return {row["code"] for row in rows}


def availability_statuses(root: Path) -> set[str]:
    _, rows = read_csv(root / STATUSES.relative_to(ROOT))
    return {row["code"] for row in rows}


def validate_spec_dependencies(root: Path, spec: dict[str, Any]) -> None:
    if spec.get("version") != 1 or spec.get("package_id") != PACKAGE_ID:
        raise MigrationError("unexpected migration specification identity")
    if spec.get("decision_code") != "spring_independent_charging_cable_concepts":
        raise MigrationError("unexpected architecture decision code")

    attribute_codes = [row["code"] for row in spec["attributes"]]
    if attribute_codes != [
        "type2_charging_cable_supplied",
        "domestic_socket_charging_cable",
    ]:
        raise MigrationError("charging-cable attribute set drifted")

    configurations = configuration_codes(root)
    sources = source_codes(root)
    statuses = availability_statuses(root)
    for row in spec["availability"]:
        if row["configuration_code"] not in configurations:
            raise MigrationError(
                f"unknown configuration: {row['configuration_code']}"
            )
        if row["source_code"] not in sources:
            raise MigrationError(f"unknown source: {row['source_code']}")
        if row["availability_status"] not in statuses:
            raise MigrationError(
                f"unknown availability status: {row['availability_status']}"
            )
        if row["attribute_code"] not in attribute_codes:
            raise MigrationError(
                f"unknown migration attribute: {row['attribute_code']}"
            )

    non_imports = spec.get("explicit_non_imports", [])
    if non_imports != [
        {
            "configuration_code": "spring_expression_electric70_automatic",
            "attribute_code": "domestic_socket_charging_cable",
            "status": "unresolved",
            "reason": "The selected-configuration PDF omits unselected options and therefore proves neither optional availability nor unavailability of the domestic-socket cable.",
        }
    ]:
        raise MigrationError("Expression domestic-cable non-import boundary drifted")


def expected_attribute_rows(spec: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "code": str(row["code"]),
            "category": str(row["category"]),
            "name": str(row["name"]),
            "data_type": str(row["data_type"]),
            "unit": str(row["unit"]),
            "description": str(row["description"]),
            "status": str(row["status"]),
        }
        for row in spec["attributes"]
    ]


def expected_availability_rows(spec: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "code": str(row["code"]),
            "configuration_code": str(row["configuration_code"]),
            "attribute_code": str(row["attribute_code"]),
            "availability_status": str(row["availability_status"]),
            "observation_date": str(row["observation_date"]),
            "source_code": str(row["source_code"]),
            "notes": str(row["notes"]),
        }
        for row in spec["availability"]
    ]


def apply_attributes(
    path: Path,
    expected: list[dict[str, str]],
) -> tuple[int, list[dict[str, str]]]:
    fields, rows = read_csv(path)
    if fields != list(ATTRIBUTE_FIELDS):
        raise MigrationError(f"unexpected attributes header: {fields!r}")
    by_code = {row["code"]: row for row in rows}
    new_rows: list[dict[str, str]] = []
    next_id = next_numeric_id(rows)
    for expected_row in expected:
        current = by_code.get(expected_row["code"])
        if current is not None:
            require_exact_existing(
                current,
                expected_row,
                label=f"attribute {expected_row['code']}",
            )
            continue
        row = {"id": str(next_id), **expected_row}
        next_id += 1
        new_rows.append(row)
        by_code[row["code"]] = row
    append_csv_rows(path, ATTRIBUTE_FIELDS, new_rows)
    return len(new_rows), new_rows


def apply_availability(
    path: Path,
    expected: list[dict[str, str]],
) -> tuple[int, list[dict[str, str]]]:
    fields, rows = read_csv(path)
    if fields != list(AVAILABILITY_FIELDS):
        raise MigrationError(f"unexpected availability header: {fields!r}")
    by_code = {row["code"]: row for row in rows}
    by_semantic = {
        (
            row["configuration_code"],
            row["attribute_code"],
            row["observation_date"],
            row["source_code"],
        ): row
        for row in rows
    }
    new_rows: list[dict[str, str]] = []
    next_id = next_numeric_id(rows)
    for expected_row in expected:
        current = by_code.get(expected_row["code"])
        if current is not None:
            require_exact_existing(
                current,
                expected_row,
                label=f"availability {expected_row['code']}",
            )
            continue
        semantic = (
            expected_row["configuration_code"],
            expected_row["attribute_code"],
            expected_row["observation_date"],
            expected_row["source_code"],
        )
        collision = by_semantic.get(semantic)
        if collision is not None:
            raise MigrationError(
                "availability semantic collision: "
                f"{collision['code']} vs {expected_row['code']}"
            )
        row = {"id": str(next_id), **expected_row}
        next_id += 1
        new_rows.append(row)
        by_code[row["code"]] = row
        by_semantic[semantic] = row
    append_csv_rows(path, AVAILABILITY_FIELDS, new_rows)
    return len(new_rows), new_rows


def write_report(
    root: Path,
    *,
    before_attributes: int,
    before_availability: int,
    before_master_rows: int,
    attribute_rows_added: list[dict[str, str]],
    availability_rows_added: list[dict[str, str]],
) -> dict[str, Any]:
    _, attributes = read_csv(root / ATTRIBUTES.relative_to(ROOT))
    _, availability = read_csv(root / AVAILABILITY.relative_to(ROOT))
    after_master_rows = master_row_count(root)
    payload: dict[str, Any] = {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "package_id": PACKAGE_ID,
        "decision_code": "spring_independent_charging_cable_concepts",
        "migration": {
            "attributes_added": len(attribute_rows_added),
            "availability_rows_added": len(availability_rows_added),
            "attribute_codes": [
                "type2_charging_cable_supplied",
                "domestic_socket_charging_cable",
            ],
            "availability_codes": [row["code"] for row in availability_rows_added],
            "expression_domestic_socket_state": "unresolved_no_row_created",
            "historical_commercial_records_changed": 0,
        },
        "counts": {
            "before": {
                "attributes": before_attributes,
                "availability_records": before_availability,
                "master_rows": before_master_rows,
            },
            "after": {
                "attributes": len(attributes),
                "availability_records": len(availability),
                "master_rows": after_master_rows,
            },
            "delta": {
                "attributes": len(attributes) - before_attributes,
                "availability_records": len(availability) - before_availability,
                "master_rows": after_master_rows - before_master_rows,
            },
        },
        "evidence_boundary": {
            "type2_standard_configurations": [
                "spring_essential_electric70_automatic",
                "spring_expression_electric70_automatic",
                "spring_extreme_electric100_automatic",
            ],
            "domestic_socket_optional_configurations": [
                "spring_essential_electric70_automatic",
                "spring_extreme_electric100_automatic",
            ],
            "domestic_socket_unresolved_configurations": [
                "spring_expression_electric70_automatic"
            ],
        },
        "next_package": {
            "package_id": NEXT_PACKAGE_ID,
            "goal": "Review the historical Spring charging-cable commercial item against its source wording and introduce a superseding current commercial representation only if the evidence requires it, without rewriting history.",
        },
    }
    write_json(root / REPORT_JSON.relative_to(ROOT), payload)

    after = payload["counts"]["after"]
    delta = payload["counts"]["delta"]
    markdown = f"""# Spring Charging-Cable Representation Migration

**Status:** complete  
**Date:** 2026-08-02

## Result

The accepted independent-cable architecture is now represented by two boolean canonical attributes:

- `type2_charging_cable_supplied`;
- `domestic_socket_charging_cable`.

Five exact-current configuration-level availability observations were added: Type 2 is standard in Essential 70, Expression 70 and Extreme 100; the domestic-socket cable is optional in Essential 70 and Extreme 100.

No domestic-socket row was created for Expression 70 because its saved-configuration PDF does not enumerate unselected options.

## Data impact

- attributes added: **{delta['attributes']}**;
- availability records added: **{delta['availability_records']}**;
- net master-row increase: **{delta['master_rows']}**;
- attributes after migration: **{after['attributes']}**;
- availability records after migration: **{after['availability_records']}**;
- historical commercial records changed: **0**.

## Next package

`{NEXT_PACKAGE_ID}` will review the historical Spring cable commercial item without rewriting its source-bounded history.
"""
    report_md = root / REPORT_MD.relative_to(ROOT)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(markdown, encoding="utf-8")
    return payload


def update_state(root: Path, report: dict[str, Any]) -> None:
    state_path = root / STATE.relative_to(ROOT)
    state = read_json(state_path)
    after = report["counts"]["after"]
    state["updated_on"] = "2026-08-02"
    state["phase"] = "Spring Charging Cable Representation Migration"
    state["reference_delivery"] = {
        "name": "Spring Expression Saved State Artifact Intake",
        "pull_request": 459,
        "head_sha": "4d4f6c4585976419f7c8a0de1aab7a8720f1aabd",
        "quality_run": 30748935727,
    }
    state["baseline"]["rows"] = after["master_rows"]
    state["baseline"]["availability_records"] = after["availability_records"]
    state["baseline"]["attributes"] = after["attributes"]
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "bounded_schema_and_data_migration",
        "name": "Spring Charging Cable Representation Migration",
        "status": "complete",
        "goal": "Add two independent boolean charging-cable attributes and import only exact-current configuration-level availability supported by the accepted evidence matrix, while preserving historical commercial records.",
        "manifest_paths": [
            "CHANGELOG.md",
            "README.md",
            "data/imports/configuration_attribute_availability/spring_charging_cable_representation_20260802.json",
            "data/master/attributes.csv",
            "data/master/configuration_attribute_availability.csv",
            "data/reporting/spring_charging_cable_representation_migration.json",
            "data/reporting/spring_charging_cable_representation_migration.md",
            "project/SESSION_STATE.md",
            "project/STATE_SUMMARY.md",
            "project/packages/spring-charging-cable-representation-migration-20260802.md",
            "project/state.json",
            "tests/test_spring_charging_cable_representation_migration_20260802.py",
            "tools/migrate_spring_charging_cable_representation_20260802.py",
            "tools/review_spring_saved_state_artifact_intake_20260802.py"
        ],
    }
    state["next_package"] = {
        "package_id": NEXT_PACKAGE_ID,
        "kind": "bounded_commercial_semantics_review",
        "name": "Spring Charging Cable Commercial Semantics Review",
        "status": "planned",
        "goal": "Review the historical Spring charging-cable commercial item against its source wording and introduce a superseding current commercial representation only if the evidence requires it, without rewriting history.",
        "manifest_paths": [
            "data/master/commercial_items.csv",
            "data/master/commercial_item_attributes.csv",
            "data/master/commercial_item_configurations.csv",
            "data/reporting/",
            "project/STATE_SUMMARY.md",
            "project/state.json"
        ],
    }
    write_json(state_path, state)


def apply(root: Path = ROOT) -> None:
    spec = read_json(root / SPEC.relative_to(ROOT))
    validate_spec_dependencies(root, spec)

    _, attributes_before_rows = read_csv(root / ATTRIBUTES.relative_to(ROOT))
    _, availability_before_rows = read_csv(root / AVAILABILITY.relative_to(ROOT))
    before_master_rows = master_row_count(root)

    _, added_attributes = apply_attributes(
        root / ATTRIBUTES.relative_to(ROOT),
        expected_attribute_rows(spec),
    )
    _, added_availability = apply_availability(
        root / AVAILABILITY.relative_to(ROOT),
        expected_availability_rows(spec),
    )
    report = write_report(
        root,
        before_attributes=len(attributes_before_rows),
        before_availability=len(availability_before_rows),
        before_master_rows=before_master_rows,
        attribute_rows_added=added_attributes,
        availability_rows_added=added_availability,
    )
    update_state(root, report)
    verify(root)


def verify(root: Path = ROOT) -> None:
    spec = read_json(root / SPEC.relative_to(ROOT))
    validate_spec_dependencies(root, spec)

    attribute_fields, attributes = read_csv(root / ATTRIBUTES.relative_to(ROOT))
    if attribute_fields != list(ATTRIBUTE_FIELDS):
        raise MigrationError("attributes header drifted")
    by_attribute = {row["code"]: row for row in attributes}
    for expected in expected_attribute_rows(spec):
        actual = by_attribute.get(expected["code"])
        if actual is None:
            raise MigrationError(f"missing attribute: {expected['code']}")
        require_exact_existing(actual, expected, label=f"attribute {expected['code']}")

    availability_fields, availability = read_csv(
        root / AVAILABILITY.relative_to(ROOT)
    )
    if availability_fields != list(AVAILABILITY_FIELDS):
        raise MigrationError("availability header drifted")
    by_availability = {row["code"]: row for row in availability}
    for expected in expected_availability_rows(spec):
        actual = by_availability.get(expected["code"])
        if actual is None:
            raise MigrationError(f"missing availability row: {expected['code']}")
        require_exact_existing(
            actual,
            expected,
            label=f"availability {expected['code']}",
        )

    snapshot = read_json(root / SNAPSHOT.relative_to(ROOT))
    matrix = {
        row["configuration_code"]: row
        for row in snapshot["charging_cable_evidence_matrix"]
    }
    if matrix["spring_expression_electric70_automatic"]["type2_cable"] != "standard":
        raise MigrationError("Expression Type 2 evidence drifted")
    if matrix["spring_expression_electric70_automatic"]["domestic_socket_cable"] != "unresolved":
        raise MigrationError("Expression domestic-cable evidence boundary drifted")
    if "spring_independent_charging_cable_concepts" not in (
        root / DECISION.relative_to(ROOT)
    ).read_text(encoding="utf-8"):
        raise MigrationError("accepted charging-cable decision is missing")

    report = read_json(root / REPORT_JSON.relative_to(ROOT))
    migration = report["migration"]
    if migration["attributes_added"] != 2:
        raise MigrationError("migration report attribute delta drifted")
    if migration["availability_rows_added"] != 5:
        raise MigrationError("migration report availability delta drifted")
    if migration["historical_commercial_records_changed"] != 0:
        raise MigrationError("historical commercial records were rewritten")
    if report["counts"]["delta"] != {
        "attributes": 2,
        "availability_records": 5,
        "master_rows": 7,
    }:
        raise MigrationError("migration report master-data delta drifted")

    state = read_json(root / STATE.relative_to(ROOT))
    if state["current_package"]["package_id"] == PACKAGE_ID:
        expression_domestic = [
            row
            for row in availability
            if row["configuration_code"] == "spring_expression_electric70_automatic"
            and row["attribute_code"] == "domestic_socket_charging_cable"
        ]
        if expression_domestic:
            raise MigrationError(
                "Expression domestic-cable row was created without exact option evidence"
            )
        if state["next_package"]["package_id"] != NEXT_PACKAGE_ID:
            raise MigrationError("unexpected follow-up package")
        if state["baseline"]["rows"] != master_row_count(root):
            raise MigrationError("canonical master-row baseline drifted")
        if state["baseline"]["attributes"] != len(attributes):
            raise MigrationError("canonical attribute baseline drifted")
        if state["baseline"]["availability_records"] != len(availability):
            raise MigrationError("canonical availability baseline drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    else:
        verify()
    print("Spring charging-cable representation migration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
