from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATHS = (
    "data/reporting/jogger_ecog120_manual_completeness.json",
    "data/reporting/jogger_ecog120_automatic_completeness.json",
    "data/reporting/jogger_hybrid155_automatic_completeness.json",
    "data/reporting/jogger_tce110_manual_completeness.json",
)


class JoggerElasticityCompletenessContextTest(unittest.TestCase):
    def test_aligner_check_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/align_jogger_elasticity_completeness_context.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_jogger_elasticity_slots_use_fourth_gear(self) -> None:
        slot_count = 0
        for relative in SCOPE_PATHS:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            slots = [
                slot for slot in payload["technical_slots"]
                if slot["attribute_code"] == "elasticity_80_120"
            ]
            self.assertTrue(slots, relative)
            self.assertTrue(all(slot.get("gear_number") == "4" for slot in slots), relative)
            slot_count += len(slots)
        self.assertEqual(slot_count, 6)

    def test_all_32_jogger_observations_match_a_declared_slot(self) -> None:
        declared: set[tuple[str, str, str, str]] = set()
        for relative in SCOPE_PATHS:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            for configuration in payload["configurations"]:
                for slot in payload["technical_slots"]:
                    if slot["attribute_code"] == "elasticity_80_120":
                        declared.add((
                            configuration["configuration_code"],
                            slot["attribute_code"],
                            slot.get("fuel_type_code", ""),
                            slot.get("gear_number", ""),
                        ))

        with (ROOT / "data/master/configuration_attribute_values.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            observations = [
                row for row in csv.DictReader(handle)
                if row["attribute_code"] == "elasticity_80_120"
                and row["configuration_code"].startswith("jogger_")
            ]

        self.assertEqual(len(observations), 32)
        observed = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
                row["gear_number"],
            )
            for row in observations
        }
        self.assertEqual(observed, declared)


if __name__ == "__main__":
    unittest.main()
