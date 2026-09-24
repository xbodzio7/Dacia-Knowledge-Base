import json
from pathlib import Path
P=Path("data/reporting/catalogue_gap_002_exact_state_capture_20260925_batch_022.json")
d=json.loads(P.read_text(encoding="utf-8"))
o=d["observations"]
assert len(o)==5
assert all(x["selected_colour"]=="biel alpejska" for x in o)
assert all(x["visible_colour_count"]==6 and len(x["colours"])==6 for x in o)
assert [x["price_pln"] for x in o]==[124900,128900,133400,137600,137200]
assert all(x["technical"] for x in o)
assert len({x["configuration_code"] for x in o})==5
