#!/usr/bin/env python3
"""Align current-repository contracts after the final Sandero source closure."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"
RESIDUAL_IMPORTER = ROOT / "tools" / "import_sandero_residual_source_closure_20260801.py"
PACKAGE = ROOT / "project" / "packages" / "sandero-residual-source-closure-20260801.md"

AVAILABILITY_COUNT_TESTS = (
    "tests/test_sandero_50_kmh_noise_level_model.py",
    "tests/test_sandero_50_kmh_noise_level_values.py",
    "tests/test_sandero_equipment_availability.py",
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

HISTORICAL_SOURCE_TESTS = (
    "tests/test_sandero_stepway_essential_source_gap_20260626.py",
    "tests/test_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    "tests/test_sandero_stepway_extreme_source_gap_20260626.py",
)

HISTORICAL_SOURCE_TOOLS = (
    "tools/import_sandero_stepway_essential_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_source_gap_20260626.py",
    "tools/import_sandero_stepway_extreme_auto_source_gap_20260626.py",
    "tools/import_sandero_stepway_extreme_source_gap_20260626.py",
)

MANIFEST_ADDITIONS = tuple(
    sorted(
        {
            *AVAILABILITY_COUNT_TESTS,
            *HISTORICAL_SOURCE_TESTS,
            *HISTORICAL_SOURCE_TOOLS,
            "tests/configuration_comparison_context_filter_contract.py",
            "tests/configuration_comparison_pair_summary_contract.py",
            "tests/test_duster_ecog120_reporting_scope.py",
            "tests/test_existing_configuration_missing_data_analysis.py",
            "tests/test_sandero_ecog120_manual_reporting_scope.py",
            "tests/test_spring_technical_20260219.py",
            "tools/align_sandero_residual_source_closure_contracts_20260801.py",
        }
    )
)

OLD_REPORTING_CONTRACTS = '''EXPECTED_TECHNICAL = {'applicable': 300, 'coverage_percent': '95.33', 'denominator': 300, 'missing': 14, 'not_applicable': 0, 'present': 286}
EXPECTED_EQUIPMENT = {'applicable': 345,
 'coverage_percent': '86.67',
 'denominator': 345,
 'missing': 46,
 'not_applicable': 0,
 'not_available': 23,
 'optional': 0,
 'recorded': 299,
 'standard': 276,
 'unknown': 0}
EXPECTED_SOURCE_REGISTRATION = {'expected': 5, 'future': 0, 'inactive': 0, 'metadata_complete': 5, 'missing': 0, 'registered': 5}
EXPECTED_AREAS = {'covered': 10, 'denominator': 20, 'missing': 0, 'partial': 10, 'source_missing': 0}
EXPECTED_SECTIONS = {'covered': 135, 'denominator': 175, 'missing': 7, 'not_applicable': 0, 'partial': 33, 'source_missing': 0}
EXPECTED_COMPARISON_SUMMARY = {'prices': {'comparisons': 10, 'equal': 0, 'different': 10, 'not_comparable': 0},
 'technical': {'comparisons': 688, 'equal': 467, 'different': 166, 'not_comparable': 55},
 'equipment': {'comparisons': 690, 'equal': 528, 'different': 17, 'not_comparable': 145},
 'total_differences': 193}
EXPECTED_EVIDENCE_SUMMARY = {'total': 60, 'ambiguous': 0, 'found': 0, 'not_stated': 43, 'out_of_scope': 17}
EXPECTED_PAIR_TYPES = {'different_version_same_transmission': 10}
EXPECTED_NOT_COMPARABLE = {'technical': 55, 'equipment': 145, 'prices': 0}
EXPECTED_RANGED = 43
EXPECTED_TECHNICAL_GAPS = 14
EXPECTED_EQUIPMENT_GAPS = 46
EXPECTED_COVERAGE_GAPS = 60
'''

NEW_REPORTING_CONTRACTS = '''EXPECTED_TECHNICAL = {'applicable': 300, 'coverage_percent': '96.00', 'denominator': 300, 'missing': 12, 'not_applicable': 0, 'present': 288}
EXPECTED_EQUIPMENT = {'applicable': 345,
 'coverage_percent': '86.96',
 'denominator': 345,
 'missing': 45,
 'not_applicable': 0,
 'not_available': 23,
 'optional': 0,
 'recorded': 300,
 'standard': 277,
 'unknown': 0}
EXPECTED_SOURCE_REGISTRATION = {'expected': 5, 'future': 0, 'inactive': 0, 'metadata_complete': 5, 'missing': 0, 'registered': 5}
EXPECTED_AREAS = {'covered': 12, 'denominator': 20, 'missing': 0, 'partial': 8, 'source_missing': 0}
EXPECTED_SECTIONS = {'covered': 138, 'denominator': 175, 'missing': 7, 'not_applicable': 0, 'partial': 30, 'source_missing': 0}
EXPECTED_COMPARISON_SUMMARY = {'prices': {'comparisons': 10, 'equal': 0, 'different': 10, 'not_comparable': 0},
 'technical': {'comparisons': 688, 'equal': 469, 'different': 171, 'not_comparable': 48},
 'equipment': {'comparisons': 690, 'equal': 529, 'different': 20, 'not_comparable': 141},
 'total_differences': 201}
EXPECTED_EVIDENCE_SUMMARY = {'total': 57, 'ambiguous': 0, 'found': 0, 'not_stated': 40, 'out_of_scope': 17}
EXPECTED_PAIR_TYPES = {'different_version_same_transmission': 10}
EXPECTED_NOT_COMPARABLE = {'technical': 48, 'equipment': 141, 'prices': 0}
EXPECTED_RANGED = 43
EXPECTED_TECHNICAL_GAPS = 12
EXPECTED_EQUIPMENT_GAPS = 45
EXPECTED_COVERAGE_GAPS = 57
'''


class AlignmentError(RuntimeError):
    pass


def read(path: str | Path) -> str:
    target = ROOT / path if isinstance(path, str) else path
    return target.read_text(encoding="utf-8")


def write(path: str | Path, content: str) -> None:
    target = ROOT / path if isinstance(path, str) else path
    target.write_text(content, encoding="utf-8", newline="\n")


def replace_exact(path: str | Path, old: str, new: str) -> None:
    content = read(path)
    if old in content:
        content = content.replace(old, new)
        write(path, content)
        return
    if new not in content:
        raise AlignmentError(f"expected contract text not found: {path}")


def replace_number(path: str, old: int, new: int) -> None:
    content = read(path)
    pattern = re.compile(rf"\b{old}\b")
    updated, count = pattern.subn(str(new), content)
    if count:
        write(path, updated)
        return
    if not re.search(rf"\b{new}\b", content):
        raise AlignmentError(f"numeric contract {old}->{new} not found: {path}")


def replace_test_selection_block(path: str, end_method: str) -> None:
    content = read(path)
    lines = content.splitlines(keepends=True)
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if "selected = " in line and '["selected_next_package"]' in line
        )
        end = next(
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith(f"    def {end_method}")
        )
    except StopIteration:
        if 'self.assertIsNone(selected)' in content and '["eligible_candidate_count"], 0' in content:
            return
        raise AlignmentError(f"selection test block not found: {path}")
    selected_expression = lines[start].strip().split(" = ", 1)[1]
    payload_expression = selected_expression.rsplit("[", 1)[0]
    replacement = [
        f"        selected = {selected_expression}\n",
        '        self.assertIsNone(selected)\n',
        f'        self.assertEqual({payload_expression}["summary"]["eligible_candidate_count"], 0)\n',
        "\n",
    ]
    lines[start:end] = replacement
    write(path, "".join(lines))


def replace_importer_selection_block(path: str) -> None:
    content = read(path)
    lines = content.splitlines(keepends=True)
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if 'selected = expected_analysis.get("selected_next_package")' in line
        )
        end = next(
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("    state = ")
        )
    except StopIteration:
        desired = 'expected_analysis["summary"]["eligible_candidate_count"] != 0'
        if desired in content:
            return
        raise AlignmentError(f"selection importer block not found: {path}")
    replacement = [
        '    selected = expected_analysis.get("selected_next_package")\n',
        '    if (\n',
        '        selected is not None\n',
        '        or expected_analysis["summary"]["eligible_candidate_count"] != 0\n',
        '    ):\n',
        '        raise ContractError(\n',
        '            f"analysis should have no eligible source after residual closure: {selected}"\n',
        '        )\n',
    ]
    lines[start:end] = replacement
    write(path, "".join(lines))


def update_importer_manifest() -> list[str]:
    content = read(RESIDUAL_IMPORTER)
    match = re.search(
        r"MANIFEST_PATHS = \[\n(?P<body>.*?)\n\]\n\n\nclass ClosureError",
        content,
        flags=re.DOTALL,
    )
    if match is None:
        raise AlignmentError("residual importer manifest block not found")
    existing = re.findall(r'^    "([^"]+)",$', match.group("body"), flags=re.MULTILINE)
    manifest = list(existing)
    for path in MANIFEST_ADDITIONS:
        if path not in manifest:
            manifest.append(path)
    rendered = "MANIFEST_PATHS = [\n" + "".join(
        f'    "{path}",\n' for path in manifest
    ) + "]\n\n\nclass ClosureError"
    updated = content[: match.start()] + rendered + content[match.end() :]
    write(RESIDUAL_IMPORTER, updated)
    return manifest


def update_state_manifest(manifest: Iterable[str]) -> None:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    current = payload.get("current_package")
    if not isinstance(current, dict) or current.get("package_id") != "sandero_residual_source_closure_006":
        raise AlignmentError("current package is not the Sandero residual closure")
    current["manifest_paths"] = list(manifest)
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_package_record() -> None:
    content = read(PACKAGE)
    marker = "## Result\n"
    section = (
        "## Quality-contract alignment\n\n"
        "Current-repository snapshots and historical completed-package checks were advanced "
        "to the post-closure state. They now accept zero eligible source candidates, preserve "
        "all seven exhausted candidates, and include the one new availability record and two "
        "new scalar values without altering historical package evidence.\n\n"
    )
    if section in content:
        return
    if marker not in content:
        raise AlignmentError("package result marker not found")
    write(PACKAGE, content.replace(marker, section + marker, 1))


def apply() -> None:
    for path in AVAILABILITY_COUNT_TESTS:
        replace_number(path, 422, 423)

    replace_exact(
        "tests/test_sandero_equipment_availability.py",
        '    "sandero_iii_journey_ecog120_manual": 63,',
        '    "sandero_iii_journey_ecog120_manual": 64,',
    )
    replace_exact(
        "tests/test_sandero_equipment_availability.py",
        '            Counter({"standard": 392, "not_available": 30}),',
        '            Counter({"standard": 393, "not_available": 30}),',
    )
    replace_exact(
        "tests/test_sandero_equipment_availability.py",
        '''        self.assertTrue(
            all(
                row["notes"].startswith("Source page 3:")
                or row["notes"].startswith("Source page 4:")
                for row in self.rows
            )
        )
''',
        '''        for row in self.rows:
            self.assertRegex(
                row["notes"],
                r"^Source page [34](?:, section [^:]+)?:",
            )
''',
    )

    replace_exact(
        "tests/test_sandero_ecog120_manual_reporting_scope.py",
        OLD_REPORTING_CONTRACTS,
        NEW_REPORTING_CONTRACTS,
    )
    replace_exact(
        "tests/test_duster_ecog120_reporting_scope.py",
        '        self.assertEqual(default["summary"]["total_differences"], 400)',
        '        self.assertEqual(default["summary"]["total_differences"], 411)',
    )
    replace_exact(
        "tests/configuration_comparison_context_filter_contract.py",
        "        self.assertEqual(len(core.difference_csv_rows(report)), 400)",
        "        self.assertEqual(len(core.difference_csv_rows(report)), 411)",
    )
    replace_exact(
        "tests/configuration_comparison_pair_summary_contract.py",
        "            400,\n        )",
        "            411,\n        )",
    )
    replace_exact(
        "tests/test_existing_configuration_missing_data_analysis.py",
        '        self.assertGreaterEqual(summary["eligible_candidate_count"], 1)',
        '        self.assertEqual(summary["eligible_candidate_count"], 0)',
    )
    replace_test_selection_block(
        "tests/test_existing_configuration_missing_data_analysis.py",
        "test_not_applicable_slots_are_not_reported_missing",
    )

    for path in (
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    ):
        replace_exact(
            path,
            '        self.assertEqual(payload["summary"]["missing_technical_count"], 101)',
            '        self.assertEqual(payload["summary"]["missing_technical_count"], 97)',
        )
        replace_exact(
            path,
            '        self.assertEqual(payload["summary"]["exhausted_source_candidate_count"], 6)',
            '        self.assertEqual(payload["summary"]["exhausted_source_candidate_count"], 7)',
        )
    replace_exact(
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
        '        self.assertEqual(review["reconciliation"]["resolved_unique_slots"], 7)',
        '        self.assertEqual(review["reconciliation"]["resolved_unique_slots"], 6)',
    )
    for path in HISTORICAL_SOURCE_TESTS:
        replace_test_selection_block(path, "test_full_materialized_contract_passes")

    for path in (
        "tools/import_sandero_stepway_essential_source_gap_20260626.py",
        "tools/import_sandero_stepway_expression_source_gap_20260626.py",
    ):
        replace_number(path, 101, 97)
        replace_exact(path, "expected 115 remaining technical records", "expected 97 remaining technical records")
        replace_exact(path, "expected exactly 6 exhausted-source candidates", "expected exactly 7 exhausted-source candidates")
        replace_exact(path, '["exhausted_source_candidate_count"] != 6', '["exhausted_source_candidate_count"] != 7')
    for path in HISTORICAL_SOURCE_TOOLS:
        replace_importer_selection_block(path)

    replace_exact(
        "tests/test_spring_technical_20260219.py",
        '        self.assertEqual(state["baseline"]["configuration_values"], 3565)',
        '        self.assertEqual(state["baseline"]["configuration_values"], 3567)',
    )
    replace_exact(
        "tests/test_spring_technical_20260219.py",
        '        self.assertEqual(counts["configuration_attribute_values"], 3488)',
        '        self.assertEqual(counts["configuration_attribute_values"], 3490)',
    )

    update_package_record()
    manifest = update_importer_manifest()
    update_state_manifest(manifest)


def check() -> None:
    for path in AVAILABILITY_COUNT_TESTS:
        if re.search(r"\b422\b", read(path)):
            raise AlignmentError(f"legacy availability count remains: {path}")
    manual = read("tests/test_sandero_ecog120_manual_reporting_scope.py")
    if NEW_REPORTING_CONTRACTS not in manual or OLD_REPORTING_CONTRACTS in manual:
        raise AlignmentError("Sandero manual reporting contracts are stale")
    for path in HISTORICAL_SOURCE_TESTS:
        content = read(path)
        if 'self.assertIsNotNone(selected)' in content:
            raise AlignmentError(f"historical test still expects an eligible source: {path}")
    for path in HISTORICAL_SOURCE_TOOLS:
        content = read(path)
        if 'analysis did not advance to an eligible source' in content:
            raise AlignmentError(f"historical importer still requires an eligible source: {path}")
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    manifest = set(payload["current_package"]["manifest_paths"])
    missing = set(MANIFEST_ADDITIONS) - manifest
    if missing:
        raise AlignmentError(f"package manifest is missing aligned contracts: {sorted(missing)}")
    print("Sandero residual source closure contract alignment: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if not args.check:
            apply()
        check()
    except (AlignmentError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
