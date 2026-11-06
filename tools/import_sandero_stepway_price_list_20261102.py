#!/usr/bin/env python3
"""Deterministic import/check for the Polish Sandero MY26 2026-11-02 price list."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "project" / "sources" / "sandero_stepway_price_my26_20261102_import_spec.json"
PREVIOUS_PRICE_SOURCE = "src_pl_sandero_stepway_price_my26_20260811"

TABLES = {
    "source": ("sources.csv", "source", ("code",)),
    "source_configurations": ("source_configurations.csv", "source_configurations", ("source_code", "configuration_code")),
    "source_versions": ("source_versions.csv", "source_versions", ("source_code", "version_code")),
    "configuration_prices": ("configuration_prices.csv", "configuration_prices", ("code",)),
    "configuration_attribute_values": ("configuration_attribute_values.csv", "configuration_attribute_values", ("code",)),
    "commercial_items": ("commercial_items.csv", "commercial_items", ("code",)),
    "commercial_item_configurations": ("commercial_item_configurations.csv", "commercial_item_configurations", ("code",)),
}


class ContractError(RuntimeError):
    """Raised when repository data differs from the reviewed import specification."""


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def key_for(row: dict[str, Any], fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in fields)


def reconcile_table(
    table_name: str,
    expected_rows: list[dict[str, Any]],
    *,
    apply: bool,
) -> int:
    filename, spec_key, key_fields = TABLES[table_name]
    path = MASTER / filename
    fieldnames, current = read_csv(path)
    by_key = {key_for(row, key_fields): row for row in current}
    missing: list[dict[str, str]] = []

    for expected in expected_rows:
        key = key_for(expected, key_fields)
        actual = by_key.get(key)
        if actual is None:
            missing.append({field: str(expected.get(field, "")) for field in fieldnames})
        elif actual != {field: str(expected.get(field, "")) for field in fieldnames}:
            raise ContractError(f"{filename}: conflicting row for key {key}")

    if apply and missing:
        write_csv(path, fieldnames, current + missing)
    return len(missing)


def reconcile_item_notes(updates: dict[str, dict[str, str]], *, apply: bool) -> int:
    path = MASTER / "commercial_items.csv"
    fieldnames, rows = read_csv(path)
    changed = 0
    for row in rows:
        update = updates.get(row["code"])
        if not update:
            continue
        previous = update["previous"]
        expected = update["current"]
        if row["notes"] == expected:
            continue
        if row["notes"] != previous:
            raise ContractError(
                f"commercial_items.csv: unexpected notes for {row['code']!r}"
            )
        row["notes"] = expected
        changed += 1
    if changed and apply:
        write_csv(path, fieldnames, rows)
    return changed


def verify_semantics(spec: dict[str, Any]) -> None:
    source = spec["source"]
    if source["document_date"] != "2026-11-02" or source["market"] != "PL":
        raise ContractError("Source date/market does not match the reviewed cennik")
    if not source["external_reference"].endswith("/3b4618d7da.pdf"):
        raise ContractError("Unexpected official PDF reference")
    if source["file_path"] or source["sha256"]:
        raise ContractError("This source is URL-only; do not invent a local path or hash")

    prices = spec["configuration_prices"]
    previous_path = MASTER / "configuration_prices.csv"
    _, all_prices = read_csv(previous_path)
    previous = {
        row["configuration_code"]: int(row["amount"])
        for row in all_prices
        if row["source_code"] == PREVIOUS_PRICE_SOURCE
    }
    if len(prices) != 15:
        raise ContractError("Expected exactly 15 changed catalogue price observations")
    for row in prices:
        old = previous.get(row["configuration_code"])
        if old is None or int(row["amount"]) - old != 500:
            raise ContractError(
                f"Unexpected catalogue price delta for {row['configuration_code']}"
            )

    for row in spec["unchanged_price_confirmations"]:
        if previous.get(row["configuration_code"]) != row["amount"]:
            raise ContractError(
                f"Unchanged hybrid155 price confirmation differs for {row['configuration_code']}"
            )

    technical = spec["configuration_attribute_values"]
    if len(technical) != 69 or len({row["code"] for row in technical}) != 69:
        raise ContractError("Expected 69 unique page-4/page-5 technical observations")
    if any(row["source_code"] != source["code"] or row["observation_date"] != "2026-11-02" for row in technical):
        raise ContractError("Technical observations must use the exact cennik source and date")
    page4 = [row for row in technical if "page 4" in row["notes"]]
    page5 = [row for row in technical if "page 5" in row["notes"]]
    if len(page4) != 42 or len(page5) != 27:
        raise ContractError("Technical page evidence totals differ from the reviewed source inventory")
    natural_keys = [
        (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        for row in technical
    ]
    if len(set(natural_keys)) != len(natural_keys):
        raise ContractError("Duplicate technical observation scope/date in the import specification")
    if Counter(row["attribute_code"] for row in page4) != {
        "fuel_consumption_combined": 8,
        "co2_emissions": 9,
        "cargo_volume_vda": 9,
        "injection_type": 4,
        "acceleration_0_100": 4,
        "electric_motor_torque": 4,
        "electric_motor_torque_rpm": 4,
    }:
        raise ContractError("Page-4 technical observation breakdown differs from the source review")
    if Counter(row["attribute_code"] for row in page5) != {
        "overall_width": 9,
        "overall_length": 2,
        "overall_width_with_mirrors": 2,
        "overall_height": 2,
        "front_track": 2,
        "rear_track": 2,
        "front_overhang": 2,
        "rear_overhang": 2,
        "wheelbase": 2,
        "ground_clearance": 2,
    }:
        raise ContractError("Page-5 dimension observation breakdown differs from the source review")

    mappings = spec["commercial_item_configurations"]
    if len(mappings) != 209:
        raise ContractError("Expected 209 current commercial configuration mappings")
    if Counter(row["availability_status"] for row in mappings) != {
        "optional": 102,
        "not_available": 99,
        "standard": 8,
    }:
        raise ContractError("Commercial mapping status totals differ from the cennik matrix")
    if len(spec["source_configurations"]) != 19 or len(spec["source_versions"]) != 6:
        raise ContractError("Source relationships must cover 19 configurations and six grades")


def check(spec: dict[str, Any]) -> None:
    verify_semantics(spec)
    for table_name, (_, spec_key, _) in TABLES.items():
        expected_rows = spec[spec_key]
        if isinstance(expected_rows, dict):
            expected_rows = [expected_rows]
        reconcile_table(table_name, expected_rows, apply=False)
    reconcile_item_notes(spec["commercial_item_notes_updates"], apply=False)


def apply(spec: dict[str, Any]) -> dict[str, int]:
    verify_semantics(spec)
    results: dict[str, int] = {}
    for table_name, (_, spec_key, _) in TABLES.items():
        expected_rows = spec[spec_key]
        if isinstance(expected_rows, dict):
            expected_rows = [expected_rows]
        results[table_name] = reconcile_table(
            table_name, expected_rows, apply=True
        )
    results["commercial_item_notes"] = reconcile_item_notes(
        spec["commercial_item_notes_updates"], apply=True
    )
    check(spec)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="append the reviewed cennik rows")
    parser.add_argument("--check", action="store_true", help="verify the reviewed rows (default)")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if args.apply:
        results = apply(spec)
        print("Sandero MY26 2026-11-02 cennik applied:", results)
    else:
        check(spec)
        print("Sandero MY26 2026-11-02 cennik contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
