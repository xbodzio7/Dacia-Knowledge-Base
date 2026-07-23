from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
sys.path.insert(0, str(REPOSITORY / "tests"))

import configuration_shortlist as cli  # noqa: E402
import test_configuration_shortlist as shortlist_fixture  # noqa: E402
from reporting.configuration_shortlist import (  # noqa: E402
    ShortlistCriteria,
    collect_report,
)
from reporting.configuration_shortlist_html import (  # noqa: E402
    collect_browser_catalog,
    render_html,
)


class ConfigurationShortlistHtmlTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        helper = shortlist_fixture.ConfigurationShortlistTests()
        repository = helper.fixture(root)
        helper.write_csv(
            repository / "data" / "master" / "attributes.csv",
            (
                "id",
                "code",
                "category",
                "name",
                "data_type",
                "unit",
                "description",
                "status",
            ),
            [
                (1, "heated_steering_wheel", "Comfort", "Heated steering wheel", "boolean", "", "", "active"),
                (2, "navigation_system", "Infotainment", "Navigation system", "boolean", "", "", "active"),
                (3, "rear_view_camera", "Parking", "Rear-view camera", "boolean", "", "", "active"),
            ],
        )
        return repository

    def catalog(
        self,
        root: Path,
        criteria: ShortlistCriteria | None = None,
    ) -> tuple[Path, dict[str, object]]:
        repository = self.fixture(root)
        return repository, collect_browser_catalog(
            repository,
            criteria or ShortlistCriteria(),
        )

    def test_catalog_contains_complete_snapshot_facets_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        self.assertEqual(catalog["as_of"], "2026-01-01")
        self.assertEqual(len(catalog["configurations"]), 4)
        self.assertEqual(
            [item["configuration_code"] for item in catalog["configurations"]],
            ["cfg_a", "cfg_c", "cfg_b", "cfg_d"],
        )
        self.assertEqual(
            [item["code"] for item in catalog["facets"]["models"]],
            ["model_a", "model_b"],
        )
        equipment = {
            item["code"]: item for item in catalog["facets"]["equipment"]
        }
        self.assertEqual(equipment["heated_steering_wheel"]["recorded_configurations"], 3)
        self.assertEqual(equipment["heated_steering_wheel"]["missing_configurations"], 1)
        first = catalog["configurations"][0]
        self.assertEqual(first["catalog_price"]["source_code"], "src_a")
        self.assertEqual(
            first["equipment"]["rear_view_camera"]["source_code"],
            "src_a",
        )

    def test_renderer_is_deterministic_offline_and_escapes_embedded_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        catalog["configurations"][0]["model_name"] = "A </script><script>alert(1)</script>"
        rendered = render_html(catalog)
        self.assertEqual(rendered, render_html(catalog))
        self.assertTrue(rendered.startswith("<!doctype html>"))
        self.assertNotIn("</script><script>alert(1)</script>", rendered)
        self.assertIn("\\u003c/script\\u003e", rendered)
        self.assertNotIn("http://", rendered)
        self.assertNotIn("https://", rendered)
        for control in (
            "models",
            "versions",
            "transmissions",
            "powertrains",
            "minimum-price",
            "maximum-price",
            "seats",
            "required-equipment",
        ):
            self.assertIn(f'id="{control}"', rendered)
        self.assertNotIn('id="required-standard-equipment"', rendered)
        self.assertIn('>Wyposażenie\n      <select id="required-equipment"', rendered)
        self.assertIn('.filters{display:grid;grid-template-columns:1fr', rendered)
        self.assertIn('class="result-card-hero"', rendered)
        self.assertIn('class="configuration-code" hidden', rendered)

    def test_initial_cli_filters_are_embedded_without_reducing_catalog(self) -> None:
        criteria = ShortlistCriteria(
            models=("model_a",),
            transmissions=("automatic",),
            maximum_price=Decimal("95000"),
            required_equipment=("heated_steering_wheel",),
            required_standard_equipment=("navigation_system",),
        )
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory), criteria)
        self.assertEqual(len(catalog["configurations"]), 4)
        self.assertEqual(
            catalog["initial_filters"],
            {
                "models": ["model_a"],
                "versions": [],
                "transmissions": ["automatic"],
                "powertrains": [],
                "minimum_price_pln": None,
                "maximum_price_pln": "95000",
                "seats": None,
                "required_equipment": ["heated_steering_wheel"],
                "required_standard_equipment": ["navigation_system"],
            },
        )
        rendered = render_html(catalog)
        self.assertNotIn('id="required-standard-equipment"', rendered)
        self.assertIn("filters.required_standard_equipment || []", rendered)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_equipment_facets_remove_impossible_combination_before_zero_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_browser.js"
        program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const catalog = JSON.parse(fs.readFileSync(0, "utf8"));
