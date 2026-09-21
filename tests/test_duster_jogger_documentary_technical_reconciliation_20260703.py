import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(name):
    with (ROOT / "data/master" / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

class DocumentaryTechnical007(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = rows("configuration_attribute_values.csv")
        cls.ranges = rows("configuration_attribute_value_ranges.csv")

    def test_duster_source_configurations(self):
        source = "src_pl_duster_price_my26_20260703"
        values = [r for r in self.values if r["source_code"] == source and r["observation_date"] == "2026-07-03"]
        self.assertEqual(len({r["configuration_code"] for r in values}), 16)
        self.assertGreater(len(values), 300)

    def test_jogger_source_configurations(self):
        source = "src_pl_jogger_price_my26_20260703"
        values = [r for r in self.values if r["source_code"] == source and r["observation_date"] == "2026-07-03"]
        self.assertEqual(len({r["configuration_code"] for r in values}), 22)
        self.assertGreater(len(values), 500)

    def test_jogger_seat_dependent_acceleration(self):
        source = "src_pl_jogger_price_my26_20260703"
        got = {(r["configuration_code"], r["fuel_type_code"]): r["value"] for r in self.values if r["source_code"] == source and r["attribute_code"] == "acceleration_0_100"}
        self.assertEqual(got[("jogger_expression_5seat_ecog120_manual", "lpg")], "10.9")
        self.assertEqual(got[("jogger_expression_7seat_ecog120_manual", "lpg")], "11.0")
        self.assertEqual(got[("jogger_expression_5seat_tce110_manual", "petrol")], "10.5")
        self.assertEqual(got[("jogger_expression_7seat_tce110_manual", "petrol")], "11.2")

    def test_duster_hybrid155_voltage_boundary(self):
        source = "src_pl_duster_price_my26_20260703"
        got = {r["value"] for r in self.values if r["source_code"] == source and r["attribute_code"] == "hybrid_system_voltage"}
        self.assertIn("230", got)

if __name__ == "__main__":
    unittest.main()
