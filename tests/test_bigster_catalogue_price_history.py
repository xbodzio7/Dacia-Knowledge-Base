from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "bigster_catalogue_price_history.py"

class BigsterCataloguePriceHistoryTests(unittest.TestCase):
    def test_history_is_deterministic_source_traceable_and_exactly_comparable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "history.json"
            md_path = Path(directory) / "history.md"
            command = [sys.executable, str(SCRIPT), "--json", str(json_path), "--markdown", str(md_path)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            first_json, first_md = json_path.read_text(encoding="utf-8"), md_path.read_text(encoding="utf-8")
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json_path.read_text(encoding="utf-8"), first_json)
            self.assertEqual(md_path.read_text(encoding="utf-8"), first_md)
            data = json.loads(first_json)
            self.assertEqual(len(data["events"]), 13)
            self.assertEqual(data["scope"]["coverage"]["changed"], 0)
            self.assertEqual(data["scope"]["coverage"]["unchanged"], 13)
            self.assertTrue(all(
                e["previous_source_code"] == "src_pl_bigster_price_my26_20261001"
                and e["current_source_code"] == "src_pl_bigster_price_my26_20261102"
                and e["previous_value"] == e["current_value"] and e["delta_value"] == 0
                and e["previous_master_observation_code"] and e["current_master_observation_code"]
                for e in data["events"]
            ))
            self.assertIn("Nie zakładano równoważności nazw", first_md)
            check = subprocess.run(command + ["--check"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

if __name__ == "__main__":
    unittest.main()
