import csv,json
from pathlib import Path
m=json.loads(Path("data/reporting/jogger_price_list_equipment_matrix_025_20260927.json").read_text(encoding="utf-8"))
assert m["result"]["configurations"]==22
assert m["result"]["new_rows"]==520
rows=list(csv.DictReader(Path("data/master/configuration_attribute_availability.csv").open(encoding="utf-8",newline="")))
assert len([r["code"] for r in rows])==len({r["code"] for r in rows})
cfgs={r["configuration_code"] for r in rows if r["source_code"]=="src_pl_jogger_price_my26_20260703"}
assert len([c for c in cfgs if c.startswith("jogger_")])==22
