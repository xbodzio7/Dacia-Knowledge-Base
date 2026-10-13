import csv
import json
import unittest
from pathlib import Path


class JoggerPriceListEquipmentMatrix025Tests(unittest.TestCase):
    def test_matrix_is_source_dated_unique_and_covers_all_configurations(self):
        report_path = Path("data/reporting/jogger_price_list_equipment_matrix_025_20260927.json")
        manifest = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["result"]["configurations"], 22)
        self.assertEqual(manifest["result"]["new_rows"], 520)

        rows = list(
            csv.DictReader(
                Path("data/master/configuration_attribute_availability.csv").open(
                    encoding="utf-8", newline=""
                )
            )
        )
        ids = [row["id"] for row in rows]
        codes = [row["code"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(codes), len(set(codes)))

        matrix_rows = [
            row
            for row in rows
            if row["source_code"] == "src_pl_jogger_price_my26_20260703"
            and 9284 <= int(row["id"]) <= 9803
        ]
        self.assertEqual(len(matrix_rows), 520)
        self.assertEqual(len({row["configuration_code"] for row in matrix_rows}), 22)
        self.assertTrue(all(row["observation_date"] == "2026-07-03" for row in matrix_rows))
        self.assertTrue(all(row["configuration_code"].startswith("jogger_") for row in matrix_rows))


if __name__ == "__main__":
    unittest.main()
