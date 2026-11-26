#!/usr/bin/env python3
"""Verify closure of the official brochure selected-gear performance import."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import configuration_comparison  # noqa: E402
import configuration_comparison_context  # noqa: E402

MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "brochure_gear_performance_import_closure_review.json"
VALUES = MASTER / "configuration_attribute_values.csv"
CONFIGURATIONS = MASTER / "configurations.csv"
SOURCES = {
    "src_pl_sandero_brochure_20260202": (4, 16),
    "src_pl_sandero_stepway_brochure_20260202": (5, 22),
    "src_pl_jogger_brochure_20251217": (22, 32),
}
EXPECTED_GEAR_COUNTS = Counter({"4": 50, "5": 14, "6": 6})
EXPECTED_FUEL_COUNTS = Counter({"lpg": 29, "petrol": 41})
EXPECTED_CONTEXTS = {
    "fuel_type_code=lpg;gear_number=4",
    "fuel_type_code=lpg;gear_number=5",
    "fuel_type_code=lpg;gear_number=6",
    "fuel_type_code=petrol;gear_number=4",
    "fuel_type_code=petrol;gear_number=5",
    "fuel_type_code=petrol;gear_number=6",
}
REPORTING_SPECS = (
    "configuration_completeness.json",
    "jogger_ecog120_automatic_completeness.json",
    "jogger_ecog120_manual_completeness.json",
    "jogger_hybrid155_automatic_completeness.json",
    "jogger_tce110_manual_completeness.json",
    "sandero_ecog120_automatic_completeness.json",
    "sandero_ecog120_manual_completeness.json",
    "sandero_stepway_ecog120_automatic_completeness.json",
)
IMPORTER = ROOT / "tools" / "import_brochure_gear_performance_20260726.py"


class ClosureError(RuntimeError):
    """Raised when the reviewed selected-gear milestone drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def reviewed_values() -> list[dict[str, str]]:
    return [
        row
        for row in read_rows(VALUES)
        if row.get("attribute_code") == "elasticity_80_120"
        and row.get("source_code") in SOURCES
    ]


