import json
from pathlib import Path
P=Path("data/reporting/catalogue_gap_002_exact_state_capture_20260924_batch_019.json")
d=json.loads(P.read_text(encoding="utf-8"))
o=d["observations"]
assert len(o)==6
assert len(d["duplicate_enrichment"])==1
assert all(x["selected_colour"]=="biel alpejska" for x in o)
assert all(x["visible_colour_count"]==len(x["colours"]) for x in o)
assert [x["price_pln"] for x in o]==[133000,89400,90200,84600,126100,125900]
assert all(x["technical"] for x in o)
