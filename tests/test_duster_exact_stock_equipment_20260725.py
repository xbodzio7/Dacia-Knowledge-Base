from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SOURCE_CODE = "src_pl_duster_exact_stock_equipment_20260724"
PRICE_SOURCE = "src_pl_duster_price_my26_20260703"
DATE = "2026-07-24"
CONFIGURATION_COUNTS = {
    "duster_iii_expression_ecog120_4x2_automatic": 54,
    "duster_iii_extreme_ecog120_4x2_automatic": 75,
    "duster_iii_journey_ecog120_4x2_automatic": 74,
}

def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

class DusterExactStockEquipment20260725Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = rows("sources.csv")
        cls.availability = [row for row in rows("configuration_attribute_availability.csv") if row["source_code"] == SOURCE_CODE]
        cls.commercial = rows("commercial_item_configurations.csv")
        cls.snapshot_path = REPOSITORY / "project" / "sources" / "dacia-pl-duster-exact-stock-equipment-20260724.json"
        cls.snapshot = json.loads(cls.snapshot_path.read_text(encoding="utf-8"))

    def test_snapshot_hash_matches_registered_source(self) -> None:
        source = next(row for row in self.sources if row["code"] == SOURCE_CODE)
        self.assertEqual(hashlib.sha256(self.snapshot_path.read_bytes()).hexdigest(), source["sha256"])
        self.assertEqual(source["document_date"], DATE)

    def test_exact_equipment_counts_and_statuses(self) -> None:
        self.assertEqual(len(self.availability), 203)
        self.assertEqual(Counter(row["availability_status"] for row in self.availability), {"standard": 199, "not_available": 4})
        self.assertEqual(Counter(row["configuration_code"] for row in self.availability), Counter(CONFIGURATION_COUNTS))

    def test_non_inference_boundaries_remain_absent(self) -> None:
        keys = {(row["configuration_code"], row["attribute_code"]) for row in self.availability}
        self.assertFalse(any(attribute == "shark_fin_antenna" for _, attribute in keys))
        self.assertNotIn(("duster_iii_expression_ecog120_4x2_automatic", "side_mirrors_folding"), keys)

    def test_explicit_negative_states_are_preserved(self) -> None:
        negative = {(row["configuration_code"], row["attribute_code"]) for row in self.availability if row["availability_status"] == "not_available"}
        self.assertEqual(negative, {
            ("duster_iii_expression_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
            ("duster_iii_extreme_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
            ("duster_iii_extreme_ecog120_4x2_automatic", "adjustable_boot_floor"),
            ("duster_iii_journey_ecog120_4x2_automatic", "driver_seat_belt_height_adjustment"),
        })

    def test_four_package_offers_and_four_selected_states(self) -> None:
        scoped = [row for row in self.commercial if row["code"].endswith("exact_stock_offer_20260703") or row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(scoped), 8)
        self.assertEqual(Counter(row["availability_status"] for row in scoped), {"optional": 4, "standard": 4})
        selected = [row for row in scoped if row["source_code"] == SOURCE_CODE]
        self.assertTrue(all(row["amount"] == "" for row in selected))
        self.assertEqual({row["price_date"] for row in selected}, {DATE})
        offers = [row for row in scoped if row["source_code"] == PRICE_SOURCE]
        self.assertEqual(sorted(int(row["amount"]) for row in offers), [2200, 2200, 2300, 2300])

    def test_selected_package_components_are_standard(self) -> None:
        standard = {(row["configuration_code"], row["attribute_code"]) for row in self.availability if row["availability_status"] == "standard"}
        for config in ("duster_iii_extreme_ecog120_4x2_automatic", "duster_iii_journey_ecog120_4x2_automatic"):
            for attribute in ("front_parking_sensors", "rear_parking_sensors", "360_camera_system", "blind_spot_monitoring", "heated_front_seats", "heated_steering_wheel", "heated_windscreen"):
                self.assertIn((config, attribute), standard)

    def test_snapshot_preserves_primary_and_supporting_extreme_cards(self) -> None:
        extreme = next(card for card in self.snapshot["cards"] if card["stock_id"] == "121540")
        self.assertEqual(extreme["supporting_current_url"].rsplit("/", 1)[-1], "127567")
        self.assertEqual({row["commercial_item_code"] for row in extreme["selected_packages"]}, {"duster_parking_package", "duster_winter_plus_extreme_package"})

    def test_importer_check_is_green(self) -> None:
        completed = subprocess.run([sys.executable, "tools/import_duster_exact_stock_equipment_20260725.py", "--check"], cwd=REPOSITORY, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

if __name__ == "__main__":
    unittest.main()
