from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "post_brochure_priority_selection_review.json"
VERIFIER = ROOT / "tools" / "review_post_brochure_priority_selection_20260726.py"

EXPECTED_SCORES = {
    "data_products_v1_7_0_release_preparation": 100,
    "cross_model_comparison_view_review": 82,
    "pdf_candidate_extraction_automation_review": 67,
    "exact_configuration_expansion_review": 57,
    "ambiguous_brochure_evidence_resolution": 39,
}
EXPECTED_SCOPE_FILES = {
    "bigster_hybrid155_4x2_automatic_completeness.json",
    "bigster_hybridg150_4x4_automatic_completeness.json",
    "bigster_mildhybrid140_4x2_manual_completeness.json",
    "bigster_mildhybridg140_4x2_manual_completeness.json",
    "duster_ecog100_completeness.json",
    "duster_ecog120_automatic_completeness.json",
    "duster_ecog120_completeness.json",
    "duster_hybrid140_completeness.json",
    "duster_hybrid155_completeness.json",
    "duster_mildhybrid130_4x2_completeness.json",
    "duster_mildhybrid130_4x4_completeness.json",
    "duster_mildhybrid140_4x2_completeness.json",
    "jogger_ecog120_automatic_completeness.json",
    "jogger_ecog120_manual_completeness.json",
    "jogger_hybrid155_automatic_completeness.json",
    "jogger_tce110_manual_completeness.json",
    "sandero_ecog120_automatic_completeness.json",
    "sandero_ecog120_manual_completeness.json",
    "sandero_stepway_ecog120_automatic_completeness.json",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class PostBrochurePrioritySelectionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.candidates = {
            item["code"]: item for item in cls.report["candidates"]
        }

    def test_review_metadata_and_weight_policy_are_exact(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "post_brochure_priority_selection_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["source_milestone"],
            "brochure_generic_dimensions_import_closure_review.json",
        )
        weights = self.report["selection_policy"]["weights_percent"]
        self.assertEqual(sum(weights.values()), 100)
        self.assertEqual(
            weights,
            {
                "consumer_value": 30,
                "evidence_readiness": 25,
                "existing_tooling_reuse": 20,
                "low_implementation_risk": 15,
                "dependency_clearance": 10,
            },
        )

    def test_five_candidates_have_exact_rank_status_and_scores(self) -> None:
        self.assertEqual(set(self.candidates), set(EXPECTED_SCORES))
        self.assertEqual(
            [item["rank"] for item in self.report["candidates"]],
            [1, 2, 3, 4, 5],
        )
        self.assertEqual(
            {
                code: item["weighted_score"]
                for code, item in self.candidates.items()
            },
            EXPECTED_SCORES,
        )
        self.assertEqual(
            self.candidates[
                "data_products_v1_7_0_release_preparation"
            ]["status"],
            "selected",
        )
        self.assertEqual(
            self.candidates["exact_configuration_expansion_review"]["status"],
            "blocked_evidence",
        )
        self.assertEqual(
            self.candidates[
                "ambiguous_brochure_evidence_resolution"
            ]["status"],
            "blocked_ambiguity",
        )

    def test_release_preparation_is_selected_with_stable_non_goals(self) -> None:
        self.assertEqual(
            self.report["selection"]["code"],
            "data_products_v1_7_0_release_preparation",
        )
        self.assertEqual(self.report["selection"]["weighted_score"], 100)
        contract = self.report["release_preparation_contract"]
        self.assertEqual(contract["target_version"], "1.7.0")
        self.assertEqual(contract["target_tag"], "data-products-v1.7.0")
        self.assertEqual(
            contract["publication_mode"],
            "manual_after_verified_preparation",
        )
        self.assertEqual(
            set(contract["non_goals"]),
            {
                "ranking",
                "recommendations",
                "cross_scope_pair_generation",
                "inferred_values",
                "new_data_imports",
            },
        )
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.7.0 Release Preparation",
        )

    def test_repository_readiness_covers_72_configurations_and_19_scopes(self) -> None:
        active = [
            row
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active"
        ]
        self.assertEqual(len(active), 72)
        self.assertEqual(
            self.report["repository_readiness"]["active_configurations"],
            72,
        )
        self.assertEqual(
            self.report["repository_readiness"][
                "independent_comparison_scopes"
            ],
            19,
        )
        self.assertTrue(
            all((REPORTING / filename).is_file() for filename in EXPECTED_SCOPE_FILES)
        )
        self.assertEqual(len(EXPECTED_SCOPE_FILES), 19)
        self.assertEqual(
            self.report["repository_readiness"]["candidate_release_files"],
            83,
        )
        self.assertEqual(
            self.report["repository_readiness"]["candidate_release_pair_count"],
            114,
        )
        self.assertEqual(
            self.report["repository_readiness"][
                "candidate_release_difference_count"
            ],
            1695,
        )

    def test_blocked_candidates_match_preserved_evidence_boundaries(self) -> None:
        exact = self.candidates["exact_configuration_expansion_review"]
        self.assertEqual(
            set(exact["blockers"]),
            {
                "sandero_tce100_without_exact_configuration",
                "stepway_tce110_without_exact_configuration",
                "duster_hybridg150_without_exact_configuration",
                "duster_4x4_dimensions_without_exact_source_relationship",
            },
        )
        ambiguous = self.candidates[
            "ambiguous_brochure_evidence_resolution"
        ]
        self.assertEqual(
            ambiguous["blockers"],
            ["jogger_mass_table_label_conflict"],
        )
        residual = json.loads(
            (
                REPORTING / "official_brochure_residual_evidence_review.json"
            ).read_text(encoding="utf-8")
        )
        stable_codes = {
            item["code"] for item in residual["stable_non_import"]
        }
        self.assertTrue(
            {
                "sandero_tce100_without_exact_configuration",
                "stepway_tce110_without_exact_configuration",
                "duster_hybridg150_without_exact_configuration",
                "jogger_mass_table_label_conflict",
            }
            <= stable_codes
        )

    def test_existing_release_tooling_is_reused(self) -> None:
        required = (
            ROOT / "tools/reporting/data_product_release.py",
            ROOT / "tools/reporting/data_product_release_download.py",
            ROOT / "tools/reporting/data_product_workspace_verify.py",
            ROOT / "tools/reporting/configuration_comparison_bundle.py",
            ROOT / "tools/configuration_shortlist.py",
        )
        self.assertTrue(all(path.is_file() for path in required))
        readiness = self.report["repository_readiness"]
        self.assertEqual(
            readiness["latest_documented_public_release"],
            "data-products-v1.6.1",
        )
        self.assertEqual(
            readiness["candidate_release_semantic_boundaries"],
            {
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

    def test_priority_verifier_reproduces_repository_contract(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr or completed.stdout,
        )
        self.assertIn(
            "PASS: post-brochure priority selection review",
            completed.stdout,
        )

    def test_project_state_preserves_priority_selection_baseline(self) -> None:
    state = json.loads(
        (ROOT / "project/state.json").read_text(encoding="utf-8")
    )
    self.assertTrue(state["phase"])
    self.assertTrue(state["current_package"]["name"])
    self.assertIn(
        state["current_package"]["status"],
        {"planned", "active", "blocked", "complete"},
    )
    self.assertTrue(state["next_package"]["name"])
    self.assertGreaterEqual(state["baseline"]["tests"], 963)
    self.assertGreaterEqual(state["baseline"]["rows"], 9688)
    self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
    self.assertGreaterEqual(
        state["baseline"]["configuration_value_ranges"],
        244,
    )
    self.assertGreaterEqual(state["baseline"]["attributes"], 385)



if __name__ == "__main__":
    unittest.main()
