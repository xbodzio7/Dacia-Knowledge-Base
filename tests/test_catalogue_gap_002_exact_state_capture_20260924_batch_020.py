import json
from pathlib import Path
P=Path("data/reporting/catalogue_gap_002_exact_state_capture_20260924_batch_020.json")
d=json.loads(P.read_text(encoding="utf-8"))
o=d["observations"]
assert len(o)==4
assert len(d["duplicate_enrichment"])==2
assert all(x["selected_colour"]=="biel alpejska" for x in o)
assert all(x["visible_colour_count"]==len(x["colours"]) for x in o)
assert [x["price_pln"] for x in o]==[101400,71700,103800,103600]
assert all(x["technical"] for x in o)
