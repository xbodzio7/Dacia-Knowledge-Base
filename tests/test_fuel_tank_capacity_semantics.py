from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "data" / "master" / "attributes.csv"
IMPORTS = ROOT / "data" / "imports" / "configuration_values"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_spec(name: str) -> dict:
    return json.loads((IMPORTS / name).read_text(encoding="utf-8"))


class FuelTankCapacitySemanticsTests(unittest.TestCase):
    def test_existing_canonical_attributes_cover_total_and_filling_capacity(self) -> None:
        rows = {row["code"]: row for row in read_csv(ATTRIBUTES)}
        self.assertEqual(rows["fuel_tank_capacity"]["id"], "128")
        self.assertEqual(rows["fuel_tank_capacity"]["data_type"], "decimal")
        self.assertEqual(rows["fuel_tank_capacity"]["unit"], "L")
        self.assertEqual(rows["lpg_vessel_capacity_total"]["id"], "362")
        self.assertEqual(rows["lpg_vessel_capacity_total"]["data_type"], "decimal")
        self.assertEqual(rows["lpg_vessel_capacity_total"]["unit"], "L")
        self.assertEqual(rows["lpg_vessel_filling_capacity"]["id"], "363")
        self.assertEqual(rows["lpg_vessel_filling_capacity"]["data_type"], "decimal")
        self.assertEqual(rows["lpg_vessel_filling_capacity"]["unit"], "L")
        self.assertNotIn("fuel_tank_capacity_total", rows)
        self.assertNotIn("fuel_tank_capacity_usable", rows)

    def test_jogger_cennik_imports_explicit_lpg_total_and_filling_values(self) -> None:
        total = read_spec("jogger-page6-lpg-vessel-capacity-total-20260401.json")
        filling = read_spec("jogger-page6-lpg-vessel-filling-capacity-20260401.json")
        self.assertEqual(total["attribute_code"], "lpg_vessel_capacity_total")
        self.assertEqual(filling["attribute_code"], "lpg_vessel_filling_capacity")
        self.assertEqual(total["source_page"], 6)
        self.assertEqual(filling["source_page"], 6)
        self.assertEqual(total["fuel_type_code"], "lpg")
        self.assertEqual(filling["fuel_type_code"], "lpg")
        self.assertEqual(len(total["rows"]), 10)
        self.assertEqual(len(filling["rows"]), 10)
        self.assertEqual({row["value"] for row in total["rows"]}, {"50"})
        self.assertEqual({row["value"] for row in filling["rows"]}, {"40"})
        self.assertTrue(all("całkowita pojemność/pojemność napełniania: 50/40" in row["source_text"] for row in total["rows"]))
        self.assertTrue(all("całkowita pojemność/pojemność napełniania: 50/40" in row["source_text"] for row in filling["rows"]))
        self.assertEqual(
            {row["configuration_code"] for row in total["rows"]},
            {row["configuration_code"] for row in filling["rows"]},
        )

    def test_jogger_generic_capacity_rows_keep_petrol_context_separate(self) -> None:
        spec = read_spec("jogger-page6-fuel-tank-capacity-20260401.json")
        ecog_rows = [
            row for row in spec["rows"]
            if "ecog120" in row["configuration_code"]
        ]
        self.assertTrue(ecog_rows)
        self.assertTrue(all(row.get("fuel_type_code") == "petrol" for row in ecog_rows))
        self.assertTrue(all(row["value"] == "50" for row in ecog_rows))


if __name__ == "__main__":
    unittest.main()
