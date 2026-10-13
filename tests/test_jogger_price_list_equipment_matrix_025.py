import csv
import json
from pathlib import Path

manifest = json.loads(
    Path("data/reporting/jogger_price_list_equipment_matrix_025_20260927.json").read_text(encoding="utf-8")
)
assert manifest["result"]["configurations"] == 22
assert manifest["result"]["new_rows"] == 520
rows = list(csv.DictReader(Path("data/master/configuration_attribute_availability.csv").open(encoding="utf-8", newline="")))
codes = [row["code"] for row in rows]
assert len(codes) == len(set(codes))
jogger_rows = [row for row in rows if row["source_code"] == "src_pl_jogger_price_my26_20260703"]
assert len(jogger_rows) == 520
assert len({row["configuration_code"] for row in jogger_rows}) == 22
assert all(row["observation_date"] == "2026-07-03" for row in jogger_rows)
assert all(row["configuration_code"].startswith("jogger_") for row in jogger_rows)
assert len({row["id"] for row in rows}) == len(rows)
