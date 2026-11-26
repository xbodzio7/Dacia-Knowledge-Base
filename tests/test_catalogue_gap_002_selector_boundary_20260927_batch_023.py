import json
from pathlib import Path

P = Path("data/reporting/catalogue_gap_002_selector_boundary_20260927_batch_023.json")
d = json.loads(P.read_text(encoding="utf-8"))

assert d["kind"] == "catalogue_gap_002_selector_boundary_capture"
assert d["result"]["new_exact_surfaces"] == 0
assert d["result"]["remaining_unresolved_exact_surfaces"] == 10
assert len(d["unresolved_exact_surfaces"]) == 10
assert d["policy"]["selected_exact_state_required"] is True
assert d["policy"]["absence_interpreted_as_unavailability"] is False
assert d["policy"]["master_data_mutated"] is False
assert d["current_selector_boundary"]["current_powertrain_families_exposed"] == [
    "Eco-G 120",
    "mild hybrid 140",
    "hybrid 155",
    "tribrid 150 4x4",
]
