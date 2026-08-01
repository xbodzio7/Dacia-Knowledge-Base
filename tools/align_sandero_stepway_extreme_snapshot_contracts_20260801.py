#!/usr/bin/env python3
"""Align deterministic repository snapshots after the Stepway Extreme import."""
from __future__ import annotations

import csv
import json
import pprint
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import configuration_comparison as comparison  # noqa: E402
import configuration_comparison_context as context_filter  # noqa: E402
import configuration_comparison_pair_summary as pair_summary  # noqa: E402
import configuration_completeness as completeness  # noqa: E402
import source_coverage  # noqa: E402
from tools import existing_configuration_missing_data_analysis as analysis  # noqa: E402

AS_OF = "2026-06-26"
SANDERO_SPEC = ROOT / "data/reporting/sandero_ecog120_manual_completeness.json"
SANDERO_EVIDENCE = ROOT / "data/reporting/sandero_ecog120_manual_gap_evidence.json"
DEFAULT_COMPLETENESS = ROOT / comparison.DEFAULT_COMPLETENESS_SPEC
DEFAULT_EVIDENCE = ROOT / comparison.DEFAULT_EVIDENCE_SPEC
AVAILABILITY = ROOT / "data/master/configuration_attribute_availability.csv"
RANGES = ROOT / "data/master/configuration_attribute_value_ranges.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
RECONCILIATION = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
STATE = ROOT / "project/state.json"

CHANGED_PATHS = {
    "tools/align_sandero_stepway_extreme_snapshot_contracts_20260801.py",
    "tools/import_sandero_stepway_essential_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_source_gap_20260626.py",
    "tools/review_official_brochure_residual_evidence_20260726.py",
    "tests/configuration_comparison_context_filter_contract.py",
    "tests/configuration_comparison_pair_summary_contract.py",
    "tests/test_configuration_value_ranges.py",
    "tests/test_duster_ecog120_reporting_scope.py",
    "tests/test_jogger_payload_performance_ranges.py",
    "tests/test_official_brochure_residual_evidence_review.py",
    "tests/test_sandero_50_kmh_noise_level_model.py",
    "tests/test_sandero_50_kmh_noise_level_values.py",
    "tests/test_sandero_ecog120_manual_reporting_scope.py",
    "tests/test_sandero_equipment_availability.py",
    "tests/test_sandero_euro_6e_bis_model.py",
    "tests/test_sandero_euro_6e_bis_values.py",
    "tests/test_sandero_exterior_colour_values.py",
    "tests/test_sandero_front_wheel_drive_values.py",
    "tests/test_sandero_maximum_payload_model.py",
    "tests/test_sandero_number_of_doors_values.py",
    "tests/test_sandero_passive_safety_availability.py",
    "tests/test_sandero_standard_tyre_specification.py",
    "tests/test_sandero_stepway_essential_source_gap_20260626.py",
    "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    "tests/test_sandero_total_valve_count_model.py",
    "tests/test_spring_technical_20260219.py",
}


