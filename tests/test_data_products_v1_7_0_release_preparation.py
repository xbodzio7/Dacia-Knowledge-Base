from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "data_products_v1_7_0_release_preparation.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_7_0_release_preparation_20260726.py"
STATE = ROOT / "project" / "state.json"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.7.0.md"
TARGET_AUDIT = (
    ROOT / "project" / "releases" / "data-products-v1.7.0-publication-audit.json"
)
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DataProductsV170ReleasePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_release_identity_are_frozen(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "data_products_v1_7_0_release_preparation",
        )
        self.assertEqual(self.report["prepared_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        identity = self.report["release_identity"]
        self.assertEqual(identity["release_version"], "1.7.0")
        self.assertEqual(identity["release_tag"], "data-products-v1.7.0")
        self.assertEqual(identity["publication_status"], "not_published")
        self.assertEqual(identity["final_source_commit"], "assigned_after_squash_merge")
        self.assertEqual(identity["final_asset_identity"], "assigned_by_post_merge_preflight")

    def test_candidate_baseline_covers_complete_current_portfolio(self) -> None:
        baseline = self.report["candidate_baseline"]
        self.assertEqual(baseline["selected_configuration_count"], 72)
        self.assertEqual(baseline["scope_group_count"], 19)
        self.assertEqual(baseline["comparable_scope_count"], 19)
        self.assertEqual(baseline["singleton_scope_count"], 0)
        self.assertEqual(baseline["pair_count"], 114)
        self.assertEqual(baseline["difference_count"], 1695)
        self.assertEqual(baseline["archive_member_count"], 83)
        self.assertEqual(
            set(baseline["formats"]),
            {"JSON", "Markdown", "CSV", "HTML", "XLSX"},
        )
        active = [row for row in rows(MASTER / "configurations.csv") if row["status"] == "active"]
        self.assertEqual(len(active), 72)

    def test_preparation_verification_includes_offline_and_previous_release(self) -> None:
        verification = self.report["preparation_verification"]
        self.assertEqual(verification["deterministic_double_build"], "pass")
        self.assertEqual(verification["release_asset_verification"], "pass")
        self.assertEqual(verification["candidate_offline_workspace_verification"], "pass")
        self.assertEqual(verification["previous_public_release_download_verification"], "pass")
        self.assertEqual(verification["previous_public_release"], "data-products-v1.6.1")
        self.assertEqual(
            verification["previous_public_release_commit"],
            "4b77571c788b862a6543161b9343a35f464bd7c6",
        )
        self.assertFalse(verification["publication_performed"])

    def test_diagnostic_receipt_is_not_final_publication_identity(self) -> None:
        receipt = self.report["diagnostic_candidate_receipt"]
        self.assertEqual(
            receipt["identity_status"],
            "diagnostic_only_not_publication_identity",
        )
        self.assertIsInstance(receipt["workflow_run"], int)
        self.assertRegex(receipt["source_commit"], r"[0-9a-f]{40}")
        self.assertIn("not final", receipt["reason_not_final"].lower())
        self.assertEqual(
            set(receipt["assets"]),
            {
                "dacia-knowledge-base-data-products-v1.7.0.zip",
                "data-product-release-manifest.json",
                "SHA256SUMS",
            },
        )
        for record in receipt["assets"].values():
            self.assertGreater(record["size_bytes"], 0)
            self.assertIsNotNone(SHA256.fullmatch(record["sha256"]))
        self.assertIsNotNone(SHA256.fullmatch(receipt["workspace_index_sha256"]))

    def test_semantic_boundaries_and_asset_inventory_are_unchanged(self) -> None:
        self.assertEqual(
            self.report["semantic_boundaries"],
            {
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
                "master_data_changed": False,
                "existing_evidence_states_preserved": True,
            },
        )
        self.assertEqual(
            self.report["required_publication_assets"],
            [
                "dacia-knowledge-base-data-products-v1.7.0.zip",
                "data-product-release-manifest.json",
                "SHA256SUMS",
            ],
        )

    def test_publication_sequence_requires_preflight_publish_audit_and_record(self) -> None:
        sequence = self.report["publication_sequence"]
        self.assertEqual([item["order"] for item in sequence], [1, 2, 3, 4, 5])
        self.assertEqual(
            [item["stage"] for item in sequence],
            [
                "merge_preparation",
                "preflight",
                "publish",
                "audit",
                "record_publication",
            ],
        )
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.7.0 Preflight",
        )
        self.assertEqual(TARGET_RELEASE.is_file(), TARGET_AUDIT.is_file())
        if TARGET_AUDIT.is_file():
            audit = json.loads(TARGET_AUDIT.read_text(encoding="utf-8"))
            self.assertEqual(audit["release_id"], 360090447)
            self.assertEqual(audit["tag"], "data-products-v1.7.0")
            self.assertEqual(
                audit["target_commit_sha"],
                "99e0e19b86cad6eae619f37702464e6a5a761cd8",
            )
            self.assertEqual(audit["verification"], "PASS")

    def test_preparation_verifier_reproduces_repository_contract(self) -> None:
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
            "PASS: Data Products v1.7.0 release preparation",
            completed.stdout,
        )

    def test_project_state_preserves_published_release_baseline(self) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    self.assertTrue(state["phase"])
    self.assertTrue(state["current_package"]["name"])
    self.assertIn(
        state["current_package"]["status"],
        {"planned", "active", "blocked", "complete"},
    )
    self.assertTrue(state["next_package"]["name"])
    self.assertGreaterEqual(state["baseline"]["tests"], 971)
    self.assertGreaterEqual(state["baseline"]["rows"], 9688)
    self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
    self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
    self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
