from __future__ import annotations

import csv
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "configuration_values" / "jogger-page6-injection-type-20260401.json"
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerInjectionTypeImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = importer.load_spec(SPEC)
        cls.values = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] == "injection_type"
            and row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
        ]
        cls.by_key = {
            (row["configuration_code"], row["fuel_type_code"]): row
            for row in cls.values
        }

    def test_spec_and_master_rows_form_exact_contiguous_contract(self) -> None:
        self.assertEqual(self.spec.id_start, 1037)
        self.assertEqual(self.spec.attribute_code, "injection_type")
        self.assertEqual(len(self.spec.rows), 32)
        self.assertEqual(len(self.values), 32)
        self.assertEqual([int(row["id"]) for row in self.values], list(range(1037, 1069)))
        self.assertFalse(importer.verify_import(ROOT, self.spec).missing_rows)

    def test_group_and_fuel_context_counts_match_selection(self) -> None:
        counts = Counter((row["value"], row["fuel_type_code"]) for row in self.values)
        self.assertEqual(
            counts,
            Counter({
                ("direct_injection", "petrol"): 10,
                ("port_injection", "lpg"): 10,
                ("direct_injection", ""): 6,
                ("multi_point_injection", ""): 6,
            }),
        )
        self.assertEqual(len({row["configuration_code"] for row in self.values}), 22)

    def test_every_ecog_configuration_preserves_both_fuel_semantics(self) -> None:
        eco_g_codes = {
            row["configuration_code"]
            for row in self.values
            if "_ecog120_" in row["configuration_code"]
        }
        self.assertEqual(len(eco_g_codes), 10)
        for code in eco_g_codes:
            with self.subTest(configuration=code):
                self.assertEqual(self.by_key[(code, "petrol")]["value"], "direct_injection")
                self.assertEqual(self.by_key[(code, "lpg")]["value"], "port_injection")

    def test_tce_and_hybrid_mappings_use_existing_enum_values(self) -> None:
        enum_values = {
            row["code"]
            for row in csv_rows(MASTER / "enums" / "injection_types.csv")
            if row["status"] == "active"
        }
        self.assertTrue({row["value"] for row in self.values} <= enum_values)
        for row in self.values:
            code = row["configuration_code"]
            if code.endswith("_tce110_manual"):
                self.assertEqual((row["value"], row["fuel_type_code"]), ("direct_injection", ""))
            if code.endswith("_hybrid155_automatic"):
                self.assertEqual((row["value"], row["fuel_type_code"]), ("multi_point_injection", ""))

    def test_registered_source_page_and_exact_text_verify(self) -> None:
        importer.verify_registered_sources(ROOT, self.spec, verify_text=True)
        self.assertEqual(self.spec.source_page, 6)
        self.assertEqual(self.spec.source_section, "SILNIKI")
        self.assertEqual(
            {row.source_text for row in self.spec.rows},
            {"benzyna bezpośredni/LPG pośredni", "bezpośredni", "wielopunktowy"},
        )


if __name__ == "__main__":
    unittest.main()
