from __future__ import annotations

import csv
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "import_duster_equipment_availability.py"
SPEC = importlib.util.spec_from_file_location(
    "import_duster_equipment_availability",
    MODULE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
IMPORTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = IMPORTER
SPEC.loader.exec_module(IMPORTER)

MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterEquipmentAvailabilityImportTests(unittest.TestCase):
    def test_two_declarative_matrices_define_fifty_eight_unique_attributes(self) -> None:
        matrix = IMPORTER.load_matrices()
        self.assertEqual(len(matrix), 58)
        self.assertEqual(len({row["attribute_code"] for row in matrix}), 58)

    def test_every_matrix_attribute_is_active_in_the_canonical_catalogue(self) -> None:
        matrix_codes = {row["attribute_code"] for row in IMPORTER.load_matrices()}
        active = {
            row["code"] for row in rows("attributes.csv")
            if row["status"] == "active"
        }
        self.assertTrue(matrix_codes <= active)

    def test_import_covers_exactly_twenty_four_active_duster_configurations(self) -> None:
        configurations = IMPORTER.duster_configurations()
        self.assertEqual(len(configurations), 24)
        self.assertEqual(
            {row["version_code"] for row in configurations},
            {
                "duster_iii_essential",
                "duster_iii_expression",
                "duster_iii_extreme",
                "duster_iii_journey",
                "duster_iii_journey_plus",
            },
        )

    def test_generated_rows_have_the_exact_status_distribution(self) -> None:
        generated = IMPORTER.generated_rows()
        self.assertEqual(len(generated), 1392)
        self.assertEqual(
            Counter(row["availability_status"] for row in generated),
            Counter({"standard": 1092, "optional": 112, "not_available": 188}),
        )

    def test_each_duster_configuration_receives_fifty_eight_attributes(self) -> None:
        counts = Counter(
            row["configuration_code"] for row in IMPORTER.generated_rows()
        )
        self.assertEqual(set(counts.values()), {58})
        self.assertEqual(len(counts), 24)

    def test_master_rows_match_the_generated_contract(self) -> None:
        actual = [
            row for row in rows("configuration_attribute_availability.csv")
            if row["configuration_code"].startswith("duster_iii_")
        ]
        self.assertEqual(len(actual), 1392)
        self.assertEqual(
            IMPORTER.semantic_payload(actual),
            IMPORTER.semantic_payload(IMPORTER.generated_rows()),
        )

    def test_existing_sandero_availability_is_preserved(self) -> None:
        actual = rows("configuration_attribute_availability.csv")
        sandero = [
            row for row in actual
            if not row["configuration_code"].startswith(("duster_iii_", "jogger_"))
        ]
        self.assertEqual(len(actual), 2977)
        self.assertEqual(len(sandero), 419)

    def test_evidence_boundary_excludes_ambiguous_domains(self) -> None:
        matrix_codes = {row["attribute_code"] for row in IMPORTER.load_matrices()}
        self.assertTrue({
            "heated_front_seats",
            "high_beam_assist",
            "navigation_system",
            "wireless_charging",
        } <= matrix_codes)
        self.assertTrue({
            "exterior_color",
            "upholstery_variant",
            "wheel_size",
            "adaptive_cruise_control",
            "driver_seat_lumbar_adjustment",
            "passenger_seat_adjustment",
        }.isdisjoint(matrix_codes))
        self.assertEqual(
            IMPORTER.file_sha256(IMPORTER.SOURCE),
            IMPORTER.SOURCE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
