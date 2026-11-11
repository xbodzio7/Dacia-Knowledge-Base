from __future__ import annotations
import csv,sys,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import import_bigster_price_list_commercial_matrix_20261001_20261102 as importer
from reporting.commercial_offers import collect_commercial_components
MASTER=ROOT/"data"/"master"
OCT="src_pl_bigster_price_my26_20261001";NOV="src_pl_bigster_price_my26_20261102"
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def components(code):
    result=collect_commercial_components(ROOT,[code],"2026-11-02")
    return {r["code"]:r for r in result.get(code,[])}
class BigsterCommercialMatrixTests(unittest.TestCase):
    def test_importer_contract(self):
        self.assertEqual(importer.check(),{"new_items":2,"new_mappings":172,"rows_2026_10_01":86,"rows_2026_11_02":86})
    def test_source_and_config_scope(self):
        sources={r["code"]:r for r in read(MASTER/"sources.csv")}
        self.assertEqual(sources[OCT]["sha256"],importer.OCT_SHA)
        self.assertEqual(sources[NOV]["file_path"],"")
        self.assertEqual(sources[NOV]["sha256"],"592f28852118b57fe6bdef75864ea479d9e01bb9af9a166108014eff4ae85b5b")
        self.assertIn("SHA-256 verified from uploaded raw bytes",sources[NOV]["notes"])
        prices=read(MASTER/"configuration_prices.csv")
        a={r["configuration_code"] for r in prices if r["source_code"]==OCT and r["price_date"]=="2026-10-01"}
        b={r["configuration_code"] for r in prices if r["source_code"]==NOV and r["price_date"]=="2026-11-02"}
        self.assertEqual(len(a),13);self.assertEqual(a,b)
        links=read(MASTER/"source_configurations.csv")
        self.assertEqual({r["configuration_code"] for r in links if r["source_code"]==OCT},a)
        self.assertFalse([r for r in links if r["source_code"]==NOV])
    def test_paint_options_registered(self):
        items={r["code"]:r for r in read(MASTER/"commercial_items.csv")}
        for code,name in (("bigster_metallic_paint_option","Lakier metalizowany"),("bigster_two_tone_body_option","Nadwozie dwukolorowe")):
            self.assertEqual(items[code]["name"],name);self.assertEqual(items[code]["item_type"],"option")
            self.assertEqual(items[code]["observation_date"],"2026-10-01");self.assertEqual(items[code]["source_code"],OCT)
    def test_dated_price_matrix(self):
        rows=read(MASTER/"commercial_item_configurations.csv")
        for source,date,metal,two,spare in ((OCT,"2026-10-01",3000,1400,800),(NOV,"2026-11-02",3100,1500,900)):
            subset=[r for r in rows if r["source_code"]==source]
            self.assertEqual(len(subset),86)
            self.assertEqual({int(r["amount"]) for r in subset if r["commercial_item_code"]=="bigster_metallic_paint_option"},{metal})
            self.assertEqual({int(r["amount"]) for r in subset if r["commercial_item_code"]=="bigster_two_tone_body_option"},{two})
            spare_rows=[r for r in subset if r["commercial_item_code"]=="bigster_spare_wheel_option"]
            self.assertEqual(Counter(r["availability_status"] for r in spare_rows),{"unknown":10,"optional":3})
            self.assertEqual({int(r["amount"]) for r in spare_rows if r["availability_status"]=="optional"},{spare})
            self.assertTrue(all(r["price_date"]==date for r in subset))
    def test_unchanged_option_and_package_prices(self):
        rows=read(MASTER/"commercial_item_configurations.csv")
        expected={"bigster_19inch_wheel_option":1200,"bigster_panoramic_roof_option":4300,"bigster_power_tailgate_option":1300,"bigster_media_nav_live_option":2400,"bigster_easy_package":2700,"bigster_parking_package":2200,"bigster_winter_package":1200,"bigster_winter_plus_package":2300}
        for source in (OCT,NOV):
            for code,amount in expected.items():
                found={int(r["amount"]) for r in rows if r["source_code"]==source and r["commercial_item_code"]==code and r["availability_status"]=="optional"}
                self.assertEqual(found,{amount},(source,code))
    def test_unknown_boundary_hides_stale_price_but_not_hybrid155_price(self):
        other=components("bigster_expression_tribrid150_4x4_automatic")["bigster_spare_wheel_option"]
        self.assertEqual(other["availability_status"],"unknown");self.assertIsNone(other["amount"])
        hybrid=components("bigster_expression_hybrid155_4x2_automatic")
        self.assertEqual(hybrid["bigster_spare_wheel_option"]["availability_status"],"optional")
        self.assertEqual(hybrid["bigster_spare_wheel_option"]["amount"],900.0)
        self.assertEqual(hybrid["bigster_metallic_paint_option"]["amount"],3100.0)
        self.assertEqual(hybrid["bigster_media_nav_live_option"]["amount"],2400.0)
        self.assertEqual(hybrid["bigster_easy_package"]["amount"],2700.0)
        self.assertEqual(hybrid["bigster_winter_package"]["amount"],1200.0)
        self.assertEqual(hybrid["bigster_winter_plus_package"]["amount"],2300.0)
