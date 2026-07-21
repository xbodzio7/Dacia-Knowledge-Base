from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
sys.path.insert(0, str(REPOSITORY / "tests"))

import test_configuration_shortlist_html as shortlist_html_fixture  # noqa: E402
from reporting.configuration_comparison_bundle import (  # noqa: E402
    collect_selection,
)
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import (  # noqa: E402
    collect_browser_catalog,
)
from reporting.configuration_shortlist_selection_html import (  # noqa: E402
    render_html,
)


@unittest.skipUnless(shutil.which("node"), "Node.js is required")
class ConfigurationSelectionExportTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, dict[str, object]]:
        helper = shortlist_html_fixture.ConfigurationShortlistHtmlTests()
        repository = helper.fixture(root)
        catalog = collect_browser_catalog(
            repository,
            ShortlistCriteria(),
        )
        return repository, catalog

    def run_node(
        self,
        catalog: dict[str, object],
        operation: str,
        payload: dict[str, object],
    ) -> object:
        script = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_selection.js"
        )
        program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const input = JSON.parse(fs.readFileSync(0, "utf8"));
let output;
switch (input.operation) {
  case "normalize":
    output = api.normalizeSelection(input.catalog, input.payload.codes);
    break;
  case "union":
    output = api.unionSelection(
      input.catalog,
      input.payload.selected,
      input.payload.visible
    );
    break;
  case "remove":
    output = api.removeSelection(
      input.catalog,
      input.payload.selected,
      input.payload.code
    );
    break;
  case "payload":
    output = api.buildSelectionPayload(
      input.catalog,
      input.payload.codes
    );
    break;
  case "json":
    output = api.renderSelectionJson(input.catalog, input.payload.codes);
    break;
  case "codes":
    output = api.renderCodeList(input.catalog, input.payload.codes);
    break;
  case "filenames":
    output = {
      json: api.exportFilename(input.catalog, input.payload.codes, "json"),
      txt: api.exportFilename(input.catalog, input.payload.codes, "txt")
    };
    break;
  default:
    throw new Error(`unknown operation ${input.operation}`);
}
process.stdout.write(JSON.stringify(output));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            input=json.dumps(
                {
                    "catalog": catalog,
                    "operation": operation,
                    "payload": payload,
                },
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    def test_selection_normalizes_order_duplicates_and_unknown_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        result = self.run_node(
            catalog,
            "normalize",
            {
                "codes": [
                    "cfg_d",
                    "unknown",
                    "cfg_a",
                    "cfg_d",
                    " cfg_c ",
                ]
            },
        )
        self.assertEqual(result, ["cfg_a", "cfg_c", "cfg_d"])

    def test_visible_selection_is_union_and_persists_hidden_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        result = self.run_node(
            catalog,
            "union",
            {
                "selected": ["cfg_a"],
                "visible": ["cfg_d", "cfg_c"],
            },
        )
        self.assertEqual(result, ["cfg_a", "cfg_c", "cfg_d"])
        changed_view = self.run_node(
            catalog,
            "union",
            {"selected": result, "visible": ["cfg_b"]},
        )
        self.assertEqual(
            changed_view,
            ["cfg_a", "cfg_c", "cfg_b", "cfg_d"],
        )

    def test_individual_removal_preserves_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        result = self.run_node(
            catalog,
            "remove",
            {
                "selected": ["cfg_d", "cfg_a", "cfg_c"],
                "code": "cfg_c",
            },
        )
        self.assertEqual(result, ["cfg_a", "cfg_d"])

    def test_json_payload_is_deterministic_and_preserves_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        first = self.run_node(
            catalog,
            "json",
            {"codes": ["cfg_b", "cfg_a", "cfg_b"]},
        )
        second = self.run_node(
            catalog,
            "json",
            {"codes": ["cfg_a", "cfg_b"]},
        )
        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(
            payload["export_type"],
            "interactive_configuration_selection",
        )
        self.assertEqual(payload["as_of"], "2026-01-01")
        self.assertEqual(
            payload["selection_summary"],
            {
                "selected_configuration_count": 2,
                "catalog_configuration_count": 4,
            },
        )
        self.assertEqual(
            [item["configuration_code"] for item in payload["results"]],
            ["cfg_a", "cfg_b"],
        )
        self.assertEqual(
            payload["results"][0]["catalog_price"]["source_code"],
            "src_a",
        )
        self.assertNotIn("generated_at", payload)

    def test_plain_codes_and_filenames_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        codes = self.run_node(
            catalog,
            "codes",
            {"codes": ["cfg_d", "cfg_a"]},
        )
        filenames = self.run_node(
            catalog,
            "filenames",
            {"codes": ["cfg_d", "cfg_a"]},
        )
        self.assertEqual(codes, "cfg_a\ncfg_d\n")
        self.assertEqual(
            filenames,
            {
                "json": (
                    "dacia-configuration-selection-2026-01-01-2.json"
                ),
                "txt": (
                    "dacia-configuration-selection-2026-01-01-2.txt"
                ),
            },
        )

    def test_empty_selection_has_valid_empty_exports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        payload = self.run_node(
            catalog,
            "payload",
            {"codes": []},
        )
        codes = self.run_node(catalog, "codes", {"codes": []})
        self.assertEqual(payload["selection_summary"]["selected_configuration_count"], 0)
        self.assertEqual(payload["results"], [])
        self.assertEqual(codes, "")

    def test_exported_json_is_consumed_by_comparison_bundle_parser(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, catalog = self.fixture(root / "repository")
            rendered = self.run_node(
                catalog,
                "json",
                {"codes": ["cfg_b", "cfg_a"]},
            )
            export_path = root / "selection.json"
            export_path.write_text(rendered, encoding="utf-8")
            selected, sources = collect_selection((), (export_path,))
        self.assertEqual(selected, ("cfg_a", "cfg_b"))
        self.assertEqual(
            sources["shortlist_reports"][0]["configuration_count"],
            2,
        )
        self.assertEqual(
            sources["shortlist_reports"][0]["as_of"],
            "2026-01-01",
        )

    def test_html_contains_selection_controls_and_offline_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        rendered = render_html(catalog)
        for identifier in (
            "selection-panel",
            "selected-count",
            "select-visible",
            "clear-selection",
            "download-selection-json",
            "download-selection-codes",
            "selected-list",
        ):
            self.assertIn(f'id="{identifier}"', rendered)
        self.assertIn("interactive_configuration_selection", rendered)
        self.assertIn("configuration-select", rendered)
        self.assertIn("Format interaktywnej shortlisty HTML v1.2.", rendered)
        self.assertIn("equipment-picker-scroll", rendered)
        self.assertIn("Pokaż tylko wybrane", rendered)
        self.assertIn("configuration_shortlist_v12", rendered)
        self.assertNotIn("configuration_shortlist_v11", rendered)
        self.assertNotIn("http://", rendered)
        self.assertNotIn("https://", rendered)
        self.assertEqual(rendered, render_html(catalog))


if __name__ == "__main__":
    unittest.main()
