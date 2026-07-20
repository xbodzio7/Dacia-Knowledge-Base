#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import project_state


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "project/state.json"
SUMMARY_PATH = ROOT / "project/STATE_SUMMARY.md"


def main() -> int:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Initial Data Product Release Publication",
        "pull_request": 160,
        "head_sha": "fdef0e4788a2927203f8621196e9eff3a38c5443",
        "quality_run": 848,
    }
    state["current_package"] = {
        "name": "Data Product Release Consumption Review",
        "status": "complete",
        "goal": (
            "Assess discoverability, download, verification and user workflow "
            "of data-products-v1.0.0 and select the next utilization improvement "
            "without expanding source data."
        ),
    }
    state["next_package"] = {
        "name": "Verified Data Product Release Download CLI",
        "status": "planned",
        "goal": (
            "Download an explicit immutable release version, verify its GitHub "
            "tag and three canonical assets, safely extract validated contents "
            "and report ready-to-open user entry points."
        ),
    }
    project_state.validate_state(state)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    SUMMARY_PATH.write_text(
        project_state.render_summary(state),
        encoding="utf-8",
        newline="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
