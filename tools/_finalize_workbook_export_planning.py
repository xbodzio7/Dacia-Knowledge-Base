from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
state["reference_delivery"] = {
    "name": "Data Product Utilization Milestone Review",
    "pull_request": 152,
    "head_sha": "1f58a89db47d2204bcfaeb085a8ac61f89ec1548",
    "quality_run": 761,
}
state["current_package"] = {
    "name": "Configuration Comparison Workbook Export Planning Review",
    "status": "complete",
    "goal": "Define a deterministic XLSX workbook contract that reuses existing comparison and bundle outputs while preserving scope isolation, unknown states and source provenance.",
}
state["next_package"] = {
    "name": "Configuration Comparison Workbook Export",
    "status": "planned",
    "goal": "Add one deterministic six-sheet XLSX workbook to each transactional comparison bundle using a fixed standard-library OOXML writer and manifest-backed verification.",
}
STATE.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
