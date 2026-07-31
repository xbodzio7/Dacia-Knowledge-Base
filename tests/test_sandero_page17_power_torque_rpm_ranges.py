"""Verify the exact Sandero page 17 power- and torque-RPM range receipt."""

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
MASTER = ROOT / "data/master"
SPECS = ROOT / "data/imports/configuration_value_ranges"
PDF = ROOT / "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
SOURCE = "src_pl_sandero_brochure_20260202"
SHA = "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97"
SPEC_NAMES = {
    "sandero-page17-max-power-rpm-ranges-20260202.json",
    "sandero-page17-max-torque-rpm-ranges-20260202.json",
}
TARGETS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoPage17PowerTorqueRpmRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
        cls.selected = sorted([r for r in cls.ranges if 279 <= int(r["id"]) <= 298], key=lambda r: int(r["id"]))
        cls.specs = {name: json.loads((SPECS / name).read_text(encoding="utf-8")) for name in SPEC_NAMES}

    def test_two_specs_and_contiguous_exact_receipt(self) -> None:
        self.assertEqual(sum(len(s["rows"]) for s in self.specs.values()), 20)
        self.assertEqual([int(r["id"]) for r in self.selected], list(range(279, 299)))
        self.assertEqual(Counter(r["attribute_code"] for r in self.selected), Counter({"max_power_rpm": 11, "max_torque_rpm": 9}))

    def test_source_date_unit_and_closed_intervals(self) -> None:
        self.assertEqual({r["source_code"] for r in self.selected}, {SOURCE})
        self.assertEqual({r["observation_date"] for r in self.selected}, {"2026-02-02"})
        self.assertEqual({(r["lower_inclusive"], r["upper_inclusive"]) for r in self.selected}, {("true", "true")})
        for payload in self.specs.values():
            self.assertEqual(payload["attribute_contract"], {"data_type": "integer", "unit": "rpm", "status": "active"})
            self.assertEqual(payload["source_page"], 17)
            self.assertEqual(payload["source_section"], "SILNIKI")

    def test_power_ranges_preserve_exact_fuel_context(self) -> None:
        actual = Counter((r["fuel_type_code"], r["minimum_value"], r["maximum_value"]) for r in self.selected if r["attribute_code"] == "max_power_rpm")
        self.assertEqual(actual, Counter({("petrol", "5000", "5250"): 3, ("lpg", "4500", "5000"): 4, ("petrol", "4500", "5750"): 4}))

    def test_torque_ranges_preserve_missing_automatic_petrol_boundary(self) -> None:
        torque = [r for r in self.selected if r["attribute_code"] == "max_torque_rpm"]
        actual = Counter((r["fuel_type_code"], r["minimum_value"], r["maximum_value"]) for r in torque)
        self.assertEqual(actual, Counter({("petrol", "2900", "3500"): 3, ("lpg", "1750", "3750"): 4, ("petrol", "2000", "4000"): 2}))
        self.assertFalse(any(r["fuel_type_code"] == "petrol" and r["configuration_code"].endswith("ecog120_automatic") for r in torque))

    def test_exact_active_targets_are_linked_to_source(self) -> None:
        configurations = {r["code"]: r for r in rows(MASTER / "configurations.csv")}
        linked = {r["configuration_code"] for r in rows(MASTER / "source_configurations.csv") if r["source_code"] == SOURCE and r["relationship"] == "brochure_technical_data_for"}
        self.assertEqual({r["configuration_code"] for r in self.selected}, TARGETS)
        self.assertTrue(all(configurations[c]["status"] == "active" for c in TARGETS))
        self.assertTrue(TARGETS <= linked)

    def test_registered_pdf_and_exact_source_fragments(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SHA)
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 17))
        fragments = {r["source_text"] for payload in self.specs.values() for r in payload["rows"]}
        for fragment in fragments:
            self.assertIn(_compact_text(fragment), page)

    def test_reconciliation_non_import_boundaries_remain_absent(self) -> None:
        self.assertEqual(len(self.selected), 20)
        self.assertFalse(any(r["attribute_code"] not in {"max_power_rpm", "max_torque_rpm"} for r in self.selected))
        self.assertFalse(any(r["configuration_code"].endswith("ecog120_automatic") and r["attribute_code"] == "max_torque_rpm" and r["fuel_type_code"] == "petrol" for r in self.selected))


if __name__ == "__main__":
    unittest.main()
