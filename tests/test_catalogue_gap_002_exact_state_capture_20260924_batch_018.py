import json
from pathlib import Path

P=Path("data/reporting/catalogue_gap_002_exact_state_capture_20260924_batch_018.json")
data=json.loads(P.read_text(encoding="utf-8"))
obs=data["observations"]
assert len(obs)==7
assert {o["configuration_code"] for o in obs}=={
"duster_expression_mild_hybrid_140_manual","duster_extreme_ecog120_automatic","duster_journey_ecog120_automatic","duster_expression_hybrid155_automatic","duster_extreme_hybrid155_automatic","duster_journey_hybrid155_automatic","duster_expression_hybridg150_4x4_automatic"}
assert [o["price_pln"] for o in obs]==[97600,102900,103100,112100,118100,118300,119900]
assert all(o["visible_colour_count"]==7 for o in obs)
assert all(o["selected_colour"]=="biel alpejska" for o in obs)
assert all(len(o["colours"])==7 for o in obs)
assert all(o["technical"] for o in obs)
