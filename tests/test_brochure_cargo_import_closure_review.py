from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT_PATH = ROOT / "data" / "reporting" / "brochure_cargo_import_closure_review.json"
SOURCES = {
    "src_pl_sandero_brochure_20260202": (4, 20),
    "src_pl_sandero_stepway_brochure_20260202": (5, 25),
    "src_pl_jogger_brochure_20251217": (22, 110),
    "src_pl_bigster_brochure_20251210": (11, 68),
    "src_pl_duster_mini_brochure_20251020": (10, 64),
}
IMPORTERS = (
    "tools/import_sandero_stepway_brochure_cargo_20260725.py",
    "tools/import_jogger_brochure_cargo_20260726.py",
    "tools/import_bigster_brochure_cargo_20260726.py",
    "tools/import_duster_brochure_cargo_20260726.py",
)
CONTEXT_FIELDS = (
    "measurement_basis_code",
    "second_row_state_code",
    "third_row_state_code",
    "compartment_code",
    "spare_wheel_state_code",
    "tyre_repair_kit_state_code",
    "double_floor_state_code",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"missing CSV header: {path}")
        return list(reader)


class BrochureCargoImportClosureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.values = [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") in SOURCES
            and row.get("attribute_code") == "boot_capacity"
        ]
        cls.contexts = rows(MASTER / "configuration_cargo_volume_contexts.csv")
        cls.relationships = [
            row for row in rows(MASTER / "source_configurations.csv")
            if row.get("source_code") in SOURCES
            and row.get("relationship") == "brochure_technical_data_for"
        ]

    def test_closure_receipt_matches_master_totals_by_source(self) -> None:
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(self.report["totals"], {
            "sources": 5,
            "configurations": 52,
            "values": 287,
            "contexts": 287,
            "source_configuration_relationships": 52,
        })
        value_counts = Counter(row["source_code"] for row in self.values)
        relationship_counts = Counter(row["source_code"] for row in self.relationships)
        for source, (configurations, values) in SOURCES.items():
            self.assertEqual(value_counts[source], values, source)
            self.assertGreaterEqual(relationship_counts[source], configurations, source)
        self.assertEqual(len(self.values), 287)
        self.assertGreaterEqual(len(self.relationships), 52)

    def test_every_brochure_value_has_one_exact_context(self) -> None:
        value_codes = {row["code"] for row in self.values}
        contexts = [row for row in self.contexts if row["configuration_attribute_value_code"] in value_codes]
        self.assertEqual(len(contexts), 287)
        self.assertEqual({row["configuration_attribute_value_code"] for row in contexts}, value_codes)
        self.assertEqual(len({row["configuration_attribute_value_code"] for row in contexts}), 287)
        self.assertEqual({row["measurement_basis_code"] for row in contexts}, {"vda_iso_3832", "ordinary_litre"})

    def test_reporting_keys_do_not_collapse_context_variants(self) -> None:
        context_by_value = {row["configuration_attribute_value_code"]: row for row in self.contexts}
        grouped: dict[tuple[str, str], list[tuple[str, ...]]] = defaultdict(list)
        for value in self.values:
            context = context_by_value[value["code"]]
            signature = tuple(context[field] for field in CONTEXT_FIELDS)
            grouped[(value["source_code"], value["configuration_code"])].append(signature)
        self.assertEqual(len(grouped), 52)
        for key, signatures in grouped.items():
            self.assertEqual(len(signatures), len(set(signatures)), key)
            self.assertGreaterEqual(len(signatures), 4, key)

    def test_all_four_importers_reproduce_current_contract(self) -> None:
        for importer in IMPORTERS:
            with self.subTest(importer=importer):
                completed = subprocess.run(
                    [sys.executable, importer, "--check"],
                    cwd=ROOT, text=True, capture_output=True, check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                self.assertIn("PASS:", completed.stdout)

    def test_deferrals_and_historical_closure_baseline_are_preserved(self) -> None:
        self.assertEqual(len(self.report["deferred_evidence"]), 6)
        self.assertEqual(
            {item["code"] for item in self.report["deferred_evidence"]},
            {
                "jogger_7seat_maximum_third_row_state",
                "bigster_hybrid_g_150_4x4_equipment_contradiction",
                "bigster_generic_dimensions_powertrain_projection",
                "duster_ecog120_manual_to_automatic_projection",
                "duster_hybrid_g_150_4x4_unmodeled",
                "duster_generic_dimensions_powertrain_projection",
            },
        )
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 808)
        self.assertGreaterEqual(state["baseline"]["rows"], 8782)


if __name__ == "__main__":
    unittest.main()
