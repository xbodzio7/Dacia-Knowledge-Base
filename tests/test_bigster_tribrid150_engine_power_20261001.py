from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import import_configuration_values as importer  # noqa: E402


class BigsterTribrid150EnginePowerTests(unittest.TestCase):
    def test_three_tribrid_configurations_have_exact_engine_power(self) -> None:
        path = (
            ROOT / "data" / "imports" / "configuration_values"
            / "bigster-page6-tribrid150-engine-power-20261001.json"
        )
        spec = importer.load_spec(path)
        expected = {
            "bigster_expression_tribrid150_4x4_automatic",
            "bigster_extreme_tribrid150_4x4_automatic",
            "bigster_journey_tribrid150_4x4_automatic",
        }

        self.assertEqual(spec.attribute_code, "engine_power")
        self.assertEqual(spec.observation_date, "2026-10-01")
        self.assertEqual(spec.source_page, 6)
        self.assertEqual(spec.source_section, "SILNIKI")
        self.assertEqual(
            {row.configuration_code for row in spec.rows},
            expected,
        )
        self.assertEqual({row.value for row in spec.rows}, {"103"})
        self.assertEqual(
            {row.source_text for row in spec.rows},
            {"103 (140) przy 5 000"},
        )
        importer.verify_registered_sources(ROOT, spec, verify_text=False)
        plan = importer.verify_import(ROOT, spec)
        self.assertEqual(plan.missing_rows, ())
        self.assertEqual(len(plan.existing_rows), 3)


if __name__ == "__main__":
    unittest.main()
