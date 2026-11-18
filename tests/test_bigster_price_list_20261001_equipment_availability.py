from __future__ import annotations

import csv
import hashlib
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "bigster_equipment_availability_20261001.csv"
SOURCE_PATH = ROOT / "owner_supplied" / "2026-10-01" / "d477c604e8.pdf"
SOURCE_CODE = "src_pl_bigster_price_my26_20261001"
SOURCE_SHA256 = "0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPriceList20261001EquipmentAvailabilityTests(unittest.TestCase):
    def test_master_equipment_evidence_matches_all_564_source_spec_rows(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA256)
        spec = read_rows(SPEC_PATH)
        master = read_rows(MASTER / "configuration_attribute_availability.csv")
        source_rows = [row for row in master if row["source_code"] == SOURCE_CODE]

        self.assertEqual(len(spec), 564)
        self.assertEqual(len(source_rows), 564)
        self.assertEqual(
            Counter(row["availability_status"] for row in source_rows),
            Counter({"standard": 465, "not_available": 53, "optional": 46}),
        )
        self.assertEqual(
            {row["configuration_code"] for row in spec},
            {
                "bigster_expression_mildhybridg140_4x2_automatic",
                "bigster_extreme_mildhybridg140_4x2_automatic",
                "bigster_journey_mildhybridg140_4x2_automatic",
                "bigster_expression_tribrid150_4x4_automatic",
                "bigster_extreme_tribrid150_4x4_automatic",
                "bigster_journey_tribrid150_4x4_automatic",
            },
        )
        self.assertEqual(len({row["attribute_code"] for row in spec}), 94)
        linked = {
            row["configuration_code"]
            for row in read_rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE_CODE
        }
        self.assertTrue({row["configuration_code"] for row in spec} <= linked)

        actual_by_code = {row["code"]: row for row in source_rows}
        self.assertEqual(len(actual_by_code), 564)
        self.assertEqual([int(row["id"]) for row in source_rows], list(range(8720, 9284)))
        for item in spec:
            code = f"{item['configuration_code']}_{item['attribute_code']}_20261001"
            self.assertIn(code, actual_by_code)
            actual = actual_by_code[code]
            expected_notes = (
                f"Source page {item['source_page']}: {item['source_label']}. "
                "Trim-level status expanded only to this source-backed configuration."
            )
            if item["normalization_notes"].strip():
                expected_notes += f" {item['normalization_notes'].strip()}"
            self.assertEqual(actual["configuration_code"], item["configuration_code"], code)
            self.assertEqual(actual["attribute_code"], item["attribute_code"], code)
            self.assertEqual(actual["availability_status"], item["availability_status"], code)
            self.assertEqual(actual["observation_date"], "2026-10-01", code)
            self.assertEqual(actual["source_code"], SOURCE_CODE, code)
            self.assertEqual(actual["notes"], expected_notes, code)


if __name__ == "__main__":
    unittest.main()
