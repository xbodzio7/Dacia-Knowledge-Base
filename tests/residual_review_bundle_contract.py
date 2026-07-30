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
CLOSURE = (
    ROOT
    / "data"
    / "reporting"
    / "verified_pdf_candidate_residual_review_closure.json"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def last_prioritization_package() -> dict:
    packages = read_json(PRIORITIZATION)["packages"]
    return packages[-1]


def verified_closure_final_package() -> dict:
    last = last_prioritization_package()
    closure = read_json(CLOSURE)
    verification = closure.get("verification", {})
    packages = read_json(PRIORITIZATION)["packages"]
    if not (
        closure.get("status") == "complete"
        and closure.get("scope", {}).get("package_count") == len(packages)
        and closure.get("scope", {}).get("last_package_id") == last["package_id"]
        and verification.get("package_ids_sequential_and_unique") is True
        and verification.get("one_complete_review_report_per_package") is True
        and verification.get("candidate_ids_assigned_exactly_once") is True
        and verification.get("candidate_ids_and_exact_text_match_prioritization") is True
    ):
        raise residual_review_bundle.ResidualReviewBundleError(
            "canonical residual closure is missing or not verified"
        )
    source = next(
        item
        for item in read_json(SOURCE_RECEIPT)["sources"]
        if item["source_code"] == last["source_code"]
    )
    review_bundle = {
        key: last[key]
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
        )
    }
    review_bundle.update(
        {
            "source_path": source["file_path"],
            "source_sha256": source["sha256"],
            "prioritization_path": str(PRIORITIZATION.relative_to(ROOT)),
            "source_receipt_path": str(SOURCE_RECEIPT.relative_to(ROOT)),
        }
    )
    return {
        "package_id": last["package_id"],
        "kind": "residual_review",
        "status": "complete",
        "review_bundle": review_bundle,
    }


def active_state_package(state: dict) -> tuple[dict, bool]:
    try:
        package_id = residual_review_bundle.default_package_id(state)
        queue_complete = False
    except residual_review_bundle.ResidualReviewBundleError as original_error:
        current = state.get("current_package")
        last = last_prioritization_package()
        if (
            isinstance(current, dict)
            and current.get("kind") == "residual_review"
            and current.get("status") == "complete"
            and current.get("package_id") == last.get("package_id")
        ):
            return current, True
        try:
            return verified_closure_final_package(), True
        except (FileNotFoundError, KeyError, StopIteration, json.JSONDecodeError):
            raise original_error
    for key in ("current_package", "next_package"):
        package = state.get(key)
        if isinstance(package, dict) and package.get("package_id") == package_id:
            return package, queue_complete
    raise AssertionError(f"state package not found: {package_id}")


class ResidualReviewBundleContractTests(unittest.TestCase):
    def test_state_declares_residual_review_or_completed_queue_boundary(self) -> None:
        state = read_json(STATE)
        package, queue_complete = active_state_package(state)
        self.assertEqual(state["version"], 1)
        bundle = package["review_bundle"]
        self.assertEqual(package["kind"], "residual_review")
        if queue_complete:
            self.assertEqual(package["status"], "complete")
        else:
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
        state_package, _queue_complete = active_state_package(state)
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
        package, queue_complete = active_state_package(state)
        if queue_complete:
            with self.assertRaisesRegex(
                residual_review_bundle.ResidualReviewBundleError,
                "does not declare an active or next residual review package",
            ):
                residual_review_bundle.default_package_id(state)
        else:
            self.assertEqual(
                residual_review_bundle.default_package_id(state),
                package["package_id"],
            )

    def test_bundle_contains_exact_candidates_and_verified_files(self) -> None:
        state = read_json(STATE)
        state_package, _queue_complete = active_state_package(state)
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

    def test_queue_completion_resolves_the_final_explicit_package(self) -> None:
        last = last_prioritization_package()
        state = {
            "current_package": {
                "package_id": last["package_id"],
                "kind": "residual_review",
                "status": "complete",
            },
            "next_package": {
                "package_id": "post_residual_review_milestone_closure_001",
                "kind": "milestone_review",
                "status": "planned",
            },
        }
        package, queue_complete = active_state_package(state)
        self.assertTrue(queue_complete)
        self.assertEqual(package["package_id"], last["package_id"])
        with self.assertRaises(residual_review_bundle.ResidualReviewBundleError):
            residual_review_bundle.default_package_id(state)

    def test_post_closure_state_resolves_final_verified_package(self) -> None:
        state = read_json(STATE)
        closure = read_json(CLOSURE)
        last = last_prioritization_package()
        self.assertEqual(closure["status"], "complete")
        self.assertEqual(closure["scope"]["last_package_id"], last["package_id"])
        self.assertTrue(
            closure["verification"]["candidate_ids_and_exact_text_match_prioritization"]
        )
        package, queue_complete = active_state_package(state)
        self.assertTrue(queue_complete)
        self.assertEqual(package["package_id"], last["package_id"])

    def test_output_directory_must_be_empty(self) -> None:
        state = read_json(STATE)
        package, _queue_complete = active_state_package(state)
        package_id = package["package_id"]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            output.mkdir()
            (output / "existing.txt").write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(
                residual_review_bundle.ResidualReviewBundleError,
                "must be empty",
            ):
                residual_review_bundle.build_bundle(ROOT, package_id, output)

    def test_workflow_resolves_final_package_and_uploads_the_bundle(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "residual-review-bundle.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("python tools/residual_review_bundle.py", workflow)
        self.assertIn("queue_complete", workflow)
        self.assertIn("packages[-1]", workflow)
        self.assertIn("verified_pdf_candidate_residual_review_closure.json", workflow)
        self.assertIn('closure.get("scope", {}).get("last_package_id")', workflow)
        self.assertIn('--package-id "${{ steps.package.outputs.package_id }}"', workflow)
        self.assertIn("actions/upload-artifact@", workflow)
        self.assertIn("retention-days: 14", workflow)
        self.assertNotIn("permissions:\n  contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
