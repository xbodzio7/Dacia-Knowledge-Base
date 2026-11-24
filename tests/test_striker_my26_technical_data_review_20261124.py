from __future__ import annotations
import csv, json, unittest
from pathlib import Path
from tools.import_configuration_values import load_spec as load_value_spec, verify_import as verify_value_import, verify_registered_sources
from tools.import_configuration_value_ranges import load_spec as load_range_spec, verify_import as verify_range_import
ROOT=Path(__file__).resolve().parents[1]; SOURCE="src_pl_striker_price_my26_20261102"
VALUE_DIR=ROOT/"data/imports/configuration_values"; RANGE_DIR=ROOT/"data/imports/configuration_value_ranges"
CONFIGS={"striker_essential_mildhybridg140_4x2_manual","striker_expression_mildhybridg140_4x2_manual","striker_expression_mildhybridg140_4x2_automatic","striker_extreme_mildhybridg140_4x2_automatic","striker_journey_mildhybridg140_4x2_automatic","striker_expression_hybrid150_4x4_automatic","striker_extreme_hybrid150_4x4_automatic","striker_journey_hybrid150_4x4_automatic","striker_expression_hybrid155_4x2_automatic","striker_extreme_hybrid155_4x2_automatic","striker_journey_hybrid155_4x2_automatic"}
def read(p):
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
class StrikerMy26TechnicalDataReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.values=read(ROOT/"data/master/configuration_attribute_values.csv");cls.ranges=read(ROOT/"data/master/configuration_attribute_value_ranges.csv");cls.sources=read(ROOT/"data/master/sources.csv");cls.links=read(ROOT/"data/master/source_configurations.csv")
  cls.sv=[r for r in cls.values if r["source_code"]==SOURCE];cls.sr=[r for r in cls.ranges if r["source_code"]==SOURCE]
 def find(self,c,a,f=""):return [r for r in self.sv if r["configuration_code"]==c and r["attribute_code"]==a and r["fuel_type_code"]==f]
 def test_source_registry_and_exact_configuration_scope(self):
  s=[r for r in self.sources if r["code"]==SOURCE];self.assertEqual(len(s),1);self.assertEqual((s[0]["document_date"],s[0]["market"],s[0]["file_path"],s[0]["sha256"]),("2026-11-02","PL","PDF/Cenniki/striker-price.pdf","d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35"))
  links=[r for r in self.links if r["source_code"]==SOURCE];self.assertEqual({r["configuration_code"] for r in links},CONFIGS);self.assertEqual(len(links),11);self.assertTrue(all(r["relationship"]=="documents" for r in links))
 def test_exact_import_spec_counts_and_master_totals(self):
  self.assertEqual(len(list(VALUE_DIR.glob("striker_my26_technical_*_20261102.json")),42);self.assertEqual(len(list(RANGE_DIR.glob("striker_my26_technical_*_20261102.json")),3)
  self.assertEqual(len(self.sv),423);self.assertEqual(len(self.sr),21);self.assertEqual(len({r["id"] for r in self.sv}),423);self.assertEqual(len({r["code"] for r in self.sv}),423);self.assertEqual(len({r["id"] for r in self.sr}),21);self.assertEqual(len({r["code"] for r in self.sr}),21)
 def test_every_scalar_and_range_spec_verifies_against_master(self):
  for p in sorted(VALUE_DIR.glob("striker_my26_technical_*_20261102.json")):self.assertFalse(verify_value_import(ROOT,load_value_spec(p)).missing_rows,p.name)
  for p in sorted(RANGE_DIR.glob("striker_my26_technical_*_20261102.json")):self.assertFalse(verify_range_import(ROOT,load_range_spec(p)).missing_rows,p.name)
 def test_archived_source_hash_and_page_text_boundaries(self):
  verify_registered_sources(ROOT,load_value_spec(VALUE_DIR/"striker_my26_technical_engine_power_20261102.json"),verify_text=True)
  verify_registered_sources(ROOT,load_value_spec(VALUE_DIR/"striker_my26_technical_overall_length_20261102.json"),verify_text=False)
 def test_powertrain_types_and_engine_facts(self):
  for c in CONFIGS:
   h="_hybrid155_" in c;t="hev" if h else "mhev";d="1789" if h else "1199";cy="4" if h else "3";val="16" if h else "12";p="80" if h else "103";tor="172" if h else "230"
   for a,v in (("engine_type",t),("hybrid_system_type",t),("engine_displacement",d),("cylinder_count",cy),("total_valve_count",val),("engine_power",p),("engine_torque",tor),("emission_standard","euro_6e_bis"),("particulate_filter","true")):
    f=self.find(c,a);self.assertEqual(len(f),1,(c,a));self.assertEqual(f[0]["value"],v,(c,a))
 def test_hybrid_motor_battery_and_voltage_facts(self):
  for c in CONFIGS:
   h="_hybrid155_" in c;self.assertEqual(self.find(c,"hybrid_system_voltage")[0]["value"],"280" if h else "48");self.assertEqual(self.find(c,"hybrid_battery_capacity_source_stated")[0]["value"],"1.4" if h else "0.839")
   if "_hybrid150_" in c:self.assertEqual(self.find(c,"traction_motor_power")[0]["value"],"10");self.assertFalse(self.find(c,"hybrid_system_power_total"))
   if h:
    for a,v in (("traction_motor_power","36"),("starter_generator_power","15"),("hybrid_system_power_total","116"),("electric_motor_torque","205"),("electric_motor_torque_rpm","1630")):self.assertEqual(self.find(c,a)[0]["value"],v)
 def test_fuel_specific_acceleration_tank_and_injection(self):
  for c in CONFIGS:
   if "_mildhybridg140_" in c:
    e=("10.6","10.8") if c.endswith("_manual") else ("10.3","10.4");self.assertEqual(self.find(c,"acceleration_0_100","petrol")[0]["value"],e[0]);self.assertEqual(self.find(c,"acceleration_0_100","lpg")[0]["value"],e[1])
    for f in ("petrol","lpg"):self.assertEqual(self.find(c,"fuel_tank_capacity",f)[0]["value"],"50")
    self.assertEqual(self.find(c,"injection_type","petrol")[0]["value"],"direct_injection");self.assertEqual(self.find(c,"injection_type","lpg")[0]["value"],"multi_point_injection")
   else:self.assertEqual(self.find(c,"acceleration_0_100")[0]["value"],"9.6" if "_hybrid150_" in c else "9.5");self.assertEqual(self.find(c,"fuel_tank_capacity")[0]["value"],"50")
 def test_co2_and_consumption_ranges_are_not_flattened(self):
  mild=[c for c in CONFIGS if "_mildhybridg140_" in c];self.assertEqual(len([r for r in self.sr if r["attribute_code"]=="co2_emissions"]),10);self.assertEqual(len([r for r in self.sr if r["attribute_code"]=="fuel_consumption_combined"]),5);self.assertEqual(len([r for r in self.sr if r["attribute_code"]=="max_power_rpm"]),6)
  for c in mild:
   for f in ("petrol","lpg"):self.assertTrue(any(r["configuration_code"]==c and r["attribute_code"]=="co2_emissions" and r["fuel_type_code"]==f for r in self.sr))
  for c in CONFIGS:
   e="4.2" if "_hybrid155_" in c else "5.3" if "_hybrid150_" in c or c.endswith("_manual") else "5.4";self.assertEqual(self.find(c,"fuel_consumption_combined")[0]["value"],e)
  for c in [x for x in CONFIGS if "_hybrid155_" in x]:self.assertFalse(self.find(c,"co2_emissions"));self.assertFalse(any(r["configuration_code"]==c and r["attribute_code"]=="co2_emissions" for r in self.sr))
 def test_dimensions_are_source_dated_and_exact(self):
  for c in CONFIGS:
   for a,v in (("overall_length","4620"),("overall_width","1824"),("overall_width_with_mirrors","2086"),("wheelbase","2704"),("front_track","1574"),("rear_track","1548"),("front_overhang","894"),("rear_overhang","1022"),("seasonal_tyre_type","summer")):self.assertEqual(self.find(c,a)[0]["value"],v)
   four="_hybrid150_" in c
   for a,v in (("overall_height","1541" if four else "1525"),("height_with_tailgate_open","2087" if four else "2069"),("ground_clearance","200" if four else "190")):self.assertEqual(self.find(c,a)[0]["value"],v)
 def test_mass_and_luggage_facts_preserve_source_semantics(self):
  for c in CONFIGS:
   gr="h150" if "_hybrid150_" in c else "h155" if "_hybrid155_" in c else "auto" if "_automatic" in c else "manual";e={"manual":("1915","1500","515","602"),"auto":("1930","1500","503","602"),"h150":("1945","1500","497","586"),"h155":("1905","1250","501","556")}[gr]
   for a,v in zip(("gross_vehicle_weight","braked_trailer_weight","maximum_payload","boot_capacity"),e):self.assertEqual(self.find(c,a)[0]["value"],v)
   self.assertFalse(self.find(c,"minimum_kerb_weight"))
 def test_unresolved_facts_are_not_silently_imported(self):
  for a in ("minimum_kerb_weight","kerb_weight","standard_tyre_specification","front_tyre_size","rear_tyre_size","cargo_volume_vda_to_luggage_cover","cargo_volume_vda_to_seatback","interior_width","interior_height"):self.assertFalse([r for r in self.sv if r["attribute_code"]==a],a)
  self.assertFalse(any(r["attribute_code"]=="co2_emissions" and "_hybrid155_" in r["configuration_code"] for r in self.sv+self.sr))
 def test_report_and_completeness_scope_record_boundaries(self):
  r=json.loads((ROOT/"data/reporting/striker_my26_technical_data_review_20261124_001.json").read_text(encoding="utf-8"));self.assertEqual(r["migration"]["scalar_values"],423);self.assertEqual(r["migration"]["range_values"],21);self.assertEqual(len(r["configuration_scope"]["configurations"]),11);self.assertIn("95/96",str(r["unresolved"]))
  s=json.loads((ROOT/"data/reporting/striker_my26_technical_completeness_20261124.json").read_text(encoding="utf-8"));self.assertEqual({x["configuration_code"] for x in s["configurations"]},CONFIGS);self.assertTrue(s["technical_slots"])
