from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "sandero_my26_20261102_ecog120_injection_lpg_semantics_review_20261119_001.json"
SOURCE_CODE = "src_pl_sandero_stepway_price_my26_20261102"
SANDERO_SHA256 = "8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c"
JOGGER_SHA256 = "12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46"

CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoEcoG120SemanticsReviewTests(unittest.TestCase):
    def test_archived_sandero_and_jogger_sources_are_hash_verified(self) -> None:
        sandero = ROOT / "owner_supplied" / "2026-11-02" / "3b4618d7da.pdf"
        jogger = ROOT / "owner_supplied" / "2026-10-01" / "f5cdbd7878.pdf"
        self.assertEqual(hashlib.sha256(sandero.read_bytes()).hexdigest(), SANDERO_SHA256)
        self.assertEqual(hashlib.sha256(jogger.read_bytes()).hexdigest(), JOGGER_SHA256)

        sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
        self.assertEqual(sources[SOURCE_CODE]["sha256"], SANDERO_SHA256)
        self.assertEqual(sources[SOURCE_CODE]["document_date"], "2026-11-02")
        self.assertEqual(sources[SOURCE_CODE]["file_path"], "owner_supplied/2026-11-02/3b4618d7da.pdf")
        jogger_source = sources["src_pl_jogger_price_my26_20261001"]
        self.assertEqual(jogger_source["sha256"], JOGGER_SHA256)
        self.assertEqual(jogger_source["document_date"], "2026-10-01")

    def test_exact_nine_configuration_scope_and_all_18_capacity_observations(self) -> None:
        links = [
            row for row in read_csv(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE_CODE and row["relationship"] == "documents"
        ]
        eco_g_links = {
            row["configuration_code"] for row in links
            if "ecog120" in row["configuration_code"]
        }
        self.assertEqual(eco_g_links, CONFIGURATIONS)

        values = read_csv(MASTER / "configuration_attribute_values.csv")
        observations = [
            row for row in values
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-11-02"
            and row["configuration_code"] in CONFIGURATIONS
        ]
        capacity_rows = [row for row in observations if row["attribute_code"] == "fuel_tank_capacity"]
        self.assertEqual(len(capacity_rows), 18)
        self.assertEqual(
            [int(row["id"]) for row in sorted(capacity_rows, key=lambda row: int(row["id"]))],
            list(range(8509, 8527)),
        )
        self.assertEqual(
            Counter((row["fuel_type_code"], row["value"]) for row in capacity_rows),
            Counter({("petrol", "50"): 9, ("lpg", "40"): 9}),
        )
        self.assertEqual({row["configuration_code"] for row in capacity_rows}, CONFIGURATIONS)

    def test_no_unproven_injection_or_lpg_vessel_classification_was_added(self) -> None:
        values = read_csv(MASTER / "configuration_attribute_values.csv")
        source_rows = [
            row for row in values
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-11-02"
            and row["configuration_code"] in CONFIGURATIONS
        ]
        self.assertFalse([row for row in source_rows if row["attribute_code"] == "injection_type"])
        self.assertFalse([
            row for row in source_rows
            if row["attribute_code"] in {"lpg_vessel_capacity_total", "lpg_vessel_filling_capacity"}
        ])

        engines = read_csv(MASTER / "engines.csv")
        model_engines = read_csv(MASTER / "model_engines.csv")
        self.assertFalse([
            row for row in engines
            if "eco-g 120" in row["name"].lower() or "ecog120" in row["code"].lower()
        ])
        self.assertFalse([
            row for row in model_engines
            if "ecog120" in row["engine_code"].lower()
        ])

    def test_review_report_preserves_both_explicit_deferrals(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "closed_with_explicit_source_ambiguity")
        self.assertEqual(report["scope"]["configuration_count"], 9)
        self.assertEqual(report["scope"]["existing_fuel_capacity_observations"], 18)
        self.assertEqual(report["outcome"]["master_data_changed"], False)
        self.assertEqual(report["outcome"]["master_rows_added"], 0)
        self.assertEqual(report["outcome"]["master_rows_updated"], 0)
        findings = {item["finding_id"]: item for item in report["findings"]}
        self.assertEqual(
            set(findings),
            {
                "sandero-ecog120-fuel-specific-injection",
                "sandero-ecog120-lpg-total-versus-fillable-capacity",
            },
        )
        self.assertTrue(all(item["status"] == "needs_review" for item in findings.values()))
        self.assertIn("Do not transfer", findings["sandero-ecog120-fuel-specific-injection"]["detail"])
        self.assertIn("do not migrate", findings["sandero-ecog120-lpg-total-versus-fillable-capacity"]["detail"].lower())

        metadata = report["report_metadata"]
        self.assertEqual(metadata["report_id"], report["report_id"])
        self.assertEqual(metadata["base_commit_sha"], report["analysed_commit_sha"])
        self.assertEqual(metadata["status"], "needs_review")
        self.assertEqual(metadata["scope"], report["report_metadata"]["scope"])
        self.assertTrue(metadata["input_files"])


if __name__ == "__main__":
    unittest.main()
