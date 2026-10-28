from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools"/"import_bigster_brochure_page22_availability.py"
def load():
 spec=importlib.util.spec_from_file_location("bigster_page22_import",SCRIPT)
 module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def test_page22_contract_is_exact_and_source_bound():
 m=load(); rows=m.generated_rows()
 assert len(rows)==28
 assert {r["attribute_code"] for r in rows}=={"power_tailgate","dual_zone_climate_control"}
 assert all(r["source_code"]==m.SOURCE_CODE and r["observation_date"]=="2025-12-10" for r in rows)
def test_page22_grade_states():
 m=load(); rows=m.generated_rows()
 by={(r["configuration_code"],r["attribute_code"]):r["availability_status"] for r in rows}
 assert by[("bigster_essential_mildhybrid140_4x2_manual","power_tailgate")]=="not_available"
 assert by[("bigster_journey_hybrid155_4x2_automatic","power_tailgate")]=="standard"
 assert by[("bigster_extreme_hybridg150_4x4_automatic","power_tailgate")]=="optional"
 assert by[("bigster_essential_mildhybridg140_4x2_manual","dual_zone_climate_control")]=="not_available"
 assert by[("bigster_expression_hybrid155_4x2_automatic","dual_zone_climate_control")]=="standard"
