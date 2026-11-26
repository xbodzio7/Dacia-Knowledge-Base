import json
from pathlib import Path
d=json.loads(Path("data/reporting/catalogue_gap_002_exact_state_capture_20260924_batch_021.json").read_text(encoding="utf-8"))
assert len(d["observations"])==2
assert [x["price_pln"] for x in d["observations"]]==[101400,71700]
assert all(x["selected_colour"]=="biel alpejska" for x in d["observations"])
assert all(x["visible_colour_count"]==len(x["colours"]) for x in d["observations"])