class AlignmentError(RuntimeError):
    pass


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AlignmentError(f"missing CSV header: {path}")
        return list(reader)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_required(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old in text:
        text = text.replace(old, new)
        write_text(target, text)
        return
    if new not in text:
        raise AlignmentError(f"missing snapshot in {path}: {old!r}")


def replace_regex(path: str, pattern: str, replacement: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise AlignmentError(
            f"expected one regex replacement in {path}, found {count}: {pattern}"
        )
    write_text(target, updated)


def python_literal(value: object) -> str:
    return pprint.pformat(value, sort_dicts=False, width=120)


def sandero_reports() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    return (
        completeness.collect_report(ROOT, SANDERO_SPEC, AS_OF),
        source_coverage.collect_report(ROOT, SANDERO_SPEC, AS_OF),
        comparison.collect_report(ROOT, SANDERO_SPEC, SANDERO_EVIDENCE, AS_OF),
    )


def render_sandero_reporting_test(
    complete: dict[str, object],
    coverage: dict[str, object],
    compared: dict[str, object],
) -> str:
    pairs = compared["pairs"]
    pair_types = Counter(pair["pair_type"] for pair in pairs)
    not_comparable = {
        domain: sum(
            pair["summary"][domain]["not_comparable"]
            for pair in pairs
        )
        for domain in ("technical", "equipment", "prices")
    }
    ranged = [
        item
        for pair in pairs
        for item in pair["technical"]
        if "minimum_value" in item["left"]
        or "minimum_value" in item["right"]
    ]
    configurations = {
        "sandero_iii_expression_ecog120_manual",
        "sandero_iii_journey_ecog120_manual",
        "sandero_stepway_iii_essential_ecog120_manual",
        "sandero_stepway_iii_expression_ecog120_manual",
        "sandero_stepway_iii_extreme_ecog120_manual",
    }
    return f'''from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import configuration_completeness as completeness  # noqa: E402
import configuration_comparison as comparison  # noqa: E402
import source_coverage  # noqa: E402

AS_OF = "2026-06-26"
SPEC = REPOSITORY / "data/reporting/sandero_ecog120_manual_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/sandero_ecog120_manual_gap_evidence.json"
CONFIGURATIONS = {python_literal(configurations)}
EXPECTED_TECHNICAL = {python_literal(complete["technical"])}
EXPECTED_EQUIPMENT = {python_literal(complete["equipment"])}
EXPECTED_SOURCE_REGISTRATION = {python_literal(coverage["source_registration"])}
EXPECTED_AREAS = {python_literal(coverage["areas"])}
EXPECTED_SECTIONS = {python_literal(coverage["sections"])}
EXPECTED_COMPARISON_SUMMARY = {python_literal(compared["summary"])}
EXPECTED_EVIDENCE_SUMMARY = {python_literal(compared["evidence_summary"])}
EXPECTED_PAIR_TYPES = {python_literal(dict(pair_types))}
EXPECTED_NOT_COMPARABLE = {python_literal(not_comparable)}
EXPECTED_RANGED = {len(ranged)}
EXPECTED_TECHNICAL_GAPS = {len(complete["gaps"]["technical"])}
EXPECTED_EQUIPMENT_GAPS = {len(complete["gaps"]["equipment"])}
EXPECTED_COVERAGE_GAPS = {len(coverage["gaps"])}


class SanderoEcoG120ManualReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_five_manual_configurations(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 5)
        self.assertEqual(scope["technical_slots"], 60)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 5)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(self.completeness["technical"], EXPECTED_TECHNICAL)
        self.assertEqual(self.completeness["equipment"], EXPECTED_EQUIPMENT)
        self.assertEqual(len(self.completeness["gaps"]["technical"]), EXPECTED_TECHNICAL_GAPS)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), EXPECTED_EQUIPMENT_GAPS)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(self.coverage["source_registration"], EXPECTED_SOURCE_REGISTRATION)
        self.assertEqual(self.coverage["areas"], EXPECTED_AREAS)
        self.assertEqual(self.coverage["sections"], EXPECTED_SECTIONS)
        self.assertEqual(
            self.coverage["records"]["technical"]["present"],
            EXPECTED_TECHNICAL["present"],
        )
        self.assertEqual(
            self.coverage["records"]["equipment"]["present"],
            EXPECTED_EQUIPMENT["recorded"],
        )
        self.assertEqual(self.coverage["records"]["prices"]["present"], 5)
        self.assertEqual(len(self.coverage["gaps"]), EXPECTED_COVERAGE_GAPS)

    def test_ten_pairs_are_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 10)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter(EXPECTED_PAIR_TYPES),
        )
        for domain, expected in EXPECTED_NOT_COMPARABLE.items():
            with self.subTest(domain=domain):
                self.assertEqual(
                    sum(pair["summary"][domain]["not_comparable"] for pair in pairs),
                    expected,
                )

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(self.comparison["summary"], EXPECTED_COMPARISON_SUMMARY)

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], EXPECTED_EVIDENCE_SUMMARY)
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(len(ranged), EXPECTED_RANGED)

    def test_all_five_prices_are_present_and_all_ten_pair_prices_differ(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 5)
        self.assertEqual(
            sum(pair["summary"]["prices"]["different"] for pair in self.comparison["pairs"]),
            10,
        )


if __name__ == "__main__":
    unittest.main()
'''


def align_previous_source_gap_contracts() -> None:
    payload = analysis.collect(ROOT)
    missing = int(payload["summary"]["missing_technical_count"])
    exhausted = int(payload["summary"]["exhausted_source_candidate_count"])
    paths = (
        "tools/import_sandero_stepway_essential_source_gap_20260626.py",
        "tools/import_sandero_stepway_expression_source_gap_20260626.py",
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    )
    for path in paths:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        text = text.replace("125", str(missing))
        text = re.sub(
            r'(exhausted_source_candidate_count"\]\s*(?:!=|,))\s*3',
            rf'\g<1> {exhausted}',
            text,
        )
        text = text.replace(
            "expected exactly three exhausted-source candidates",
            f"expected exactly {exhausted} exhausted-source candidates",
        )
        write_text(target, text)


def align_range_contracts(range_count: int) -> None:
    replace_required(
        "tests/test_configuration_value_ranges.py",
        "len(rows[1:]), 307",
        f"len(rows[1:]), {range_count}",
    )
    replace_required(
        "tests/test_configuration_value_ranges.py",
        "checked, 307",
        f"checked, {range_count}",
    )
    replace_required(
        "tests/test_configuration_value_ranges.py",
        "count, 307",
        f"count, {range_count}",
    )
    replace_required(
        "tests/test_jogger_payload_performance_ranges.py",
        "len(self.ranges), 307",
        f"len(self.ranges), {range_count}",
    )


def align_availability_contracts() -> None:
    configurations = {
        "sandero_iii_expression_ecog120_manual",
        "sandero_iii_journey_ecog120_manual",
        "sandero_stepway_iii_essential_ecog120_manual",
        "sandero_stepway_iii_expression_ecog120_automatic",
        "sandero_stepway_iii_expression_ecog120_manual",
        "sandero_stepway_iii_extreme_ecog120_automatic",
        "sandero_stepway_iii_extreme_ecog120_manual",
    }
    rows = [
        row
        for row in read_rows(AVAILABILITY)
        if row["configuration_code"] in configurations
        and row["observation_date"] == AS_OF
    ]
    total = len(rows)
    status_counts = Counter(row["availability_status"] for row in rows)
    configuration_counts = Counter(row["configuration_code"] for row in rows)
    paths = (
        "tests/test_sandero_50_kmh_noise_level_model.py",
        "tests/test_sandero_50_kmh_noise_level_values.py",
        "tests/test_sandero_euro_6e_bis_model.py",
        "tests/test_sandero_euro_6e_bis_values.py",
        "tests/test_sandero_exterior_colour_values.py",
        "tests/test_sandero_front_wheel_drive_values.py",
        "tests/test_sandero_maximum_payload_model.py",
        "tests/test_sandero_number_of_doors_values.py",
        "tests/test_sandero_passive_safety_availability.py",
        "tests/test_sandero_standard_tyre_specification.py",
        "tests/test_sandero_total_valve_count_model.py",
    )
    for path in paths:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        if "419" in text:
            text = text.replace("419", str(total))
        elif str(total) not in text:
            raise AlignmentError(f"availability snapshot not found in {path}")
        write_text(target, text)

    path = "tests/test_sandero_equipment_availability.py"
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    text = re.sub(
        r'("sandero_stepway_iii_extreme_ecog120_manual":)\s*\d+',
        rf'\g<1> {configuration_counts["sandero_stepway_iii_extreme_ecog120_manual"]}',
        text,
    )
    text = re.sub(
        r'self\.assertEqual\(len\(self\.rows\),\s*\d+\)',
        f'self.assertEqual(len(self.rows), {total})',
        text,
    )
    text = re.sub(
        r'Counter\(\{"standard":\s*\d+,\s*"not_available":\s*\d+\}\)',
        (
            'Counter({"standard": '
            f'{status_counts["standard"]}, "not_available": '
            f'{status_counts["not_available"]}'
            '})'
        ),
        text,
    )
    write_text(target, text)


def align_comparison_contracts(default_report: dict[str, object]) -> None:
    total = len(comparison.difference_csv_rows(default_report))
    replace_required(
        "tests/test_duster_ecog120_reporting_scope.py",
        'default["summary"]["total_differences"], 377',
        f'default["summary"]["total_differences"], {total}',
    )
    replace_required(
        "tests/configuration_comparison_pair_summary_contract.py",
        "            377,",
        f"            {total},",
    )

    path = "tests/configuration_comparison_context_filter_contract.py"
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    text = re.sub(
        r'self\.assertEqual\(len\(core\.difference_csv_rows\(report\)\),\s*\d+\)',
        f'self.assertEqual(len(core.difference_csv_rows(report)), {total})',
        text,
    )
    contexts = context_filter.difference_contexts(default_report)
    keys = (
        "",
        "fuel_type_code=",
        "fuel_type_code=lpg",
        "fuel_type_code=petrol",
        "market=PL;currency_code=PLN",
    )
    expected_counts = {
        key: len(
            context_filter.difference_csv_rows(
                default_report,
                difference_context=key,
                known_contexts=contexts,
            )
        )
        for key in keys
    }
    replacement = "expected_counts = " + python_literal(expected_counts)
    text, count = re.subn(
        r'expected_counts = \{.*?\n        \}',
        replacement,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise AlignmentError("context-count snapshot block not found")
    write_text(target, text)

    rows = pair_summary.pair_summary_rows(default_report)
    pair_total = sum(int(row["total_different"]) for row in rows)
    if pair_total != total:
        raise AlignmentError(
            f"pair-summary total {pair_total} differs from comparison total {total}"
        )


def align_dimension_contracts() -> None:
    versions = {
        row["code"]: row
        for row in read_rows(ROOT / "data/master/versions.csv")
    }
    models = {
        row["code"]: versions.get(row.get("version_code", ""), {}).get(
            "model_code", ""
        )
        for row in read_rows(ROOT / "data/master/configurations.csv")
        if row.get("status") == "active"
    }
    core_dimensions = {
        "overall_length",
        "overall_width",
        "overall_width_with_mirrors",
        "overall_height",
        "roof_height_with_rails",
        "wheelbase",
        "ground_clearance",
        "front_track",
        "rear_track",
        "front_overhang",
        "rear_overhang",
        "approach_angle",
        "departure_angle",
    }
    stepway = [
        row
        for row in read_rows(VALUES)
        if models.get(row["configuration_code"]) == "sandero_stepway_iii"
        and row["attribute_code"] in core_dimensions
    ]
    count = len(stepway)
    replace_required(
        "tools/review_official_brochure_residual_evidence_20260726.py",
        'len(selected["sandero_stepway_iii"]) == 56',
        f'len(selected["sandero_stepway_iii"]) == {count}',
    )
    replace_required(
        "tests/test_official_brochure_residual_evidence_review.py",
        'len(selected["sandero_stepway_iii"]), 56',
        f'len(selected["sandero_stepway_iii"]), {count}',
    )


def align_spring_contracts(state: dict[str, object], range_count: int) -> None:
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    counts = reconciliation["summary"]["active_evidence_record_counts"]
    path = "tests/test_spring_technical_20260219.py"
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    replacements = {
        'state["baseline"]["configuration_values"], 3558': (
            'state["baseline"]["configuration_values"], '
            f'{state["baseline"]["configuration_values"]}'
        ),
        'state["baseline"]["configuration_value_ranges"], 307': (
            'state["baseline"]["configuration_value_ranges"], '
            f'{range_count}'
        ),
        'counts["configuration_attribute_values"], 3481': (
            'counts["configuration_attribute_values"], '
            f'{counts["configuration_attribute_values"]}'
        ),
        'counts["configuration_attribute_value_ranges"], 307': (
            'counts["configuration_attribute_value_ranges"], '
            f'{counts["configuration_attribute_value_ranges"]}'
        ),
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
        elif new not in text:
            raise AlignmentError(f"Spring snapshot missing: {old}")
    write_text(target, text)


def update_manifest() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    manifest = set(state["current_package"].get("manifest_paths", []))
    manifest.update(CHANGED_PATHS)
    state["current_package"]["manifest_paths"] = sorted(manifest)
    STATE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def apply() -> None:
    range_count = len(read_rows(RANGES))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    complete, coverage, compared = sandero_reports()
    write_text(
        ROOT / "tests/test_sandero_ecog120_manual_reporting_scope.py",
        render_sandero_reporting_test(complete, coverage, compared),
    )
    align_previous_source_gap_contracts()
    align_range_contracts(range_count)
    align_availability_contracts()
    default_report = comparison.collect_report(
        ROOT,
        DEFAULT_COMPLETENESS,
        DEFAULT_EVIDENCE,
    )
    align_comparison_contracts(default_report)
    align_dimension_contracts()
    align_spring_contracts(state, range_count)
    update_manifest()
    print(
        "Sandero Stepway Extreme snapshot contracts aligned: "
        f"ranges={range_count}, differences={len(comparison.difference_csv_rows(default_report))}"
    )


if __name__ == "__main__":
    apply()
