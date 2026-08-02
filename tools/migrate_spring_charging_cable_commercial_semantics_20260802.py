#!/usr/bin/env python3
"""Apply or verify Spring charging-cable commercial semantics."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/imports/commercial_items/spring_charging_cable_commercial_semantics_20260802.json"
ITEMS = ROOT / "data/master/commercial_items.csv"
MEMBERSHIPS = ROOT / "data/master/commercial_item_attributes.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
ATTRIBUTES = ROOT / "data/master/attributes.csv"
CONFIGURATIONS = ROOT / "data/master/configurations.csv"
SOURCES = ROOT / "data/master/sources.csv"
STATE = ROOT / "project/state.json"
REPORT_JSON = ROOT / "data/reporting/spring_charging_cable_commercial_semantics_review.json"
REPORT_MD = ROOT / "data/reporting/spring_charging_cable_commercial_semantics_review.md"

PACKAGE_ID = "spring_charging_cable_commercial_semantics_review_001"
NEXT_PACKAGE_ID = "spring_expression_domestic_socket_option_resolution_001"

ITEM_FIELDS = (
    "id",
    "code",
    "name",
    "item_type",
    "observation_date",
    "source_code",
    "status",
    "notes",
)
MEMBERSHIP_FIELDS = (
    "id",
    "code",
    "commercial_item_code",
    "attribute_code",
    "source_text",
    "notes",
)
MAPPING_FIELDS = (
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
)


class MigrationError(RuntimeError):
    """Raised when the bounded migration contract is violated."""


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


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fields),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows: list[dict[str, str]]) -> int:
    values: list[int] = []
    for row in rows:
        raw = row.get("id", "").strip()
        if not raw.isdigit():
            raise MigrationError(f"non-numeric id: {raw!r}")
        values.append(int(raw))
    return max(values, default=0) + 1


def codes(path: Path) -> set[str]:
    _, rows = read_csv(path)
    return {row["code"] for row in rows}


def master_rows(root: Path) -> int:
    total = 0
    for path in sorted((root / "data/master").rglob("*.csv")):
        _, rows = read_csv(path)
        total += len(rows)
    return total


def validate_spec(root: Path, spec: dict[str, Any]) -> None:
    if spec.get("version") != 1 or spec.get("package_id") != PACKAGE_ID:
        raise MigrationError("unexpected specification identity")

    historical = spec["historical_type2_membership"]
    if historical["commercial_item_code"] != "spring_type2_charging_cable_option":
        raise MigrationError("unexpected historical Type 2 item")
    if historical["old_attribute_code"] != "charging_connector_type":
        raise MigrationError("unexpected old Type 2 membership")
    if historical["new_attribute_code"] != "type2_charging_cable_supplied":
        raise MigrationError("unexpected corrected Type 2 membership")

    current = spec["current_domestic_socket_item"]
    if current["code"] != "spring_domestic_socket_charging_cable_option":
        raise MigrationError("unexpected current domestic-cable item")
    if current["membership"]["attribute_code"] != "domestic_socket_charging_cable":
        raise MigrationError("unexpected domestic-cable membership")
    if {row["configuration_code"] for row in current["mappings"]} != {
        "spring_essential_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise MigrationError("domestic-cable mapping scope drifted")
    if any(row["amount"] != "1500" for row in current["mappings"]):
        raise MigrationError("domestic-cable amount drifted")
    if current["explicit_non_import"]["configuration_code"] != "spring_expression_electric70_automatic":
        raise MigrationError("Expression non-import boundary drifted")

    attribute_codes = codes(root / ATTRIBUTES.relative_to(ROOT))
    configuration_codes = codes(root / CONFIGURATIONS.relative_to(ROOT))
    source_codes = codes(root / SOURCES.relative_to(ROOT))
    for attribute in (
        historical["new_attribute_code"],
        current["membership"]["attribute_code"],
    ):
        if attribute not in attribute_codes:
            raise MigrationError(f"missing canonical attribute: {attribute}")
    if current["source_code"] not in source_codes:
        raise MigrationError(f"missing source: {current['source_code']}")
    for row in current["mappings"]:
        if row["configuration_code"] not in configuration_codes:
            raise MigrationError(f"missing configuration: {row['configuration_code']}")
        if row["source_code"] not in source_codes:
            raise MigrationError(f"missing mapping source: {row['source_code']}")


def expected_current_item(spec: dict[str, Any]) -> dict[str, str]:
    current = spec["current_domestic_socket_item"]
    return {
        "code": current["code"],
        "name": current["name"],
        "item_type": current["item_type"],
        "observation_date": current["observation_date"],
        "source_code": current["source_code"],
        "status": current["status"],
        "notes": current["notes"],
    }


def expected_type2_membership(spec: dict[str, Any]) -> dict[str, str]:
    historical = spec["historical_type2_membership"]
    return {
        "code": historical["new_membership_code"],
        "commercial_item_code": historical["commercial_item_code"],
        "attribute_code": historical["new_attribute_code"],
        "source_text": historical["source_text"],
        "notes": "Historical brochure option describes the physical Type 2 cable. Membership was corrected after the canonical supplied-cable attribute was introduced; all source-bounded option mappings remain unchanged.",
    }


def expected_domestic_membership(spec: dict[str, Any]) -> dict[str, str]:
    current = spec["current_domestic_socket_item"]
    membership = current["membership"]
    return {
        "code": membership["code"],
        "commercial_item_code": current["code"],
        "attribute_code": membership["attribute_code"],
        "source_text": membership["source_text"],
        "notes": membership["notes"],
    }


def expected_domestic_mappings(spec: dict[str, Any]) -> list[dict[str, str]]:
    current = spec["current_domestic_socket_item"]
    return [
        {
            "code": row["code"],
            "commercial_item_code": current["code"],
            "configuration_code": row["configuration_code"],
            "availability_status": row["availability_status"],
            "amount": row["amount"],
            "currency_code": row["currency_code"],
            "price_date": row["price_date"],
            "source_code": row["source_code"],
            "notes": row["notes"],
        }
        for row in current["mappings"]
    ]


def without_id(row: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in row.items() if key != "id"}


def require_exact(actual: dict[str, str], expected: dict[str, str], label: str) -> None:
    if without_id(actual) != expected:
        raise MigrationError(
            f"{label} differs from specification: {without_id(actual)!r} != {expected!r}"
        )


def apply(root: Path = ROOT) -> None:
    spec = read_json(root / SPEC.relative_to(ROOT))
    validate_spec(root, spec)

    item_path = root / ITEMS.relative_to(ROOT)
    membership_path = root / MEMBERSHIPS.relative_to(ROOT)
    mapping_path = root / MAPPINGS.relative_to(ROOT)

    item_fields, items = read_csv(item_path)
    membership_fields, memberships = read_csv(membership_path)
    mapping_fields, mappings = read_csv(mapping_path)
    if item_fields != list(ITEM_FIELDS):
        raise MigrationError("commercial item header drifted")
    if membership_fields != list(MEMBERSHIP_FIELDS):
        raise MigrationError("commercial membership header drifted")
    if mapping_fields != list(MAPPING_FIELDS):
        raise MigrationError("commercial mapping header drifted")

    before_master = master_rows(root)
    before_counts = {
        "commercial_items": len(items),
        "commercial_item_attributes": len(memberships),
        "commercial_item_configurations": len(mappings),
        "master_rows": before_master,
    }

    historical = spec["historical_type2_membership"]
    old_code = historical["old_membership_code"]
    expected_type2 = expected_type2_membership(spec)
    old_rows = [row for row in memberships if row["code"] == old_code]
    new_rows = [row for row in memberships if row["code"] == expected_type2["code"]]
    membership_corrected = 0
    if old_rows and new_rows:
        raise MigrationError("both old and corrected Type 2 memberships exist")
    if len(old_rows) == 1:
        old = old_rows[0]
        if old["commercial_item_code"] != historical["commercial_item_code"]:
            raise MigrationError("historical Type 2 membership item drifted")
        if old["attribute_code"] != historical["old_attribute_code"]:
            raise MigrationError("historical Type 2 membership attribute drifted")
        if old["source_text"] != historical["source_text"]:
            raise MigrationError("historical Type 2 source text drifted")
        replacement = {"id": old["id"], **expected_type2}
        memberships[memberships.index(old)] = replacement
        membership_corrected = 1
    elif len(new_rows) == 1:
        require_exact(new_rows[0], expected_type2, "corrected Type 2 membership")
    else:
        raise MigrationError("historical Type 2 membership is missing")

    expected_item = expected_current_item(spec)
    item_index = {row["code"]: row for row in items}
    items_added = 0
    current_item = item_index.get(expected_item["code"])
    if current_item is None:
        current_item = {"id": str(next_id(items)), **expected_item}
        items.append(current_item)
        items_added = 1
    else:
        require_exact(current_item, expected_item, "domestic-cable commercial item")

    expected_membership = expected_domestic_membership(spec)
    membership_index = {row["code"]: row for row in memberships}
    memberships_added = 0
    current_membership = membership_index.get(expected_membership["code"])
    if current_membership is None:
        current_membership = {
            "id": str(next_id(memberships)),
            **expected_membership,
        }
        memberships.append(current_membership)
        memberships_added = 1
    else:
        require_exact(
            current_membership,
            expected_membership,
            "domestic-cable commercial membership",
        )

    mapping_index = {row["code"]: row for row in mappings}
    mappings_added = 0
    for expected_mapping in expected_domestic_mappings(spec):
        current_mapping = mapping_index.get(expected_mapping["code"])
        if current_mapping is None:
            current_mapping = {
                "id": str(next_id(mappings)),
                **expected_mapping,
            }
            mappings.append(current_mapping)
            mapping_index[current_mapping["code"]] = current_mapping
            mappings_added += 1
        else:
            require_exact(
                current_mapping,
                expected_mapping,
                f"domestic-cable mapping {expected_mapping['configuration_code']}",
            )

    expression_rows = [
        row
        for row in mappings
        if row["commercial_item_code"] == expected_item["code"]
        and row["configuration_code"] == "spring_expression_electric70_automatic"
    ]
    if expression_rows:
        raise MigrationError("Expression domestic-cable mapping lacks exact evidence")

    historical_mappings = [
        row
        for row in mappings
        if row["commercial_item_code"] == historical["commercial_item_code"]
    ]
    if len(historical_mappings) != 3:
        raise MigrationError("historical Type 2 mapping count drifted")
    if {row["availability_status"] for row in historical_mappings} != {"optional"}:
        raise MigrationError("historical Type 2 mapping status was rewritten")
    if {row["source_code"] for row in historical_mappings} != {"src_pl_spring_brochure_20260219"}:
        raise MigrationError("historical Type 2 mapping source was rewritten")

    write_csv(item_path, ITEM_FIELDS, items)
    write_csv(membership_path, MEMBERSHIP_FIELDS, memberships)
    write_csv(mapping_path, MAPPING_FIELDS, mappings)

    after_counts = {
        "commercial_items": len(items),
        "commercial_item_attributes": len(memberships),
        "commercial_item_configurations": len(mappings),
        "master_rows": master_rows(root),
    }
    delta = {
        key: after_counts[key] - before_counts[key]
        for key in before_counts
    }
    if delta != {
        "commercial_items": 1,
        "commercial_item_attributes": 1,
        "commercial_item_configurations": 2,
        "master_rows": 3,
    } and any(delta.values()):
        raise MigrationError(f"unexpected commercial migration delta: {delta}")

    report = {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "package_id": PACKAGE_ID,
        "decision": {
            "historical_type2_item": "preserved_as_source_bounded_option_observation",
            "historical_type2_membership": "corrected_to_type2_charging_cable_supplied",
            "historical_type2_mappings_changed": 0,
            "current_domestic_socket_item": "added",
            "expression_domestic_socket_state": "unresolved_no_mapping_created",
        },
        "counts": {
            "before": before_counts,
            "after": after_counts,
            "delta": delta,
        },
        "current_domestic_socket_mappings": [
            {
                "configuration_code": row["configuration_code"],
                "availability_status": row["availability_status"],
                "amount_pln": int(row["amount"]),
                "source_code": row["source_code"],
            }
            for row in expected_domestic_mappings(spec)
        ],
        "next_package": {
            "package_id": NEXT_PACKAGE_ID,
            "goal": "Capture exact current Expression option evidence for the domestic-socket charging cable without inferring from selected-equipment PDFs.",
        },
    }
    write_json(root / REPORT_JSON.relative_to(ROOT), report)
    report_md = root / REPORT_MD.relative_to(ROOT)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(
        """# Spring Charging-Cable Commercial Semantics Review

