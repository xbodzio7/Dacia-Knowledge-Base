from __future__ import annotations

import csv
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MASTER = ROOT / "data" / "master"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_values"
TYPE_SPEC = SPEC_DIR / "jogger-page6-gearbox-type-20260401.json"
COUNT_SPEC = SPEC_DIR / "jogger-page6-gear-count-20260401.json"
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerGearboxReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.type_spec = importer.load_spec(TYPE_SPEC)
        cls.count_spec = importer.load_spec(COUNT_SPEC)
        cls.values = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
            and row["attribute_code"] in {"gearbox_type", "gear_count"}
        ]
        cls.by_key = {
            (row["configuration_code"], row["attribute_code"]): row
            for row in cls.values
        }

    def test_two_specs_form_exact_contiguous_38_row_contract(self) -> None:
        self.assertEqual(self.type_spec.id_start, 1069)
        self.assertEqual(self.count_spec.id_start, 1091)
        self.assertEqual(len(self.type_spec.rows), 22)
        self.assertEqual(len(self.count_spec.rows), 16)
        self.assertEqual(len(self.values), 38)
        self.assertEqual([int(row["id"]) for row in self.values], list(range(1069, 1107)))
        self.assertFalse(importer.verify_import(ROOT, self.type_spec).missing_rows)
        self.assertFalse(importer.verify_import(ROOT, self.count_spec).missing_rows)

    def test_gearbox_type_distribution_matches_four_source_groups(self) -> None:
        type_rows = [row for row in self.values if row["attribute_code"] == "gearbox_type"]
        self.assertEqual(
            Counter(row["value"] for row in type_rows),
            Counter({"manual": 12, "dct": 4, "hybrid": 6}),
        )
        self.assertEqual(len({row["configuration_code"] for row in type_rows}), 22)

    def test_six_gear_count_is_source_stated_only_for_manual_and_dct(self) -> None:
        count_rows = [row for row in self.values if row["attribute_code"] == "gear_count"]
        self.assertEqual(len(count_rows), 16)
        self.assertEqual({row["value"] for row in count_rows}, {"6"})
        self.assertTrue(all("_hybrid155_" not in row["configuration_code"] for row in count_rows))
        hybrid_codes = {
            row["configuration_code"]
            for row in self.values
            if row["attribute_code"] == "gearbox_type" and row["value"] == "hybrid"
        }
        self.assertEqual(len(hybrid_codes), 6)
        for code in hybrid_codes:
            self.assertNotIn((code, "gear_count"), self.by_key)

    def test_master_gearbox_entities_preserve_exact_existing_contracts(self) -> None:
        gearboxes = {row["code"]: row for row in csv_rows(MASTER / "gearboxes.csv")}
        self.assertEqual(
            (gearboxes["mt6"]["type"], gearboxes["mt6"]["gears"], gearboxes["mt6"]["status"]),
            ("manual", "6", "current"),
        )
        self.assertEqual(
            (gearboxes["edc6"]["type"], gearboxes["edc6"]["gears"], gearboxes["edc6"]["status"]),
            ("dct", "6", "current"),
        )
        self.assertEqual(
            (gearboxes["e_dht155"]["type"], gearboxes["e_dht155"]["gears"], gearboxes["e_dht155"]["status"]),
            ("hybrid", "", "current"),
        )

    def test_jogger_model_associations_close_old_hybrid_and_open_my26_entities(self) -> None:
        associations = {
            row["gearbox_code"]: row
            for row in csv_rows(MASTER / "model_gearboxes.csv")
            if row["model_code"] == "jogger"
        }
        self.assertEqual(set(associations), {"mt6", "e_dht140", "edc6", "e_dht155"})
        self.assertEqual((associations["mt6"]["available_from"], associations["mt6"]["available_to"]), ("2021", ""))
        self.assertEqual((associations["e_dht140"]["available_from"], associations["e_dht140"]["available_to"]), ("2023", "2025"))
        self.assertEqual((associations["edc6"]["available_from"], associations["edc6"]["available_to"]), ("2026", ""))
        self.assertEqual((associations["e_dht155"]["available_from"], associations["e_dht155"]["available_to"]), ("2026", ""))

    def test_registered_source_hash_and_declared_page_text_contract(self) -> None:
        for spec in (self.type_spec, self.count_spec):
            with self.subTest(spec=spec.path.name):
                importer.verify_registered_sources(ROOT, spec, verify_text=False)
                self.assertEqual(spec.source_page, 6)
                self.assertEqual(spec.source_section, "SILNIKI")
        self.assertEqual(
            {row.source_text for row in self.type_spec.rows},
            {"manualna", "automatyczna dwusprzęgłowa", "automatyczna Multi-mode"},
        )
        self.assertEqual({row.source_text for row in self.count_spec.rows}, {"6-biegowa"})


if __name__ == "__main__":
    unittest.main()
