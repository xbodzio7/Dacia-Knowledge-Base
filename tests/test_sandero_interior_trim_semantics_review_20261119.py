from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT_PATH = ROOT / "data" / "reporting" / "sandero_my26_20261102_interior_dimensions_and_trim_semantics_review_20261119_001.json"
REGISTRY_PATH = ROOT / "data" / "reporting" / "report_registry.json"
SOURCE_PATH = ROOT / "owner_supplied" / "2026-11-02" / "3b4618d7da.pdf"
SOURCE_SHA256 = "8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c"
SOURCE_CODE = "src_pl_sandero_stepway_price_my26_20261102"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoInteriorTrimSemanticsReviewTests(unittest.TestCase):
    def test_official_source_hash_and_registration_are_consistent(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA256)
        sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
        source = sources[SOURCE_CODE]
        self.assertEqual(source["sha256"], SOURCE_SHA256)
        self.assertEqual(source["document_date"], "2026-11-02")
        self.assertEqual(source["file_path"], "owner_supplied/2026-11-02/3b4618d7da.pdf")

    def test_existing_attribute_catalogue_does_not_authorize_semantic_overloading(self) -> None:
        attributes = {row["code"]: row for row in read_csv(MASTER / "attributes.csv")}
        self.assertTrue({"interior_length", "interior_width", "interior_height"} <= set(attributes))
        self.assertTrue({"upholstery_variant", "centre_console_variant", "wheel_design", "wheel_material", "wheel_finish"} <= set(attributes))
        # Existing fields are intentionally narrow; no distinct canonical fields
        # currently represent the reviewed grille/mirror/handle/insert/decal finishes.
        self.assertFalse({
            "grille_finish",
            "mirror_cap_finish",
            "exterior_door_handle_finish",
            "dashboard_insert_finish",
            "air_vent_surround_finish",
            "decorative_decal_pattern",
            "rubber_mat_pattern",
        } & set(attributes))

    def test_report_closes_review_without_promoting_ambiguous_values(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "closed_with_explicit_source_ambiguity")
        self.assertEqual(report["scope"]["source_code"], SOURCE_CODE)
        self.assertEqual(report["scope"]["printed_pages"], [2, 3, 6])
        self.assertEqual(report["scope"]["source_configurations_reviewed"], 19)
        findings = {item["finding_id"]: item for item in report["findings"]}
        self.assertEqual(set(findings), {
            "sandero-interior-dimension-callouts",
            "sandero-decorative-trim-descriptors",
        })
        self.assertTrue(all(item["status"] == "needs_review" for item in findings.values()))
        self.assertTrue(all(item["evidence_refs"] for item in findings.values()))
        outcome = report["outcome"]
        self.assertEqual(outcome["master_rows_added"], 0)
        self.assertEqual(outcome["master_rows_updated"], 0)
        self.assertEqual(outcome["attributes_added"], 0)
        self.assertEqual(outcome["import_spec_rows_changed"], 0)
        self.assertFalse(outcome["master_data_changed"])
        self.assertFalse(outcome["source_binary_changed"])
        metadata = report["report_metadata"]
        self.assertEqual(metadata["report_id"], report["report_id"])
        self.assertEqual(metadata["base_commit_sha"], report["analysed_commit_sha"])
        self.assertEqual(metadata["status"], "needs_review")
        self.assertTrue(metadata["input_files"])

    def test_report_registry_contains_the_exact_report_artifacts(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        entries = [item for item in registry["reports"] if item["report_id"] == "sandero_my26_20261102_interior_dimensions_and_trim_semantics_review_20261119_001"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["json_path"], "data/reporting/sandero_my26_20261102_interior_dimensions_and_trim_semantics_review_20261119_001.json")
        self.assertEqual(entries[0]["markdown_path"], "data/reporting/sandero_my26_20261102_interior_dimensions_and_trim_semantics_review_20261119_001.md")


if __name__ == "__main__":
    unittest.main()
