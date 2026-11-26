from __future__ import annotations

import csv
import json
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


    def test_hill_descent_control_qualifier_remains_explicitly_unresolved(self) -> None:
        report = json.loads((ROOT / "data" / "reporting" / "bigster_20261001_price_list_page_inventory_review_20261015.json").read_text(encoding="utf-8"))
        audit = report["cross_checks"]["page4_5_matrix_reconciliation_20261119"]
        finding = audit["unresolved_findings"]["hill_descent_control"]
        self.assertEqual(audit["status"], "reviewed_with_one_source_qualification_conflict")
        self.assertEqual(audit["scope"]["attributes"], 94)
        self.assertEqual(audit["scope"]["master_observations"], 564)
        self.assertEqual(audit["outcome"]["attribute_groups_consistent_with_matrix"], 93)
        self.assertEqual(finding["matrix_by_grade"], {"essential": "not_available", "expression": "standard", "extreme": "standard", "journey": "standard"})
        self.assertIn("Extreme oraz 4x4", finding["qualifier"])
        self.assertIn("Do sprawdzenia", finding["disposition"])
        self.assertEqual(list(finding["existing_statuses_by_configuration"].values()), ["not_available", "not_available", "not_available", "not_available", "standard", "not_available"])
        self.assertEqual(audit["outcome"]["master_rows_updated"], 0)
        self.assertEqual(audit["outcome"]["availability_statuses_changed"], 0)


if __name__ == "__main__":
    unittest.main()
