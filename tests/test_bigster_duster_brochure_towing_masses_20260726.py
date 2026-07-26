from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "bigster-duster-towing-masses-20260726.json"
IMPORTER = ROOT / "tools" / "import_bigster_duster_brochure_towing_masses_20260726.py"
SOURCES = {
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
}
ATTRIBUTES = {"gross_train_weight", "unbraked_trailer_weight"}
REPORTING_SPECS = {
    "bigster_hybrid155_4x2_automatic_completeness.json",
    "bigster_hybridg150_4x4_automatic_completeness.json",
    "bigster_mildhybrid140_4x2_manual_completeness.json",
    "bigster_mildhybridg140_4x2_manual_completeness.json",
    "duster_ecog120_completeness.json",
    "duster_hybrid155_completeness.json",
    "duster_mildhybrid140_4x2_completeness.json",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterDusterBrochureTowingMassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") in SOURCES
            and row.get("attribute_code") in ATTRIBUTES
        ]

    def test_exact_counts_ids_sources_attributes_and_configurations(self) -> None:
        self.assertEqual(len(self.values), 48)
        self.assertEqual([int(row["id"]) for row in self.values], list(range(2225, 2273)))
        self.assertEqual(Counter(row["source_code"] for row in self.values), Counter({
            "src_pl_bigster_brochure_20251210": 28,
            "src_pl_duster_mini_brochure_20251020": 20,
        }))
        self.assertEqual(Counter(row["attribute_code"] for row in self.values), Counter({
            "gross_train_weight": 24,
            "unbraked_trailer_weight": 24,
        }))
        self.assertEqual(len({row["configuration_code"] for row in self.values}), 24)
        self.assertEqual(len({row["code"] for row in self.values}), 48)
        self.assertEqual({row["fuel_type_code"] for row in self.values}, {""})
        self.assertEqual({row["gear_number"] for row in self.values}, {""})

    def test_bigster_values_follow_four_exact_powertrain_columns(self) -> None:
        expected = {
            "mildhybridg140": ("3430", "740", 4),
            "mildhybrid140": ("3390", "710", 4),
            "hybridg150": ("3545", "750", 3),
            "hybrid155": ("2940", "745", 3),
        }
        bigster = [row for row in self.values if row["configuration_code"].startswith("bigster_")]
        for token, (gross, unbraked, count) in expected.items():
            configurations = {
                row["configuration_code"]
                for row in bigster
                if token in row["configuration_code"]
            }
            self.assertEqual(len(configurations), count)
            for configuration in configurations:
                actual = {
                    row["attribute_code"]: row["value"]
                    for row in bigster
                    if row["configuration_code"] == configuration
                }
                self.assertEqual(actual, {
                    "gross_train_weight": gross,
                    "unbraked_trailer_weight": unbraked,
                })

    def test_duster_values_preserve_pages_and_powertrain_boundaries(self) -> None:
        expected = {
            "ecog120": ("3305", "695", 4, "page 20"),
            "mildhybrid140": ("3330", "685", 3, "page 20"),
            "hybrid155": ("2655", "725", 3, "page 21"),
        }
        duster = [row for row in self.values if row["configuration_code"].startswith("duster_iii_")]
        for token, (gross, unbraked, count, page) in expected.items():
            configurations = {
                row["configuration_code"]
                for row in duster
                if token in row["configuration_code"]
            }
            self.assertEqual(len(configurations), count)
            for configuration in configurations:
                selected = [row for row in duster if row["configuration_code"] == configuration]
                self.assertEqual({row["attribute_code"]: row["value"] for row in selected}, {
                    "gross_train_weight": gross,
                    "unbraked_trailer_weight": unbraked,
                })
                self.assertTrue(all(page in row["notes"] for row in selected))

    def test_new_relationships_cover_only_bigster_hybrid_g_150(self) -> None:
        relationships = rows(MASTER / "source_configurations.csv")
        new_rows = [row for row in relationships if row["id"] in {"217", "218", "219"}]
        self.assertEqual(len(new_rows), 3)
        self.assertEqual({row["source_code"] for row in new_rows}, {"src_pl_bigster_brochure_20251210"})
        self.assertEqual({row["relationship"] for row in new_rows}, {"brochure_technical_data_for"})
        self.assertEqual(
            {row["configuration_code"] for row in new_rows},
            {
                "bigster_expression_hybridg150_4x4_automatic",
                "bigster_extreme_hybridg150_4x4_automatic",
                "bigster_journey_hybridg150_4x4_automatic",
            },
        )

    def test_exclusions_keep_newer_automatic_and_unmodeled_duster_out(self) -> None:
        configurations = {row["configuration_code"] for row in self.values}
        self.assertFalse(any(code.startswith("duster_iii_") and "hybridg150" in code for code in configurations))
        self.assertFalse(any(code.endswith("ecog120_4x2_automatic") for code in configurations))
        self.assertEqual(
            {item["code"] for item in self.spec["excluded_evidence"]},
            {
                "duster_hybridg150_without_exact_configuration",
                "duster_ecog120_automatic_uses_newer_homologation",
                "no_cross_powertrain_projection",
                "no_other_mass_rows",
            },
        )

    def test_reporting_scopes_include_both_towing_slots(self) -> None:
        reporting = ROOT / "data" / "reporting"
        for filename in REPORTING_SPECS:
            with self.subTest(filename=filename):
                payload = json.loads((reporting / filename).read_text(encoding="utf-8"))
                slots = {
                    (item["attribute_code"], item.get("fuel_type_code", ""))
                    for item in payload["technical_slots"]
                }
                self.assertIn(("gross_train_weight", ""), slots)
                self.assertIn(("unbraked_trailer_weight", ""), slots)

    def test_importer_is_append_only_and_idempotent(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Bigster and Duster brochure towing masses", completed.stdout)

    def test_project_state_advances_to_jogger_hybrid_completion(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Bigster and Duster Brochure Towing Mass Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Jogger Brochure Hybrid Performance Completion")
        self.assertEqual(state["baseline"]["configuration_values"], 2272)
        self.assertEqual(state["baseline"]["rows"], 8939)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)


if __name__ == "__main__":
    unittest.main()
