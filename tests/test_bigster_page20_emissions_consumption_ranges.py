from __future__ import annotations

import csv
import hashlib
import json
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "imports" / "configuration_value_ranges" / "bigster-page20-emissions-consumption-ranges-20251210.json"
MASTER = ROOT / "data" / "master" / "configuration_attribute_value_ranges.csv"
VALUES = ROOT / "data" / "master" / "configuration_attribute_values.csv"
CONFIGURATIONS = ROOT / "data" / "master" / "configurations.csv"
SOURCE_CONFIGURATIONS = ROOT / "data" / "master" / "source_configurations.csv"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class BigsterPage20EmissionsConsumptionRangesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = read_json(SPEC)
        cls.rows = cls.spec["rows"]
        cls.codes = {row["code"] for row in cls.rows}
        cls.master_rows = [row for row in read_csv(MASTER) if row["code"] in cls.codes]
        cls.exact = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"]): row
            for row in read_csv(VALUES)
        }

    def test_source_receipt_and_batch_contract(self) -> None:
        self.assertEqual(self.spec["kind"], "configuration_attribute_value_ranges_batch")
        self.assertEqual(self.spec["id_start"], 245)
        self.assertEqual(self.spec["row_count"], 30)
        self.assertEqual(len(self.rows), 30)
        self.assertEqual(self.spec["source_page"], 20)
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), self.spec["source_sha256"])
        self.assertEqual(set(self.spec["attribute_contracts"]), {"co2_emissions", "fuel_consumption_combined"})

    def test_rows_are_exactly_ids_245_through_274_and_unique(self) -> None:
        self.assertEqual([int(row["id"]) for row in self.rows], list(range(245, 275)))
        self.assertEqual(len(self.codes), 30)
        keys = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]) for row in self.rows}
        self.assertEqual(len(keys), 30)

    def test_master_rows_match_the_import_manifest_exactly(self) -> None:
        expected_fields = list(read_csv(MASTER)[0].keys())
        expected = [{key: row[key] for key in expected_fields} for row in self.rows]
        self.assertEqual(self.master_rows, expected)

    def test_ranges_are_inclusive_and_upper_endpoints_match_current_exact_values(self) -> None:
        for row in self.rows:
            self.assertEqual(row["lower_inclusive"], "true")
            self.assertEqual(row["upper_inclusive"], "true")
            self.assertLess(Decimal(row["minimum_value"]), Decimal(row["maximum_value"]))
            key = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"])
            exact = self.exact[key]
            self.assertEqual(Decimal(exact["value"]), Decimal(row["maximum_value"]))
            self.assertEqual(row["upper_exact_value"], row["maximum_value"])

    def test_all_configurations_are_current_and_linked_to_the_source(self) -> None:
        configuration_codes = {row["code"] for row in read_csv(CONFIGURATIONS)}
        imported = {row["configuration_code"] for row in self.rows}
        self.assertTrue(imported <= configuration_codes)
        linked = {row["configuration_code"] for row in read_csv(SOURCE_CONFIGURATIONS) if row["source_code"] == self.spec["source_code"]}
        self.assertTrue(imported <= linked)
        self.assertEqual(len(imported), 11)

    def test_powertrain_and_fuel_counts_match_the_page20_cells(self) -> None:
        counts: dict[tuple[str, str, str], int] = {}
        for row in self.rows:
            key = (row["powertrain"], row["attribute_code"], row["fuel_type_code"])
            counts[key] = counts.get(key, 0) + 1
        self.assertEqual(counts, {
            ("mild_hybrid_g_140", "co2_emissions", "petrol"): 4,
            ("mild_hybrid_g_140", "co2_emissions", "lpg"): 4,
            ("mild_hybrid_g_140", "fuel_consumption_combined", "petrol"): 4,
            ("mild_hybrid_g_140", "fuel_consumption_combined", "lpg"): 4,
            ("mild_hybrid_140", "co2_emissions", "petrol"): 4,
            ("mild_hybrid_140", "fuel_consumption_combined", "petrol"): 4,
            ("hybrid_155", "co2_emissions", "petrol"): 3,
            ("hybrid_155", "fuel_consumption_combined", "petrol"): 3,
        })

    def test_hybrid_g_150_exact_pairs_and_conflicts_are_excluded(self) -> None:
        self.assertEqual(len(self.spec["exclusions"]), 1)
        exclusion = self.spec["exclusions"][0]
        self.assertEqual(exclusion["powertrain"], "hybrid_g_150_4x4")
        self.assertIn("exact pairs", exclusion["reason"])
        self.assertFalse(any("hybridg150" in row["configuration_code"] for row in self.rows))


if __name__ == "__main__":
    unittest.main()