const state = api.reconcileEquipmentSelection(catalog, {
  models: ["model_b"], versions: [], transmissions: [], powertrains: [],
  required_equipment: ["heated_steering_wheel", "navigation_system"],
  required_standard_equipment: []
});
process.stdout.write(JSON.stringify(state));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            input=json.dumps(catalog, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=True,
        )
        state = json.loads(completed.stdout)
        self.assertGreater(state["base_match_count"], 0)
        self.assertGreater(len(state["compatible_configurations"]), 0)
        self.assertEqual(
            set(state["selected_equipment"]) | set(state["removed_equipment"]),
            {"heated_steering_wheel", "navigation_system"},
        )
        self.assertEqual(state["selected_equipment"], ["navigation_system"])
        self.assertEqual(state["removed_equipment"], ["heated_steering_wheel"])
        self.assertNotIn("heated_steering_wheel", state["available_equipment"])
        for code in state["available_equipment"]:
            self.assertIsInstance(code, str)

    def test_historical_catalog_uses_only_records_available_as_of_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(
                Path(directory),
                ShortlistCriteria(as_of="2025-06-01"),
            )
        self.assertEqual(catalog["as_of"], "2025-06-01")
        first = catalog["configurations"][0]
        self.assertEqual(first["configuration_code"], "cfg_a")
        self.assertEqual(first["catalog_price"]["amount"], "65000")
        self.assertEqual(first["number_of_seats"]["state"], "missing")
        self.assertEqual(first["equipment"], {})

    def test_cli_html_contains_full_catalog_while_json_remains_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = self.fixture(root / "repository")
            json_path = root / "shortlist.json"
            html_path = root / "shortlist.html"
            result = cli.main(
                [
                    "--model",
                    "model_a",
                    "--transmission",
                    "automatic",
                    "--json",
                    str(json_path),
                    "--html",
                    str(html_path),
                ],
                repository=repository,
            )
            self.assertEqual(result, 0)
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(
                [item["configuration_code"] for item in report["results"]],
                ["cfg_b"],
            )
            html = html_path.read_text(encoding="utf-8")
            for code in ("cfg_a", "cfg_b", "cfg_c", "cfg_d"):
                self.assertIn(code, html)
            self.assertIn('"models":["model_a"]', html)


    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_browser_control_contract_uses_clean_models_dependent_versions_and_multi_powertrains(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        rendered = render_html(catalog)
        self.assertIn('<label id="versions-field" hidden>Wersje', rendered)
        self.assertIn('<select id="versions" multiple size="5" disabled>', rendered)
        self.assertIn('<select id="transmissions"></select>', rendered)
        self.assertIn('<select id="powertrains" multiple size="5"></select>', rendered)
        self.assertIn("HTMLFormElement.prototype.reset.call(filters)", rendered)

        script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_browser.js"
        program = r"""
const api = require(process.argv[1]);
const versions = [
  {code: "a_one", name: "One", model_code: "model_a"},
  {code: "a_two", name: "Two", model_code: "model_a"},
  {code: "b_one", name: "One", model_code: "model_b"}
];
process.stdout.write(JSON.stringify({
  model: api.modelOptionLabel({code: "model_a", name: "Model A"}),
  version: api.versionOptionLabel(versions[0]),
  none: api.versionsForModels(versions, []).map((item) => item.code),
  modelA: api.versionsForModels(versions, ["model_a"]).map((item) => item.code),
  both: api.versionsForModels(versions, ["model_a", "model_b"]).map((item) => item.code)
}));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            text=True,
            capture_output=True,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["model"], "Model A")
        self.assertNotIn("(", result["model"])
        self.assertEqual(result["version"], "One")
        self.assertEqual(result["none"], [])
        self.assertEqual(result["modelA"], ["a_one", "a_two"])
        self.assertEqual(result["both"], ["a_one", "a_two", "b_one"])

    def run_node(
        self,
        catalog: dict[str, object],
        scenarios: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        script = REPOSITORY / "tools" / "reporting" / "configuration_shortlist_browser.js"
        program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const output = input.scenarios.map((criteria) => {
  const outcome = api.filterCatalog(input.catalog, criteria);
  return {
    codes: outcome.results.map((item) => item.configuration_code),
    summary: outcome.summary
  };
});
process.stdout.write(JSON.stringify(output));
"""
        completed = subprocess.run(
            ["node", "-e", program, str(script)],
            input=json.dumps(
                {"catalog": catalog, "scenarios": scenarios},
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_javascript_filter_matches_python_engine(self) -> None:
        scenarios = [
            ShortlistCriteria(),
            ShortlistCriteria(models=("model_a",)),
            ShortlistCriteria(
                transmissions=("automatic",),
                maximum_price=Decimal("95000"),
            ),
            ShortlistCriteria(seats=7),
            ShortlistCriteria(
                required_equipment=("heated_steering_wheel",),
            ),
            ShortlistCriteria(
                required_standard_equipment=(
                    "heated_steering_wheel",
                ),
            ),
            ShortlistCriteria(
                required_equipment=("navigation_system",),
            ),
        ]
        with tempfile.TemporaryDirectory() as directory:
            repository, catalog = self.catalog(Path(directory))
            browser = self.run_node(
                catalog,
                [
                    {
                        "models": list(item.models),
                        "versions": list(item.versions),
                        "transmissions": list(item.transmissions),
                        "powertrains": list(item.powertrains),
                        "minimum_price_pln": (
                            str(item.minimum_price)
                            if item.minimum_price is not None
                            else None
                        ),
                        "maximum_price_pln": (
                            str(item.maximum_price)
                            if item.maximum_price is not None
                            else None
                        ),
                        "seats": item.seats,
                        "required_equipment": list(
                            item.required_equipment
                        ),
                        "required_standard_equipment": list(
                            item.required_standard_equipment
                        ),
                    }
                    for item in scenarios
                ],
            )
            expected = [collect_report(repository, item) for item in scenarios]
        for browser_result, python_result in zip(browser, expected):
            self.assertEqual(
                browser_result["codes"],
                [
                    item["configuration_code"]
                    for item in python_result["results"]
                ],
            )
            self.assertEqual(
                browser_result["summary"],
                python_result["summary"],
            )

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_browser_only_search_filters_labels_without_mutating_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.catalog(Path(directory))
        result = self.run_node(
            catalog,
            [{"search": "hybrid", "required_equipment": []}],
        )[0]
        self.assertEqual(result["codes"], ["cfg_c", "cfg_d"])
        self.assertEqual(len(catalog["configurations"]), 4)
        self.assertEqual(
            result["summary"]["exclusion_reason_counts"],
            {"search": 2},
        )


if __name__ == "__main__":
    unittest.main()
