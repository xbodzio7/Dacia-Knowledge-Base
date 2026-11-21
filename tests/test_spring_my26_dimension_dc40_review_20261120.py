from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
SOURCES = ROOT / "data/master/sources.csv"
REVIEW = ROOT / "project/packages/spring-my26-dimension-and-dc40-review-20261120.md"

SOURCE = "src_pl_spring_price_my26_20260206"
EXPECTED = {
    "spring_expression_electric70_automatic": "8545",
    "spring_extreme_electric100_automatic": "8546",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringMy26DimensionAndDc40ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = read_rows(VALUES)
        cls.sources = read_rows(SOURCES)

    def test_155_mm_is_imported_only_for_exact_15_inch_configurations(self) -> None:
        rows = [
            row for row in self.values
            if row["source_code"] == SOURCE
            and row["attribute_code"] == "ground_clearance"
            and row["observation_date"] == "2026-02-06"
        ]
        self.assertEqual(
            {row["configuration_code"]: row["id"] for row in rows},
            EXPECTED,
        )
        self.assertTrue(all(row["value"] == "155" for row in rows))
        self.assertTrue(all("page 6" in row["notes"].lower() for row in rows))
        self.assertTrue(all("15" in row["notes"] for row in rows))

    def test_essential_is_not_assigned_the_15_inch_clearance_value(self) -> None:
        self.assertFalse(
            any(
                row["configuration_code"] == "spring_essential_electric70_automatic"
                and row["attribute_code"] == "ground_clearance"
                and row["source_code"] == SOURCE
                for row in self.values
            )
        )

    def test_existing_configurator_laden_and_unladen_observations_are_preserved(self) -> None:
        for configuration in (
            "spring_essential_electric70_automatic",
            "spring_expression_electric70_automatic",
            "spring_extreme_electric100_automatic",
        ):
            by_attribute = {
                row["attribute_code"]: row["value"]
                for row in self.values
                if row["configuration_code"] == configuration
                and row["source_code"].startswith("src_pl_cfgpdf_spring_")
                and row["attribute_code"] in {
                    "ground_clearance_laden",
                    "ground_clearance_unladen",
                }
            }
            self.assertEqual(
                by_attribute,
                {
                    "ground_clearance_laden": "115.3",
                    "ground_clearance_unladen": "146.1",
                },
            )

    def test_source_registry_and_review_record_the_package_semantics(self) -> None:
        source = next(row for row in self.sources if row["code"] == SOURCE)
        self.assertIn("155 mm ground-clearance observations", source["notes"])
        self.assertIn("POWER", source["notes"])
        review = REVIEW.read_text(encoding="utf-8")
        self.assertIn("No standalone Extreme DC40 option is added", review)
        self.assertIn("Overall height 1519 mm", review)
        self.assertIn("1900 mm", review)


    def test_comparison_scopes_accept_the_new_ground_clearance_observations(self) -> None:
        import json

        for path in (
            ROOT / "data/reporting/spring_electric70_automatic_completeness.json",
            ROOT / "data/reporting/spring_electric100_automatic_completeness.json",
        ):
            specification = json.loads(path.read_text(encoding="utf-8"))
            slots = {row["attribute_code"] for row in specification["technical_slots"]}
            self.assertIn("ground_clearance", slots)
            clearance = next(row for row in specification["technical_slots"] if row["attribute_code"] == "ground_clearance")
            self.assertEqual(clearance["source_code"], SOURCE)

        evidence = json.loads(
            (ROOT / "data/reporting/spring_electric70_automatic_gap_evidence.spec").read_text(encoding="utf-8")
        )
        self.assertFalse(
            any(
                row["configuration_code"] == "spring_essential_electric70_automatic"
                and row["attribute_code"] == "ground_clearance"
                and row.get("source_code") == SOURCE
                for row in evidence["decisions"]
            )
        )


if __name__ == "__main__":
    unittest.main()
