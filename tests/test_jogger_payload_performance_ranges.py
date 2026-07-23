from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPECS = ROOT / "data" / "imports" / "configuration_value_ranges"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
SOURCE = "src_pl_jogger_price_my26_20260401"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"
SELECTED_NAMES = {
    "jogger-page6-ecog120-manual-maximum-payload-range-20260401.json",
    "jogger-page6-ecog120-automatic-maximum-payload-range-20260401.json",
    "jogger-page6-tce110-manual-maximum-payload-range-20260401.json",
    "jogger-page6-hybrid155-automatic-maximum-payload-range-20260401.json",
    "jogger-page6-hybrid155-automatic-acceleration-0-100-range-20260401.json",
    "jogger-page6-ecog120-manual-max-power-rpm-range-20260401.json",
    "jogger-page6-ecog120-manual-max-torque-rpm-range-20260401.json",
    "jogger-page6-ecog120-automatic-max-power-rpm-range-20260401.json",
    "jogger-page6-ecog120-automatic-max-torque-rpm-range-20260401.json",
    "jogger-page6-tce110-manual-max-power-rpm-range-20260401.json",
    "jogger-page6-tce110-manual-max-torque-rpm-range-20260401.json",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPayloadPerformanceRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = {
            row["code"]: row
            for row in read_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_")
        }
        cls.ranges = read_rows(MASTER / "configuration_attribute_value_ranges.csv")
        cls.selected = [row for row in cls.ranges if 65 <= int(row["id"]) <= 144]
        cls.scalars = read_rows(MASTER / "configuration_attribute_values.csv")
        cls.specs = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in SPECS.glob("jogger-page6-*-range-20260401.json")
            if path.name in SELECTED_NAMES
        }

    def test_eleven_specs_materialize_contiguous_ids_65_to_144(self) -> None:
        self.assertEqual(set(self.specs), SELECTED_NAMES)
        self.assertEqual(sum(len(spec["rows"]) for spec in self.specs.values()), 80)
        self.assertEqual(len(self.selected), 80)
        self.assertEqual({int(row["id"]) for row in self.selected}, set(range(65, 145)))

    def test_payload_denominator_is_seat_qualified(self) -> None:
        expected = {
            ("Eco-G 120", "manual", "5", "453", "473"): 3,
            ("Eco-G 120", "manual", "7", "598", "619"): 3,
            ("Eco-G 120", "automatic", "5", "450", "459"): 2,
            ("Eco-G 120", "automatic", "7", "596", "606"): 2,
            ("TCe 110", "manual", "5", "455", "492"): 3,
            ("TCe 110", "manual", "7", "594", "634"): 3,
            ("hybrid 155", "automatic", "5", "457", "471"): 3,
            ("hybrid 155", "automatic", "7", "595", "612"): 3,
        }
        actual: Counter[tuple[str, str, str, str, str]] = Counter()
        for row in self.selected:
            if row["attribute_code"] != "maximum_payload":
                continue
            configuration = self.configurations[row["configuration_code"]]
            seats = "7" if "_7seat_" in row["configuration_code"] else "5"
            actual[(configuration["powertrain_label"], configuration["transmission_type"], seats, row["minimum_value"], row["maximum_value"])] += 1
        self.assertEqual(actual, Counter(expected))

    def test_hybrid_acceleration_range_is_preserved_without_endpoint_inference(self) -> None:
        rows = [row for row in self.selected if row["attribute_code"] == "acceleration_0_100"]
        self.assertEqual(len(rows), 6)
        self.assertEqual({(row["minimum_value"], row["maximum_value"], row["fuel_type_code"]) for row in rows}, {("8.9", "9", "")})
        self.assertEqual({row["configuration_code"] for row in rows}, {code for code, item in self.configurations.items() if item["powertrain_label"] == "hybrid 155"})

    def test_engine_speed_ranges_preserve_group_and_fuel_contexts(self) -> None:
        expected = {
            ("Eco-G 120", "manual", "max_power_rpm", "lpg", "4500", "5000"): 6,
            ("Eco-G 120", "manual", "max_power_rpm", "petrol", "4500", "5750"): 6,
            ("Eco-G 120", "manual", "max_torque_rpm", "lpg", "1750", "3750"): 6,
            ("Eco-G 120", "manual", "max_torque_rpm", "petrol", "2000", "4000"): 6,
            ("Eco-G 120", "automatic", "max_power_rpm", "lpg", "4500", "5000"): 4,
            ("Eco-G 120", "automatic", "max_power_rpm", "petrol", "4500", "5750"): 4,
            ("Eco-G 120", "automatic", "max_torque_rpm", "lpg", "1750", "3750"): 4,
            ("Eco-G 120", "automatic", "max_torque_rpm", "petrol", "2000", "4000"): 4,
            ("TCe 110", "manual", "max_power_rpm", "petrol", "5000", "5250"): 6,
            ("TCe 110", "manual", "max_torque_rpm", "petrol", "2900", "3500"): 6,
        }
        actual: Counter[tuple[str, str, str, str, str, str]] = Counter()
        for row in self.selected:
            if row["attribute_code"] not in {"max_power_rpm", "max_torque_rpm"}:
                continue
            configuration = self.configurations[row["configuration_code"]]
            actual[(configuration["powertrain_label"], configuration["transmission_type"], row["attribute_code"], row["fuel_type_code"], row["minimum_value"], row["maximum_value"])] += 1
        self.assertEqual(actual, Counter(expected))

    def test_all_selected_ranges_are_closed_dated_and_source_backed(self) -> None:
        self.assertTrue(all(row["lower_inclusive"] == "true" for row in self.selected))
        self.assertTrue(all(row["upper_inclusive"] == "true" for row in self.selected))
        self.assertEqual({row["observation_date"] for row in self.selected}, {"2026-04-01"})
        self.assertEqual({row["source_code"] for row in self.selected}, {SOURCE})
        self.assertEqual({row["attribute_code"] for row in self.selected}, {"maximum_payload", "acceleration_0_100", "max_power_rpm", "max_torque_rpm"})

    def test_prior_ranges_and_scalar_values_remain_unchanged(self) -> None:
        self.assertEqual(len(self.ranges), 158)
        self.assertEqual(len([row for row in self.ranges if int(row["id"]) <= 64]), 64)
        self.assertEqual(len(self.scalars), 1756)
        scalar_keys = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]) for row in self.scalars}
        selected_keys = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]) for row in self.selected}
        self.assertFalse(scalar_keys & selected_keys)

    def test_registered_pdf_hash_and_source_texts_are_verified(self) -> None:
        self.assertTrue(PDF.is_file())
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        if shutil.which("pdftotext") is None:
            return
        pages = [_compact_text(text) for _, text in extract_page_candidates(PDF, 6)]
        source_texts = {row["source_text"] for spec in self.specs.values() for row in spec["rows"]}
        self.assertEqual(len(source_texts), 11)
        for text in source_texts:
            compact = _compact_text(text)
            self.assertTrue(any(compact in page for page in pages), text)

    def test_state_exposes_updated_range_denominators(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        baseline = state["baseline"]
        self.assertEqual(baseline["tests"], 709)
        self.assertEqual(baseline["rows"], 7669)
        self.assertEqual(baseline["configuration_values"], 1756)
        self.assertEqual(baseline["configuration_value_ranges"], 158)
        self.assertEqual(baseline["configuration_range_import_specs"], 20)


if __name__ == "__main__":
    unittest.main()
