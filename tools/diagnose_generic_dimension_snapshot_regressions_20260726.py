#!/usr/bin/env python3
"""Regenerate the gap plan and persist compact reporting diagnostics."""

from __future__ import annotations

import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
REPORTING = ROOT / "data" / "reporting"
OUTPUT = ROOT / ".github" / "generic-dimension-reporting-diagnostics.json"

sys.path.insert(0, str(TOOLS))

import configuration_completeness as completeness  # noqa: E402
import configuration_comparison as comparison  # noqa: E402
import configuration_gap_resolution_plan as gap_plan  # noqa: E402
import source_coverage  # noqa: E402
from reporting.configuration_comparison_bundle import create_bundle  # noqa: E402
from reporting.deterministic_xlsx_model import MAIN_NS  # noqa: E402

SCOPES = {
    "sandero_manual": (
        "sandero_ecog120_manual_completeness.json",
        "sandero_ecog120_manual_gap_evidence.json",
        "2026-06-26",
    ),
    "duster_ecog100": (
        "duster_ecog100_completeness.json",
        "duster_ecog100_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_ecog120": (
        "duster_ecog120_completeness.json",
        "duster_ecog120_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_hybrid140": (
        "duster_hybrid140_completeness.json",
        "duster_hybrid140_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_hybrid155": (
        "duster_hybrid155_completeness.json",
        "duster_hybrid155_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_mildhybrid130_4x2": (
        "duster_mildhybrid130_4x2_completeness.json",
        "duster_mildhybrid130_4x2_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_mildhybrid130_4x4": (
        "duster_mildhybrid130_4x4_completeness.json",
        "duster_mildhybrid130_4x4_gap_evidence.spec",
        "2026-02-06",
    ),
    "duster_mildhybrid140_4x2": (
        "duster_mildhybrid140_4x2_completeness.json",
        "duster_mildhybrid140_4x2_gap_evidence.spec",
        "2026-02-06",
    ),
    "jogger_ecog120_automatic": (
        "jogger_ecog120_automatic_completeness.json",
        "jogger_ecog120_automatic_gap_evidence.spec",
        "2026-04-01",
    ),
    "jogger_ecog120_manual": (
        "jogger_ecog120_manual_completeness.json",
        "jogger_ecog120_manual_gap_evidence.spec",
        "2026-04-01",
    ),
    "jogger_hybrid155_automatic": (
        "jogger_hybrid155_automatic_completeness.json",
        "jogger_hybrid155_automatic_gap_evidence.spec",
        "2026-04-01",
    ),
    "jogger_tce110_manual": (
        "jogger_tce110_manual_completeness.json",
        "jogger_tce110_manual_gap_evidence.spec",
        "2026-04-01",
    ),
}
SELECTED = (
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "duster_iii_expression_ecog100_4x2_manual",
)


def regenerate_gap_plan() -> None:
    evidence_path = ROOT / gap_plan.DEFAULT_EVIDENCE_SPEC
    plan_path = ROOT / gap_plan.DEFAULT_PLAN_SPEC
    evidence = gap_plan.read_json(evidence_path, "evidence specification")
    expected = gap_plan.build_expected_plan_spec(ROOT, evidence)
    plan_path.write_text(gap_plan.render_json(expected), encoding="utf-8")


def scope_diagnostic(
    spec_name: str,
    evidence_name: str,
    as_of: str,
) -> dict[str, object]:
    spec = REPORTING / spec_name
    evidence = REPORTING / evidence_name
    complete = completeness.collect_report(ROOT, spec, as_of)
    covered = source_coverage.collect_report(ROOT, spec, as_of)
    compared = comparison.collect_report(ROOT, spec, evidence, as_of)
    return {
        "scope": {
            "active_configurations": complete["scope"]["active_configurations"],
            "reporting_configurations": complete["scope"]["reporting_configurations"],
            "sources": complete["scope"]["sources"],
            "technical_slots": complete["scope"]["technical_slots"],
            "equipment_attributes": complete["scope"]["equipment_attributes"],
        },
        "technical": complete["technical"],
        "equipment": complete["equipment"],
        "gap_counts": {
            "technical": len(complete["gaps"]["technical"]),
            "equipment": len(complete["gaps"]["equipment"]),
        },
        "coverage_areas": covered["areas"],
        "coverage_sections": covered["sections"],
        "coverage_records": covered["records"],
        "comparison_summary": compared["summary"],
        "evidence_summary": compared["evidence_summary"],
        "pair_count": len(compared["pairs"]),
        "technical_not_comparable_sum": sum(
            pair["summary"]["technical"]["not_comparable"]
            for pair in compared["pairs"]
        ),
        "technical_not_comparable_values": sorted(
            {
                pair["summary"]["technical"]["not_comparable"]
                for pair in compared["pairs"]
            }
        ),
    }


def default_diagnostic() -> dict[str, object]:
    spec = REPORTING / "configuration_completeness.json"
    evidence = REPORTING / "configuration_gap_evidence.json"
    complete = completeness.collect_report(ROOT, spec)
    covered = source_coverage.collect_report(ROOT, spec)
    compared = comparison.collect_report(ROOT, spec, evidence)
    return {
        "scope": {
            "active_configurations": complete["scope"]["active_configurations"],
            "reporting_configurations": complete["scope"]["reporting_configurations"],
            "sources": complete["scope"]["sources"],
            "technical_slots": complete["scope"]["technical_slots"],
            "equipment_attributes": complete["scope"]["equipment_attributes"],
        },
        "technical": complete["technical"],
        "equipment": complete["equipment"],
        "coverage_areas": covered["areas"],
        "coverage_sections": covered["sections"],
        "coverage_records": covered["records"],
        "comparison_summary": compared["summary"],
        "evidence_summary": compared["evidence_summary"],
        "pair_count": len(compared["pairs"]),
    }


def workbook_dimensions() -> list[str]:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "bundle"
        manifest = create_bundle(ROOT, output, direct_codes=SELECTED)
        workbook = output / manifest["workbook"]["path"]
        dimensions: list[str] = []
        with ZipFile(workbook) as archive:
            for index in range(1, 9):
                root = ET.fromstring(
                    archive.read(f"xl/worksheets/sheet{index}.xml")
                )
                dimension = root.find(f"{{{MAIN_NS}}}dimension")
                if dimension is None:
                    raise RuntimeError(f"dimension missing for sheet {index}")
                dimensions.append(dimension.attrib["ref"])
        return dimensions


def main() -> int:
    regenerate_gap_plan()
    payload = {
        "scopes": {
            name: scope_diagnostic(*parameters)
            for name, parameters in SCOPES.items()
        },
        "default": default_diagnostic(),
        "workbook_dimensions": workbook_dimensions(),
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("PASS: gap plan regenerated and compact diagnostics persisted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
