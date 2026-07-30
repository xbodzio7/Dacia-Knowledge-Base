"""Verify the Jogger page 19 acceleration import, live contracts and baseline compatibility."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from decimal import Decimal
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-acceleration-0-100-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
BROCHURE_SOURCE = "src_pl_jogger_brochure_20251217"
PRICE_SOURCE = "src_pl_jogger_price_my26_20260401"
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED = {
    ("jogger_expression_5seat_tce110_manual", "petrol"): "10.5",
    ("jogger_extreme_5seat_tce110_manual", "petrol"): "10.5",
    ("jogger_journey_5seat_tce110_manual", "petrol"): "10.5",
    ("jogger_essential_5seat_ecog120_manual", "lpg"): "10.9",
    ("jogger_essential_5seat_ecog120_manual", "petrol"): "11.9",
    ("jogger_expression_5seat_ecog120_manual", "lpg"): "10.9",
    ("jogger_expression_5seat_ecog120_manual", "petrol"): "11.9",
    ("jogger_extreme_5seat_ecog120_manual", "lpg"): "10.9",
    ("jogger_extreme_5seat_ecog120_manual", "petrol"): "11.9",
    ("jogger_extreme_5seat_ecog120_automatic", "lpg"): "10.4",
    ("jogger_extreme_5seat_ecog120_automatic", "petrol"): "11.4",
    ("jogger_journey_5seat_ecog120_automatic", "lpg"): "10.4",
    ("jogger_journey_5seat_ecog120_automatic", "petrol"): "11.4",
    ("jogger_expression_7seat_tce110_manual", "petrol"): "11.2",
    ("jogger_extreme_7seat_tce110_manual", "petrol"): "11.2",
    ("jogger_journey_7seat_tce110_manual", "petrol"): "11.2",
    ("jogger_essential_7seat_ecog120_manual", "lpg"): "11",
    ("jogger_essential_7seat_ecog120_manual", "petrol"): "12",
    ("jogger_expression_7seat_ecog120_manual", "lpg"): "11",
    ("jogger_expression_7seat_ecog120_manual", "petrol"): "12",
    ("jogger_extreme_7seat_ecog120_manual", "lpg"): "11",
    ("jogger_extreme_7seat_ecog120_manual", "petrol"): "12",
    ("jogger_extreme_7seat_ecog120_automatic", "lpg"): "10.7",
    ("jogger_extreme_7seat_ecog120_automatic", "petrol"): "11.7",
    ("jogger_journey_7seat_ecog120_automatic", "lpg"): "10.7",
    ("jogger_journey_7seat_ecog120_automatic", "petrol"): "11.7",
}
TARGETS = {configuration for configuration, _fuel in EXPECTED}
TCE_EXPECTED = {
    configuration: value
    for (configuration, fuel), value in EXPECTED.items()
    if fuel == "petrol" and "_tce110_" in configuration
}
ECOG_EXPECTED = {
    (configuration, fuel): value
    for (configuration, fuel), value in EXPECTED.items()
    if "_ecog120_" in configuration
}
HYBRID_TARGETS = {
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def decimal_map(values: dict) -> dict:
    return {key: Decimal(value) for key, value in values.items()}


class JoggerPage19AccelerationSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3336)
        self.assertEqual(self.spec["attribute_code"], "acceleration_0_100")
        self.assertEqual(
            self.spec["attribute_contract"],
            {"data_type": "decimal", "unit": "s", "status": "active"},
        )
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], "Wersja")

    def test_exact_26_configuration_fuel_targets_are_in_spec_once(self) -> None:
        actual = {
            (row["configuration_code"], row["fuel_type_code"]): row["value"]
            for row in self.spec["rows"]
        }
        self.assertEqual(len(self.spec["rows"]), 26)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(actual), len(self.spec["rows"]))
        self.assertEqual(
            {row["source_code"] for row in self.spec["rows"]},
            {BROCHURE_SOURCE},
        )

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row
                for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"] == "acceleration_0_100"
                and (row["configuration_code"], row["fuel_type_code"]) in EXPECTED
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual(
            [int(row["id"]) for row in selected],
            list(range(3336, 3362)),
        )
        self.assertEqual(
            {
                (row["configuration_code"], row["fuel_type_code"]): row["value"]
                for row in selected
            },
            EXPECTED,
        )
        self.assertEqual(
            {row["observation_date"] for row in selected},
            {"2025-12-17"},
        )

    def test_later_official_source_observations_coexist_unchanged(self) -> None:
        fuel_scoped = [
            row
            for row in self.values
            if row["source_code"] == PRICE_SOURCE
            and row["attribute_code"] == "acceleration_0_100"
            and (row["configuration_code"], row["fuel_type_code"]) in ECOG_EXPECTED
        ]
        self.assertEqual(len(fuel_scoped), 20)
        self.assertEqual(
            {
                (row["configuration_code"], row["fuel_type_code"]): Decimal(row["value"])
                for row in fuel_scoped
            },
            decimal_map(ECOG_EXPECTED),
        )

        tce_unscoped = [
            row
            for row in self.values
            if row["source_code"] == PRICE_SOURCE
            and row["attribute_code"] == "acceleration_0_100"
            and row["configuration_code"] in TCE_EXPECTED
            and row["fuel_type_code"] == ""
        ]
        self.assertEqual(len(tce_unscoped), 6)
        self.assertEqual(
            {
                row["configuration_code"]: Decimal(row["value"])
                for row in tce_unscoped
            },
            decimal_map(TCE_EXPECTED),
        )
        self.assertEqual(
            {row["observation_date"] for row in fuel_scoped + tce_unscoped},
            {"2026-04-01"},
        )

    def test_six_existing_hybrid_brochure_observations_remain_unchanged(self) -> None:
        selected = [
            row
            for row in self.values
            if row["source_code"] == BROCHURE_SOURCE
            and row["attribute_code"] == "acceleration_0_100"
            and row["configuration_code"] in HYBRID_TARGETS
        ]
        self.assertEqual(len(selected), 6)
        self.assertEqual({row["fuel_type_code"] for row in selected}, {""})
        five = {
            row["value"]
            for row in selected
            if "_5seat_" in row["configuration_code"]
        }
        seven = {
            row["value"]
            for row in selected
            if "_7seat_" in row["configuration_code"]
        }
        self.assertEqual(five, {"8.9"})
        self.assertEqual(seven, {"9"})

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
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
        self.assertTrue(TARGETS.isdisjoint(HYBRID_TARGETS))

    def test_page_text_contains_both_exact_acceleration_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(
            _compact_text(text)
            for _, text in extract_page_candidates(PDF, 19)
        )
        self.assertIn(
            _compact_text("Wersja 5-miejscowa 10,5 10,9 11,9 10,4 11,4 8,9"),
            page_text,
        )
        self.assertIn(
            _compact_text("Wersja 7-miejscowa 11,2 11 12 10,7 11,7 9"),
            page_text,
        )


if __name__ == "__main__":
    unittest.main()
