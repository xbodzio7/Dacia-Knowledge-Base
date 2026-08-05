from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

from reporting.commercial_offers import (  # noqa: E402
    CONFIGURATOR_OBSERVATION_KIND,
    collect_commercial_components,
    commercial_offer_rows,
)


class ConfigurationShortlistConfiguratorObservationFiltersTests(unittest.TestCase):
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

    def test_exact_bundle_is_joined_without_cross_phase_inference(self) -> None:
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
            sum(len(item["standard_equipment_source_lines"]) for item in observations),
            1355,
        )
        stepway = next(
            item for item in observations
            if item["exact_configuration_code"] == "U56SQT"
        )
        self.assertEqual(
            stepway["canonical_configuration_code"],
            "sandero_stepway_iii_expression_ecog120_manual",
        )
        self.assertEqual(stepway["source_phase"], "F.2")
        self.assertEqual(stepway["selected_colour"]["value"], "biel alpejska")
        self.assertTrue(stepway["exact_saved_configuration_only"])
        before_observation = collect_commercial_components(
            REPOSITORY,
            self.canonical_codes(),
            "2026-08-03",
        )
        self.assertFalse(
            any(
                item.get("kind") == CONFIGURATOR_OBSERVATION_KIND
                for items in before_observation.values()
                for item in items
            )
        )

    def test_transport_records_do_not_leak_into_commercial_exports(self) -> None:
        rows = commercial_offer_rows(
            REPOSITORY,
            self.canonical_codes(),
            "2026-08-04",
        )
        self.assertFalse(
            any(row.get("kind") == CONFIGURATOR_OBSERVATION_KIND for row in rows)
        )
        self.assertFalse(
            any(
                str(row.get("code", "")).startswith(
                    f"{CONFIGURATOR_OBSERVATION_KIND}::"
                )
                for row in rows
            )
        )

    def test_browser_contract_uses_exact_saved_state_semantics(self) -> None:
        script_path = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_equipment_groups.js"
        )
        script = script_path.read_text(encoding="utf-8")
        for required in (
            'const OBSERVATION_KIND = "configurator_observation"',
            "Dane potwierdzone konfiguracją producenta",
            "Tylko konfiguracje potwierdzone dokładnym zapisem producenta",
            "Wybrany kolor zapisanej konfiguracji",
            "Wybrane koła zapisanej konfiguracji",
            "Wybrana tapicerka zapisanej konfiguracji",
            "Dokładne wiersze wyposażenia standardowego",
            "Nie oznaczają dostępności innych kolorów",
            "configuration.price_components = components.filter",
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
  standard_equipment_source_lines: ["wiersz A", "wiersz B"]
}};
if (!api.observationMatches(observation, {{
  confirmed_only: true,
  colours: ["biel alpejska"],
  wheels: ["koła A"],
  upholsteries: ["tapicerka A"],
  standard_equipment: ["wiersz B"]
}})) process.exit(1);
if (api.observationMatches(observation, {{
  confirmed_only: false,
  colours: ["inny kolor"],
  wheels: [],
  upholsteries: [],
  standard_equipment: []
}})) process.exit(2);
if (api.observationMatches(null, {{
  confirmed_only: true,
  colours: [],
  wheels: [],
  upholsteries: [],
  standard_equipment: []
}})) process.exit(3);
"""
        subprocess.run([node, "-e", probe], check=True)


if __name__ == "__main__":
    unittest.main()
