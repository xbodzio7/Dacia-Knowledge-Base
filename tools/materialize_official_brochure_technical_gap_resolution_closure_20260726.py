#!/usr/bin/env python3
"""Advance project state to the completed official brochure gap resolution closure."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"


def main() -> int:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    payload["updated_on"] = "2026-07-26"
    payload["phase"] = "Official Brochure Technical Gap Resolution Closure Review"
    payload["current_package"] = {
        "name": "Official Brochure Technical Gap Resolution Closure Review",
        "status": "complete",
        "goal": "Verify that all four packages from the official brochure technical gap priority queue are complete, reconcile their receipts against the original 29 classifications, and retain all ambiguous, unmodeled and no-observation evidence as explicit deferrals.",
    }
    payload["next_package"] = {
        "name": "Official Brochure Residual Evidence Review",
        "status": "planned",
        "goal": "Re-audit the sixteen residual brochure classifications against the current repository, determine whether generic dimensions or newly modeled exact configurations have become actionable, and preserve blank, superseded and ambiguous evidence as explicit non-imports.",
    }
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: official brochure gap resolution closure state materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
