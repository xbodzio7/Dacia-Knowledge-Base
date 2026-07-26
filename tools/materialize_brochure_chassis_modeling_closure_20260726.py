#!/usr/bin/env python3
"""Advance project state to the completed brochure chassis modeling closure review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"


def main() -> int:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    payload["updated_on"] = "2026-07-26"
    payload["phase"] = "Brochure Chassis Modeling Closure Review"
    payload["current_package"] = {
        "name": "Brochure Chassis Modeling Closure Review",
        "status": "complete",
        "goal": "Verify that all five D-016 chassis modeling resolutions are imported, all source and reporting contracts remain green, and the separate Jogger mass-table label conflict remains explicitly unresolved.",
    }
    payload["next_package"] = {
        "name": "Official Brochure Technical Gap Resolution Closure Review",
        "status": "planned",
        "goal": "Verify that all four packages from the official brochure technical gap priority queue are complete, reconcile their receipts against the original 29 classifications, and retain all ambiguous, unmodeled and no-observation evidence as explicit deferrals.",
    }
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: brochure chassis closure project state materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
