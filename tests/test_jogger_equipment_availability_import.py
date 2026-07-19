from __future__ import annotations

import csv
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "import_jogger_equipment_availability.py"
SPEC = importlib.util.spec_from_file_location("import_jogger_equipment_availability", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
IMPORTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = IMPORTER
SPEC.loader.exec_module(IMPORTER)
MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerEquipmentAvailabilityImportTests(unittest.TestCase):
    def test_two_versioned_matrices_define_fifty_three_unique_attributes(self) -> None:
        matrix = IMPORTER.load_matrices()
        self.assertEqual(len(matrix), 53)
        self.assertEqual(len({row["attribute_code"] for row in matrix}), 53)

    def test_every_matrix_attribute_is_active_boolean(self) -> None:
        attributes = {row["code"]: row for row in rows("attributes.csv")}
        for matrix in IMPORTER.load_matrices():
            attribute = attributes[matrix["attribute_code"]]
            self.assertEqual(attribute["status"], "active")
            self.assertEqual(attribute["data_type"], "boolean")

    def test_import_covers_exactly_twenty_two_active_jogger_configurations(self) -> None:
        configurations = IMPORTER.jogger_configurations()
        self.assertEqual(len(configurations), 22)
        self.assertEqual(
            Counter(IMPORTER.configuration_group(row) for row in configurations),
            Counter({"essential": 2, "expression_non_hybrid": 4, "expression_hybrid": 2, "extreme": 8, "journey": 6}),
        )

    def test_generated_rows_have_exact_distribution_and_conditional_statuses(self) -> None:
        generated = IMPORTER.generated_rows()
        self.assertEqual(len(generated), 1166)
        self.assertEqual(
            Counter(row["availability_status"] for row in generated),
            Counter({"standard": 920, "optional": 84, "not_available": 162}),
        )
        status = {(row["configuration_code"], row["attribute_code"]): row["availability_status"] for row in generated}
        self.assertEqual(status[("jogger_expression_5seat_tce110_manual", "electronic_parking_brake")], "optional")
        self.assertEqual(status[("jogger_expression_5seat_hybrid155_automatic", "electronic_parking_brake")], "standard")
        self.assertEqual(status[("jogger_extreme_5seat_tce110_manual", "360_camera_system")], "optional")
        self.assertEqual(status[("jogger_journey_5seat_tce110_manual", "360_camera_system")], "standard")

    def test_each_jogger_configuration_receives_fifty_three_attributes(self) -> None:
        counts = Counter(row["configuration_code"] for row in IMPORTER.generated_rows())
        self.assertEqual(len(counts), 22)
        self.assertEqual(set(counts.values()), {53})

    def test_master_rows_match_generated_contract_and_contiguous_suffix(self) -> None:
        actual = [row for row in rows("configuration_attribute_availability.csv") if row["configuration_code"].startswith("jogger_")]
        self.assertEqual(len(actual), 1166)
        self.assertEqual(IMPORTER.semantic_payload(actual), IMPORTER.semantic_payload(IMPORTER.generated_rows()))
        self.assertEqual([int(row["id"]) for row in actual], list(range(1812, 2978)))
        self.assertTrue(all(row["source_code"] == "src_pl_jogger_price_my26_20260401" for row in actual))
        self.assertTrue(all(row["observation_date"] == "2026-04-01" for row in actual))

    def test_existing_sandero_and_duster_availability_is_preserved(self) -> None:
        actual = rows("configuration_attribute_availability.csv")
        jogger = [row for row in actual if row["configuration_code"].startswith("jogger_")]
        duster = [row for row in actual if row["configuration_code"].startswith("duster_iii_")]
        sandero = [row for row in actual if not row["configuration_code"].startswith(("jogger_", "duster_iii_"))]
        self.assertEqual(len(actual), 2977)
        self.assertEqual((len(jogger), len(duster), len(sandero)), (1166, 1392, 419))

    def test_evidence_boundary_and_registered_source_hash_are_locked(self) -> None:
        matrix_codes = {row["attribute_code"] for row in IMPORTER.load_matrices()}
        self.assertTrue({"heated_front_seats", "high_beam_assist", "navigation_system", "360_camera_system"} <= matrix_codes)
        self.assertTrue({"start_stop_system", "rain_sensing_wipers", "exterior_color", "upholstery_variant", "wheel_design"}.isdisjoint(matrix_codes))
        self.assertEqual(IMPORTER.file_sha256(IMPORTER.SOURCE), IMPORTER.SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
