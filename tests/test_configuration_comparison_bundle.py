from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import configuration_comparison_bundle as cli  # noqa: E402
from reporting.configuration_comparison_bundle import (  # noqa: E402
    BundleError,
    collect_selection,
    create_bundle,
    discover_scopes,
)

SANDERO_MANUAL = (
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
)
SANDERO_AUTOMATIC = (
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
)
JOGGER_AUTOMATIC = (
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
)
DUSTER_SINGLETON = "duster_iii_expression_ecog100_4x2_manual"


class ConfigurationComparisonBundleTests(unittest.TestCase):
    def write_shortlist(
        self,
        path: Path,
        codes: tuple[str, ...],
        as_of: str = "2026-06-26",
    ) -> None:
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "as_of": as_of,
                    "results": [
                        {"configuration_code": code} for code in codes
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def sha256(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_scope_inventory_maps_all_active_configurations_once(self) -> None:
        scopes = discover_scopes(REPOSITORY)
        self.assertEqual(len(scopes), 18)
        codes = [
            code
            for scope in scopes
            for code in scope.configuration_codes
        ]
        self.assertEqual(len(codes), 69)
        self.assertEqual(len(set(codes)), 69)
        self.assertEqual(
            sum(scope.slug.startswith("duster_") for scope in scopes),
            7,
        )
        self.assertEqual(
            sum(scope.slug.startswith("jogger_") for scope in scopes),
            4,
        )
        self.assertEqual(
            sum(scope.slug.startswith("sandero_") for scope in scopes),
            3,
        )
        self.assertEqual(
            sum(scope.slug.startswith("bigster_") for scope in scopes),
            4,
        )

    def test_selection_combines_direct_and_shortlist_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            shortlist = Path(directory) / "shortlist.json"
            self.write_shortlist(
                shortlist,
                (SANDERO_AUTOMATIC[0], SANDERO_AUTOMATIC[1]),
            )
            selected, sources = collect_selection(
                (
                    SANDERO_AUTOMATIC[0],
                    DUSTER_SINGLETON,
                    DUSTER_SINGLETON,
                ),
                (shortlist,),
            )
        self.assertEqual(
            selected,
            tuple(
                sorted(
                    {
                        *SANDERO_AUTOMATIC,
                        DUSTER_SINGLETON,
                    }
                )
            ),
        )
        self.assertEqual(sources["requested_configuration_count"], 5)
        self.assertEqual(sources["deduplicated_configuration_count"], 3)
        self.assertEqual(
            sources["shortlist_reports"][0]["as_of"],
            "2026-06-26",
        )

    def test_sandero_manual_subset_filters_extra_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            manifest = create_bundle(
                REPOSITORY,
                output,
                direct_codes=SANDERO_MANUAL,
            )
            group = manifest["groups"][0]
            report_path = output / group["files"]["json"]["path"]
            report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["comparable_scope_count"], 1)
        self.assertEqual(manifest["singleton_scope_count"], 0)
        self.assertEqual(group["configuration_codes"], list(SANDERO_MANUAL))
        self.assertEqual(group["pair_count"], 1)
        self.assertEqual(report["scope"]["active_configurations"], 2)
        self.assertEqual(report["scope"]["pair_count"], 1)
        self.assertGreater(group["evidence_summary"]["total"], 0)

    def test_cross_scope_selection_creates_two_reports_and_singleton(self) -> None:
        selected = (
            *SANDERO_AUTOMATIC,
            *JOGGER_AUTOMATIC,
            DUSTER_SINGLETON,
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            manifest = create_bundle(
                REPOSITORY,
                output,
                direct_codes=selected,
            )
            files = sorted(
                path.name for path in output.iterdir() if path.is_file()
            )
        self.assertEqual(manifest["selected_configuration_count"], 5)
        self.assertEqual(manifest["scope_group_count"], 3)
        self.assertEqual(manifest["comparable_scope_count"], 2)
        self.assertEqual(manifest["singleton_scope_count"], 1)
        self.assertFalse(manifest["cross_scope_pairs_generated"])
        statuses = [group["status"] for group in manifest["groups"]]
        self.assertEqual(statuses.count("comparable"), 2)
        self.assertEqual(statuses.count("singleton"), 1)
        self.assertEqual(len(files), 10)

    def test_manifest_file_records_match_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            manifest = create_bundle(
                REPOSITORY,
                output,
                direct_codes=SANDERO_AUTOMATIC,
            )
            group = manifest["groups"][0]
            for record in group["files"].values():
                path = output / record["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, record["size_bytes"])
                self.assertEqual(self.sha256(path), record["sha256"])
            stored = json.loads(
                (output / "comparison-bundle-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(stored, manifest)

    def test_singleton_bundle_writes_workbook_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            manifest = create_bundle(
                REPOSITORY,
                output,
                direct_codes=(DUSTER_SINGLETON, DUSTER_SINGLETON),
            )
            names = sorted(path.name for path in output.iterdir())
        self.assertEqual(manifest["selected_configuration_count"], 1)
        self.assertEqual(manifest["comparable_scope_count"], 0)
        self.assertEqual(manifest["singleton_scope_count"], 1)
        self.assertEqual(
            names,
            [
                "comparison-bundle-manifest.json",
                "configuration-comparison-workbook.xlsx",
            ],
        )

    def test_unknown_code_fails_before_output_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            with self.assertRaisesRegex(
                BundleError,
                "unknown or unmapped configuration",
            ):
                create_bundle(
                    REPOSITORY,
                    output,
                    direct_codes=("unknown_configuration",),
                )
            self.assertFalse(output.exists())

    def test_malformed_shortlist_fails_before_output_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shortlist = root / "shortlist.json"
            shortlist.write_text(
                json.dumps({"results": [{"wrong": "value"}]}),
                encoding="utf-8",
            )
            output = root / "bundle"
            with self.assertRaisesRegex(
                BundleError,
                "has no configuration_code",
            ):
                create_bundle(
                    REPOSITORY,
                    output,
                    shortlist_paths=(shortlist,),
                )
            self.assertFalse(output.exists())

    def test_nonempty_output_directory_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(
                BundleError,
                "must not exist or must be empty",
            ):
                create_bundle(
                    REPOSITORY,
                    output,
                    direct_codes=SANDERO_AUTOMATIC,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_cli_and_bundle_outputs_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shortlist = root / "shortlist.json"
            self.write_shortlist(shortlist, SANDERO_AUTOMATIC)
            first = root / "first"
            second = root / "second"
            result = cli.main(
                [
                    "--shortlist-json",
                    str(shortlist),
                    "--output-directory",
                    str(first),
                ],
                repository=REPOSITORY,
            )
            self.assertEqual(result, 0)
            create_bundle(
                REPOSITORY,
                second,
                shortlist_paths=(shortlist,),
            )
            first_files = {
                path.relative_to(first): path.read_bytes()
                for path in first.rglob("*")
                if path.is_file()
            }
            second_files = {
                path.relative_to(second): path.read_bytes()
                for path in second.rglob("*")
                if path.is_file()
            }
        self.assertEqual(first_files, second_files)


if __name__ == "__main__":
    unittest.main()
