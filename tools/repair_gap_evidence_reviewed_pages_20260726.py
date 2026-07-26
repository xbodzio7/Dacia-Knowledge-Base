#!/usr/bin/env python3
"""Repair five exact dimension evidence decisions and regenerate the gap plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
EVIDENCE = REPORTING / "configuration_gap_evidence.json"
PLAN = REPORTING / "configuration_gap_resolution_plan.json"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_gap_resolution_plan as gap_plan  # noqa: E402

EXPECTED_KEYS = {
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|front_track|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|ground_clearance|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_height|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_width_with_mirrors|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|rear_track|none",
}


class RepairError(RuntimeError):
    """Raised when the exact evidence boundary differs from the reviewed state."""


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    decisions = evidence.get("decisions")
    if not isinstance(decisions, list):
        raise RepairError("evidence decisions must be a list")

    selected = {
        str(item.get("triage_key", "")): item
        for item in decisions
        if isinstance(item, dict) and item.get("triage_key") in EXPECTED_KEYS
    }
    if set(selected) != EXPECTED_KEYS:
        missing = sorted(EXPECTED_KEYS - set(selected))
        raise RepairError(f"exact evidence decisions differ; missing={missing}")

    for key in sorted(EXPECTED_KEYS):
        item = selected[key]
        if item.get("classification") != "not_stated":
            raise RepairError(f"classification differs for {key}")
        if item.get("reason_code") != "not_stated_on_relevant_pages":
            raise RepairError(f"reason code differs for {key}")
        pages = item.get("reviewed_pages")
        if pages not in ([], [2]):
            raise RepairError(f"reviewed pages differ for {key}: {pages!r}")
        item["reviewed_pages"] = [2]

    EVIDENCE.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    expected_plan = gap_plan.build_expected_plan_spec(ROOT, evidence)
    PLAN.write_text(gap_plan.render_json(expected_plan), encoding="utf-8")
    print("PASS: repaired five reviewed-page decisions and regenerated gap plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
