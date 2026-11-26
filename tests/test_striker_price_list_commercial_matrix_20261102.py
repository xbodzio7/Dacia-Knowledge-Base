from __future__ import annotations
import csv,sys,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MASTER=ROOT/"data"/"master";SOURCE="src_pl_striker_price_my26_20261102"
sys.path.insert(0,str(ROOT/"tools"))
import import_striker_price_list_commercial_matrix_20261102 as importer
def rows(name):
 with (MASTER/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
class StrikerCommercialMatrixTests(unittest.TestCase):
 def test_importer_contract_and_exact_totals(self):
  self.assertEqual(importer.check(),{"new_items":11,"new_mappings":121,"optional":60,"standard":3,"not_available":51,"package":7})
 def test_source_identity_and_exact_scope(self):
  s=next(r for r in rows("sources.csv") if r["code"]==SOURCE)
  self.assertEqual((s["external_reference"],s["file_path"],s["sha256"]),(importer.SOURCE_URL,importer.SOURCE_PATH,importer.SOURCE_SHA256))
  links=[r for r in rows("source_configurations.csv") if r["source_code"]==SOURCE]
  self.assertEqual(len(links),11);self.assertEqual({r["configuration_code"] for r in links},set(importer.EXPECTED_CONFIGS))
  prices=[r for r in rows("configuration_prices.csv") if r["source_code"]==SOURCE and r["price_date"]=="2026-11-02"]
  self.assertEqual(len(prices),11);self.assertEqual({r["configuration_code"] for r in prices},set(importer.EXPECTED_CONFIGS))
 def test_exact_item_and_status_distribution(self):
  m=[r for r in rows("commercial_item_configurations.csv") if r["source_code"]==SOURCE]
  self.assertEqual(len(m),121);self.assertEqual(Counter(r["availability_status"] for r in m),Counter({"optional":60,"standard":3,"not_available":51,"package":7}))
  self.assertEqual(Counter(r["commercial_item_code"] for r in m),Counter({c:11 for c in {r["commercial_item_code"] for r in m}}))
  all_mappings=rows("commercial_item_configurations.csv")
  self.assertEqual(len({r["id"] for r in all_mappings}),len(all_mappings))
  self.assertEqual(len({r["code"] for r in all_mappings}),len(all_mappings))
 def test_prices_and_grade_applicability(self):
  m=[r for r in rows("commercial_item_configurations.csv") if r["source_code"]==SOURCE]
  exp={"striker_metallic_paint_option":("3100",11),"striker_all_season_tires_option":("1000",6),"striker_19inch_alloy_wheels_option":("1200",6),"striker_panoramic_glass_roof_option":("4300",3),"striker_heated_washer_nozzles_and_windscreen_option":("1000",3),"striker_winter_package":("1200",7),"striker_winter_plus_package":("2300",7),"striker_techno_package":("1300",4),"striker_techno_2_package":("1300",3),"striker_city_package":("2200",4),"striker_city_2_package":("2200",6)}
  for code,(amount,count) in exp.items():
   found=[r for r in m if r["commercial_item_code"]==code and r["availability_status"]=="optional"]
   self.assertEqual(len(found),count,code);self.assertEqual({r["amount"] for r in found},{amount},code)
  std=[r for r in m if r["commercial_item_code"]=="striker_panoramic_glass_roof_option" and r["availability_status"]=="standard"]
  self.assertEqual(len(std),3);self.assertTrue(all("_extreme_" in r["configuration_code"] for r in std))
 def test_P_marker_is_classified_as_package_per_owner_decision(self):
  m=[r for r in rows("commercial_item_configurations.csv") if r["source_code"]==SOURCE and r["commercial_item_code"]=="striker_heated_washer_nozzles_and_windscreen_option"]
  self.assertEqual(Counter(r["availability_status"] for r in m),Counter({"package":7,"optional":3,"not_available":1}))
  self.assertTrue(all("literal marker P" in r["notes"] and not r["amount"] for r in m if r["availability_status"]=="package"))
 def test_packages_are_not_misrepresented_as_equipment_imports(self):
  it={r["code"]:r for r in rows("commercial_items.csv")}
  for c in ("striker_winter_package","striker_winter_plus_package","striker_techno_package","striker_techno_2_package","striker_city_package","striker_city_2_package"):self.assertEqual(it[c]["item_type"],"package")
  self.assertFalse(any(r["commercial_item_code"].startswith("striker_") for r in rows("commercial_item_attributes.csv")))
 def test_history_and_natural_keys_are_preserved(self):
  m=rows("commercial_item_configurations.csv")
  source_rows=[r for r in m if r["source_code"]==SOURCE]
  self.assertEqual(len(source_rows),121)
  keys=[(r["commercial_item_code"],r["configuration_code"],r["source_code"],r["price_date"]) for r in source_rows]
  self.assertEqual(len(keys),len(set(keys)))
  source_items=[r for r in rows("commercial_items.csv") if r["source_code"]==SOURCE]
  self.assertEqual(len(source_items),11)
if __name__=="__main__":unittest.main()
