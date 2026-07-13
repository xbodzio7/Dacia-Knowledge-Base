from __future__ import annotations

import csv
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
ATTRIBUTES_PATH = MASTER / "attributes.csv"
VALUES_PATH = MASTER / "configuration_attribute_values.csv"
AVAILABILITY_PATH = MASTER / "configuration_attribute_availability.csv"

EXPECTED_VALUES = {tuple(item) for item in [('sandero_iii_expression_ecog120_manual', 'upholstery_variant', 'materiałowa w kolorze czarnym i wstawkami denim'), ('sandero_iii_expression_ecog120_manual', 'wheel_design', 'ATARA'), ('sandero_iii_expression_ecog120_manual', 'wheel_material', 'steel'), ('sandero_iii_expression_ecog120_manual', 'wheel_size', '16"'), ('sandero_iii_journey_ecog120_manual', 'upholstery_variant', 'materiałowa w kolorze denim i czarnymi wstawkami'), ('sandero_iii_journey_ecog120_manual', 'wheel_design', 'TAMIA'), ('sandero_iii_journey_ecog120_manual', 'wheel_material', 'alloy'), ('sandero_iii_journey_ecog120_manual', 'wheel_size', '16"'), ('sandero_stepway_iii_essential_ecog120_manual', 'upholstery_variant', 'materiałowa stepway'), ('sandero_stepway_iii_essential_ecog120_manual', 'wheel_material', 'steel'), ('sandero_stepway_iii_essential_ecog120_manual', 'wheel_size', '16"'), ('sandero_stepway_iii_expression_ecog120_automatic', 'upholstery_variant', 'materiałowa stepway'), ('sandero_stepway_iii_expression_ecog120_automatic', 'wheel_design', 'ATARA'), ('sandero_stepway_iii_expression_ecog120_automatic', 'wheel_material', 'steel'), ('sandero_stepway_iii_expression_ecog120_automatic', 'wheel_size', '16"'), ('sandero_stepway_iii_expression_ecog120_manual', 'upholstery_variant', 'materiałowa stepway'), ('sandero_stepway_iii_expression_ecog120_manual', 'wheel_design', 'ATARA'), ('sandero_stepway_iii_expression_ecog120_manual', 'wheel_material', 'steel'), ('sandero_stepway_iii_expression_ecog120_manual', 'wheel_size', '16"'), ('sandero_stepway_iii_extreme_ecog120_automatic', 'upholstery_variant', 'microclud extreme'), ('sandero_stepway_iii_extreme_ecog120_automatic', 'wheel_design', 'TAMIA'), ('sandero_stepway_iii_extreme_ecog120_automatic', 'wheel_finish', 'black'), ('sandero_stepway_iii_extreme_ecog120_automatic', 'wheel_material', 'alloy'), ('sandero_stepway_iii_extreme_ecog120_automatic', 'wheel_size', '16"'), ('sandero_stepway_iii_extreme_ecog120_manual', 'upholstery_variant', 'microclud extreme'), ('sandero_stepway_iii_extreme_ecog120_manual', 'wheel_design', 'TAMIA'), ('sandero_stepway_iii_extreme_ecog120_manual', 'wheel_finish', 'black'), ('sandero_stepway_iii_extreme_ecog120_manual', 'wheel_material', 'alloy'), ('sandero_stepway_iii_extreme_ecog120_manual', 'wheel_size', '16"')]}
EXPECTED_CONFIG_COUNTS = Counter({'sandero_iii_expression_ecog120_manual': 4, 'sandero_iii_journey_ecog120_manual': 4, 'sandero_stepway_iii_essential_ecog120_manual': 3, 'sandero_stepway_iii_expression_ecog120_automatic': 4, 'sandero_stepway_iii_expression_ecog120_manual': 4, 'sandero_stepway_iii_extreme_ecog120_automatic': 5, 'sandero_stepway_iii_extreme_ecog120_manual': 5})
SOURCE_SELECTIONS = {'sandero_iii_expression_ecog120_manual': ('16" felgi stalowe ATARA', 'tapicerka materiałowa w kolorze czarnym i wstawkami denim'), 'sandero_iii_journey_ecog120_manual': ('16" felgi aluminiowe TAMIA', 'tapicerka materiałowa w kolorze denim i czarnymi wstawkami'), 'sandero_stepway_iii_essential_ecog120_manual': ('16" felgi stalowe ERALIA', 'tapicerka materiałowa stepway'), 'sandero_stepway_iii_expression_ecog120_automatic': ('16" felgi stalowe ATARA', 'tapicerka materiałowa stepway'), 'sandero_stepway_iii_expression_ecog120_manual': ('16" felgi stalowe ATARA', 'tapicerka materiałowa stepway'), 'sandero_stepway_iii_extreme_ecog120_automatic': ('16" felgi aluminiowe TAMIA BLACK', 'tapicerka microclud extreme'), 'sandero_stepway_iii_extreme_ecog120_manual': ('16" felgi aluminiowe TAMIA BLACK', 'tapicerka microclud extreme')}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoWheelUpholsteryValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.all_values = read_rows(VALUES_PATH)
        cls.rows = [row for row in cls.all_values if 169 <= int(row["id"]) <= 197]
        cls.availability = read_rows(AVAILABILITY_PATH)

    def test_new_attributes_are_active_strings(self) -> None:
        imported = {
            row["code"]: row
            for row in self.attributes
            if row["code"] in {"wheel_design", "upholstery_variant"}
        }
        self.assertEqual(set(imported), {"wheel_design", "upholstery_variant"})
        self.assertEqual({row["data_type"] for row in imported.values()}, {"string"})
        self.assertEqual({row["status"] for row in imported.values()}, {"active"})
        self.assertTrue(all(not row["unit"] for row in imported.values()))

    def test_package_ids_shape_and_count(self) -> None:
        self.assertEqual(len(self.all_values), 197)
        self.assertEqual(len(self.rows), 29)
        self.assertEqual({int(row["id"]) for row in self.rows}, set(range(169, 198)))
        self.assertEqual(
            list(self.rows[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "fuel_type_code", "value", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_configuration_source_and_date_coverage(self) -> None:
        self.assertEqual(
            Counter(row["configuration_code"] for row in self.rows),
            EXPECTED_CONFIG_COUNTS,
        )
        self.assertEqual(len({row["source_code"] for row in self.rows}), 7)
        self.assertEqual({row["observation_date"] for row in self.rows}, {"2026-06-26"})
        self.assertEqual({row["fuel_type_code"] for row in self.rows}, {""})

    def test_values_match_controlled_manifest(self) -> None:
        actual = {
            (row["configuration_code"], row["attribute_code"], row["value"])
            for row in self.rows
        }
        self.assertEqual(actual, EXPECTED_VALUES)

    def test_stepway_essential_conflict_boundary(self) -> None:
        rows = {
            row["attribute_code"]: row
            for row in self.rows
            if row["configuration_code"]
            == "sandero_stepway_iii_essential_ecog120_manual"
        }
        self.assertEqual(
            set(rows),
            {"wheel_size", "wheel_material", "upholstery_variant"},
        )
        self.assertEqual(rows["wheel_material"]["value"], "steel")
        self.assertIn("ERALIA", rows["wheel_material"]["notes"])
        self.assertIn("TAMIA BI-TON", rows["wheel_material"]["notes"])
        self.assertIn("intentionally omitted", rows["wheel_material"]["notes"])

    def test_notes_preserve_section_and_wording(self) -> None:
        for row in self.rows:
            wheel, upholstery = SOURCE_SELECTIONS[row["configuration_code"]]
            if row["attribute_code"] == "upholstery_variant":
                self.assertTrue(
                    row["notes"].startswith("Source page 2, section Tapicerka:")
                )
                self.assertIn(upholstery, row["notes"])
            elif (
                row["configuration_code"]
                == "sandero_stepway_iii_essential_ecog120_manual"
                and row["attribute_code"] == "wheel_material"
            ):
                self.assertTrue(
                    row["notes"].startswith(
                        "Source pages 2-3, sections Felgi/WYGLĄD:"
                    )
                )
            else:
                self.assertTrue(
                    row["notes"].startswith("Source page 2, section Felgi:")
                )
                self.assertIn(wheel, row["notes"])

    def test_values_are_not_availability_booleans(self) -> None:
        forbidden = {
            "wheel_size", "wheel_material", "wheel_design",
            "wheel_finish", "upholstery_variant",
        }
        self.assertFalse(
            any(row["attribute_code"] in forbidden for row in self.availability)
        )

    def test_internal_ordering_criteria_are_excluded(self) -> None:
        combined = "\n".join(
            [*(row["code"] for row in self.attributes),
             *(row["value"] for row in self.rows),
             *(row["notes"] for row in self.rows)]
        ).casefold()
        self.assertNotIn(
            "kryterium techniczne niezbędne do zamówienia klimatyzacji",
            combined,
        )

    def test_package_codes_are_unique(self) -> None:
        self.assertEqual(
            len({row["code"].casefold() for row in self.rows}),
            len(self.rows),
        )


if __name__ == "__main__":
    unittest.main()
