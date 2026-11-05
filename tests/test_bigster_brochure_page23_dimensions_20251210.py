from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_bigster_brochure_20251210"
SOURCE_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_values"
MASTER = ROOT / "data" / "master"

EXPECTED = {
    "overall_width": "1813",
    "overall_width_with_mirrors": "2069",
    "front_track": "1580",
    "rear_track": "1565",
    "wheelbase": "2702",
    "front_overhang": "854",
    "rear_overhang": "1014",
}
EXPECTED_ID_STARTS = {
    "overall_width": 8290,
    "overall_width_with_mirrors": 8304,
    "front_track": 8318,
    "rear_track": 8332,
    "wheelbase": 8346,
    "front_overhang": 8360,
    "rear_overhang": 8374,
    "ground_clearance": 8388,
    "overall_height": 8402,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterBrochurePage23DimensionsTests(unittest.TestCase):
    def test_exact_historical_dimensions_scope_values_and_provenance(self) -> None:
        all_page23_specs = sorted(SPEC_DIR.glob("bigster-page23-*-20251210.json"))
        specs = [
            path for path in all_page23_specs
            if json.loads(path.read_text(encoding="utf-8"))["attribute_code"]
            in EXPECTED_ID_STARTS
        ]
        self.assertEqual(len(specs), 9)
        spec_data = [json.loads(path.read_text(encoding="utf-8")) for path in specs]
        by_attribute = {spec["attribute_code"]: spec for spec in spec_data}
        self.assertEqual(set(by_attribute), set(EXPECTED_ID_STARTS))

        configurations = read_csv(MASTER / "configurations.csv")
        active = {row["code"] for row in configurations if row["status"] == "active"}
        source_links = read_csv(MASTER / "source_configurations.csv")
        linked = {
            row["configuration_code"]
            for row in source_links
            if row["source_code"] == SOURCE
            and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertEqual(len(linked), 14)
        self.assertTrue(linked <= active)

        expected = {}
        expected_notes = {}
        for attribute, spec in by_attribute.items():
            self.assertEqual(spec["kind"], "configuration_attribute_values")
            self.assertEqual(spec["attribute_code"], attribute)
            self.assertEqual(spec["observation_date"], "2025-12-10")
            self.assertEqual(spec["source_page"], 23)
            self.assertEqual(spec["source_section"], "WYMIARY")
            self.assertEqual(spec["attribute_contract"], {
                "data_type": "integer", "unit": "mm", "status": "active"
            })
            self.assertEqual(spec["id_start"], EXPECTED_ID_STARTS[attribute])
            self.assertEqual(len(spec["rows"]), 14)
            for row in spec["rows"]:
                config = row["configuration_code"]
                self.assertIn(config, linked)
                self.assertEqual(row["source_code"], SOURCE)
                if attribute in EXPECTED:
                    value = EXPECTED[attribute]
                elif attribute == "ground_clearance":
                    value = "219" if "_4x4_" in config else "220"
                else:
                    value = "1706" if "_4x4_" in config else "1712"
                self.assertEqual(row["value"], value)
                key = (config, attribute)
                self.assertNotIn(key, expected)
                expected[key] = value
                expected_notes[key] = f"Source page 23, section WYMIARY: {row['source_text']}"

        self.assertEqual(len(expected), 126)
        self.assertEqual(set(config for config, _ in expected), linked)

        master_values = read_csv(MASTER / "configuration_attribute_values.csv")
        imported = [
            row for row in master_values
            if row["source_code"] == SOURCE
            and row["observation_date"] == "2025-12-10"
            and row["attribute_code"] in by_attribute
        ]
        self.assertEqual(len(imported), 126)
        self.assertEqual(
            [int(row["id"]) for row in sorted(imported, key=lambda r: int(r["id"]))],
            list(range(8290, 8416)),
        )
        actual = {
            (row["configuration_code"], row["attribute_code"]): row["value"]
            for row in imported
        }
        self.assertEqual(actual, expected)
        actual_notes = {
            (row["configuration_code"], row["attribute_code"]): row["notes"]
            for row in imported
        }
        self.assertEqual(actual_notes, expected_notes)
        self.assertEqual(len({row["code"] for row in imported}), 126)

        later = [
            row for row in master_values
            if row["source_code"] == "src_pl_bigster_price_my26_20260703"
            and row["attribute_code"] in by_attribute
        ]
        self.assertTrue(later)
        self.assertTrue(any(row["attribute_code"] == "overall_width" and row["value"] == "1812" for row in later))
        self.assertTrue(any(row["attribute_code"] == "front_track" and row["value"] == "1573" for row in later))
        self.assertTrue(any(row["attribute_code"] == "rear_track" and row["value"] == "1547" for row in later))

        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SOURCE_SHA)


if __name__ == "__main__":
    unittest.main()
