from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MASTER = ROOT / "data" / "master"
SPEC = (
    ROOT
    / "data"
    / "imports"
    / "configuration_values"
    / "jogger-page6-minimum-kerb-weight-20260401.json"
)
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerMinimumKerbWeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = importer.load_spec(SPEC)
        cls.attributes = {
            row["code"]: row for row in csv_rows(MASTER / "attributes.csv")
        }
        cls.configurations = {
            row["code"]
            for row in csv_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_") and row["status"] == "active"
        }
        cls.values = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] == "minimum_kerb_weight"
            and row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
        ]
        cls.by_configuration = {
            row["configuration_code"]: row for row in cls.values
        }

    def test_attribute_is_active_minimum_specific_integer_weight(self) -> None:
        attribute = self.attributes["minimum_kerb_weight"]
        self.assertEqual(attribute["category"], "Weights")
        self.assertEqual(attribute["data_type"], "integer")
        self.assertEqual(attribute["unit"], "kg")
        self.assertEqual(attribute["status"], "active")
        self.assertIn("minimum", attribute["description"].lower())
        self.assertIn("kerb_weight", self.attributes)
        self.assertNotEqual(attribute["code"], "kerb_weight")

    def test_spec_and_master_rows_form_exact_contiguous_contract(self) -> None:
        self.assertEqual(self.spec.id_start, 1107)
        self.assertEqual(self.spec.attribute_code, "minimum_kerb_weight")
        self.assertEqual(len(self.spec.rows), 22)
        self.assertEqual(len(self.values), 22)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(1107, 1129)),
        )
        self.assertFalse(importer.verify_import(ROOT, self.spec).missing_rows)

    def test_every_active_jogger_configuration_has_exactly_one_value(self) -> None:
        self.assertEqual(set(self.by_configuration), self.configurations)
        self.assertEqual(len(self.by_configuration), len(self.values))

    def test_powertrain_and_seat_values_match_the_source_pairs(self) -> None:
        expected = {
            ("ecog120_manual", "5seat"): "1292",
            ("ecog120_manual", "7seat"): "1321",
            ("ecog120_automatic", "5seat"): "1326",
            ("ecog120_automatic", "7seat"): "1354",
            ("tce110_manual", "5seat"): "1193",
            ("tce110_manual", "7seat"): "1221",
            ("hybrid155_automatic", "5seat"): "1359",
            ("hybrid155_automatic", "7seat"): "1388",
        }
        for code, row in self.by_configuration.items():
            seat = "5seat" if "_5seat_" in code else "7seat"
            group = next(group for group, _ in expected if group in code)
            self.assertEqual(row["value"], expected[(group, seat)], code)
        self.assertEqual(
            Counter(row["value"] for row in self.values),
            Counter({
                "1292": 3,
                "1321": 3,
                "1326": 2,
                "1354": 2,
                "1193": 3,
                "1221": 3,
                "1359": 3,
                "1388": 3,
            }),
        )

    def test_minimum_qualifier_is_not_flattened_to_kerb_weight(self) -> None:
        all_values = csv_rows(MASTER / "configuration_attribute_values.csv")
        self.assertFalse(
            [
                row
                for row in all_values
                if row["source_code"] == SOURCE_CODE
                and row["observation_date"] == "2026-04-01"
                and row["attribute_code"] == "kerb_weight"
            ]
        )
        self.assertTrue(
            all("minimum kerb weight" in row["notes"] for row in self.values)
        )

    def test_registered_source_page_hash_and_text_contract(self) -> None:
        importer.verify_registered_sources(ROOT, self.spec, verify_text=False)
        self.assertEqual(self.spec.source_page, 6)
        self.assertEqual(self.spec.source_section, "MASY (kg)")
        self.assertEqual(
            {row.source_text for row in self.spec.rows},
            {
                "1292 / 1321",
                "1326 / 1354",
                "1193 / 1221",
                "1359 / 1388",
            },
        )
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)


if __name__ == "__main__":
    unittest.main()