def verify_report(payload: dict[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported closure review version")
    ensure(payload.get("kind") == "brochure_gear_performance_import_closure_review", "unexpected closure review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "closure review is not complete")
    ensure(payload.get("canonical_attribute") == "elasticity_80_120", "canonical attribute differs")

    sources = payload.get("sources")
    ensure(isinstance(sources, list) and len(sources) == 3, "expected three reviewed sources")
    by_source = {str(item.get("source_code", "")): item for item in sources if isinstance(item, dict)}
    ensure(set(by_source) == set(SOURCES), "closure source set differs")
    for source_code, (configuration_count, value_count) in SOURCES.items():
        item = by_source[source_code]
        ensure(item.get("configurations") == configuration_count, f"configuration count differs: {source_code}")
        ensure(item.get("values") == value_count, f"value count differs: {source_code}")

    totals = payload.get("totals")
    ensure(isinstance(totals, dict), "closure totals are missing")
    ensure(totals.get("sources") == 3, "closure source total differs")
    ensure(totals.get("configurations") == 31, "closure configuration total differs")
    ensure(totals.get("values") == 70, "closure value total differs")
    ensure(Counter(totals.get("gear_counts", {})) == EXPECTED_GEAR_COUNTS, "closure gear totals differ")
    ensure(Counter(totals.get("fuel_counts", {})) == EXPECTED_FUEL_COUNTS, "closure fuel totals differ")
    ensure(totals.get("reporting_scopes") == 8, "closure reporting scope total differs")
    ensure(totals.get("difference_contexts") == 6, "closure context total differs")

    reporting = payload.get("reporting_contract")
    ensure(isinstance(reporting, dict), "reporting contract is missing")
    ensure(set(reporting.get("gear_contexts", [])) == EXPECTED_CONTEXTS, "reported gear contexts differ")
    surfaces = set(reporting.get("covered_surfaces", []))
    ensure(
        surfaces
        == {
            "configuration_completeness",
            "source_coverage",
            "configuration_gap_resolution_plan",
            "configuration_comparison",
            "configuration_shortlist",
            "comparison_bundle",
            "comparison_workbook",
            "data_product_release",
        },
        "reporting surface contract differs",
    )

    deferred = payload.get("deferred_evidence")
    ensure(isinstance(deferred, list) and len(deferred) == 6, "expected six explicit deferrals")
    ensure(
        {str(item.get("code", "")) for item in deferred if isinstance(item, dict)}
        == {
            "sandero_tce_column_without_exact_configuration",
            "stepway_tce110_without_exact_configuration",
            "stepway_automatic_fifth_and_sixth_gear_blank",
            "jogger_only_fourth_gear_stated",
            "no_cross_fuel_projection",
            "no_cross_configuration_projection",
        },
        "deferred evidence set differs",
    )
    ensure(all(str(item.get("reason", "")).strip() for item in deferred), "empty deferral reason")
    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Official Brochure Technical Gap Review", "next package differs")


def verify_values(rows: Sequence[dict[str, str]]) -> None:
    ensure(len(rows) == 70, "expected exactly 70 reviewed values")
    ensure(len({row.get("code", "") for row in rows}) == 70, "reviewed value codes are not unique")
    ensure(len({row.get("configuration_code", "") for row in rows}) == 31, "expected 31 exact configurations")
    ensure(Counter(row.get("source_code", "") for row in rows) == Counter({code: count for code, (_, count) in SOURCES.items()}), "source value counts differ")
    ensure(Counter(row.get("gear_number", "") for row in rows) == EXPECTED_GEAR_COUNTS, "master gear counts differ")
    ensure(Counter(row.get("fuel_type_code", "") for row in rows) == EXPECTED_FUEL_COUNTS, "master fuel counts differ")
    ensure(all(row.get("gear_number", "") in {"4", "5", "6"} for row in rows), "blank or unexpected gear imported")
    ensure([int(row["id"]) for row in rows] == list(range(2119, 2189)), "reviewed IDs are not contiguous")

    stepway_automatic = [
        row
        for row in rows
        if row.get("configuration_code", "").startswith("sandero_stepway_")
        and row.get("configuration_code", "").endswith("_automatic")
    ]
    ensure(len(stepway_automatic) == 4, "expected four automatic Stepway observations")
    ensure({row.get("gear_number", "") for row in stepway_automatic} == {"4"}, "unstated automatic Stepway gears were inferred")
    ensure(
        not any(
            row.get("configuration_code", "").startswith(("sandero_iii_tce", "sandero_stepway_iii_tce"))
            for row in rows
        ),
        "unmodeled Sandero or Stepway TCe value was imported",
    )


def verify_configurations(rows: Iterable[dict[str, str]]) -> None:
    active = {
        row.get("code", "")
        for row in read_rows(CONFIGURATIONS)
        if row.get("status") == "active"
    }
    target = {row.get("configuration_code", "") for row in rows}
    ensure(target <= active, "reviewed value targets an inactive or unknown configuration")
    ensure(sum(code.startswith("sandero_iii_") for code in target) == 4, "Sandero configuration scope differs")
    ensure(sum(code.startswith("sandero_stepway_iii_") for code in target) == 5, "Stepway configuration scope differs")
    ensure(sum(code.startswith("jogger_") for code in target) == 22, "Jogger configuration scope differs")
    jogger = {code for code in target if code.startswith("jogger_")}
    ensure(sum("_5seat_" in code for code in jogger) == 11, "Jogger five-seat scope differs")
    ensure(sum("_7seat_" in code for code in jogger) == 11, "Jogger seven-seat scope differs")


def verify_reporting_specs() -> None:
    reporting = ROOT / "data" / "reporting"
    for filename in REPORTING_SPECS:
        payload = json.loads((reporting / filename).read_text(encoding="utf-8"))
        slots = {
            (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", "")))
            for item in payload.get("technical_slots", [])
            if isinstance(item, dict)
        }
        ensure(any(attribute == "elasticity_80_120" for attribute, _ in slots), f"selected-gear slot missing: {filename}")

    report = configuration_comparison.collect_report(
        ROOT,
        ROOT / configuration_comparison.DEFAULT_COMPLETENESS_SPEC,
        ROOT / configuration_comparison.DEFAULT_EVIDENCE_SPEC,
    )
    contexts = set(configuration_comparison_context.difference_contexts(report))
    ensure(EXPECTED_CONTEXTS <= contexts, "comparison contexts omit selected-gear observations")


def verify_importer() -> None:
    completed = subprocess.run(
        [sys.executable, str(IMPORTER), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    ensure(completed.returncode == 0, completed.stderr or completed.stdout)
    ensure("PASS: exact brochure selected-gear performance values" in completed.stdout, "importer PASS receipt missing")


def check() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    verify_report(payload)
    rows = reviewed_values()
    verify_values(rows)
    verify_configurations(rows)
    verify_reporting_specs()
    verify_importer()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ClosureError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("PASS: brochure selected-gear performance import closure review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
