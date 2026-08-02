from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_legacy_pdf_assimilation_closure.json"
HISTORICAL_PACKAGE_ID = "spring_legacy_pdf_assimilation_closure_001"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringLegacyPdfAssimilationClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_exact_source_hashes_and_all_28_pages_are_closed(self) -> None:
        expected = {
            "PDF/Broszury/DACIA SPRING broszura 20260219.pdf": "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d",
            "PDF/Cenniki/DACIA SPRING cennik MY25 stock 20260708.pdf": "809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0",
        }
        self.assertEqual(self.report["page_accounting"]["reviewed_pages"], 28)
        self.assertEqual(self.report["page_accounting"]["unreviewed_pages"], 0)
        for relative, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)

    def test_every_ledger_area_has_one_closure_outcome(self) -> None:
        accounting = self.report["ledger_accounting"]
        self.assertEqual(accounting["area_count"], 22)
        self.assertEqual(accounting["unclassified_area_count"], 0)
        outcomes = accounting["closure_outcomes"]
        self.assertEqual(len(outcomes), 22)
        self.assertEqual(len({item["area"] for item in outcomes}), 22)
        self.assertEqual(
            Counter(accounting["initial_status_counts"]),
            Counter({"candidate": 12, "deferred": 4, "represented": 3, "conflict": 2, "out_of_scope": 1}),
        )

    def test_all_36_approved_observations_are_materialized(self) -> None:
        receipt = self.report["materialized_observations"]
        self.assertEqual(receipt["approved_observation_count"], 36)
        self.assertEqual(receipt["materialized_observation_count"], 36)
        self.assertEqual(receipt["value_id_range"], [3569, 3604])
        selected = [
            row for row in rows(ROOT / "data/master/configuration_attribute_values.csv")
            if 3569 <= int(row["id"]) <= 3604
        ]
        self.assertEqual(len(selected), 36)
        self.assertEqual({row["source_code"] for row in selected}, {"src_pl_spring_brochure_20260219"})

    def test_all_six_technical_deferrals_remain_explicit(self) -> None:
        self.assertEqual(
            set(self.report["preserved_deferrals"]),
            {
                "battery_mass_204_kg_my2025_stock_only",
                "battery_voltage_354_v_my2025_stock_only",
                "battery_capacity_24_3_kwh_measurement_basis_unqualified",
                "charging_times_context_dependent",
                "ground_clearance_15_inch_wheel_only",
                "range_and_maximum_speed_not_reimported",
            },
        )

    def test_four_documentary_conflicts_remain_preserved(self) -> None:
        conflicts = self.report["preserved_conflicts"]
        self.assertEqual(len(conflicts), 4)
        text = (ROOT / "project/source-audit/spring-source-conflicts-20260802.md").read_text(encoding="utf-8")
        for code in ("C-001", "C-002", "C-003", "C-004"):
            self.assertIn(code, text)

    def test_every_required_downstream_receipt_is_complete(self) -> None:
        self.assertEqual(len(self.report["downstream_receipts"]), 12)
        for relative in self.report["downstream_receipts"]:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "complete", relative)

    def test_no_eligible_source_candidate_remains(self) -> None:
        closure = self.report["source_candidate_closure"]
        self.assertEqual(closure["eligible_candidate_count"], 0)
        self.assertIsNone(closure["selected_next_source_package"])
        analysis = json.loads((ROOT / "data/reporting/existing_configuration_missing_data_analysis.json").read_text(encoding="utf-8"))
        self.assertEqual(analysis["summary"]["eligible_candidate_count"], 0)
        self.assertIsNone(analysis["selected_next_package"])

    def test_closure_tool_verify_mode_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/review_spring_legacy_pdf_assimilation_closure_20260802.py", "--verify"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_state_preserves_source_milestone_closure_contract(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        current_id = state["current_package"]["package_id"]
        if current_id == HISTORICAL_PACKAGE_ID:
            self.assertEqual(state["phase"], "Data Product Release")
            self.assertEqual(
                state["next_package"]["package_id"],
                "data_products_v1_11_0_accelerated_release_preparation_001",
            )
            self.assertEqual(state["next_package"]["status"], "planned")
        else:
            self.assertGreaterEqual(state["baseline"]["configuration_values"], 3604)
            self.assertGreaterEqual(state["baseline"]["tests"], 1829)
            self.assertEqual(
                self.report["release_handoff"]["selected_next_package"],
                "data_products_v1_11_0_accelerated_release_preparation_001",
            )

    def test_state_manifest_tracks_all_closure_outputs_while_current(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        manifest = set(state["current_package"]["manifest_paths"])
        required = {
            "tools/review_spring_legacy_pdf_assimilation_closure_20260802.py",
            "data/reporting/spring_legacy_pdf_assimilation_closure.json",
            "data/reporting/spring_legacy_pdf_assimilation_closure.md",
            "project/packages/spring-legacy-pdf-assimilation-closure-20260802.md",
            "tests/test_spring_legacy_pdf_assimilation_closure_20260802.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        }
        for relative in required - {"project/state.json", "project/STATE_SUMMARY.md"}:
            self.assertTrue((ROOT / relative).is_file(), relative)
        if state["current_package"]["package_id"] == HISTORICAL_PACKAGE_ID:
            self.assertTrue(required.issubset(manifest))
        else:
            self.assertEqual(state["current_package"]["status"], "complete")
            self.assertGreaterEqual(state["baseline"]["configuration_values"], 3604)


if __name__ == "__main__":
    unittest.main()
