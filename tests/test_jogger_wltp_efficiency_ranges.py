from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from tools.configuration_value_range_reporting import range_relation
from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPECS = ROOT / "data" / "imports" / "configuration_value_ranges"
SOURCE = "src_pl_jogger_price_my26_20260401"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"
SPEC_NAMES = {
    "jogger-page6-ecog120-manual-fuel-consumption-range-20260401.json",
    "jogger-page6-ecog120-manual-co2-emissions-range-20260401.json",
    "jogger-page6-ecog120-automatic-fuel-consumption-range-20260401.json",
    "jogger-page6-ecog120-automatic-co2-emissions-range-20260401.json",
    "jogger-page6-tce110-manual-fuel-consumption-range-20260401.json",
    "jogger-page6-tce110-manual-co2-emissions-range-20260401.json",
    "jogger-page6-hybrid155-automatic-fuel-consumption-range-20260401.json",
    "jogger-page6-hybrid155-automatic-co2-emissions-range-20260401.json",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerWltpEfficiencyRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = {
            row["code"]: row
            for row in rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_")
        }
        cls.range_rows = [
            row
            for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
            if 1 <= int(row["id"]) <= 64
        ]
        cls.scalar_rows = rows(MASTER / "configuration_attribute_values.csv")
        cls.specs = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in SPECS.glob("jogger-page6-*-range-20260401.json")
            if path.name in SPEC_NAMES
        }

    def test_eight_specs_materialize_contiguous_ids_1_to_64(self) -> None:
        self.assertEqual(set(self.specs), SPEC_NAMES)
        self.assertEqual(sum(len(spec["rows"]) for spec in self.specs.values()), 64)
        self.assertEqual(len(self.range_rows), 64)
        self.assertEqual({int(row["id"]) for row in self.range_rows}, set(range(1, 65)))
        self.assertEqual(len({row["code"] for row in self.range_rows}), 64)

    def test_exact_group_fuel_and_endpoint_denominator(self) -> None:
        expected = {
            ("Eco-G 120", "manual", "fuel_consumption_combined", "lpg", "7.3", "7.4"): 6,
            ("Eco-G 120", "manual", "fuel_consumption_combined", "petrol", "5.8", "5.9"): 6,
            ("Eco-G 120", "manual", "co2_emissions", "lpg", "119", "121"): 6,
            ("Eco-G 120", "manual", "co2_emissions", "petrol", "133", "134"): 6,
            ("Eco-G 120", "automatic", "fuel_consumption_combined", "lpg", "7.5", "7.6"): 4,
            ("Eco-G 120", "automatic", "fuel_consumption_combined", "petrol", "6", "6.1"): 4,
            ("Eco-G 120", "automatic", "co2_emissions", "lpg", "121", "123"): 4,
            ("Eco-G 120", "automatic", "co2_emissions", "petrol", "137", "138"): 4,
            ("TCe 110", "manual", "fuel_consumption_combined", "petrol", "5.7", "5.8"): 6,
            ("TCe 110", "manual", "co2_emissions", "petrol", "129", "131"): 6,
            ("hybrid 155", "automatic", "fuel_consumption_combined", "petrol", "4.5", "4.6"): 6,
            ("hybrid 155", "automatic", "co2_emissions", "petrol", "103", "104"): 6,
        }
        actual: Counter[tuple[str, str, str, str, str, str]] = Counter()
        for row in self.range_rows:
            configuration = self.configurations[row["configuration_code"]]
            actual[
                (
                    configuration["powertrain_label"],
                    configuration["transmission_type"],
                    row["attribute_code"],
                    row["fuel_type_code"],
                    row["minimum_value"],
                    row["maximum_value"],
                )
            ] += 1
        self.assertEqual(actual, Counter(expected))

    def test_all_22_active_configurations_receive_exact_slots(self) -> None:
        by_configuration: defaultdict[str, set[tuple[str, str]]] = defaultdict(set)
        for row in self.range_rows:
            by_configuration[row["configuration_code"]].add(
                (row["attribute_code"], row["fuel_type_code"])
            )
        self.assertEqual(set(by_configuration), set(self.configurations))
        for code, configuration in self.configurations.items():
            if configuration["powertrain_label"] == "Eco-G 120":
                expected = {
                    ("fuel_consumption_combined", "lpg"),
                    ("fuel_consumption_combined", "petrol"),
                    ("co2_emissions", "lpg"),
                    ("co2_emissions", "petrol"),
                }
            else:
                expected = {
                    ("fuel_consumption_combined", "petrol"),
                    ("co2_emissions", "petrol"),
                }
            self.assertEqual(by_configuration[code], expected)

    def test_every_range_is_closed_dated_and_source_backed(self) -> None:
        self.assertTrue(all(row["lower_inclusive"] == "true" for row in self.range_rows))
        self.assertTrue(all(row["upper_inclusive"] == "true" for row in self.range_rows))
        self.assertEqual({row["observation_date"] for row in self.range_rows}, {"2026-04-01"})
        self.assertEqual({row["source_code"] for row in self.range_rows}, {SOURCE})
        self.assertTrue(all(row["notes"].startswith("Source page 6, section OSIĄGI:") for row in self.range_rows))

    def test_no_scalar_range_semantic_collision_exists(self) -> None:
        scalar = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
                row["observation_date"],
            )
            for row in self.scalar_rows
        }
        ranged = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
                row["observation_date"],
            )
            for row in self.range_rows
        }
        self.assertFalse(scalar & ranged)
        self.assertEqual(len(self.scalar_rows), 1204)

    def test_registered_pdf_hash_and_unique_source_texts_are_verified(self) -> None:
        self.assertTrue(PDF.is_file())
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        if shutil.which("pdftotext") is None:
            return
        candidates = extract_page_candidates(PDF, 6)
        compact_pages = [_compact_text(text) for _, text in candidates]
        source_texts = {
            row["source_text"]
            for spec in self.specs.values()
            for row in spec["rows"]
        }
        self.assertEqual(len(source_texts), 12)
        for text in source_texts:
            compact = _compact_text(text)
            self.assertTrue(any(compact in page for page in compact_pages), text)

    def test_homogeneous_group_ranges_compare_as_identical(self) -> None:
        grouped: defaultdict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
        for row in self.range_rows:
            configuration = self.configurations[row["configuration_code"]]
            grouped[
                (
                    configuration["powertrain_label"],
                    configuration["transmission_type"],
                    row["attribute_code"],
                    row["fuel_type_code"],
                )
            ].append(row)
        for group in grouped.values():
            left = {
                "minimum_value": group[0]["minimum_value"],
                "maximum_value": group[0]["maximum_value"],
                "lower_inclusive": True,
                "upper_inclusive": True,
            }
            for row in group[1:]:
                right = {
                    "minimum_value": row["minimum_value"],
                    "maximum_value": row["maximum_value"],
                    "lower_inclusive": True,
                    "upper_inclusive": True,
                }
                self.assertEqual(range_relation(left, right), "identical")

    def test_state_exposes_scalar_and_range_denominators(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        baseline = state["baseline"]
        self.assertEqual(baseline["tests"], 565)
        self.assertEqual(baseline["rows"], 5155)
        self.assertEqual(baseline["configuration_values"], 1204)
        self.assertEqual(baseline["configuration_import_specs"], 71)
        self.assertEqual(baseline["configuration_value_ranges"], 144)
        self.assertEqual(baseline["configuration_range_import_specs"], 19)


if __name__ == "__main__":
    unittest.main()
