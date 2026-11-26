from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
POWER_SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybridg150-max-power-rpm-20251210.json"
TORQUE_SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybridg150-max-torque-rpm-20251210.json"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
BROCHURE_SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
TARGETS = {
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20HybridG150RpmConflictObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.power_spec = json.loads(POWER_SPEC.read_text(encoding="utf-8"))
        cls.torque_spec = json.loads(TORQUE_SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_specs_preserve_exact_source_receipts(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.power_spec["id_start"], 3302)
        self.assertEqual(self.torque_spec["id_start"], 3305)
        self.assertEqual(self.power_spec["attribute_code"], "max_power_rpm")
        self.assertEqual(self.torque_spec["attribute_code"], "max_torque_rpm")
        self.assertEqual(self.power_spec["attribute_contract"], {"data_type": "integer", "unit": "rpm", "status": "active"})
        self.assertEqual(self.torque_spec["attribute_contract"], {"data_type": "integer", "unit": "rpm", "status": "active"})
        self.assertEqual({row["source_text"] for row in self.power_spec["rows"]}, {"103 (140 KM) przy 4500 obr./min – silnik spalinowy"})
        self.assertEqual({row["source_text"] for row in self.torque_spec["rows"]}, {"230 przy 4000 (silnik spalinowy)"})

    def test_six_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["configuration_code"] in TARGETS
                and row["attribute_code"] in {"max_power_rpm", "max_torque_rpm"}
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3302, 3308)))
        self.assertEqual(Counter((row["attribute_code"], row["value"]) for row in selected), Counter({("max_power_rpm", "4500"): 3, ("max_torque_rpm", "4000"): 3}))
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})

    def test_all_three_active_targets_are_covered_once_per_attribute(self) -> None:
        for spec in (self.power_spec, self.torque_spec):
            configurations = [row["configuration_code"] for row in spec["rows"]]
            self.assertEqual(set(configurations), TARGETS)
            self.assertEqual(len(configurations), len(set(configurations)))
        active = {row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}
        self.assertTrue(TARGETS <= active)

    def test_later_price_source_observations_remain_unchanged(self) -> None:
        later = [
            row for row in self.values
            if row["source_code"] == PRICE_SOURCE
            and row["configuration_code"] in TARGETS
            and row["attribute_code"] in {"max_power_rpm", "max_torque_rpm"}
        ]
        self.assertEqual({int(row["id"]) for row in later if row["attribute_code"] == "max_power_rpm"}, {1504, 1505, 1506})
        self.assertEqual({int(row["id"]) for row in later if row["attribute_code"] == "max_torque_rpm"}, {1518, 1519, 1520})
        self.assertEqual(Counter((row["attribute_code"], row["value"]) for row in later), Counter({("max_power_rpm", "5000"): 3, ("max_torque_rpm", "1750"): 3}))
        self.assertEqual({row["observation_date"] for row in later}, {"2026-07-03"})

    def test_conflicting_sources_coexist_without_natural_key_collision(self) -> None:
        selected = [
            row for row in self.values
            if row["configuration_code"] in TARGETS
            and row["attribute_code"] in {"max_power_rpm", "max_torque_rpm"}
            and row["source_code"] in {BROCHURE_SOURCE, PRICE_SOURCE}
        ]
        self.assertEqual(len(selected), 12)
        keys = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"], row["source_code"])
            for row in selected
        }
        self.assertEqual(len(keys), 12)

    def test_motor_specific_1630_rpm_context_is_not_imported(self) -> None:
        brochure_rows = [row for row in self.values if row["source_code"] == BROCHURE_SOURCE and row["configuration_code"] in TARGETS]
        self.assertFalse(any(row["value"] == "1630" and row["attribute_code"] in {"max_power_rpm", "max_torque_rpm"} for row in brochure_rows))

    def test_targets_have_registered_source_relationship(self) -> None:
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(TARGETS <= linked)

    def test_page_text_contains_both_combustion_engine_fragments(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("103 (140 KM) przy 4500 obr./min – silnik spalinowy"), page_text)
        self.assertIn(_compact_text("230 przy 4000 (silnik spalinowy)"), page_text)


if __name__ == "__main__":
    unittest.main()
