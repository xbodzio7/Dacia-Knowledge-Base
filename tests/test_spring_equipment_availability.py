from __future__ import annotations

import csv
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "import_spring_equipment_availability.py"
SPEC = importlib.util.spec_from_file_location("import_spring_equipment_availability", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
IMPORTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = IMPORTER
SPEC.loader.exec_module(IMPORTER)
MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringEquipmentAvailabilityTests(unittest.TestCase):
    def test_versioned_spec_has_exact_matrix_dimensions(self) -> None:
        spec = IMPORTER.load_spec()
        self.assertEqual(len(spec), 126)
        self.assertEqual(len({row["configuration_code"] for row in spec}), 3)
        self.assertEqual(len({row["attribute_code"] for row in spec}), 42)
        self.assertEqual(set(Counter(row["configuration_code"] for row in spec).values()), {42})

    def test_every_matrix_attribute_is_active_and_compatible(self) -> None:
        attributes = {row["code"]: row for row in rows("attributes.csv")}
        for code in {row["attribute_code"] for row in IMPORTER.load_spec()}:
            self.assertEqual(attributes[code]["status"], "active")
            if code == "rear_seat_folding":
                self.assertEqual(attributes[code]["data_type"], "string")
            else:
                self.assertEqual(attributes[code]["data_type"], "boolean")

    def test_selected_configurations_and_brochure_versions_are_exact(self) -> None:
        configurations = IMPORTER.spring_configurations()
        self.assertEqual(
            {row["code"]: row["version_code"] for row in configurations},
            IMPORTER.CONFIGURATION_VERSIONS,
        )
        version_pairs = {
            (row["source_code"], row["version_code"])
            for row in rows("source_versions.csv")
        }
        for version in IMPORTER.CONFIGURATION_VERSIONS.values():
            self.assertIn((IMPORTER.SOURCE_CODE, version), version_pairs)
        source_links = [
            row for row in rows("source_configurations.csv")
            if row["source_code"] == IMPORTER.SOURCE_CODE
            and row["configuration_code"] in IMPORTER.CONFIGURATION_VERSIONS
        ]
        self.assertEqual(len(source_links), 3)
        self.assertEqual([int(row["id"]) for row in source_links], [248, 249, 250])
        self.assertTrue(all(row["relationship"] == "documents" for row in source_links))

    def test_generated_rows_have_exact_status_distribution(self) -> None:
        generated = IMPORTER.generated_rows()
        self.assertEqual(len(generated), 126)
        self.assertEqual(
            Counter(row["availability_status"] for row in generated),
            Counter({"standard": 106, "optional": 7, "not_available": 13}),
        )

    def test_direct_matrix_cells_preserve_grade_differences(self) -> None:
        status = {
            (row["configuration_code"], row["attribute_code"]): row["availability_status"]
            for row in IMPORTER.generated_rows()
        }
        self.assertEqual(status[("spring_essential_electric70_automatic", "rear_view_camera")], "not_available")
        self.assertEqual(status[("spring_expression_electric70_automatic", "rear_view_camera")], "optional")
        self.assertEqual(status[("spring_extreme_electric100_automatic", "rear_view_camera")], "standard")
        self.assertEqual(status[("spring_extreme_electric100_automatic", "front_parking_sensors")], "optional")
        self.assertEqual(status[("spring_extreme_electric100_automatic", "media_control_system")], "not_available")
        self.assertEqual(status[("spring_expression_electric70_automatic", "dc_charging_supported")], "optional")

    def test_master_rows_match_generated_contract_and_contiguous_suffix(self) -> None:
        actual = [
            row for row in rows("configuration_attribute_availability.csv")
            if row["source_code"] == IMPORTER.SOURCE_CODE
            and row["configuration_code"] in IMPORTER.CONFIGURATION_VERSIONS
        ]
        self.assertEqual(len(actual), 126)
        self.assertEqual(IMPORTER.semantic_payload(actual), IMPORTER.semantic_payload(IMPORTER.generated_rows()))
        self.assertEqual([int(row["id"]) for row in actual], list(range(5771, 5897)))
        self.assertTrue(all(row["observation_date"] == "2026-02-19" for row in actual))

    def test_existing_availability_is_preserved_before_spring_suffix(self) -> None:
        actual = rows("configuration_attribute_availability.csv")
        baseline = [row for row in actual if int(row["id"]) <= 5770]
        spring = [row for row in actual if int(row["id"]) >= 5771]
        self.assertEqual(len(baseline), 5770)
        self.assertEqual(len(spring), 126)
        self.assertFalse(any(row["configuration_code"].startswith("spring_") for row in baseline))

    def test_source_hash_and_evidence_boundary_are_locked(self) -> None:
        self.assertEqual(IMPORTER.file_sha256(IMPORTER.SOURCE), IMPORTER.SOURCE_SHA256)
        codes = {row["attribute_code"] for row in IMPORTER.load_spec()}
        self.assertTrue({"front_parking_sensors", "dc_charging_supported", "remote_firmware_updates"} <= codes)
        self.assertTrue(
            {
                "exterior_color",
                "wheel_design",
                "upholstery_variant",
                "charging_cable_type",
                "front_power_socket_12v",
                "youclip_mount_count",
                "maximum_speed",
            }.isdisjoint(codes)
        )
        self.assertTrue(all(row["source_page"] in {"19", "20"} for row in IMPORTER.load_spec()))


if __name__ == "__main__":
    unittest.main()
