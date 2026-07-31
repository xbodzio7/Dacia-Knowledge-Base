from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SNAPSHOT = REPOSITORY / "project" / "sources" / "dacia-pl-duster-ecog120-automatic-stock-20260724.json"
SOURCE_CODE = "src_pl_duster_ecog120_automatic_stock_20260724"
SNAPSHOT_SHA256 = "a25c2244699b463343879fb1d1fa995793666d3e5619da2021acd81404688e98"
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}

sys.path.insert(0, str(REPOSITORY / "tools"))
import configuration_completeness  # noqa: E402
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402


class DusterEcoG120AutomaticStock20260724Tests(unittest.TestCase):
    def rows(self, name: str) -> list[dict[str, str]]:
        with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def source_rows(self, name: str) -> list[dict[str, str]]:
        if name == "sources.csv":
            return [row for row in self.rows(name) if row["code"] == SOURCE_CODE]
        return [row for row in self.rows(name) if row.get("source_code") == SOURCE_CODE]

    def test_snapshot_is_registered_with_exact_hash_and_stock_card_boundary(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        source = self.source_rows("sources.csv")
        self.assertEqual(len(source), 1)
        self.assertEqual(hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(), SNAPSHOT_SHA256)
        self.assertEqual(source[0]["sha256"], SNAPSHOT_SHA256)
        self.assertEqual(source[0]["source_type"], "web_snapshot")
        self.assertEqual(source[0]["document_date"], "2026-07-24")
        self.assertEqual(payload["volatility"], "dynamic_official_stock_cards")

    def test_three_exact_automatic_configurations_are_active(self) -> None:
        rows = [row for row in self.rows("configurations.csv") if row["code"] in CONFIGURATION_CODES]
        self.assertEqual(len(rows), 3)
        self.assertEqual({row["code"] for row in rows}, CONFIGURATION_CODES)
        self.assertEqual({row["transmission_type"] for row in rows}, {"automatic"})
        self.assertEqual({row["powertrain_label"] for row in rows}, {"Eco-G 120 4x2"})
        self.assertEqual({row["status"] for row in rows}, {"active"})
        self.assertEqual(
            {row["version_code"] for row in rows},
            {"duster_iii_expression", "duster_iii_extreme", "duster_iii_journey"},
        )

    def test_exact_catalogue_prices_exclude_promotional_amounts(self) -> None:
        prices = self.source_rows("configuration_prices.csv")
        self.assertEqual(len(prices), 3)
        self.assertEqual(
            {row["configuration_code"]: int(row["amount"]) for row in prices},
            {
                "duster_iii_expression_ecog120_4x2_automatic": 96900,
                "duster_iii_extreme_ecog120_4x2_automatic": 110300,
                "duster_iii_journey_ecog120_4x2_automatic": 107600,
            },
        )
        self.assertEqual({row["price_type"] for row in prices}, {"catalog_gross"})
        self.assertEqual({row["currency_code"] for row in prices}, {"PLN"})
        self.assertTrue(all("Promotional and financing prices excluded" in row["notes"] for row in prices))

    def test_folding_mirrors_are_standard_only_where_exactly_proven(self) -> None:
        rows = self.source_rows("configuration_attribute_availability.csv")
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["attribute_code"] for row in rows}, {"side_mirrors_folding"})
        self.assertEqual({row["availability_status"] for row in rows}, {"standard"})
        self.assertEqual(
            {row["configuration_code"] for row in rows},
            {
                "duster_iii_extreme_ecog120_4x2_automatic",
                "duster_iii_journey_ecog120_4x2_automatic",
            },
        )
        self.assertNotIn(
            "duster_iii_expression_ecog120_4x2_automatic",
            {row["configuration_code"] for row in rows},
        )
        self.assertFalse(any(row["attribute_code"] == "shark_fin_antenna" for row in rows))

    def test_snapshot_preserves_expression_and_antenna_non_imports(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        observations = {item["version_name"]: item for item in payload["configurations"]}
        expression_non_imports = {
            item["attribute_code"]: item["reason"]
            for item in observations["Expression"]["non_imports"]
        }
        self.assertIn("side_mirrors_folding", expression_non_imports)
        self.assertIn("conflicts", expression_non_imports["side_mirrors_folding"])
        for item in observations.values():
            self.assertIn(
                "shark_fin_antenna",
                {entry["attribute_code"] for entry in item["non_imports"]},
            )

    def test_source_relationships_are_exact_and_not_broadened(self) -> None:
        self.assertEqual(
            {row["model_code"] for row in self.source_rows("source_models.csv")},
            {"duster_iii"},
        )
        self.assertEqual(len(self.source_rows("source_versions.csv")), 3)
        self.assertEqual(
            {row["configuration_code"] for row in self.source_rows("source_configurations.csv")},
            CONFIGURATION_CODES,
        )

    def test_browser_catalog_contains_new_configurations_and_current_mirror_states(self) -> None:
        catalog = collect_browser_catalog(REPOSITORY, ShortlistCriteria())
        self.assertEqual(len(catalog["configurations"]), 81)
        selected = {
            item["configuration_code"]: item
            for item in catalog["configurations"]
            if item["configuration_code"] in CONFIGURATION_CODES
        }
        self.assertEqual(set(selected), CONFIGURATION_CODES)
        self.assertEqual(
            int(selected["duster_iii_expression_ecog120_4x2_automatic"]["catalog_price"]["amount"]),
            96900,
        )
        self.assertEqual(
            int(selected["duster_iii_extreme_ecog120_4x2_automatic"]["catalog_price"]["amount"]),
            110300,
        )
        self.assertEqual(
            int(selected["duster_iii_journey_ecog120_4x2_automatic"]["catalog_price"]["amount"]),
            107600,
        )
        self.assertNotIn(
            "side_mirrors_folding",
            selected["duster_iii_expression_ecog120_4x2_automatic"]["equipment"],
        )
        for code in (
            "duster_iii_extreme_ecog120_4x2_automatic",
            "duster_iii_journey_ecog120_4x2_automatic",
        ):
            self.assertEqual(
                selected[code]["equipment"]["side_mirrors_folding"]["availability_status"],
                "standard",
            )
        report = configuration_completeness.collect_report(
            REPOSITORY,
            REPOSITORY / "data" / "reporting" / "duster_ecog120_automatic_completeness.json",
        )
        self.assertEqual(report["scope"]["reporting_configurations"], 3)
        self.assertEqual(report["scope"]["technical_slots"], 31)
        self.assertEqual(report["technical"]["present"], 93)
        self.assertEqual(report["technical"]["missing"], 0)
        self.assertEqual(report["equipment"]["denominator"], 0)

    def test_importer_check_reproduces_master_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/import_duster_ecog120_automatic_stock_20260724.py", "--check"],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: Duster Eco-G 120 automatic stock-card contract", result.stdout)
        engine = subprocess.run(
            [sys.executable, "tools/import_duster_ecog120_automatic_engine_20260724.py", "--check"],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(engine.returncode, 0, engine.stderr)
        self.assertIn("PASS: Duster Eco-G 120 automatic intrinsic-engine contract", engine.stdout)


if __name__ == "__main__":
    unittest.main()
