from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_STORED, ZipFile

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import reporting.configuration_comparison_bundle as bundle_module  # noqa: E402
from reporting.configuration_comparison_bundle import (  # noqa: E402
    BundleError,
    create_bundle,
)
from reporting.deterministic_xlsx_model import (  # noqa: E402
    FIXED_TIME,
    MAIN_NS,
    WorkbookError,
)
from reporting.deterministic_xlsx_sheet import (  # noqa: E402
    read_workbook,
    workbook_entries,
)

SELECTED = (
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "duster_iii_expression_ecog100_4x2_manual",
)
SHEET_NAMES = (
    "Overview",
    "Scopes",
    "Configurations",
    "Comparisons",
    "Sources",
    "Artifacts",
)


class ConfigurationComparisonWorkbookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.output = cls.root / "bundle"
        cls.manifest = create_bundle(
            REPOSITORY,
            cls.output,
            direct_codes=SELECTED,
        )
        cls.workbook_path = cls.output / cls.manifest["workbook"]["path"]
        cls.workbook = read_workbook(cls.workbook_path)

    @staticmethod
    def _table(rows: list[list[object]]) -> list[dict[str, object]]:
        headers = [str(item) for item in rows[0]]
        output: list[dict[str, object]] = []
        for row in rows[1:]:
            padded = [*row, *([None] * (len(headers) - len(row)))]
            output.append(dict(zip(headers, padded, strict=True)))
        return output

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_manifest_records_workbook_file(self) -> None:
        record = self.manifest["workbook"]
        self.assertEqual(
            record["path"],
            "configuration-comparison-workbook.xlsx",
        )
        self.assertTrue(self.workbook_path.is_file())
        self.assertEqual(record["size_bytes"], self.workbook_path.stat().st_size)
        self.assertEqual(record["sha256"], self._sha256(self.workbook_path))
        stored = json.loads(
            (self.output / "comparison-bundle-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(stored["workbook"], record)

    def test_package_parts_sheet_order_and_zip_metadata(self) -> None:
        expected = (
            "[Content_Types].xml",
            "_rels/.rels",
            "docProps/app.xml",
            "docProps/core.xml",
            "xl/workbook.xml",
            "xl/_rels/workbook.xml.rels",
            "xl/styles.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
            "xl/worksheets/sheet3.xml",
            "xl/worksheets/sheet4.xml",
            "xl/worksheets/sheet5.xml",
            "xl/worksheets/sheet6.xml",
        )
        self.assertEqual(workbook_entries(self.workbook_path), expected)
        self.assertEqual(tuple(self.workbook), SHEET_NAMES)
        with ZipFile(self.workbook_path) as archive:
            for item in archive.infolist():
                self.assertEqual(item.compress_type, ZIP_STORED)
                self.assertEqual(item.date_time, (1980, 1, 1, 0, 0, 0))

    def test_sheet_dimensions_filters_and_frozen_headers(self) -> None:
        expected_dimensions = (
            "A1:B15",
            "A1:AH4",
            "A1:J6",
            "A1:AQ204",
            "A1:K5",
            "A1:E9",
        )
        with ZipFile(self.workbook_path) as archive:
            for index, expected in enumerate(expected_dimensions, start=1):
                root = ET.fromstring(
                    archive.read(f"xl/worksheets/sheet{index}.xml")
                )
                dimension = root.find(f"{{{MAIN_NS}}}dimension")
                self.assertIsNotNone(dimension)
                assert dimension is not None
                self.assertEqual(dimension.attrib["ref"], expected)
                self.assertIsNotNone(root.find(f".//{{{MAIN_NS}}}pane"))
                auto_filter = root.find(f"{{{MAIN_NS}}}autoFilter")
                if index == 1:
                    self.assertIsNone(auto_filter)
                else:
                    self.assertIsNotNone(auto_filter)

    def test_overview_matches_bundle_summary(self) -> None:
        overview = {
            str(row[0]): row[1]
            for row in self.workbook["Overview"][1:]
        }
        self.assertEqual(overview["workbook_version"], 1)
        self.assertEqual(overview["bundle_version"], self.manifest["version"])
        self.assertEqual(overview["selected_configuration_count"], 5)
        self.assertEqual(overview["scope_group_count"], 3)
        self.assertEqual(overview["comparable_scope_count"], 2)
        self.assertEqual(overview["singleton_scope_count"], 1)
        self.assertFalse(overview["cross_scope_pairs_generated"])
        self.assertEqual(overview["total_pair_count"], 2)
        self.assertEqual(overview["total_difference_count"], 19)
        self.assertFalse(overview["ranking_generated"])
        self.assertFalse(overview["recommendations_generated"])
        self.assertFalse(overview["inferred_values_generated"])

    def test_scopes_preserve_comparable_and_singleton_groups(self) -> None:
        rows = self._table(self.workbook["Scopes"])
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            Counter(row["status"] for row in rows),
            Counter({"comparable": 2, "singleton": 1}),
        )
        singleton = next(row for row in rows if row["status"] == "singleton")
        self.assertEqual(singleton["pair_count"], 0)
        self.assertEqual(singleton["total_differences"], 0)
        self.assertIsNone(singleton["json_path"])
        comparable = [row for row in rows if row["status"] == "comparable"]
        self.assertTrue(all(row["report_as_of"] == date(2026, 6, 26) for row in comparable))
        self.assertEqual(sum(int(row["pair_count"]) for row in rows), 2)

    def test_configurations_preserve_selection_and_metadata(self) -> None:
        rows = self._table(self.workbook["Configurations"])
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            {str(row["configuration_code"]) for row in rows},
            set(SELECTED),
        )
        self.assertTrue(all(row["model_code"] for row in rows))
        self.assertTrue(all(row["version_code"] for row in rows))
        self.assertTrue(all(row["powertrain_label"] for row in rows))
        self.assertTrue(all(row["transmission_type"] for row in rows))
        self.assertTrue(all(row["source_code"] for row in rows))

    def test_comparisons_match_all_report_items_and_states(self) -> None:
        expected_count = 0
        expected_states: Counter[str] = Counter()
        for group in self.manifest["groups"]:
            if group["status"] != "comparable":
                continue
            report = json.loads(
                (self.output / group["files"]["json"]["path"]).read_text(
                    encoding="utf-8"
                )
            )
            for pair in report["pairs"]:
                for domain in ("prices", "technical", "equipment"):
                    expected_count += len(pair[domain])
                    expected_states.update(
                        str(item["comparison"]) for item in pair[domain]
                    )
        rows = self._table(self.workbook["Comparisons"])
        self.assertEqual(len(rows), expected_count)
        self.assertEqual(
            Counter(str(row["comparison"]) for row in rows),
            expected_states,
        )
        self.assertGreater(expected_states["equal"], 0)
        self.assertGreater(expected_states["different"], 0)
        self.assertGreater(expected_states["not_comparable"], 0)

    def test_comparisons_preserve_dates_numbers_and_ranges(self) -> None:
        rows = self._table(self.workbook["Comparisons"])
        self.assertTrue(all(isinstance(row["report_as_of"], date) for row in rows))
        price = next(
            row
            for row in rows
            if row["domain"] == "prices"
            and row["delta_right_minus_left"] is not None
        )
        self.assertIsInstance(
            price["delta_right_minus_left"],
            (int, Decimal),
        )
        ranged = next(
            row
            for row in rows
            if row["left_minimum_value"] is not None
            and row["left_maximum_value"] is not None
        )
        self.assertIsInstance(ranged["left_minimum_value"], (int, Decimal))
        self.assertIsInstance(ranged["left_maximum_value"], (int, Decimal))
        self.assertIsInstance(ranged["left_lower_inclusive"], bool)
        self.assertIsInstance(ranged["left_upper_inclusive"], bool)
        dated = next(
            row
            for row in rows
            if row["left_observation_date"] is not None
        )
        self.assertIsInstance(dated["left_observation_date"], date)

    def test_sources_and_artifacts_match_referenced_records(self) -> None:
        configurations = self._table(self.workbook["Configurations"])
        comparisons = self._table(self.workbook["Comparisons"])
        referenced_sources = {
            str(row["source_code"])
            for row in configurations
            if row["source_code"]
        }
        for row in comparisons:
            for field in ("left_source_code", "right_source_code"):
                if row[field]:
                    referenced_sources.add(str(row[field]))
        sources = self._table(self.workbook["Sources"])
        self.assertEqual(
            {str(row["source_code"]) for row in sources},
            referenced_sources,
        )
        self.assertTrue(all(len(str(row["sha256"])) == 64 for row in sources))

        expected_artifacts = {
            str(record["path"])
            for group in self.manifest["groups"]
            for record in group["files"].values()
        }
        artifacts = self._table(self.workbook["Artifacts"])
        self.assertEqual(
            {str(row["path"]) for row in artifacts},
            expected_artifacts,
        )
        self.assertTrue(all(int(row["size_bytes"]) > 0 for row in artifacts))

    def test_workbook_has_no_formulas_macros_links_or_volatile_time(self) -> None:
        with ZipFile(self.workbook_path) as archive:
            names = archive.namelist()
            self.assertFalse(any("externalLinks" in name for name in names))
            self.assertFalse(any("vbaProject" in name for name in names))
            for name in names:
                if not name.startswith("xl/worksheets/"):
                    continue
                root = ET.fromstring(archive.read(name))
                self.assertEqual(root.findall(f".//{{{MAIN_NS}}}f"), [])
            core = archive.read("docProps/core.xml").decode("utf-8")
        self.assertEqual(core.count(FIXED_TIME), 2)

    def test_repeated_generation_is_byte_identical(self) -> None:
        second = self.root / "second"
        manifest = create_bundle(
            REPOSITORY,
            second,
            direct_codes=SELECTED,
        )
        second_path = second / manifest["workbook"]["path"]
        self.assertEqual(
            self.workbook_path.read_bytes(),
            second_path.read_bytes(),
        )
        self.assertEqual(
            self.manifest["workbook"]["sha256"],
            manifest["workbook"]["sha256"],
        )

    def test_workbook_failure_keeps_bundle_transactional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "bundle"
            with patch.object(
                bundle_module,
                "write_bundle_workbook",
                side_effect=WorkbookError("fixture failure"),
            ):
                with self.assertRaisesRegex(
                    BundleError,
                    "workbook generation failed: fixture failure",
                ):
                    create_bundle(
                        REPOSITORY,
                        output,
                        direct_codes=SELECTED,
                    )
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
