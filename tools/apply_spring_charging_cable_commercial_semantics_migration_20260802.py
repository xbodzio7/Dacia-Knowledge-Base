from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def migrate_items() -> None:
    path = ROOT / "data/master/commercial_items.csv"
    rows = read_rows(path)
    if not any(row["code"] == "spring_domestic_socket_charging_cable_option" for row in rows):
        rows.append(
            {
                "id": str(max(int(row["id"]) for row in rows) + 1),
                "code": "spring_domestic_socket_charging_cable_option",
                "name": "Przewód do ładowania z gniazdka domowego",
                "item_type": "option",
                "observation_date": "2026-08-02",
                "source_code": "src_pl_spring_commercial_context_20260802",
                "status": "active",
                "notes": "Exact-current separate domestic-socket charging cable option; Expression applicability remains unresolved.",
            }
        )
    write_rows(path, rows, ["id", "code", "name", "item_type", "observation_date", "source_code", "status", "notes"])


def migrate_memberships() -> None:
    path = ROOT / "data/master/commercial_item_attributes.csv"
    rows = read_rows(path)
    for row in rows:
        if row["commercial_item_code"] == "spring_type2_charging_cable_option":
            row["code"] = "spring_type2_charging_cable_option__type2_charging_cable_supplied"
            row["attribute_code"] = "type2_charging_cable_supplied"
            row["notes"] = "Corrected membership: the brochure item describes a physical Type 2 cable, not the vehicle charging connector."
    if not any(row["commercial_item_code"] == "spring_domestic_socket_charging_cable_option" for row in rows):
        rows.append(
            {
                "id": str(max(int(row["id"]) for row in rows) + 1),
                "code": "spring_domestic_socket_charging_cable_option__domestic_socket_charging_cable",
                "commercial_item_code": "spring_domestic_socket_charging_cable_option",
                "attribute_code": "domestic_socket_charging_cable",
                "source_text": "Przewód do ładowania z gniazdka domowego",
                "notes": "Separate from the supplied Type 2 cable and from the vehicle connector standard.",
            }
        )
    write_rows(path, rows, ["id", "code", "commercial_item_code", "attribute_code", "source_text", "notes"])


def migrate_mappings() -> None:
    path = ROOT / "data/master/commercial_item_configurations.csv"
    rows = read_rows(path)
    next_id = max(int(row["id"]) for row in rows) + 1
    for configuration, label in (
        ("spring_essential_electric70_automatic", "Essential 70"),
        ("spring_extreme_electric100_automatic", "Extreme 100"),
    ):
        code = f"spring_domestic_socket_charging_cable_option__{configuration}"
        if any(row["code"] == code for row in rows):
            continue
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "commercial_item_code": "spring_domestic_socket_charging_cable_option",
                "configuration_code": configuration,
                "availability_status": "optional",
                "amount": "1500",
                "currency_code": "PLN",
                "price_date": "2026-08-02",
                "source_code": "src_pl_spring_commercial_context_20260802",
                "notes": f"Exact-current {label} option state. No mapping is inferred for Spring Expression.",
            }
        )
        next_id += 1
    write_rows(
        path,
        rows,
        ["id", "code", "commercial_item_code", "configuration_code", "availability_status", "amount", "currency_code", "price_date", "source_code", "notes"],
    )


def write_artifacts() -> None:
    report = {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "package_id": "spring_charging_cable_commercial_semantics_migration_001",
        "type2_membership": {
            "commercial_item_code": "spring_type2_charging_cable_option",
            "attribute_code": "type2_charging_cable_supplied",
            "historical_mapping_count_preserved": 3,
        },
        "domestic_socket_item": {
            "commercial_item_code": "spring_domestic_socket_charging_cable_option",
            "attribute_code": "domestic_socket_charging_cable",
            "mapping_count": 2,
            "amount_pln": 1500,
            "mapped_configurations": ["spring_essential_electric70_automatic", "spring_extreme_electric100_automatic"],
            "unresolved_configurations": ["spring_expression_electric70_automatic"],
        },
        "master_data_delta": {
            "commercial_items": 1,
            "commercial_item_attributes": 1,
            "commercial_item_configurations": 2,
            "net_master_rows": 3,
            "historical_type2_mappings_changed": 0,
        },
    }
    (ROOT / "data/reporting/spring_charging_cable_commercial_semantics_migration.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "data/reporting/spring_charging_cable_commercial_semantics_migration.md").write_text(
        "# Spring Charging-Cable Commercial Semantics Migration\n\n"
        "- corrected the historical Type 2 item membership to `type2_charging_cable_supplied`;\n"
        "- preserved all three brochure-backed historical option mappings;\n"
        "- added a separate domestic-socket cable option;\n"
        "- added exact 1500 PLN optional mappings for Essential 70 and Extreme 100;\n"
        "- created no Expression mapping.\n",
        encoding="utf-8",
    )
    (ROOT / "project/packages/spring-charging-cable-commercial-semantics-migration-20260802.md").write_text(
        "# Spring Charging-Cable Commercial Semantics Migration\n\n"
        "Package: `spring_charging_cable_commercial_semantics_migration_001`\n\n"
        "Status: complete\n\n"
        "The package applies the accepted commercial semantics decision with a net three-row master-data increase and preserves historical Type 2 configuration mappings.\n",
        encoding="utf-8",
    )


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Spring Charging Cable Commercial Semantics Migration"
    state["baseline"]["rows"] = 11726
    state["current_package"] = {
        "package_id": "spring_charging_cable_commercial_semantics_migration_001",
        "kind": "bounded_commercial_data_migration",
        "name": "Spring Charging Cable Commercial Semantics Migration",
        "status": "complete",
        "goal": "Materialize the accepted Type 2 membership correction and exact-current domestic-socket commercial item without rewriting historical mappings.",
        "manifest_paths": [
            "data/master/commercial_items.csv",
            "data/master/commercial_item_attributes.csv",
            "data/master/commercial_item_configurations.csv",
            "data/reporting/spring_charging_cable_commercial_semantics_migration.json",
            "data/reporting/spring_charging_cable_commercial_semantics_migration.md",
            "project/STATE_SUMMARY.md",
            "project/state.json",
            "tests/test_spring_charging_cable_commercial_semantics_migration_20260802.py",
            "tools/apply_spring_charging_cable_commercial_semantics_migration_20260802.py",
        ],
    }
    state["next_package"] = {
        "package_id": "post_spring_charging_cable_priority_selection_review_001",
        "kind": "bounded_priority_selection_review",
        "name": "Post-Spring Charging Cable Priority Selection Review",
        "status": "planned",
        "goal": "Select the next bounded repository package from current evidence and unresolved queues without changing master data.",
        "manifest_paths": ["project/state.json", "project/STATE_SUMMARY.md", "data/reporting/"],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    migrate_items()
    migrate_memberships()
    migrate_mappings()
    write_artifacts()
    update_state()


if __name__ == "__main__":
    main()
