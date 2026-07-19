from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
state_path = ROOT / "project" / "state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["baseline"]["tests"] = 640
state["reference_delivery"] = {
    "name": "Configuration Comparison Workbook Export Planning Review",
    "pull_request": 153,
    "head_sha": "e267fa31953890f045d49d67a94fd566d3098f64",
    "quality_run": 763,
}
state["current_package"] = {
    "name": "Configuration Comparison Workbook Export",
    "status": "active",
    "goal": "Add one deterministic six-sheet XLSX workbook to each comparison bundle.",
}
state["next_package"] = {
    "name": "Data Product Distribution Planning Review",
    "status": "planned",
    "goal": "Select a stable delivery channel for the existing offline data products without expanding source data.",
}
state_path.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
for name in (
    "test_jogger_payload_performance_ranges.py",
    "test_jogger_wltp_efficiency_ranges.py",
):
    path = ROOT / "tests" / name
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'self.assertEqual(baseline["tests"], 628)',
        'self.assertEqual(baseline["tests"], 640)',
    )
    path.write_text(text, encoding="utf-8")
