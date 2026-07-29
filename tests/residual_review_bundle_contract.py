from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import residual_review_bundle


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"
PRIORITIZATION = (
    ROOT / "data" / "reporting" / "verified_pdf_candidate_residual_gap_prioritization.json"
)
SOURCE_RECEIPT = ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_state_package(state: dict) -> dict:
    package_id = residual_review_bundle.default_package_id(state)
    for key in ("current_package", "next_package"):
        package = state.get(key)
        if isinstance(package, dict) and package.get("package_id") == package_id:
            return package
    raise AssertionError(f"state package not found: {package_id}")


class ResidualReviewBundleContractTests(unittest.TestCase):
    def test_state_declares_complete_residual_review_boundary(self) -> None:
        state = read_json(STATE)
        package = selected_state_package(state)
        bundle = package["review_bundle"]
        self.assertEqual(state["version"], 1)
        self.assertEqual(package["kind"], "residual_review")
        self.assertIn(package["status"], {"planned", "in_progress"})
        self.assertIsInstance(package["package_id"], str)
        self.assertGreater(bundle["page"], 0)
        self.assertGreater(bundle["candidate_count"], 0)
        self.assertGreaterEqual(
            bundle["group_candidate_count"], bundle["candidate_count"]
        )
        self.assertGreaterEqual(bundle["chunk_count"], bundle["chunk_index"])
        self.assertEqual(len(bundle["source_sha256"]), 64)

    def test_state_metadata_matches_canonical_reports(self) -> None:
        state = read_json(STATE)
        state_package = selected_state_package(state)
        package_id = state_package["package_id"]
        state_bundle = state_package["review_bundle"]
        packages = read_json(PRIORITIZATION)["packages"]
        package = next(item for item in packages if item["package_id"] == package_id)
        sources = read_json(SOURCE_RECEIPT)["sources"]
        source = next(
            item for item in sources if item["source_code"] == package["source_code"]
        )
        for key in (
            "source_code",
            "model_code",
            "domain",
            "page",
            "candidate_count",
            "group_candidate_count",
            "chunk_index",
            "chunk_count",
            "evidence_signature_count",
            "evidence_record_count",
        ):
            self.assertEqual(state_bundle[key], package[key])
        self.assertEqual(state_bundle["source_path"], source["file_path"])
        self.assertEqual(state_bundle["source_sha256"], source["sha256"])

    def test_default_package_comes_from_canonical_state(self) -> None:
        state = read_json(STATE)
        package = selected_state_package(state)
        self.assertEqual(
            residual_review_bundle.default_package_id(state),
            package["package_id"],
        )

    def test_bundle_contains_exact_candidates_and_verified_files(self) -> None:
        state = read_json(STATE)
        state_package = selected_state_package(state)
        package_id = state_package["package_id"]
        package = residual_review_bundle.package_by_id(
            read_json(PRIORITIZATION), package_id
        )
        source = residual_review_bundle.source_by_code(
            read_json(SOURCE_RECEIPT), package["source_code"]
        )
        expected_page = package["page"]
        expected_text = f"page {expected_page} exact layout\n"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"

            def fake_text(path: Path, page: int) -> str:
                self.assertEqual(path, ROOT / source["file_path"])
                self.assertEqual(page, expected_page)
                return expected_text

            def fake_render(path: Path, page: int, target: Path) -> None:
                self.assertEqual(path, ROOT / source["file_path"])
                self.assertEqual(page, expected_page)
                target.write_bytes(b"PNG-test")

            manifest = residual_review_bundle.build_bundle(
                ROOT,
                package_id,
                output,
                text_extractor=fake_text,
                page_renderer=fake_render,
            )
            candidates = read_json(output / "candidates.json")
            self.assertEqual(
                candidates["candidate_count"], package["candidate_count"]
            )
            self.assertEqual(
                [item["candidate_id"] for item in candidates["candidates"]],
                package["candidate_ids"],
            )
            self.assertEqual(
                (output / "source-page.txt").read_text(), expected_text
            )
            self.assertEqual(
                (output / "source-page.png").read_bytes(), b"PNG-test"
            )
            self.assertEqual(manifest["source_sha256"], source["sha256"])
            for item in manifest["files"]:
                path = output / item["path"]
                self.assertEqual(item["size_bytes"], path.stat().st_size)
                self.assertEqual(
                    item["sha256"],
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )

    def test_output_directory_must_be_empty(self) -> None:
        state = read_json(STATE)
        package_id = selected_state_package(state)["package_id"]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            output.mkdir()
            (output / "existing.txt").write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(
                residual_review_bundle.ResidualReviewBundleError,
                "must be empty",
            ):
                residual_review_bundle.build_bundle(ROOT, package_id, output)

    def test_workflow_generates_and_uploads_the_bundle(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "residual-review-bundle.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("python tools/residual_review_bundle.py", workflow)
        self.assertIn("actions/upload-artifact@", workflow)
        self.assertIn("retention-days: 14", workflow)
        self.assertNotIn("permissions:\n  contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
