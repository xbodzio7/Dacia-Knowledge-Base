#!/usr/bin/env python3
"""Apply the two reviewed exact-current Spring package prices.

The importer updates only the existing Spring Extreme mapping rows named in the
reviewed import specification. It is deterministic and safe to run repeatedly.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "data/master/commercial_item_configurations.csv"
IMPORT_PATH = ROOT / "data/imports/reviewed_gap_state_materialization_20260802.csv"
EXPECTED_SOURCE = "src_pl_spring_official_configurator_20260731"
EXPECTED_DATE = "2026-07-31"
FIELDS = (
    "id", "code", "commercial_item_code", "configuration_code",
    "availability_status", "amount", "currency_code", "price_date",
    "source_code", "notes",
)
IMPORT_FIELDS = (
    "mapping_code", "commercial_item_code", "configuration_code", "amount",
    "currency_code", "price_date", "source_code", "source_path",
    "source_json_pointer", "notes",
)


def read_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise RuntimeError(f"unexpected schema for {path}")
        return list(reader)


def transformed_rows(root: Path = ROOT) -> tuple[list[dict[str, str]], int]:
    master_path = root / MASTER_PATH.relative_to(ROOT)
    import_path = root / IMPORT_PATH.relative_to(ROOT)
    rows = read_rows(master_path, FIELDS)
    imports = read_rows(import_path, IMPORT_FIELDS)
    if len(imports) != 2:
        raise RuntimeError("reviewed Spring import must contain exactly two rows")
    existing = {row["code"]: row for row in rows}
    changed = 0
    for item in imports:
        if item["source_code"] != EXPECTED_SOURCE or item["price_date"] != EXPECTED_DATE:
            raise RuntimeError("unexpected reviewed Spring source or price date")
        row = existing.get(item["mapping_code"])
        if row is None:
            raise RuntimeError(f"missing existing commercial mapping: {item['mapping_code']}")
        if row["commercial_item_code"] != item["commercial_item_code"]:
            raise RuntimeError(f"commercial item mismatch: {item['mapping_code']}")
        if row["configuration_code"] != item["configuration_code"]:
            raise RuntimeError(f"configuration mismatch: {item['mapping_code']}")
        if row["availability_status"] != "optional":
            raise RuntimeError(f"mapping is not optional: {item['mapping_code']}")
        expected = {
            "amount": item["amount"],
            "currency_code": item["currency_code"],
            "price_date": item["price_date"],
            "source_code": item["source_code"],
            "notes": item["notes"],
        }
        if any(row[key] != value for key, value in expected.items()):
            row.update(expected)
            changed += 1
    return rows, changed


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def materialize(root: Path = ROOT) -> int:
    rows, changed = transformed_rows(root)
    if changed:
        write_rows(root / MASTER_PATH.relative_to(ROOT), rows)
    return changed


def main() -> None:
    changed = materialize()
    print(f"Reviewed Spring commercial mappings updated: {changed}")


if __name__ == "__main__":
    main()
