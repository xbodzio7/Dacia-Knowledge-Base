from __future__ import annotations
import csv,sys,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data"/"master"
SOURCE="src_pl_jogger_price_my26_20261001"
sys.path.insert(0,str(ROOT/"tools"))
import import_jogger_price_list_commercial_matrix_20261001 as importer
def rows(name):
    with (MASTER/name).open(encoding="utf-8-sig",newline="") as handle:return list(csv.DictReader(handle))
class JoggerCommercialMatrix20261001Tests(unittest.TestCase):
    def test_importer_contract_and_exact_totals(self):
        self.assertEqual(importer.check(),{"new_items":1,"new_mappings":54,"optional":38,"not_available":16})
    def test_source_identity_and_configuration_boundary(self):
        source=next(r for r in rows("sources.csv") if r["code"]==SOURCE)
        self.assertEqual(source["external_reference"],importer.SOURCE_URL)
        self.assertEqual(source["file_path"],importer.SOURCE_PATH)
        self.assertEqual(source["sha256"],importer.SOURCE_SHA256)
        links=[r for r in rows("source_configurations.csv") if r["source_code"]==SOURCE]
        self.assertEqual(len(links),12)
        self.assertEqual({r["configuration_code"] for r in links},importer.EXPECTED_CONFIGS)
        prices=[r for r in rows("configuration_prices.csv") if r["source_code"]==SOURCE]
        self.assertEqual(len(prices),11)
        self.assertNotIn("jogger_essential_7seat_ecog120_manual",{r["configuration_code"] for r in prices})
    def test_exact_item_and_status_distribution(self):
        mappings=[r for r in rows("commercial_item_configurations.csv") if r["source_code"]==SOURCE]
        self.assertEqual(len(mappings),54)
        self.assertEqual(Counter(r["availability_status"] for r in mappings),Counter({"optional":38,"not_available":16}))
        self.assertEqual(Counter(r["commercial_item_code"] for r in mappings),Counter({
            "jogger_special_nonmetallic_paint_option":12,"jogger_media_nav_option":12,
            "jogger_heated_front_seats_option":6,"jogger_winter_package":12,"jogger_drive_package":12}))
    def test_prices_and_package_semantics_match_printed_cells(self):
        mappings=[r for r in rows("commercial_item_configurations.csv") if r["source_code"]==SOURCE]
        optional=[r for r in mappings if r["availability_status"]=="optional"]
        amounts=Counter((r["commercial_item_code"],r["amount"]) for r in optional)
        self.assertEqual(amounts[("jogger_special_nonmetallic_paint_option","2800")],12)
        self.assertEqual(amounts[("jogger_media_nav_option","1600")],10)
        self.assertEqual(amounts[("jogger_heated_front_seats_option","700")],4)
        self.assertEqual(amounts[("jogger_winter_package","1200")],6)
        self.assertEqual(amounts[("jogger_drive_package","1400")],6)
        heated=[r for r in mappings if r["commercial_item_code"]=="jogger_heated_front_seats_option"]
        self.assertEqual(len(heated),6)
        self.assertFalse(any("_extreme_" in r["configuration_code"] for r in heated))
        self.assertTrue(all(r["price_date"]=="2026-10-01" and r["currency_code"]=="PLN" for r in mappings))
    def test_history_and_natural_keys_are_preserved(self):
        mappings=rows("commercial_item_configurations.csv")
        self.assertEqual(len([r for r in mappings if r["source_code"]=="src_pl_jogger_price_my26_20260703"]),48)
        keys=[(r["commercial_item_code"],r["configuration_code"],r["source_code"]) for r in mappings]
        self.assertEqual(len(keys),len(set(keys)))
        prices=rows("configuration_prices.csv")
        for date in ("2026-04-01","2026-07-03"):
            historical=[r for r in prices if r["configuration_code"]=="jogger_essential_7seat_ecog120_manual" and r["price_date"]==date]
            self.assertEqual(len(historical),1);self.assertEqual(historical[0]["amount"],"82400")
if __name__=="__main__":unittest.main()
