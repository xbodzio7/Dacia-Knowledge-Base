#!/usr/bin/env python3
"""Advance project state to the completed residual official brochure evidence review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"


def main() -> int:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    payload["updated_on"] = "2026-07-26"
    payload["phase"] = "Official Brochure Residual Evidence Review"
    payload["current_package"] = {
        "name": "Official Brochure Residual Evidence Review",
        "status": "complete",
        "goal": "Re-audit the sixteen residual brochure classifications against the current repository, determine whether generic dimensions or newly modeled exact configurations have become actionable, and preserve blank, superseded and ambiguous evidence as explicit non-imports.",
    }
    payload["next_package"] = {
        "name": "Brochure Generic Dimensions Semantic Mapping Review",
        "status": "planned",
        "goal": "Visually map the Sandero, Jogger and Duster dimension diagrams to existing attributes, define exact projection scopes, and produce an import plan without inferring labels from text extraction order.",
    }
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: residual brochure evidence review state materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
