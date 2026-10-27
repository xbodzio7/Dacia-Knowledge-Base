from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybrid-battery-capacity-source-stated-20251210.json"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
BROCHURE_SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
TARGETS = {
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}
HYBRID155_TARGETS = {
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20BatteryCapacityConflictObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_preserves_source_stated_decimal_capacity_contract(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3325)
        self.assertEqual(
            self.spec["attribute_code"],
            "hybrid_battery_capacity_source_stated",
        )
        self.assertEqual(
            self.spec["attribute_contract"],
            {"data_type": "decimal", "unit": "kWh", "status": "active"},
        )
        self.assertEqual(self.spec["source_page"], 20)
        self.assertEqual(self.spec["source_section"], "BATERIA")

    def test_exact_eleven_48v_targets_are_in_spec_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.spec["rows"]]
        self.assertEqual(len(configurations), 11)
        self.assertEqual(set(configurations), TARGETS)
        self.assertEqual(len(configurations), len(set(configurations)))
        self.assertEqual({row["value"] for row in self.spec["rows"]}, {"0.84"})
        self.assertEqual(
            {row["source_text"] for row in self.spec["rows"]},
            {"48 V / 0,84 kWh"},
        )

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row
                for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"]
                == "hybrid_battery_capacity_source_stated"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual(
            [int(row["id"]) for row in selected],
            list(range(3325, 3336)),
        )
        self.assertEqual({row["value"] for row in selected}, {"0.84"})
        self.assertEqual(
            {row["observation_date"] for row in selected},
            {"2025-12-10"},
        )

    def test_later_price_source_precision_rows_remain_unchanged(self) -> None:
        later = sorted(
            [
                row
                for row in self.values
                if row["source_code"] == PRICE_SOURCE
                and row["attribute_code"]
                == "hybrid_battery_capacity_source_stated"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual(
            [int(row["id"]) for row in later],
            list(range(1447, 1458)),
        )
        self.assertEqual({row["value"] for row in later}, {"0.839"})
        self.assertEqual(
            {row["observation_date"] for row in later},
            {"2026-07-03"},
        )

    def test_both_registered_capacity_observations_coexist(self) -> None:
        selected = [
            row
            for row in self.values
            if row["attribute_code"]
            == "hybrid_battery_capacity_source_stated"
            and row["configuration_code"] in TARGETS
            and row["source_code"] in {BROCHURE_SOURCE, PRICE_SOURCE}
        ]
        self.assertEqual(len(selected), 22)
        by_configuration: dict[str, set[tuple[str, str]]] = {}
        for row in selected:
            by_configuration.setdefault(
                row["configuration_code"],
                set(),
            ).add((row["source_code"], row["value"]))
        expected = {
            (BROCHURE_SOURCE, "0.84"),
            (PRICE_SOURCE, "0.839"),
        }
        self.assertEqual(set(by_configuration), TARGETS)
        self.assertTrue(
            all(values == expected for values in by_configuration.values())
        )

    def test_hybrid155_capacity_context_remains_price_source_only(self) -> None:
        selected = sorted(
            [
                row
                for row in self.values
                if row["attribute_code"]
                == "hybrid_battery_capacity_source_stated"
                and row["configuration_code"] in HYBRID155_TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], [1458, 1459, 1460])
        self.assertEqual({row["value"] for row in selected}, {"1.4"})
        self.assertEqual({row["source_code"] for row in selected}, {PRICE_SOURCE})
        self.assertEqual(
            {row["observation_date"] for row in selected},
            {"2026-07-03"},
        )

    def test_all_targets_are_active_and_linked_to_source(self) -> None:
        active = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active"
        }
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE
            and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(TARGETS <= active)
        self.assertTrue(TARGETS <= linked)
        self.assertTrue(TARGETS.isdisjoint(HYBRID155_TARGETS))

    def test_page_text_contains_exact_48v_capacity_cell(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(
            _compact_text(text)
            for _, text in extract_page_candidates(PDF, 20)
        )
        self.assertIn(_compact_text("48 V / 0,84 kWh"), page_text)


if __name__ == "__main__":
    unittest.main()
