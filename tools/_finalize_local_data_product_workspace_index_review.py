#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import project_state


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project/state.json"
SUMMARY = ROOT / "project/STATE_SUMMARY.md"


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Verified Data Product Release Download CLI",
        "pull_request": 162,
        "head_sha": "50461aaea58c6ee7b9414d46fc32fe6de7d4a496",
        "quality_run": 869,
    }
    state["current_package"] = {
        "name": "Local Data Product Workspace Index Planning Review",
        "status": "complete",
        "goal": (
            "Select a deterministic local landing-page contract linking the "
            "downloaded shortlist, workbook, scope reports and provenance without "
            "republishing the release or expanding source data."
        ),
    }
    state["next_package"] = {
        "name": "Local Data Product Workspace Index HTML",
        "status": "planned",
        "goal": (
            "Generate one deterministic offline index.html after verified release "
            "extraction, linking primary products, every comparison scope and "
            "release provenance with safe relative paths."
        ),
    }
    project_state.validate_state(state)
    STATE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    SUMMARY.write_text(
        project_state.render_summary(state),
        encoding="utf-8",
        newline="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
