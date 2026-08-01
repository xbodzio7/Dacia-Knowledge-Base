#!/usr/bin/env python3
"""Materialize exact Sandero MY26 commercial price mappings.

The interface files are normal reviewed source files. This importer owns only the
source-backed CSV additions and is safe to run repeatedly.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_sandero_stepway_price_my26_20260703"
PRICE_DATE = "2026-07-03"

MAPPINGS = (
    ("sandero_rear_view_camera_option", "sandero_iii_expression_tce100_manual", "700"),
    ("sandero_rear_view_camera_option", "sandero_iii_expression_ecog120_automatic", "700"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_tce100_manual", "1600"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_option", "sandero_stepway_iii_expression_tce110_manual", "1600"),
    ("sandero_glass_sunroof_option", "sandero_stepway_iii_extreme_tce110_manual", "2200"),
    ("sandero_comfort_auto_package", "sandero_iii_expression_ecog120_automatic", "2000"),
    ("sandero_thermo_package", "sandero_iii_expression_tce100_manual", "1900"),
    ("sandero_thermo_package", "sandero_iii_expression_ecog120_automatic", "1900"),
    ("sandero_thermo_package", "sandero_stepway_iii_expression_tce110_manual", "1900"),
    ("sandero_winter_package", "sandero_iii_journey_tce100_manual", "1200"),
    ("sandero_winter_package", "sandero_iii_journey_ecog120_automatic", "1200"),
    ("sandero_winter_package", "sandero_stepway_iii_extreme_tce110_manual", "1200"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_easy_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
)

FIELDS = (
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


def materialize() -> int:
    path = MASTER / "commercial_item_configurations.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError("unexpected commercial mapping schema")
        rows = list(reader)

    existing = {row["code"]: row for row in rows}
    next_id = max(int(row["id"]) for row in rows) + 1
    note = (
        "Exact trim-level applicability and gross amount from the official "
        "Polish Sandero/Sandero Stepway MY26 option matrix effective "
        "2026-07-03; no cross-configuration inference."
    )
    added = 0
    for item_code, configuration_code, amount in MAPPINGS:
        code = f"{item_code}__{configuration_code}"
        expected = {
            "commercial_item_code": item_code,
            "configuration_code": configuration_code,
            "availability_status": "optional",
            "amount": amount,
            "currency_code": "PLN",
            "price_date": PRICE_DATE,
            "source_code": SOURCE,
        }
        current = existing.get(code)
        if current is not None:
            mismatches = {
                key: (current.get(key, ""), value)
                for key, value in expected.items()
                if current.get(key, "") != value
            }
            if mismatches:
                raise RuntimeError(f"conflicting mapping {code}: {mismatches}")
            continue
        row = {
            "id": str(next_id),
            "code": code,
            **expected,
            "notes": note,
        }
        rows.append(row)
        existing[code] = row
        next_id += 1
        added += 1

    if added:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    return added


def main() -> None:
    added = materialize()
    print(f"Sandero commercial price mappings added: {added}")


if __name__ == "__main__":
    main()
