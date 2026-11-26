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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterBrochureGradeDetailsTests(unittest.TestCase):
    def test_exact_grade_specific_observations_and_provenance(self) -> None:
        specs = sorted(SPEC_DIR.glob("bigster-page1[4-7]-*-20251210.json"))
        self.assertEqual(len(specs), 16)
        spec_data = [json.loads(path.read_text(encoding="utf-8")) for path in specs]
        expected_by_grade = {
            "essential": {"parking_brake_type":"manual","steering_wheel_material":"eco_leather_soft_feel","rear_seat_folding":"1/3-2/3","speaker_count":"4"},
            "expression": {"parking_brake_type":"electric","steering_wheel_material":"eco_leather_soft_feel","rear_seat_folding":"40/20/40","speaker_count":"4"},
            "journey": {"parking_brake_type":"electric","steering_wheel_material":"eco_leather_soft_feel","rear_seat_folding":"40/20/40","speaker_count":"6"},
            "extreme": {"parking_brake_type":"electric","steering_wheel_material":"eco_leather_soft_feel","rear_seat_folding":"40/20/40","speaker_count":"6"},
        }
        expected_counts = {"essential":2,"expression":4,"journey":4,"extreme":4}
        expected = {}
        for spec in spec_data:
            self.assertEqual(spec["kind"], "configuration_attribute_values")
            self.assertEqual(spec["observation_date"], "2025-12-10")
            self.assertEqual(spec["attribute_contract"]["status"], "active")
            self.assertEqual(spec["attribute_contract"]["data_type"], "string" if spec["attribute_code"] in {"parking_brake_type","steering_wheel_material","rear_seat_folding"} else "integer")
            printed_page = int(spec["source_section"].split("printed page ")[1].split(")")[0])
            grade = spec["source_section"].split("— ")[1].split(" ")[0].lower()
            self.assertEqual(spec["source_page"], printed_page + 1)
            self.assertEqual(len(spec["rows"]), expected_counts[grade])
            for row in spec["rows"]:
                config = row["configuration_code"]
                self.assertTrue(config.startswith(f"bigster_{grade}_"))
                self.assertEqual(row["source_code"], SOURCE)
                self.assertEqual(row["value"], expected_by_grade[grade][spec["attribute_code"]])
                key = (config, spec["attribute_code"])
                self.assertNotIn(key, expected)
                expected[key] = row["value"]
        self.assertEqual(len(expected), 56)

        master_values = read_csv(MASTER / "configuration_attribute_values.csv")
        imported = [row for row in master_values if row["source_code"] == SOURCE and row["observation_date"] == "2025-12-10" and row["attribute_code"] in {a for _, a in expected}]
        self.assertEqual(len(imported), 56)
        self.assertEqual([int(row["id"]) for row in sorted(imported, key=lambda r: int(r["id"]))], list(range(8234, 8290)))
        actual = {(row["configuration_code"], row["attribute_code"]): row["value"] for row in imported}
        self.assertEqual(actual, expected)
        self.assertEqual(len({row["code"] for row in imported}), 56)

        configurations = read_csv(MASTER / "configurations.csv")
        active = {row["code"] for row in configurations if row["status"] == "active"}
        linked = {row["configuration_code"] for row in read_csv(MASTER / "source_configurations.csv") if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"}
        targets = {config for config, _ in expected}
        self.assertEqual(len(targets), 14)
        self.assertTrue(targets <= active)
        self.assertTrue(targets <= linked)
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertTrue(any(row["configuration_code"].startswith("bigster_essential_") and row["attribute_code"] == "rear_seat_folding" and row["value"] == "40/60" and row["observation_date"] == "2026-08-09" for row in master_values))
        self.assertTrue(any(row["configuration_code"].startswith("bigster_journey_") and row["attribute_code"] == "speaker_count" and row["value"] == "6" and row["observation_date"] == "2026-08-09" for row in master_values))


if __name__ == "__main__":
    unittest.main()
