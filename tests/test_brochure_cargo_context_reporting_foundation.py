from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_comparison as comparison  # noqa: E402
import configuration_comparison_context as context_filter  # noqa: E402
import configuration_comparison_item_catalog as item_catalog  # noqa: E402
from reporting import configuration_shortlist as shortlist  # noqa: E402
from reporting import configuration_shortlist_html as shortlist_html  # noqa: E402
from reporting.cargo_context import (  # noqa: E402
    annotate_scalar_values,
    semantic_signature,
    technical_context,
)
from tests.test_configuration_comparison import (  # noqa: E402
    ConfigurationComparisonTests,
)


MAIN_CONTEXT = {
    "measurement_basis_code": "vda_iso_3832",
    "second_row_state_code": "upright",
    "third_row_state_code": "",
    "compartment_code": "main_luggage_compartment",
    "spare_wheel_state_code": "absent",
    "tyre_repair_kit_state_code": "present",
    "double_floor_state_code": "",
}
MAX_CONTEXT = {
    "measurement_basis_code": "vda_iso_3832",
    "second_row_state_code": "folded",
    "third_row_state_code": "",
    "compartment_code": "source_stated_total",
    "spare_wheel_state_code": "",
    "tyre_repair_kit_state_code": "",
    "double_floor_state_code": "",
}


class BrochureCargoContextReportingFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = ConfigurationComparisonTests()

    def _append_rows(self, path: Path, rows: list[list[str]]) -> None:
        with path.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerows(rows)

    def _fixture(
        self,
        root: Path,
        *,
        omit_b_maximum: bool = False,
    ) -> tuple[Path, Path, Path]:
        repository, completeness, evidence = self.base.fixture(root)
        master = repository / "data" / "master"
        self.base.write_csv(
            master / "models.csv",
            ["id", "code", "name", "status"],
            [["1", "model_a", "Model A", "active"], ["2", "model_b", "Model B", "active"]],
        )
        self.base.write_csv(
            master / "versions.csv",
            ["id", "code", "model_code", "name", "status"],
            [
                ["1", "version_a", "model_a", "Version A", "active"],
                ["2", "version_b", "model_b", "Version B", "active"],
            ],
        )
        self._append_rows(
            master / "attributes.csv",
            [["6", "boot_capacity", "Capacities", "Boot capacity", "integer", "L", "", "active"]],
        )
        value_rows = [
            ["5", "a_boot_main", "cfg_a", "boot_capacity", "", "500", "2026-06-01", "src_a", ""],
            ["6", "b_boot_main", "cfg_b", "boot_capacity", "", "500", "2026-06-01", "src_b", ""],
            ["7", "a_boot_max", "cfg_a", "boot_capacity", "", "1500", "2026-06-01", "src_a", ""],
        ]
        if not omit_b_maximum:
            value_rows.append(
                ["8", "b_boot_max", "cfg_b", "boot_capacity", "", "1400", "2026-06-01", "src_b", ""]
            )
        self._append_rows(master / "configuration_attribute_values.csv", value_rows)

        context_header = [
            "id",
            "code",
            "configuration_attribute_value_code",
            "measurement_basis_code",
            "second_row_state_code",
            "third_row_state_code",
            "compartment_code",
            "spare_wheel_state_code",
            "tyre_repair_kit_state_code",
            "double_floor_state_code",
            "notes",
        ]
        context_rows = [
            ["1", "ctx_a_main", "a_boot_main", *MAIN_CONTEXT.values(), ""],
            ["2", "ctx_b_main", "b_boot_main", *MAIN_CONTEXT.values(), ""],
            ["3", "ctx_a_max", "a_boot_max", *MAX_CONTEXT.values(), ""],
        ]
        if not omit_b_maximum:
            context_rows.append(
                ["4", "ctx_b_max", "b_boot_max", *MAX_CONTEXT.values(), ""]
            )
        self.base.write_csv(
            master / "configuration_cargo_volume_contexts.csv",
            context_header,
            context_rows,
        )

        payload = json.loads(completeness.read_text(encoding="utf-8"))
        payload["technical_slots"].append(
            {"attribute_code": "boot_capacity", "fuel_type_code": ""}
        )
        completeness.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
        return repository, completeness, evidence

    def test_signature_preserves_blank_and_explicit_absent(self) -> None:
        blank = dict(MAIN_CONTEXT, spare_wheel_state_code="")
        self.assertNotEqual(semantic_signature(blank), semantic_signature(MAIN_CONTEXT))
        self.assertIn("spare_wheel_state_code=", semantic_signature(blank))
        self.assertIn("spare_wheel_state_code=absent", semantic_signature(MAIN_CONTEXT))
        self.assertTrue(
            technical_context("", MAIN_CONTEXT).startswith("fuel_type_code=;")
        )

    def test_annotation_rejects_collapse_and_keeps_exact_payload(self) -> None:
        values = [
            {"code": "one", "attribute_code": "boot_capacity", "value": "500"},
            {"code": "two", "attribute_code": "boot_capacity", "value": "1500"},
        ]
        contexts = [
            {"configuration_attribute_value_code": "one", "code": "one_ctx", **MAIN_CONTEXT, "notes": ""},
            {"configuration_attribute_value_code": "two", "code": "two_ctx", **MAX_CONTEXT, "notes": ""},
        ]
        annotated = annotate_scalar_values(values, contexts)
        self.assertEqual(len(annotated), 2)
        self.assertNotEqual(
            annotated[0]["_cargo_context_signature"],
            annotated[1]["_cargo_context_signature"],
        )
        self.assertEqual(
            annotated[0]["_cargo_context"]["measurement_basis_code"],
            "vda_iso_3832",
        )

    def test_comparison_preserves_two_context_distinct_boot_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self._fixture(Path(directory))
            report = comparison.collect_report(repository, completeness, evidence)

        items = [
            item
            for item in report["pairs"][0]["technical"]
            if item["attribute_code"] == "boot_capacity"
        ]
        self.assertEqual(len(items), 2)
        self.assertEqual(
            {item["comparison"] for item in items},
            {"equal", "different"},
        )
        contexts = {item["context"] for item in items}
        self.assertEqual(len(contexts), 2)
        self.assertTrue(all(item.get("cargo_context") for item in items))
        maximum = next(
            item
            for item in items
            if item["cargo_context"]["second_row_state_code"] == "folded"
        )
        self.assertEqual(maximum["left"]["value"], "1500")
        self.assertEqual(maximum["right"]["value"], "1400")

    def test_missing_one_context_is_not_compared_to_another(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self._fixture(
                Path(directory), omit_b_maximum=True
            )
            report = comparison.collect_report(repository, completeness, evidence)

        items = [
            item
            for item in report["pairs"][0]["technical"]
            if item["attribute_code"] == "boot_capacity"
        ]
        self.assertEqual(len(items), 2)
        maximum = next(
            item
            for item in items
            if item["cargo_context"]["second_row_state_code"] == "folded"
        )
        self.assertEqual(maximum["comparison"], "not_comparable")
        self.assertEqual(maximum["left"]["state"], "recorded")
        self.assertEqual(maximum["right"]["state"], "missing")
        self.assertEqual(
            maximum["right"]["cargo_context"]["compartment_code"],
            "source_stated_total",
        )

    def test_difference_export_catalog_and_filter_expose_full_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self._fixture(Path(directory))
            report = comparison.collect_report(repository, completeness, evidence)

        rows = comparison.difference_csv_rows(report)
        boot_rows = [row for row in rows if row["item_code"] == "boot_capacity"]
        self.assertEqual(len(boot_rows), 1)
        context = boot_rows[0]["context"]
        self.assertIn("measurement_basis_code=vda_iso_3832", context)
        self.assertIn("second_row_state_code=folded", context)
        self.assertEqual(
            len(
                context_filter.difference_csv_rows(
                    report,
                    difference_item_code="boot_capacity",
                    difference_context=context,
                    known_contexts=context_filter.difference_contexts(report),
                )
            ),
            1,
        )
        catalog_row = next(
            row
            for row in item_catalog.catalog_rows(report)
            if row["item_code"] == "boot_capacity"
        )
        self.assertEqual(catalog_row["context_count"], "2")
        self.assertIn("compartment_code=main_luggage_compartment", catalog_row["contexts"])
        self.assertIn("compartment_code=source_stated_total", catalog_row["contexts"])

    def test_shortlist_json_csv_and_browser_preserve_cargo_observations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, _, _ = self._fixture(Path(directory))
            report = shortlist.collect_report(repository, shortlist.ShortlistCriteria())
            catalog = shortlist_html.collect_browser_catalog(
                repository,
                shortlist.ShortlistCriteria(),
            )

        self.assertEqual(len(report["results"]), 2)
        self.assertTrue(all(len(item["cargo_volumes"]) == 2 for item in report["results"]))
        csv_rows = shortlist.csv_rows(report)
        self.assertTrue(all("cargo_volumes_json" in row for row in csv_rows))
        self.assertTrue(all(len(json.loads(row["cargo_volumes_json"])) == 2 for row in csv_rows))
        cfg_a = next(
            item for item in catalog["configurations"]
            if item["configuration_code"] == "cfg_a"
        )
        cargo_values = [
            state
            for state in cfg_a["comparison_values"].values()
            if state["attribute_code"] == "boot_capacity"
        ]
        self.assertEqual(len(cargo_values), 2)
        self.assertEqual(
            len(
                [
                    facet
                    for facet in catalog["facets"]["comparison_values"]
                    if facet["attribute_code"] == "boot_capacity"
                ]
            ),
            2,
        )

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_selection_export_includes_exact_cargo_volume_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, _, _ = self._fixture(Path(directory))
            catalog = shortlist_html.collect_browser_catalog(
                repository,
                shortlist.ShortlistCriteria(),
            )
            catalog_path = Path(directory) / "catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_selection.js"
            node = subprocess.run(
                [
                    "node",
                    "-e",
                    (
                        "const fs=require('fs');"
                        f"const api=require({json.dumps(str(script))});"
                        f"const catalog=JSON.parse(fs.readFileSync({json.dumps(str(catalog_path))},'utf8'));"
                        "const payload=api.buildSelectionPayload(catalog,['cfg_a']);"
                        "process.stdout.write(JSON.stringify(payload.results[0].cargo_volumes));"
                    ),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(node.returncode, 0, node.stderr)
        values = json.loads(node.stdout)
        self.assertEqual(len(values), 2)
        self.assertEqual(
            {item["cargo_context"]["second_row_state_code"] for item in values},
            {"upright", "folded"},
        )

    def test_empty_production_relation_preserves_existing_context_counts(self) -> None:
        report = comparison.collect_report(
            REPOSITORY,
            REPOSITORY / comparison.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / comparison.DEFAULT_EVIDENCE_SPEC,
        )
        self.assertEqual(
            context_filter.difference_contexts(report),
            (
                "",
                "fuel_type_code=",
                "fuel_type_code=lpg",
                "fuel_type_code=petrol",
                "market=PL;currency_code=PLN",
            ),
        )
        self.assertEqual(len(comparison.difference_csv_rows(report)), 305)


if __name__ == "__main__":
    unittest.main()
