from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "jogger_catalogue_price_history.py"


class JoggerCataloguePriceHistoryTests(unittest.TestCase):
    def test_history_is_deterministic_and_does_not_infer_removals(self) -> None:
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
            coverage = data["scope"]["coverage"]
            self.assertEqual(len(data["events"]), 22)
            self.assertEqual(coverage["unchanged"], 11)
            self.assertEqual(coverage["changed"], 0)
            self.assertEqual(coverage["explicitly_unavailable"], 1)
            self.assertEqual(coverage["not_comparable"], 10)
            unavailable = [
                event for event in data["events"]
                if event["disposition"] == "explicitly_unavailable"
            ]
            self.assertEqual(len(unavailable), 1)
            self.assertEqual(
                unavailable[0]["configuration_code"],
                "jogger_essential_7seat_ecog120_manual",
            )
            omitted = [
                event for event in data["events"]
                if event["disposition"] == "not_comparable"
            ]
            self.assertEqual(len(omitted), 10)
            self.assertTrue(all(event["current_value"] is None for event in omitted))
            self.assertTrue(all(
                "not authorize inferring removal" in event["notes"]
                for event in omitted
            ))
            self.assertIn("Nie stwierdzono podwyżek ani obniżek", first_markdown)

            check = subprocess.run(
                command + ["--check"], cwd=ROOT, capture_output=True, text=True
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()
