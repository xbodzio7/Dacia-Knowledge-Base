from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_STORED, ZipFile

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import data_product_release as cli  # noqa: E402
import reporting.data_product_release as release_module  # noqa: E402
from reporting.configuration_comparison_bundle import BundleError  # noqa: E402
from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import (  # noqa: E402
    CHECKSUMS_NAME,
    FIXED_ZIP_TIME,
    MANIFEST_NAME,
    ReleaseError,
    archive_name,
    normalize_commit_sha,
    normalize_version,
    parse_checksums,
    release_tag,
    sha256_bytes,
    sha256_file,
    verify_release_assets,
)

VERSION = "1.2.3"
COMMIT_SHA = "1" * 40


class DataProductReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.output = cls.root / "release"
        cls.manifest = create_release_assets(
            REPOSITORY,
            cls.output,
            VERSION,
            COMMIT_SHA,
        )
        cls.archive_path = cls.output / archive_name(VERSION)
        cls.manifest_path = cls.output / MANIFEST_NAME
        cls.checksums_path = cls.output / CHECKSUMS_NAME

    def test_version_and_commit_validation(self) -> None:
        self.assertEqual(normalize_version("0.0.0"), "0.0.0")
        self.assertEqual(normalize_version(VERSION), VERSION)
        self.assertEqual(release_tag(VERSION), "data-products-v1.2.3")
        self.assertEqual(normalize_commit_sha(COMMIT_SHA), COMMIT_SHA)
        for invalid in ("v1.2.3", "1.2", "01.2.3", "1.02.3", "1.2.03", " 1.2.3"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ReleaseError):
                    normalize_version(invalid)
        with self.assertRaises(ReleaseError):
            normalize_commit_sha("A" * 40)

    def test_manifest_summary_and_canonical_assets(self) -> None:
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["release_version"], VERSION)
        self.assertEqual(self.manifest["release_tag"], release_tag(VERSION))
        self.assertEqual(self.manifest["repository_commit"], COMMIT_SHA)
        self.assertEqual(self.manifest["selected_configuration_count"], 69)
        self.assertEqual(self.manifest["scope_group_count"], 18)
        self.assertEqual(self.manifest["comparable_scope_count"], 18)
        self.assertEqual(self.manifest["singleton_scope_count"], 0)
        self.assertFalse(self.manifest["cross_scope_pairs_generated"])
        self.assertFalse(self.manifest["ranking_generated"])
        self.assertFalse(self.manifest["recommendations_generated"])
        self.assertFalse(self.manifest["inferred_values_generated"])
        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            sorted([archive_name(VERSION), MANIFEST_NAME, CHECKSUMS_NAME]),
        )

    def test_archive_inventory_is_safe_sorted_and_deterministic(self) -> None:
        with ZipFile(self.archive_path) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            self.assertEqual(names, sorted(names))
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(len(names), 79)
            self.assertTrue(all(not name.startswith("/") for name in names))
            self.assertTrue(all(".." not in Path(name).parts for name in names))
            self.assertTrue(all("\\" not in name for name in names))
            for item in infos:
                self.assertEqual(item.compress_type, ZIP_STORED)
                self.assertEqual(item.date_time, FIXED_ZIP_TIME)

    def test_shortlist_contains_all_active_configurations_and_formats(self) -> None:
        expected = {
            "shortlist/configuration-shortlist.json",
            "shortlist/configuration-shortlist.md",
            "shortlist/configuration-shortlist.csv",
            "shortlist/configuration-shortlist.html",
        }
        with ZipFile(self.archive_path) as archive:
            self.assertTrue(expected.issubset(set(archive.namelist())))
            report = json.loads(
                archive.read("shortlist/configuration-shortlist.json")
            )
            rows = list(
                csv.DictReader(
                    io.StringIO(
                        archive.read(
                            "shortlist/configuration-shortlist.csv"
                        ).decode("utf-8")
                    )
                )
            )
            html = archive.read(
                "shortlist/configuration-shortlist.html"
            ).decode("utf-8")
        self.assertEqual(report["summary"]["active_configurations"], 69)
        self.assertEqual(report["summary"]["matched_configurations"], 69)
        self.assertEqual(len(report["results"]), 69)
        self.assertEqual(len(rows), 69)
        self.assertIn("<!doctype html>", html.lower())
        self.assertNotIn("http://", html.lower())
        self.assertNotIn("https://", html.lower())

    def test_full_bundle_contains_all_scopes_and_workbook(self) -> None:
        with ZipFile(self.archive_path) as archive:
            bundle = json.loads(
                archive.read(
                    "comparison-bundle/comparison-bundle-manifest.json"
                )
            )
            names = set(archive.namelist())
        self.assertEqual(bundle["selected_configuration_count"], 69)
        self.assertEqual(bundle["scope_group_count"], 18)
        self.assertEqual(bundle["comparable_scope_count"], 18)
        self.assertEqual(bundle["singleton_scope_count"], 0)
        self.assertFalse(bundle["cross_scope_pairs_generated"])
        self.assertEqual(len(bundle["groups"]), 18)
        self.assertTrue(all(group["status"] == "comparable" for group in bundle["groups"]))
        self.assertIn(
            "comparison-bundle/configuration-comparison-workbook.xlsx",
            names,
        )

    def test_manifest_matches_every_archive_member(self) -> None:
        records = self.manifest["files"]
        self.assertEqual(
            [record["path"] for record in records],
            sorted(record["path"] for record in records),
        )
        with ZipFile(self.archive_path) as archive:
            self.assertEqual(
                [record["path"] for record in records],
                archive.namelist(),
            )
            for record in records:
                content = archive.read(record["path"])
                self.assertEqual(record["size_bytes"], len(content))
                self.assertEqual(record["sha256"], sha256_bytes(content))
                self.assertTrue(record["media_type"])

    def test_checksums_match_archive_and_manifest(self) -> None:
        archive = self.manifest["archive"]
        self.assertEqual(archive["path"], archive_name(VERSION))
        self.assertEqual(archive["size_bytes"], self.archive_path.stat().st_size)
        self.assertEqual(archive["sha256"], sha256_file(self.archive_path))
        self.assertEqual(
            parse_checksums(self.checksums_path),
            {
                archive_name(VERSION): sha256_file(self.archive_path),
                MANIFEST_NAME: sha256_file(self.manifest_path),
            },
        )
        self.assertEqual(verify_release_assets(self.output), self.manifest)

    def test_release_notes_have_no_volatile_metadata(self) -> None:
        with ZipFile(self.archive_path) as archive:
            notes = archive.read("RELEASE_NOTES.md").decode("utf-8")
        self.assertIn(f"Data Products v{VERSION}", notes)
        self.assertIn(COMMIT_SHA, notes)
        self.assertIn("Selected configurations: 69", notes)
        self.assertIn("Independent scopes: 18", notes)
        self.assertNotIn("workflow", notes.lower())
        self.assertNotIn("generated at", notes.lower())

    def test_repeated_generation_is_byte_identical(self) -> None:
        second = self.root / "second-release"
        second_manifest = create_release_assets(
            REPOSITORY,
            second,
            VERSION,
            COMMIT_SHA,
        )
        self.assertEqual(self.manifest, second_manifest)
        for name in (archive_name(VERSION), MANIFEST_NAME, CHECKSUMS_NAME):
            self.assertEqual(
                (self.output / name).read_bytes(),
                (second / name).read_bytes(),
            )

    def test_nonempty_output_is_not_overwritten(self) -> None:
        output = self.root / "nonempty"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "must not exist or must be empty"):
            create_release_assets(REPOSITORY, output, VERSION, COMMIT_SHA)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(output.iterdir()), [sentinel])

    def test_failure_keeps_publication_transactional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "release"
            with patch.object(
                release_module,
                "create_bundle",
                side_effect=BundleError("fixture failure"),
            ):
                with self.assertRaisesRegex(
                    ReleaseError,
                    "cannot build data product release: fixture failure",
                ):
                    create_release_assets(
                        REPOSITORY,
                        output,
                        VERSION,
                        COMMIT_SHA,
                    )
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_cli_verifies_existing_release_and_expected_identity(self) -> None:
        self.assertEqual(
            cli.main(
                [
                    "--verify",
                    "--version",
                    VERSION,
                    "--commit-sha",
                    COMMIT_SHA,
                    "--output-directory",
                    str(self.output),
                ],
                repository=REPOSITORY,
            ),
            0,
        )
        self.assertEqual(
            cli.main(
                [
                    "--verify",
                    "--version",
                    "9.9.9",
                    "--output-directory",
                    str(self.output),
                ],
                repository=REPOSITORY,
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
