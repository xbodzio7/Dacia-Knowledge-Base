#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
ITEMS = ROOT / "data/master/commercial_items.csv"

MAPPING_CODE = (
    "spring_domestic_socket_charging_cable_option__"
    "spring_expression_electric70_automatic"
)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def apply() -> bool:
    changed = False

    fields, rows = read_rows(MAPPINGS)
    if not any(row["code"] == MAPPING_CODE for row in rows):
        next_id = max(int(row["id"]) for row in rows) + 1
        rows.append(
            {
                "id": str(next_id),
                "code": MAPPING_CODE,
                "commercial_item_code": "spring_domestic_socket_charging_cable_option",
                "configuration_code": "spring_expression_electric70_automatic",
                "availability_status": "optional",
                "amount": "1500",
                "currency_code": "PLN",
                "price_date": "2026-07-08",
                "source_code": "src_pl_spring_price_my25_stock_20260708",
                "notes": (
                    "Official Polish Spring stock price-list charging matrix explicitly "
                    "lists FlexiCharger for Expression 70 at 1500 PLN. The saved-"
                    "configuration PDF proves selected Type 2 equipment only and does "
                    "not negate this unselected option."
                ),
            }
        )
        write_rows(MAPPINGS, fields, rows)
        changed = True

    fields, rows = read_rows(ITEMS)
    for row in rows:
        if row["code"] == "spring_domestic_socket_charging_cable_option":
            expected = (
                "Separate domestic-socket FlexiCharger option. Official Spring price-list "
                "matrix confirms 1500 PLN applicability for Essential 70, Expression 70 "
                "and Extreme 100; configuration-specific mappings retain exact sources."
            )
            if row["notes"] != expected:
                row["notes"] = expected
                write_rows(ITEMS, fields, rows)
                changed = True
            break
    else:
        raise RuntimeError("Missing domestic-socket charging cable commercial item")

    return changed


if __name__ == "__main__":
    print("changed" if apply() else "already-applied")
