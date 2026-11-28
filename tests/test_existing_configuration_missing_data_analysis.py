from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import existing_configuration_missing_data_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_WEB_SOURCE = "src_pl_sandero_official_web_configurations_20260723"


class ExistingConfigurationMissingDataAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = analysis.collect(ROOT)

    def test_report_has_stable_contract(self) -> None:
        self.assertEqual(self.payload["version"], 2)
        self.assertEqual(self.payload["as_of"], "2026-08-01")
        self.assertEqual(
            self.payload["kind"],
            "existing_configuration_missing_data_analysis",
        )
        summary = self.payload["summary"]
        self.assertGreater(summary["active_configuration_count"], 0)
        self.assertGreater(summary["completeness_scope_count"], 0)
        self.assertGreater(summary["scoped_configuration_count"], 0)
        self.assertEqual(
            summary["candidate_count"],
            summary["exhausted_source_candidate_count"]
            + summary["eligible_candidate_count"],
        )
        self.assertGreaterEqual(summary["exhausted_source_candidate_count"], 1)
        self.assertEqual(summary["eligible_candidate_count"], 0)

    def test_missing_slots_are_not_negative_and_candidates_are_ranked(self) -> None:
        for item in self.payload["configurations"]:
            self.assertGreaterEqual(item["missing_technical"], 0)
            self.assertGreaterEqual(item["missing_equipment"], 0)
            self.assertLessEqual(
                item["missing_technical"],
                item["expected_technical"],
            )
            self.assertLessEqual(
                item["missing_equipment"],
                item["expected_equipment"],
            )
        impacts = [
            item["weighted_impact"]
            for item in self.payload["ranked_candidates"]
        ]
        self.assertEqual(impacts, sorted(impacts, reverse=True))

    def test_exhausted_sources_remain_visible_but_cannot_be_selected(self) -> None:
        exhausted = [
            item
            for item in self.payload["ranked_candidates"]
            if item["selection_status"] == analysis.EXHAUSTED_CLASSIFICATION
        ]
        self.assertTrue(exhausted)
        self.assertTrue(all(item["source_review_path"] for item in exhausted))
        official_web = next(
            item
            for item in exhausted
            if item["source_code"] == OFFICIAL_WEB_SOURCE
        )
        self.assertEqual(
            official_web["source_review_path"],
            "sandero_official_web_source_gap_review.json",
        )
        selected = self.payload["selected_next_package"]
        self.assertIsNone(selected)
        self.assertEqual(self.payload["summary"]["eligible_candidate_count"], 0)

    def test_not_applicable_slots_are_not_reported_missing(self) -> None:
        for item in self.payload["configurations"]:
            self.assertGreaterEqual(item["classified_not_applicable"], 0)
            technical = {
                (
                    slot["attribute_code"],
                    slot["fuel_type_code"],
                    slot["gear_number"],
                )
                for slot in item["missing_technical_slots"]
            }
            self.assertEqual(len(technical), item["missing_technical"])
            self.assertEqual(
                len(set(item["missing_equipment_attributes"])),
                item["missing_equipment"],
            )

    def test_future_striker_price_only_scope_is_excluded_from_historical_analysis(self) -> None:
        scope_path = ROOT / "data/reporting/striker_my26_catalogue_completeness.json"
        scope = json.loads(scope_path.read_text(encoding="utf-8"))
        self.assertEqual(scope["effective_from"], "2026-11-02")
        historical = analysis.collect(ROOT, scope_as_of_value="2026-08-01")
        self.assertFalse(
            any(
                item["configuration_code"].startswith("striker_")
                for item in historical["configurations"]
            )
        )

        # Missing temporal metadata must not silently pull a future source
        # into an earlier snapshot. The collector fails closed instead.
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            shutil.copytree(ROOT / "data" / "master", temporary_root / "data" / "master")
            shutil.copytree(ROOT / "data" / "reporting", temporary_root / "data" / "reporting")
            copied_scope = (
                temporary_root
                / "data"
                / "reporting"
                / "striker_my26_catalogue_completeness.json"
            )
            copied_payload = json.loads(copied_scope.read_text(encoding="utf-8"))
            copied_payload.pop("effective_from")
            copied_scope.write_text(
                json.dumps(copied_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "effective_from is required"):
                analysis.collect(
                    temporary_root,
                    scope_as_of_value="2026-08-01",
                )

    def test_rendering_and_checked_outputs_are_deterministic(self) -> None:
        self.assertEqual(
            analysis.render_markdown(self.payload),
            analysis.render_markdown(analysis.collect(ROOT)),
        )
        report = (
            ROOT
            / "data/reporting/existing_configuration_missing_data_analysis.json"
        )
        markdown = (
            ROOT
            / "data/reporting/existing_configuration_missing_data_analysis.md"
        )
        self.assertTrue(report.is_file())
        self.assertTrue(markdown.is_file())
        document = json.loads(report.read_text(encoding="utf-8"))
        metadata = document.pop("report_metadata")
        self.assertEqual(document, self.payload)
        self.assertEqual(
            markdown.read_text(encoding="utf-8"),
            analysis.render_markdown(self.payload, metadata),
        )
        self.assertTrue(analysis.check_outputs(ROOT))

        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            shutil.copytree(
                ROOT / "data" / "master",
                temporary_root / "data" / "master",
            )
            shutil.copytree(
                ROOT / "data" / "reporting",
                temporary_root / "data" / "reporting",
            )
            shutil.copytree(
                ROOT / "project",
                temporary_root / "project",
            )
            state_path = temporary_root / "project" / "state.json"
            package_path = (
                temporary_root
                / "project"
                / "packages"
                / "post-jogger-context-completeness-reanalysis-20260801.md"
            )
            state_before = state_path.read_bytes()
            package_before = package_path.read_bytes()

            fixed_time = "2026-11-28T18:00:00+00:00"
            fixed_commit = "a" * 40
            analysis.apply(
                temporary_root,
                update_project_state=False,
                generated_at=fixed_time,
                base_commit_sha=fixed_commit,
            )
            first_json = (
                temporary_root
                / "data"
                / "reporting"
                / "existing_configuration_missing_data_analysis.json"
            ).read_bytes()
            first_markdown = (
                temporary_root
                / "data"
                / "reporting"
                / "existing_configuration_missing_data_analysis.md"
            ).read_bytes()

            self.assertEqual(state_path.read_bytes(), state_before)
            self.assertEqual(package_path.read_bytes(), package_before)
            self.assertTrue(analysis.check_outputs(temporary_root))

            analysis.apply(
                temporary_root,
                update_project_state=False,
                generated_at=fixed_time,
                base_commit_sha=fixed_commit,
            )
            self.assertEqual(
                (
                    temporary_root
                    / "data"
                    / "reporting"
                    / "existing_configuration_missing_data_analysis.json"
                ).read_bytes(),
                first_json,
            )
            self.assertEqual(
                (
                    temporary_root
                    / "data"
                    / "reporting"
                    / "existing_configuration_missing_data_analysis.md"
                ).read_bytes(),
                first_markdown,
            )
            self.assertEqual(state_path.read_bytes(), state_before)
            self.assertEqual(package_path.read_bytes(), package_before)


if __name__ == "__main__":
    unittest.main()
