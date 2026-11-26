from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/import_bigster_brochure_equipment_availability.py"
SPEC = importlib.util.spec_from_file_location("bigster_brochure_equipment_import", PATH)
assert SPEC and SPEC.loader
importer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(importer)
class BigsterBrochurePage22ResidualImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec_rows = importer.spec_records()
        cls.generated = importer.generated_rows()
        cls.page22 = [row for row in cls.spec_rows if row["source_page"] == "22"]
        cls.special = {(row["configuration_code"], row["attribute_code"]): row["availability_status"] for row in cls.spec_rows if row["attribute_code"] in importer.SPECIAL_RULES}
    def test_source_receipt_and_full_contract(self):
        self.assertEqual(importer.sha256(importer.SOURCE), importer.SOURCE_SHA256)
        self.assertEqual(len(self.spec_rows), 557)
        self.assertEqual(len(self.generated), 557)
    def test_page22_rows(self):
        self.assertEqual(len(self.page22), 400)
        self.assertEqual(len({(r["configuration_code"], r["attribute_code"]) for r in self.page22}), len(self.page22))
    def test_all_attributes_are_existing_active_booleans(self):
        from csv import DictReader
        with (ROOT / "data/master/attributes.csv").open(encoding="utf-8-sig", newline="") as stream:
            attributes = {row["code"]: row for row in DictReader(stream)}
        for row in self.spec_rows:
            self.assertEqual(attributes[row["attribute_code"]]["status"], "active")
            self.assertEqual(attributes[row["attribute_code"]]["data_type"], "boolean")
    def test_hybrid155_console_qualifier(self):
        self.assertEqual(len(self.special), 8)
        self.assertEqual({c for c,a in self.special if a=="cooled_centre_armrest"},{"bigster_journey_hybrid155_4x2_automatic","bigster_extreme_hybrid155_4x2_automatic"})
        self.assertFalse(any("hybridg150" in c for c,a in self.special if a=="cooled_centre_armrest"))
    def test_no_duplicate_source_date_slots(self):
        keys=[(r["configuration_code"],r["attribute_code"]) for r in self.generated]
        self.assertEqual(len(keys),len(set(keys)))
if __name__ == "__main__":
    unittest.main()
