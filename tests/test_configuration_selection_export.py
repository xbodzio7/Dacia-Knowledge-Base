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
  case "normalize_set":
    output = api.normalizeSelection(
      input.catalog,
      new Set(input.payload.codes)
    );
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
      input.payload.codes,
      input.payload.commercial || {}
    );
    break;
  case "json":
    output = api.renderSelectionJson(
      input.catalog,
      input.payload.codes,
      input.payload.commercial || {}
    );
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
  case "comparison":
    output = api.comparisonRows(
      input.catalog,
      input.payload.codes,
      input.payload.equipment || []
    );
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

    def test_selection_accepts_browser_set_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        result = self.run_node(
            catalog,
            "normalize_set",
            {
                "codes": [
                    "cfg_b",
                    "unknown",
                    "cfg_a",
                    "cfg_b",
                ]
            },
        )
        self.assertEqual(result, ["cfg_a", "cfg_b"])

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
        self.assertNotIn("commercial_selection", payload["results"][0])
        self.assertNotIn("commercial_selection", payload["results"][1])
        self.assertNotIn("generated_at", payload)

        commercial_json = self.run_node(
            catalog,
            "json",
            {
                "codes": ["cfg_a"],
                "commercial": {
                    "cfg_a": ["unknown", "nav_package", "nav_package"],
                },
            },
        )
        commercial_payload = json.loads(commercial_json)
        commercial = commercial_payload["results"][0]["commercial_selection"]
        self.assertEqual(commercial["selected_item_codes"], ["nav_package"])
        self.assertEqual(len(commercial["items"]), 1)
        self.assertEqual(commercial["items"][0]["code"], "nav_package")
        self.assertEqual(commercial["items"][0]["amount"], 1200)
        self.assertTrue(commercial["items"][0]["selected_state_observed"])
        self.assertEqual(
            commercial["items"][0]["selected_state_source_code"],
            "src_saved_configuration",
        )
        self.assertEqual(commercial["price_preview"]["base_amount"], 70000)
        self.assertEqual(commercial["price_preview"]["known_surcharge"], 1200)
        self.assertEqual(commercial["price_preview"]["total_amount"], 71200)
        self.assertTrue(commercial["price_preview"]["total_is_complete"])
        self.assertEqual(commercial["price_preview"]["unknown_item_codes"], [])
        self.assertFalse(
            commercial["price_preview"]["compatibility_inference_performed"]
        )

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
                {
                    "codes": ["cfg_b", "cfg_a"],
                    "commercial": {"cfg_a": ["nav_package"]},
                },
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

    def test_comparison_supports_more_than_two_configurations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, catalog = self.fixture(Path(directory))
        comparison = self.run_node(
            catalog,
            "comparison",
            {
                "codes": ["cfg_d", "cfg_a", "cfg_c"],
                "equipment": ["heated_steering_wheel"],
            },
        )
        self.assertEqual(
            [item["configuration_code"] for item in comparison["configurations"]],
            ["cfg_a", "cfg_c", "cfg_d"],
        )
        labels = [row["label"] for row in comparison["rows"]]
        self.assertIn("Cena katalogowa", labels)
        self.assertIn("Moc silnika — benzyna", labels)
        power_row = next(
            row for row in comparison["rows"]
            if row["label"] == "Moc silnika — benzyna"
        )
        self.assertEqual(
            power_row["values"],
            ["90 kW", "brak wpisu w bazie", "brak wpisu w bazie"],
        )
        self.assertIn("Cena z wybranym wyposażeniem", labels)
        for label in (
            "Heated steering wheel",
            "Navigation system",
            "Rear-view camera",
        ):
            self.assertIn(label, labels)
        equipment_rows = [
            row
            for row in comparison["rows"]
            if row["key"].startswith("equipment:")
        ]
        self.assertEqual(len(equipment_rows), 3)
        self.assertEqual(
            {row["category"] for row in equipment_rows},
            {"Komfort i wnętrze", "Multimedia", "Parkowanie"},
        )
        self.assertTrue(
            all(len(row["values"]) == 3 for row in comparison["rows"])
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
            "compare-selection",
            "comparison-panel",
            "comparison-table",
            "comparison-differences-only",
            "close-comparison",
            "download-selection-json",
            "download-selection-codes",
            "selected-list",
        ):
            self.assertIn(f'id="{identifier}"', rendered)
        self.assertIn("interactive_configuration_selection", rendered)
        self.assertIn("commercial_selection", rendered)
        self.assertIn("compatibility_inference_performed", rendered)
        self.assertIn("configuration-select", rendered)
        self.assertIn("Format interaktywnej shortlisty HTML v1.7.", rendered)
        self.assertIn("equipment-picker-scroll", rendered)
        self.assertIn("configuration_shortlist_equipment_groups_v1_9", rendered)
        self.assertIn('document.createElement("details")', rendered)
        self.assertIn("data-collapsible-equipment-group", rendered)
        self.assertIn("equipment-picker-group-summary", rendered)
        self.assertNotIn("vehicle-photo-frame-spring", rendered)
        self.assertIn("equipment-availability-note", rendered)
        self.assertIn("model-picker", rendered)
        self.assertIn("model-thumbnail-host", rendered)
        self.assertIn("vehicle-photo-frame", rendered)
        self.assertIn("config-choice-picker", rendered)
        self.assertIn("Filtruj listę wyposażenia", rendered)
        self.assertIn("comparison-model-thumbnail", rendered)
        self.assertIn("Porównaj wybrane", rendered)
        self.assertIn("Porównanie wielowariantowe", rendered)
        self.assertIn("Pokaż tylko różnice", rendered)
        self.assertIn("--parameter-column:280px", rendered)
        self.assertIn("max-height:calc(100vh - 96px)", rendered)
        self.assertIn('scope="rowgroup"', rendered)
        self.assertIn('aria-hidden="true"', rendered)
        self.assertIn("wszystkie zapisane parametry techniczne", rendered)
        self.assertIn("całe wyposażenie opisane w bazie", rendered)
        self.assertIn("configuration-price-equipment", rendered)
        self.assertIn("Wybrane wyposażenie", rendered)
        self.assertNotIn('id="required-standard-equipment"', rendered)
        self.assertNotIn('id="search"', rendered)
        self.assertNotIn('id="audit-heading"', rendered)
        self.assertIn("Pokaż tylko wybrane", rendered)
        self.assertIn("configuration_shortlist_v12", rendered)
        self.assertIn("dkb:results-rendered", rendered)
        self.assertIn(
            'results.addEventListener("dkb:results-rendered", (event) => {',
            rendered,
        )
        self.assertIn(
            'results.addEventListener("dkb:results-rendered", sync)',
            rendered,
        )
        self.assertNotIn("new MutationObserver(refresh)", rendered)
        self.assertNotIn("new MutationObserver(sync)", rendered)
        self.assertNotIn("configuration_shortlist_v11", rendered)
        self.assertNotIn("http://", rendered)
        self.assertIn("https://www.dacia.pl/media/model-a.png", rendered)

        empty_rendered = render_html(
            {
                "as_of": "2026-08-07",
                "facets": {},
                "configurations": [],
            }
        )
        self.assertIn("configurator_step_navigation_v1", empty_rendered)
        self.assertIn("configurator-step-shell", empty_rendered)
        self.assertIn("Konfigurator krok po kroku", empty_rendered)
        self.assertIn(
            "Kroki wyglądu korzystają wyłącznie z dokładnych zapisów producenta",
            empty_rendered,
        )
        self.assertNotIn('<script src=', empty_rendered)

        step_script = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_equipment_groups.js"
        ).read_text(encoding="utf-8")
        for step_id, label in (
            ("model", "Model"),
            ("version", "Wersja"),
            ("powertrain", "Silnik i skrzynia"),
            ("colour", "Kolor"),
            ("wheels", "Koła"),
            ("upholstery", "Tapicerka"),
            ("commercial", "Pakiety i opcje"),
            ("summary", "Podsumowanie"),
        ):
            self.assertIn(f'id: "{step_id}"', step_script)
            self.assertIn(f'label: "{label}"', step_script)
        self.assertEqual(step_script.count('scope: "exact_observation"'), 3)
        self.assertIn("brak potwierdzonego wyboru", step_script)
        self.assertIn("tylko dokładne obserwacje", step_script)
        self.assertNotIn("exact_current_choice_list", step_script)

        step_style = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_equipment_groups.css"
        ).read_text(encoding="utf-8")
        self.assertIn(".configurator-step-shell", step_style)
        self.assertIn(".configurator-step-list", step_style)
        self.assertIn('.configurator-step[aria-current="step"]', step_style)
        self.assertIn("@media(max-width:1200px)", step_style)
        self.assertIn("@media(max-width:760px)", step_style)

        step_program = r"""
require(process.argv[1]);
const api = globalThis.DkbConfiguratorSteps;
process.stdout.write(JSON.stringify({
  marker: api.MARKER,
  ids: api.STEPS.map((step) => step.id),
  scopes: api.STEPS.map((step) => step.scope)
}));
"""
        completed = subprocess.run(
            [
                "node",
                "-e",
                step_program,
                str(
                    REPOSITORY
                    / "tools"
                    / "reporting"
                    / "configuration_shortlist_equipment_groups.js"
                ),
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        step_result = json.loads(completed.stdout)
        self.assertEqual(
            step_result["marker"],
            "configurator_step_navigation_v1",
        )
        self.assertEqual(
            step_result["ids"],
            [
                "model",
                "version",
                "powertrain",
                "colour",
                "wheels",
                "upholstery",
                "commercial",
                "summary",
            ],
        )
        self.assertEqual(
            step_result["scopes"].count("exact_observation"),
            3,
        )
        self.assertEqual(
            step_result["scopes"][0:3],
            ["catalog_choice"] * 3,
        )
        self.assertEqual(
            step_result["scopes"][-2:],
            ["contextual_offer", "summary"],
        )

        self.assertEqual(rendered, render_html(catalog))


if __name__ == "__main__":
    unittest.main()
