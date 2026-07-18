from __future__ import annotations

import csv
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
sys.path.insert(0, str(ROOT / "tools"))

import configuration_completeness  # noqa: E402


SOURCE_CODE = "src_pl_duster_price_my26_py25_20260206"

EXPECTED_VERSIONS = {
    "duster_iii_essential": "Essential",
    "duster_iii_expression": "Expression",
    "duster_iii_extreme": "Extreme",
    "duster_iii_journey": "Journey",
    "duster_iii_journey_plus": "Journey+",
}

POWERTRAINS = (
    ("ecog100_4x2", "Eco-G 100 4x2", "manual",
     ("essential", "expression", "extreme", "journey")),
    ("mildhybrid130_4x2", "mild hybrid 130 4x2", "manual",
     ("expression", "extreme", "journey")),
    ("hybrid140_4x2", "hybrid 140 4x2", "automatic",
     ("expression", "extreme", "journey", "journey_plus")),
    ("mildhybrid130_4x4", "mild hybrid 130 4x4", "manual",
     ("expression", "extreme", "journey")),
    ("ecog120_4x2", "Eco-G 120 4x2", "manual",
     ("essential", "expression", "extreme", "journey")),
    ("mildhybrid140_4x2", "mild hybrid 140 4x2", "manual",
     ("expression", "extreme", "journey")),
    ("hybrid155_4x2", "hybrid 155 4x2", "automatic",
     ("expression", "extreme", "journey")),
)


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def expected_configurations() -> dict[str, tuple[str, str, str]]:
    result: dict[str, tuple[str, str, str]] = {}
    for token, label, transmission, trims in POWERTRAINS:
        for trim in trims:
            version_code = f"duster_iii_{trim}"
            code = f"duster_iii_{trim}_{token}_{transmission}"
            result[code] = (version_code, label, transmission)
    return result


class DusterCatalogBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = expected_configurations()
        self.assertEqual(len(self.expected), 24)

    def test_five_source_backed_versions_are_active(self) -> None:
        actual = {
            row["code"]: row
            for row in rows("versions.csv")
            if row["model_code"] == "duster_iii"
        }
        self.assertEqual(set(actual), set(EXPECTED_VERSIONS))
        for code, name in EXPECTED_VERSIONS.items():
            self.assertEqual(actual[code]["name"], name)
            self.assertEqual(actual[code]["status"], "active")

    def test_twenty_four_explicit_configurations_match_price_matrix(self) -> None:
        actual = {
            row["code"]: row
            for row in rows("configurations.csv")
            if row["version_code"].startswith("duster_iii_")
        }
        self.assertEqual(set(actual), set(self.expected))
        for code, (version, label, transmission) in self.expected.items():
            self.assertEqual(actual[code]["version_code"], version)
            self.assertEqual(actual[code]["powertrain_label"], label)
            self.assertEqual(actual[code]["transmission_type"], transmission)
            self.assertEqual(actual[code]["status"], "active")

    def test_trim_and_transmission_counts_match_source_matrix(self) -> None:
        actual = [
            row
            for row in rows("configurations.csv")
            if row["code"] in self.expected
        ]
        self.assertEqual(
            Counter(row["version_code"] for row in actual),
            Counter({
                "duster_iii_essential": 2,
                "duster_iii_expression": 7,
                "duster_iii_extreme": 7,
                "duster_iii_journey": 7,
                "duster_iii_journey_plus": 1,
            }),
        )
        self.assertEqual(
            Counter(row["transmission_type"] for row in actual),
            Counter({"manual": 17, "automatic": 7}),
        )

    def test_source_relations_cover_every_new_entity_exactly_once(self) -> None:
        version_links = [
            row for row in rows("source_versions.csv")
            if row["source_code"] == SOURCE_CODE
        ]
        configuration_links = [
            row for row in rows("source_configurations.csv")
            if row["source_code"] == SOURCE_CODE
        ]
        self.assertEqual(
            {row["version_code"] for row in version_links},
            set(EXPECTED_VERSIONS),
        )
        self.assertEqual(
            {row["configuration_code"] for row in configuration_links},
            set(self.expected),
        )
        self.assertEqual(len(version_links), 5)
        self.assertEqual(len(configuration_links), 24)
        self.assertTrue(all(row["relationship"] == "documents" for row in version_links))
        self.assertTrue(all(row["relationship"] == "documents" for row in configuration_links))

    def test_catalog_identity_remains_valid_after_equipment_enrichment(self) -> None:
        configuration_codes = set(self.expected)
        availability = [
            row for row in rows("configuration_attribute_availability.csv")
            if row["configuration_code"].startswith("duster_iii_")
        ]
        self.assertTrue(
            all(row["configuration_code"] in configuration_codes for row in availability)
        )

    def test_reporting_subset_remains_sandero_only(self) -> None:
        report = configuration_completeness.collect_report(
            ROOT,
            ROOT / "data" / "reporting" / "configuration_completeness.json",
        )
        scope = report["scope"]
        self.assertEqual(scope["reporting_configurations"], 7)
        self.assertEqual(scope["repository_status_configurations"], 53)
        self.assertEqual(scope["excluded_configurations"], 46)
        self.assertTrue(
            set(self.expected).issubset(scope["excluded_configuration_codes"])
        )


if __name__ == "__main__":
    unittest.main()
