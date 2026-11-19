from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_duster_price_my26_20261102"
SOURCE_SHA = "dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118"
PDF = ROOT / "PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf"
MASTER = ROOT / "data/master"
SPEC_DIR = ROOT / "data/imports/configuration_values"

CONFIGS_4X2 = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
CONFIGS_4X4 = {
    "duster_iii_expression_hybridg150_4x4_automatic",
    "duster_iii_extreme_hybridg150_4x4_automatic",
    "duster_iii_journey_hybridg150_4x4_automatic",
}
EXPECTED = {
    "front_track": {"4x2": "1574", "4x4": "1573", "id_start": 8527},
    "rear_track": {"4x2": "1547", "4x4": "1562", "id_start": 8533},
    "ground_clearance": {"4x2": "209", "4x4": "217", "id_start": 8539},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterPage9DimensionCrosswalkTests(unittest.TestCase):
    def test_source_archive_and_exact_16_configuration_scope(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SOURCE_SHA)
        sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
        source = sources[SOURCE]
        self.assertEqual(source["sha256"], SOURCE_SHA)
        self.assertEqual(source["document_date"], "2026-11-02")
        self.assertEqual(source["file_path"], "PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf")

        links = [
            row for row in read_csv(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "documents"
        ]
        linked = {row["configuration_code"] for row in links}
        self.assertEqual(len(links), 16)
        expected_scope = CONFIGS_4X2 | CONFIGS_4X4 | {
            "duster_iii_essential_ecog120_4x2_manual",
            "duster_iii_expression_ecog120_4x2_manual",
            "duster_iii_extreme_ecog120_4x2_manual",
            "duster_iii_journey_ecog120_4x2_manual",
            "duster_iii_expression_mildhybrid140_4x2_manual",
            "duster_iii_extreme_mildhybrid140_4x2_manual",
            "duster_iii_journey_mildhybrid140_4x2_manual",
            "duster_iii_expression_hybrid155_4x2_automatic",
            "duster_iii_extreme_hybrid155_4x2_automatic",
            "duster_iii_journey_hybrid155_4x2_automatic",
        }
        self.assertEqual(linked, expected_scope)

        configurations = {
            row["code"]: row for row in read_csv(MASTER / "configurations.csv")
        }
        self.assertTrue(all(configurations[c]["status"] == "active" for c in linked))
        self.assertTrue(all("4x2" in configurations[c]["powertrain_label"] for c in CONFIGS_4X2))
        self.assertTrue(all("4x4" in configurations[c]["powertrain_label"] for c in CONFIGS_4X4))

    def test_three_specs_encode_the_reviewed_visual_mapping(self) -> None:
        for attribute, expected in EXPECTED.items():
            path = SPEC_DIR / f"duster-page9-{attribute.replace('_', '-')}-20261102.json"
            spec = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(spec["version"], 1)
            self.assertEqual(spec["kind"], "configuration_attribute_values")
            self.assertEqual(spec["id_start"], expected["id_start"])
            self.assertEqual(spec["attribute_code"], attribute)
            self.assertEqual(spec["attribute_contract"], {
                "data_type": "integer", "unit": "mm", "status": "active"
            })
            self.assertEqual(spec["observation_date"], "2026-11-02")
            self.assertEqual(spec["source_page"], 9)
            self.assertEqual(spec["source_section"], "WYMIARY")
            self.assertEqual(len(spec["rows"]), 6)
            by_config = {row["configuration_code"]: row for row in spec["rows"]}
            self.assertEqual(set(by_config), CONFIGS_4X2 | CONFIGS_4X4)
            self.assertTrue(all(by_config[c]["value"] == expected["4x2"] for c in CONFIGS_4X2))
            self.assertTrue(all(by_config[c]["value"] == expected["4x4"] for c in CONFIGS_4X4))
            self.assertTrue(all(row["source_code"] == SOURCE for row in spec["rows"]))

    def test_master_receipt_is_exact_and_preserves_existing_history(self) -> None:
        values = read_csv(MASTER / "configuration_attribute_values.csv")
        imported = [
            row for row in values
            if row["source_code"] == SOURCE
            and row["observation_date"] == "2026-11-02"
            and row["attribute_code"] in EXPECTED
        ]
        self.assertEqual(len(imported), 18)
        self.assertEqual(
            [int(row["id"]) for row in sorted(imported, key=lambda r: int(r["id"]))],
            list(range(8527, 8545)),
        )
        expected_values = {
            (config, attribute, expected["4x2" if config in CONFIGS_4X2 else "4x4"])
            for attribute, expected in EXPECTED.items()
            for config in CONFIGS_4X2 | CONFIGS_4X4
        }
        self.assertEqual(
            {(row["configuration_code"], row["attribute_code"], row["value"]) for row in imported},
            expected_values,
        )
        self.assertEqual(len({row["code"] for row in imported}), 18)

        prior = [
            row for row in values
            if row["source_code"] == "src_pl_duster_mini_brochure_20251020"
            and row["attribute_code"] in {"front_track", "rear_track", "ground_clearance"}
        ]
        self.assertEqual(len(prior), 30)
        self.assertEqual(
            {(row["attribute_code"], row["value"]) for row in prior},
            {("front_track", "1574"), ("rear_track", "1547"), ("ground_clearance", "209")},
        )

        target_keys = {
            (config, attribute)
            for config in CONFIGS_4X2 | CONFIGS_4X4
            for attribute in EXPECTED
        }
        actual_counts = {
            key: sum(
                row["configuration_code"] == key[0] and row["attribute_code"] == key[1]
                for row in values
            )
            for key in target_keys
        }
        self.assertTrue(all(count == 1 for count in actual_counts.values()))

    def test_report_preserves_non_inference_boundaries(self) -> None:
        report = json.loads(
            (ROOT / "data/reporting/duster_my26_20261102_dimension_diagram_crosswalk_review_20261119.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["scope"]["source_configurations"], 16)
        self.assertEqual(report["scope"]["imported_scalar_values"], 18)
        self.assertEqual(report["imported_id_range"], [8527, 8544])
        excluded = {tuple(item["visual_values"]) for item in report["exclusions"]}
        self.assertIn(("1443", "1432"), excluded)
        self.assertIn(("907", "894", "14°"), excluded)
        self.assertIn(("2092",), excluded)


if __name__ == "__main__":
    unittest.main()
