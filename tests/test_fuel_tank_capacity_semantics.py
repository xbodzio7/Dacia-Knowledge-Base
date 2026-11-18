from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "data" / "master" / "attributes.csv"


def attribute_rows() -> list[dict[str, str]]:
    with ATTRIBUTES.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class FuelTankCapacitySemanticsTests(unittest.TestCase):
    def test_total_and_usable_capacities_are_distinct_canonical_attributes(self) -> None:
        rows = {
            row["code"]: row
            for row in attribute_rows()
        }
        self.assertEqual(
            rows["fuel_tank_capacity_total"],
            {
                "id": "425",
                "code": "fuel_tank_capacity_total",
                "category": "Capacities",
                "name": "Fuel tank capacity (total)",
                "data_type": "decimal",
                "unit": "L",
                "description": (
                    "Total physical fuel-tank capacity explicitly stated by "
                    "the source; not assumed to be usable capacity."
                ),
                "status": "active",
            },
        )
        self.assertEqual(
            rows["fuel_tank_capacity_usable"],
            {
                "id": "426",
                "code": "fuel_tank_capacity_usable",
                "category": "Capacities",
                "name": "Fuel tank capacity (usable)",
                "data_type": "decimal",
                "unit": "L",
                "description": (
                    "Usable fuel volume explicitly stated by the source; "
                    "not inferred from total capacity."
                ),
                "status": "active",
            },
        )

    def test_legacy_ambiguous_capacity_attribute_is_preserved(self) -> None:
        rows = {row["code"] for row in attribute_rows()}
        self.assertIn("fuel_tank_capacity", rows)
        self.assertIn("fuel_tank_capacity_total", rows)
        self.assertIn("fuel_tank_capacity_usable", rows)


if __name__ == "__main__":
    unittest.main()
