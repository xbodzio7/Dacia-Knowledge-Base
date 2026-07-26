#!/usr/bin/env python3
"""Advance project state to the completed generic dimension semantic mapping review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"


def main() -> int:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    payload["updated_on"] = "2026-07-26"
    payload["phase"] = "Brochure Generic Dimensions Semantic Mapping Review"
    payload["current_package"] = {
        "name": "Brochure Generic Dimensions Semantic Mapping Review",
        "status": "complete",
        "goal": "Visually map the Sandero, Jogger and Duster dimension diagrams to existing attributes, define exact projection scopes, and produce an import plan without inferring labels from text extraction order.",
    }
    payload["next_package"] = {
        "name": "Brochure Generic Dimensions Observation Import",
        "status": "planned",
        "goal": "Materialize the 382 approved historical exterior-dimension observations for exact source-related Sandero, Jogger and Duster 4x2 configurations, integrate reporting slots, and preserve all deferred or excluded diagram values.",
    }
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: generic dimensions semantic mapping state materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
