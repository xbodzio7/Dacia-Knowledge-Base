#!/usr/bin/env python3
"""Regenerate the gap plan and apply exact post-import snapshot repairs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import configuration_gap_resolution_plan as gap_plan  # noqa: E402
import repair_generic_dimension_snapshot_tests_20260726 as snapshots  # noqa: E402


def main() -> int:
    evidence_path = ROOT / gap_plan.DEFAULT_EVIDENCE_SPEC
    plan_path = ROOT / gap_plan.DEFAULT_PLAN_SPEC
    evidence = gap_plan.read_json(evidence_path, "evidence specification")
    expected = gap_plan.build_expected_plan_spec(ROOT, evidence)
    plan_path.write_text(gap_plan.render_json(expected), encoding="utf-8")
    snapshots.main()
    print("PASS: gap plan and generic dimension snapshots normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
