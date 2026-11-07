from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "sandero_stepway_catalogue_price_history.py"


class SanderoCataloguePriceHistoryTests(unittest.TestCase):
    def test_history_generation_is_deterministic_and_source_traceable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "history.json"
            markdown_path = Path(directory) / "history.md"
            command = [
                sys.executable, str(SCRIPT),
                "--json", str(json_path), "--markdown", str(markdown_path),
            ]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            first_json = json_path.read_text(encoding="utf-8")
            first_markdown = markdown_path.read_text(encoding="utf-8")
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json_path.read_text(encoding="utf-8"), first_json)
            self.assertEqual(markdown_path.read_text(encoding="utf-8"), first_markdown)

            data = json.loads(first_json)
            self.assertEqual(len(data["events"]), 19)
            self.assertEqual(data["scope"]["coverage"]["changed"], 15)
            self.assertEqual(data["scope"]["coverage"]["unchanged"], 4)
            self.assertEqual(data["scope"]["coverage"]["not_comparable"], 0)
            self.assertEqual(
                {event["delta_value"] for event in data["events"]},
                {0, 500},
            )
            self.assertTrue(all(
                event["previous_source_code"] == "src_pl_sandero_stepway_price_my26_20260811"
                and event["current_source_code"] == "src_pl_sandero_stepway_price_my26_20261102"
                and event["previous_evidence"].endswith("page 1")
                and event["current_evidence"].endswith("page 1")
                for event in data["events"]
            ))
            unchanged = [e for e in data["events"] if e["disposition"] == "unchanged"]
            self.assertEqual(len(unchanged), 4)
            self.assertTrue(all(e["current_master_observation_code"] is None for e in unchanged))
            self.assertIn("nie utworzono", first_markdown)

            check = subprocess.run(
                command + ["--check"], cwd=ROOT, capture_output=True, text=True
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()
