import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reporting" / "cross_model_configurator_options_packages_accessories_coverage.json"


class CrossModelConfiguratorOptionsCoverageTest(unittest.TestCase):
    def test_verified_zero_entry_boundary(self):
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(payload["scope"]["documents"], 18)
        self.assertEqual(payload["scope"]["saved_configurator_states"], 18)
        self.assertEqual(payload["scope"]["option_entries"], 0)
        self.assertEqual(payload["scope"]["package_entries"], 0)
        self.assertEqual(payload["scope"]["accessory_entries"], 0)
        records = payload["records"]
        self.assertEqual(len(records), 18)
        self.assertEqual(len({row["configurator_code"] for row in records}), 18)
        self.assertTrue(all(row["result"] == "no_option_package_or_accessory_section" for row in records))
        self.assertIn("Do not infer", payload["follow_up"])


if __name__ == "__main__":
    unittest.main()
