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

from reporting.commercial_offers import (  # noqa: E402
    CONFIGURATOR_OBSERVATION_KIND,
    collect_commercial_components,
)
from reporting.configuration_shortlist_technical_observation_release_integration import (  # noqa: E402
    EXPECTED_TECHNICAL_CATEGORIES,
    EXPECTED_TECHNICAL_SOURCE_LINES,
    _exact_observations,
)


class ConfigurationShortlistExactTechnicalObservationFiltersTests(unittest.TestCase):
    @staticmethod
    def canonical_codes() -> list[str]:
        path = (
            REPOSITORY
            / "data"
            / "reporting"
            / "cross_model_configurator_conflict_closure.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [row["canonical_configuration_code"] for row in payload["rows"]]

    def test_exact_technical_observations_join_without_semantic_coercion(self) -> None:
        components = collect_commercial_components(
            REPOSITORY,
            self.canonical_codes(),
            "2026-08-04",
        )
        observations = [
            item
            for items in components.values()
            for item in items
            if item.get("kind") == CONFIGURATOR_OBSERVATION_KIND
        ]
        self.assertEqual(len(observations), 18)
        self.assertEqual(
            sum(len(item["technical_data_categories"]) for item in observations),
            EXPECTED_TECHNICAL_CATEGORIES,
        )
        self.assertEqual(
            sum(len(item["technical_data_source_lines"]) for item in observations),
            EXPECTED_TECHNICAL_SOURCE_LINES,
        )
        self.assertTrue(
            all(
                item["semantic_technical_line_coercion_performed"] is False
                for item in observations
            )
        )
        bigster = next(
            item
            for item in observations
            if item["exact_configuration_code"] == "GGQ0LU"
        )
        self.assertIn(
            "Przyspieszenie 0-100 km/h (s)                                                      10,0",
            bigster["technical_data_source_lines"],
        )
        self.assertEqual(bigster["technical_data_source_pages"], [5])

    def test_partial_observation_bundle_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            reporting = repository / "data" / "reporting"
            reporting.mkdir(parents=True)
            for name in (
                "cross_model_configurator_commercial_data.json",
                "cross_model_configurator_standard_equipment.json",
                "cross_model_configurator_conflict_closure.json",
            ):
                shutil.copy2(REPOSITORY / "data" / "reporting" / name, reporting / name)
            with self.assertRaisesRegex(
                ValueError,
                "cross_model_configurator_technical_data.json",
            ):
                collect_commercial_components(
                    repository,
                    self.canonical_codes(),
                    "2026-08-04",
                )

    def test_release_integration_preserves_exact_counts(self) -> None:
        observations = _exact_observations(REPOSITORY)
        self.assertEqual(len(observations), 18)
        self.assertEqual(
            sum(len(item["technical_data_categories"]) for item in observations),
            EXPECTED_TECHNICAL_CATEGORIES,
        )
        self.assertEqual(
            sum(len(item["technical_data_source_lines"]) for item in observations),
            EXPECTED_TECHNICAL_SOURCE_LINES,
        )

    def test_browser_contract_filters_exact_technical_source_lines(self) -> None:
        script_path = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_equipment_groups.js"
        )
        script = script_path.read_text(encoding="utf-8")
        for required in (
            "configuration_shortlist_equipment_groups_v1_9",
            "Dokładne wiersze danych technicznych",
            "Szukaj w dokładnych wierszach danych technicznych",
            "Dane techniczne dotyczą wyłącznie dokładnie zapisanej konfiguracji",
            "technical_data_source_lines",
            'technical_data: selectedValues("#configurator-technical-data")',
        ):
            self.assertIn(required, script)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not available")
        probe = f"""
require({json.dumps(str(script_path))});
const api = globalThis.DkbConfiguratorObservationFilters;
const observation = {{
  selected_colour: {{value: "biel alpejska"}},
  selected_wheels: {{value: "koła A"}},
  selected_upholstery: {{value: "tapicerka A"}},
  standard_equipment_source_lines: ["wyposażenie A"],
  technical_data_source_lines: ["techniczne A", "techniczne B"]
}};
if (!api.observationMatches(observation, {{
  confirmed_only: true,
  colours: [],
  wheels: [],
  upholsteries: [],
  standard_equipment: [],
  technical_data: ["techniczne B"]
}})) process.exit(1);
if (api.observationMatches(observation, {{
  confirmed_only: false,
  colours: [],
  wheels: [],
  upholsteries: [],
  standard_equipment: [],
  technical_data: ["techniczne C"]
}})) process.exit(2);
"""
        subprocess.run([node, "-e", probe], check=True)


if __name__ == "__main__":
    unittest.main()