**Status:** complete  
**Date:** 2026-08-02

## Decision

The February brochure item `spring_type2_charging_cable_option` genuinely describes a physical Type 2 cable. Its three option mappings remain unchanged as historical source-bounded observations. Its semantic membership is corrected from the vehicle connector attribute to `type2_charging_cable_supplied`.

A separate current item, `spring_domestic_socket_charging_cable_option`, is added for the domestic-socket cable. Exact-current mappings are limited to Essential 70 and Extreme 100 at 1500 PLN. No Expression mapping is created.

## Data impact

- commercial items: **+1**;
- commercial-item memberships: **+1** net;
- commercial-item configuration mappings: **+2**;
- total master rows: **+3**;
- historical Type 2 mappings changed: **0**.

## Next package

`spring_expression_domestic_socket_option_resolution_001` requires an exact current Expression option-state artifact before any commercial mapping can be added.
""",
        encoding="utf-8",
    )

    state_path = root / STATE.relative_to(ROOT)
    state = read_json(state_path)
    state["updated_on"] = "2026-08-02"
    state["phase"] = "Spring Charging Cable Commercial Semantics"
    state["reference_delivery"] = {
        "name": "Spring Charging Cable Representation Migration",
        "pull_request": 461,
        "head_sha": "4d7bc3c1a92b851b7e72eab4f9c6b72b27d8b241",
        "quality_run": 30752269446,
    }
    state["baseline"]["rows"] = after_counts["master_rows"]
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "bounded_commercial_semantics_review_and_migration",
        "name": "Spring Charging Cable Commercial Semantics Review",
        "status": "complete",
        "goal": "Correct the historical Type 2 commercial membership and add only exact-current domestic-socket cable commercial mappings without rewriting historical observations.",
        "manifest_paths": [
            "CHANGELOG.md",
            "README.md",
            "data/imports/commercial_items/spring_charging_cable_commercial_semantics_20260802.json",
            "data/master/commercial_item_attributes.csv",
            "data/master/commercial_item_configurations.csv",
            "data/master/commercial_items.csv",
            "data/reporting/spring_charging_cable_commercial_semantics_review.json",
            "data/reporting/spring_charging_cable_commercial_semantics_review.md",
            "project/SESSION_STATE.md",
            "project/STATE_SUMMARY.md",
            "project/packages/spring-charging-cable-commercial-semantics-review-20260802.md",
            "project/state.json",
            "tests/test_spring_charging_cable_commercial_semantics_review_20260802.py",
            "tools/migrate_spring_charging_cable_commercial_semantics_20260802.py"
        ],
    }
    state["next_package"] = {
        "package_id": NEXT_PACKAGE_ID,
        "kind": "bounded_source_capture",
        "name": "Spring Expression Domestic-Socket Option Resolution",
        "status": "planned",
        "goal": "Capture exact current Expression option evidence for the domestic-socket charging cable without inferring from selected-equipment PDFs.",
        "manifest_paths": [
            "project/sources/",
            "data/reporting/",
            "project/STATE_SUMMARY.md",
            "project/state.json"
        ],
    }
    write_json(state_path, state)
    verify(root)


def verify(root: Path = ROOT) -> None:
    spec = read_json(root / SPEC.relative_to(ROOT))
    validate_spec(root, spec)

    _, items = read_csv(root / ITEMS.relative_to(ROOT))
    _, memberships = read_csv(root / MEMBERSHIPS.relative_to(ROOT))
    _, mappings = read_csv(root / MAPPINGS.relative_to(ROOT))

    item_index = {row["code"]: row for row in items}
    membership_index = {row["code"]: row for row in memberships}
    mapping_index = {row["code"]: row for row in mappings}

    require_exact(
        item_index[expected_current_item(spec)["code"]],
        expected_current_item(spec),
        "domestic-cable item",
    )
    require_exact(
        membership_index[expected_type2_membership(spec)["code"]],
        expected_type2_membership(spec),
        "corrected Type 2 membership",
    )
    if spec["historical_type2_membership"]["old_membership_code"] in membership_index:
        raise MigrationError("obsolete connector membership still exists")
    require_exact(
        membership_index[expected_domestic_membership(spec)["code"]],
        expected_domestic_membership(spec),
        "domestic-cable membership",
    )
    for expected in expected_domestic_mappings(spec):
        require_exact(
            mapping_index[expected["code"]],
            expected,
            f"domestic mapping {expected['configuration_code']}",
        )

    domestic_code = expected_current_item(spec)["code"]
    domestic_mappings = [
        row for row in mappings if row["commercial_item_code"] == domestic_code
    ]
    if {row["configuration_code"] for row in domestic_mappings} != {
        "spring_essential_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise MigrationError("current domestic-cable mapping scope drifted")

    historical = spec["historical_type2_membership"]
    historical_mappings = [
        row
        for row in mappings
        if row["commercial_item_code"] == historical["commercial_item_code"]
    ]
    if len(historical_mappings) != 3:
        raise MigrationError("historical Type 2 mappings were not preserved")
    if any(row["availability_status"] != "optional" for row in historical_mappings):
        raise MigrationError("historical Type 2 mapping status drifted")
    if any(row["source_code"] != "src_pl_spring_brochure_20260219" for row in historical_mappings):
        raise MigrationError("historical Type 2 mapping source drifted")

    report = read_json(root / REPORT_JSON.relative_to(ROOT))
    if report["counts"]["delta"] != {
        "commercial_items": 1,
        "commercial_item_attributes": 1,
        "commercial_item_configurations": 2,
        "master_rows": 3,
    }:
        raise MigrationError("commercial semantics report delta drifted")
    if report["decision"]["historical_type2_mappings_changed"] != 0:
        raise MigrationError("historical mappings were rewritten")

    state = read_json(root / STATE.relative_to(ROOT))
    if state["current_package"]["package_id"] == PACKAGE_ID:
        if state["baseline"]["rows"] != master_rows(root):
            raise MigrationError("canonical master-row baseline drifted")
        if state["next_package"]["package_id"] != NEXT_PACKAGE_ID:
            raise MigrationError("unexpected Expression follow-up package")


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
    print("Spring charging-cable commercial semantics: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
