from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DataProductsV111AcceleratedReleaseContractTest(unittest.TestCase):
    def test_accelerated_release_policy_remains_canonical(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        policy = state["execution_policy"]
        self.assertEqual(policy["mode"], "accelerated_milestone_closure")
        self.assertTrue(policy["full_quality_on_final_head"])
        self.assertTrue(policy["release_double_build_required"])
        self.assertTrue(policy["release_exact_source_sha_required"])

    def test_release_notes_describe_the_bounded_spring_delta(self) -> None:
        source = (
            ROOT / "tools/reporting/data_product_release.py"
        ).read_text(encoding="utf-8")
        for expected in (
            'elif version == "1.11.0":',
            "36 source-",
            "bounded common technical observations",
            "permanent-magnet synchronous motor",
            "LFP traction-battery chemistry",
            "electric steering",
            "common body dimensions",
            "public v1.10.0 remains immutable",
        ):
            self.assertIn(expected, source)

    def test_release_notes_preserve_every_technical_deferral(self) -> None:
        source = (
            ROOT / "tools/reporting/data_product_release.py"
        ).read_text(encoding="utf-8")
        for expected in (
            "204 kg",
            "354 V",
            "24.3 kWh",
            "charging times",
            "range",
            "maximum speed",
            "wheel-qualified ground clearance",
        ):
            self.assertIn(expected, source)

    def test_preparation_package_declares_exact_publication_contract(self) -> None:
        package = (
            ROOT
            / "project/packages/data-products-v1.11.0-accelerated-release-preparation-20260802.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "data-products-v1.11.0",
            "dacia-knowledge-base-data-products-v1.11.0.zip",
            "exact publication merge SHA",
            "build the assets twice",
            "compare them byte for byte",
            "public `data-products-v1.10.0` remains immutable",
        ):
            self.assertIn(expected, package)

    def test_v1_10_0_publication_receipt_remains_immutable(self) -> None:
        receipt = json.loads(
            (
                ROOT / "data/reporting/data_products_v1_10_0_publication.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["tag"], "data-products-v1.10.0")
        self.assertEqual(
            receipt["source_commit"],
            "acd58c883b8e1ebb2d06f17dec703990bdb1d9a3",
        )
        self.assertTrue(receipt["double_build_byte_identity"])

    def test_publication_receipt_or_planned_publication_is_consistent(self) -> None:
        receipt_path = ROOT / "data/reporting/data_products_v1_11_0_publication.json"
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["tag"], "data-products-v1.11.0")
            self.assertTrue(receipt["double_build_byte_identity"])
            self.assertEqual(receipt["offline_workspace_verification"], "PASS")
            self.assertTrue(receipt["public_v1_10_0_immutable"])
        else:
            package_ids = {
                state["current_package"]["package_id"],
                state["next_package"]["package_id"],
            }
            self.assertIn("data_products_v1_11_0_publication_001", package_ids)


if __name__ == "__main__":
    unittest.main()
