import csv,json
from pathlib import Path
m=json.loads(Path("data/reporting/full_price_list_option_matrix_reconciliation_024_20260927.json").read_text(encoding="utf-8"))
assert m["changes"]["new_commercial_items"]==5
assert m["changes"]["new_configuration_mappings"]==56
items=list(csv.DictReader(Path("data/master/commercial_items.csv").open(encoding="utf-8",newline="")))
rows=list(csv.DictReader(Path("data/master/commercial_item_configurations.csv").open(encoding="utf-8",newline="")))
assert len({r["code"] for r in rows})==len(rows)
assert {"duster_spare_wheel_option","duster_18inch_wheel_option","jogger_spare_wheel_option","bigster_19inch_wheel_option","bigster_spare_wheel_option"}.issubset({r["code"] for r in items})
sources={"src_pl_duster_price_my26_20260703","src_pl_jogger_price_my26_20260703","src_pl_bigster_price_my26_20260703"}
for r in rows:
    if r["code"].startswith(("duster_","jogger_","bigster_")) and r["source_code"] in sources:
        assert r["price_date"]=="2026-07-03"
