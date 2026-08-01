#!/usr/bin/env python3
"""Generate the exact Stepway Expression automatic source-gap package."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_IMPORTER = ROOT / "tools/import_sandero_stepway_extreme_source_gap_20260626.py"
OUT_IMPORTER = ROOT / "tools/import_sandero_stepway_expression_auto_source_gap_20260626.py"
OUT_TEST = ROOT / "tests/test_sandero_stepway_expression_auto_source_gap_20260626.py"
OUT_CLOSE = ROOT / "tools/close_stepway_expression_auto_reporting_dependencies_20260801.py"
OUT_ALIGN = ROOT / "tools/align_sandero_stepway_expression_auto_snapshot_contracts_20260801.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"template fragment not found: {old[:100]!r}")
    return text.replace(old, new, 1)


def replace_regex(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"expected one replacement for {pattern!r}, found {count}")
    return updated


def importer_text() -> str:
    text = TEMPLATE_IMPORTER.read_text(encoding="utf-8")
    replacements = (
        (
            '"""Import exact Stepway Extreme source-gap observations dated 2026-06-26."""',
            '"""Import exact Stepway Expression automatic source-gap observations dated 2026-06-26."""',
        ),
        (
            'sandero_stepway_extreme_source_gap_20260626.csv',
            'sandero_stepway_expression_auto_source_gap_20260626.csv',
        ),
        (
            'sandero_stepway_extreme_source_gap_review.json',
            'sandero_stepway_expression_auto_source_gap_review.json',
        ),
        (
            'sandero_stepway_extreme_source_gap_review.md',
            'sandero_stepway_expression_auto_source_gap_review.md',
        ),
        (
            'sandero-stepway-extreme-source-gap-20260801.md',
            'sandero-stepway-expression-auto-source-gap-20260801.md',
        ),
        (
            'NOWE SANDERO STEPWAY extreme stepway Eco-G 120 f.pdf',
            'NOWE SANDERO STEPWAY expression stepway Eco-G 120 auto f.pdf',
        ),
        (
            'src_pl_sandero_stepway_extreme_ecog120_mt_20260626',
            'src_pl_sandero_stepway_expression_ecog120_at_20260626',
        ),
        (
            'fe7e4012bce170eceecb993af473e6eebb8c1d5c10b33f3edfc222e59c80a115',
            '385409e33a0932e48cbd901b5805f873831ec005c6451cd6ed1623a06fa15667',
        ),
        (
            'sandero_stepway_iii_extreme_ecog120_manual',
            'sandero_stepway_iii_expression_ecog120_automatic',
        ),
        ('EXPECTED_VALUE_FIRST_ID = 3559', 'EXPECTED_VALUE_FIRST_ID = 3561'),
        ('EXPECTED_VALUE_LAST_ID = 3560', 'EXPECTED_VALUE_LAST_ID = 3563'),
        ('EXPECTED_RANGE_FIRST_ID = 308', 'EXPECTED_RANGE_FIRST_ID = 311'),
        ('EXPECTED_RANGE_LAST_ID = 310', 'EXPECTED_RANGE_LAST_ID = 313'),
        ('EXPECTED_AVAILABILITY_FIRST_ID = 5903', 'EXPECTED_AVAILABILITY_FIRST_ID = 5904'),
        ('EXPECTED_AVAILABILITY_LAST_ID = 5903', 'EXPECTED_AVAILABILITY_LAST_ID = 5904'),
        ('if len(rows) != 6:', 'if len(rows) != 7:'),
        ('expected 6 specification rows', 'expected 7 specification rows'),
    )
    for old, new in replacements:
        text = text.replace(old, new)

    contract = '''EXPECTED_SPEC = {
    ("value", "overall_height", "", "1586", "", "", ""),
    ("value", "overall_width_with_mirrors", "", "2012", "", "", ""),
    ("value", "wheel_finish", "", "stalowe", "", "", ""),
    ("range", "ground_clearance", "", "", "170", "200", ""),
    ("range", "max_torque_rpm", "lpg", "", "1750", "3750", ""),
    ("range", "max_torque_rpm", "petrol", "", "2000", "4000", ""),
    ("availability", "parking_assist_system", "", "", "", "", "standard"),
}
REMAINING_TECHNICAL = (
    {"attribute_code": "front_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
    {"attribute_code": "rear_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "lpg", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "reason": "not_stated_in_source"},
    {"attribute_code": "elasticity_80_120", "fuel_type_code": "lpg", "reason": "not_stated_in_source"},
    {"attribute_code": "elasticity_80_120", "fuel_type_code": "petrol", "reason": "not_stated_in_source"},
)
REMAINING_EQUIPMENT = (
    {"attribute_code": "gear_shift_indicator", "reason": "out_of_scope_for_automatic_transmission"},
)
MANIFEST_PATHS = [
    "data/imports/sandero_stepway_expression_auto_source_gap_20260626.csv",
    "data/master/configuration_attribute_availability.csv",
    "data/master/configuration_attribute_value_ranges.csv",
    "data/master/configuration_attribute_values.csv",
    "data/reporting/configuration_gap_evidence.json",
    "data/reporting/configuration_gap_resolution_plan.json",
    "data/reporting/configuration_gap_source_review.json",
    "data/reporting/existing_configuration_missing_data_analysis.json",
    "data/reporting/existing_configuration_missing_data_analysis.md",
    "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json",
    "data/reporting/sandero_stepway_expression_auto_source_gap_review.json",
    "data/reporting/sandero_stepway_expression_auto_source_gap_review.md",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
    "project/STATE_SUMMARY.md",
    "project/packages/sandero-stepway-expression-auto-source-gap-20260801.md",
    "project/state.json",
    "tests/test_sandero_stepway_ecog120_automatic_reporting_scope.py",
    "tests/test_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tools/align_sandero_stepway_expression_auto_snapshot_contracts_20260801.py",
    "tools/close_stepway_expression_auto_reporting_dependencies_20260801.py",
    "tools/import_sandero_stepway_expression_auto_source_gap_20260626.py",
]
'''
    text = replace_regex(
        text,
        r'EXPECTED_SPEC = \{.*?\n\}\nREMAINING_TECHNICAL = \(.*?\n\)\nREMAINING_EQUIPMENT = \(.*?\n\)\nMANIFEST_PATHS = \[.*?\n\]\n',
        contract,
    )

    review = '''def review_payload() -> dict[str, object]:
    return {
        "version": 1,
        "as_of": "2026-08-01",
        "kind": "configuration_source_gap_review",
        "model_code": MODEL_CODE,
        "configuration_code": CONFIGURATION,
        "source_code": SOURCE_CODE,
        "source_path": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": SOURCE_SHA256,
        "source_observation_date": OBSERVATION_DATE,
        "initial_gap": {
            "reviewed_unique_slots": 14,
            "technical_slots": 12,
            "equipment_slots": 2,
        },
        "resolution": {
            "scalar_values": [
                {"attribute_code": "overall_height", "value": "1586", "source_page": 6},
                {"attribute_code": "overall_width_with_mirrors", "value": "2012", "source_page": 6},
                {"attribute_code": "wheel_finish", "value": "stalowe", "source_page": 2},
            ],
            "ranges": [
                {"attribute_code": "ground_clearance", "fuel_type_code": "", "minimum_value": "170", "maximum_value": "200", "source_page": 6},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "source_page": 6},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "petrol", "minimum_value": "2000", "maximum_value": "4000", "source_page": 6},
            ],
            "availability": [
                {"attribute_code": "parking_assist_system", "availability_status": "standard", "source_page": 3}
            ],
        },
        "preserved_out_of_scope": [
            {
                "attribute_code": "gear_shift_indicator",
                "reason": "The canonical decision already classifies the manual gear-shift indicator outside the automatic-transmission scope.",
            }
        ],
        "excluded_alternatives": [
            {"attribute_code": "overall_height", "value": "1535", "reason": "Stepway height without roof rails does not describe the exact standard configuration"},
            {"attribute_code": "overall_width_with_mirrors", "value": "1853", "reason": "folded-mirror width is outside the repository comparison convention"},
        ],
        "reconciliation": {
            "classification": EXHAUSTED_CLASSIFICATION,
            "resolved_unique_slots": 7,
            "preserved_out_of_scope_slots": 1,
            "remaining_unique_slots": 6,
            "remaining_technical_slots": list(REMAINING_TECHNICAL),
            "remaining_equipment_slots": list(REMAINING_EQUIPMENT),
            "boundary": (
                "The source does not state front/rear track widths, maximum-power engine speeds or 80-120 km/h elasticity. "
                "The manual gear-shift indicator remains outside the automatic-transmission scope."
            ),
        },
    }


def render_review_markdown(payload: dict[str, object]) -> str:
'''
    text = replace_regex(text, r'def review_payload\(\).*?\ndef render_review_markdown\(payload: dict\[str, object\]\) -> str:\n', review)

    render = '''def render_review_markdown(payload: dict[str, object]) -> str:
    return (
        "# Sandero Stepway Expression Automatic Source-Gap Review\\n\\n"
        "Status: complete\\n\\n"
        f"Source `{SOURCE_CODE}` was inspected page by page against 14 unique gap decisions for `{CONFIGURATION}`.\\n\\n"
        "## Imported observations\\n\\n"
        "- `overall_height = 1586 mm` for the exact standard configuration with roof rails.\\n"
        "- `overall_width_with_mirrors = 2012 mm` with mirrors unfolded.\\n"
        "- `wheel_finish = stalowe` from the selected 16-inch ATARA steel wheels.\\n"
        "- `ground_clearance = 170-200 mm`.\\n"
        "- `max_torque_rpm = 1750-3750` for LPG and `2000-4000` for petrol.\\n"
        "- `parking_assist_system = standard`, based on the direct rear parking-assistance statement.\\n\\n"
        "## Preserved boundaries\\n\\n"
        "`front_track`, `rear_track`, both `max_power_rpm` contexts and both `elasticity_80_120` contexts are not stated. "
        "`gear_shift_indicator` remains explicitly outside the automatic-transmission scope. No value is projected from a manual sibling configuration.\\n"
    )


def package_text() -> str:
'''
    text = replace_regex(text, r'def render_review_markdown\(payload: dict\[str, object\]\) -> str:.*?\ndef package_text\(\) -> str:\n', render)

    package = '''def package_text() -> str:
    return (
        "# Sandero Stepway Expression Automatic Source Gap\\n\\n"
        "Status: complete\\n\\n"
        "Imported three exact scalar observations, three inclusive ranges and one standard equipment observation from the configuration-specific Polish PDF dated 2026-06-26. "
        "The source is formally exhausted for six unstated technical slots; the gear-shift indicator remains outside the automatic-transmission scope.\\n\\n"
        "No value or availability state was projected from another trim or transmission.\\n"
    )


def update_analysis_outputs() -> dict[str, object]:
'''
    text = replace_regex(text, r'def package_text\(\) -> str:.*?\ndef update_analysis_outputs\(\) -> dict\[str, object\]:\n', package)

    state = '''def update_state(analysis_payload: dict[str, object]) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["phase"] = "Sandero Stepway Expression Automatic Source Gap"
    state["current_package"] = {
        "package_id": "sandero_stepway_expression_auto_source_gap_004",
        "kind": "source_backed_completeness_import",
        "name": "Sandero Stepway Expression Automatic Source Gap",
        "status": "complete",
        "goal": (
            "Resolve every safely representable missing slot from the exact Stepway Expression Eco-G 120 automatic source and preserve not-stated and automatic-transmission boundaries."
        ),
        "manifest_paths": MANIFEST_PATHS,
    }
    selected = analysis_payload.get("selected_next_package")
    if selected:
        model = str(selected["model_code"])
        source = str(selected["source_code"])
        state["next_package"] = {
            "package_id": f"{analysis.slug(model)}_highest_impact_eligible_gap_005",
            "kind": "source_backed_completeness_import",
            "name": f"{model} Highest-Impact Eligible Source Gap",
            "status": "planned",
            "goal": (
                f"Inspect exact missing slots for {model} against source {source or 'mapping to be resolved'} and import only directly stated values or explicit non-applicable classifications."
            ),
            "manifest_paths": [],
        }
    else:
        state["next_package"] = {
            "package_id": "configuration_gap_closure_documentation_milestone_001",
            "kind": "documentation_milestone",
            "name": "Configuration Gap Closure Documentation Milestone",
            "status": "planned",
            "goal": "Record the completed source-backed configuration-gap closure series.",
            "manifest_paths": [],
        }
    write_json(STATE, state)


def apply() -> None:
'''
    text = replace_regex(text, r'def update_state\(analysis_payload: dict\[str, object\]\) -> None:.*?\ndef apply\(\) -> None:\n', state)

    text = replace_regex(
        text,
        r'    resolved_technical = \{.*?\n    \}\n    scoped =',
        '''    resolved_technical = {
        "ground_clearance",
        "overall_height",
        "overall_width_with_mirrors",
        "max_torque_rpm",
        "wheel_finish",
    }
    scoped =''',
    )
    text = text.replace(
        'state["current_package"]["package_id"]\n        != "sandero_stepway_extreme_source_gap_003"',
        'state["current_package"]["package_id"]\n        != "sandero_stepway_expression_auto_source_gap_004"',
    )
    text = text.replace(
        '"Stepway Extreme source-gap observations: PASS "\n        "(2 values + 3 ranges + 1 availability)"',
        '"Stepway Expression automatic source-gap observations: PASS "\n        "(3 values + 3 ranges + 1 availability)"',
    )
    return text


def test_text() -> str:
    return '''"""Contract tests for the exact Stepway Expression automatic source-gap package."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools import import_sandero_stepway_expression_auto_source_gap_20260626 as package

ROOT = Path(__file__).resolve().parents[1]


class SanderoStepwayExpressionAutomaticSourceGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = package.load_spec()
        cls.values = package.generated_value_rows(cls.spec)
        cls.ranges = package.generated_range_rows(cls.spec)
        cls.availability = package.generated_availability_rows(cls.spec)

    def test_exact_source_identity_and_specification(self) -> None:
        self.assertEqual(package.sha256(package.SOURCE), package.SOURCE_SHA256)
        self.assertEqual(len(self.spec), 7)
        self.assertEqual(len(self.values), 3)
        self.assertEqual(len(self.ranges), 3)
        self.assertEqual(len(self.availability), 1)
        self.assertEqual(
            {(row["record_type"], row["attribute_code"], row["fuel_type_code"]) for row in self.spec},
            {
                ("value", "overall_height", ""),
                ("value", "overall_width_with_mirrors", ""),
                ("value", "wheel_finish", ""),
                ("range", "ground_clearance", ""),
                ("range", "max_torque_rpm", "lpg"),
                ("range", "max_torque_rpm", "petrol"),
                ("availability", "parking_assist_system", ""),
            },
        )

    def test_three_scalar_values_are_exact(self) -> None:
        self.assertEqual(
            {(row["attribute_code"], row["fuel_type_code"]): row["value"] for row in self.values},
            {
                ("overall_height", ""): "1586",
                ("overall_width_with_mirrors", ""): "2012",
                ("wheel_finish", ""): "stalowe",
            },
        )

    def test_three_ranges_preserve_printed_endpoints(self) -> None:
        self.assertEqual(
            {(row["attribute_code"], row["fuel_type_code"]): (row["minimum_value"], row["maximum_value"]) for row in self.ranges},
            {
                ("ground_clearance", ""): ("170", "200"),
                ("max_torque_rpm", "lpg"): ("1750", "3750"),
                ("max_torque_rpm", "petrol"): ("2000", "4000"),
            },
        )
        self.assertTrue(all(row["lower_inclusive"] == "true" and row["upper_inclusive"] == "true" for row in self.ranges))

    def test_rear_parking_assistance_is_direct_standard_equipment(self) -> None:
        self.assertEqual(len(self.availability), 1)
        row = self.availability[0]
        self.assertEqual(row["attribute_code"], "parking_assist_system")
        self.assertEqual(row["availability_status"], "standard")
        self.assertIn("rear parking assistance", row["notes"])

    def test_materialized_ids_are_exact_contiguous_suffixes(self) -> None:
        values = package.selected_by_codes(package.read_rows(package.VALUE_OUTPUT), {row["code"] for row in self.values})
        ranges = package.selected_by_codes(package.read_rows(package.RANGE_OUTPUT), {row["code"] for row in self.ranges})
        availability = package.selected_by_codes(package.read_rows(package.AVAILABILITY_OUTPUT), {row["code"] for row in self.availability})
        self.assertEqual(sorted(int(row["id"]) for row in values), [3561, 3562, 3563])
        self.assertEqual(sorted(int(row["id"]) for row in ranges), [311, 312, 313])
        self.assertEqual(sorted(int(row["id"]) for row in availability), [5904])

    def test_review_partitions_resolved_out_of_scope_and_unstated_slots(self) -> None:
        review = json.loads(package.REVIEW_JSON.read_text(encoding="utf-8"))
        self.assertEqual(review, package.review_payload())
        reconciliation = review["reconciliation"]
        self.assertEqual(reconciliation["classification"], package.EXHAUSTED_CLASSIFICATION)
        self.assertEqual(reconciliation["resolved_unique_slots"], 7)
        self.assertEqual(reconciliation["preserved_out_of_scope_slots"], 1)
        self.assertEqual(reconciliation["remaining_unique_slots"], 6)

    def test_reanalysis_exhausts_source_and_advances_selection(self) -> None:
        payload = package.analysis.collect(ROOT)
        current = next(item for item in payload["ranked_candidates"] if item["source_code"] == package.SOURCE_CODE)
        self.assertEqual(current["selection_status"], package.EXHAUSTED_CLASSIFICATION)
        selected = payload["selected_next_package"]
        self.assertIsNotNone(selected)
        self.assertEqual(selected["selection_status"], "eligible")
        self.assertNotEqual(selected["source_code"], package.SOURCE_CODE)

    def test_full_materialized_contract_passes(self) -> None:
        package.verify_materialized()


if __name__ == "__main__":
    unittest.main()
'''


def close_text() -> str:
    return '''#!/usr/bin/env python3
"""Close reporting dependencies resolved by the Stepway Expression automatic source-gap import."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import verified_pdf_candidate_coverage_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATHS = (
    ROOT / "data/reporting/configuration_gap_evidence.json",
    ROOT / "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json",
)
SOURCE_REVIEW = ROOT / "data/reporting/configuration_gap_source_review.json"
TARGET_CONFIGURATION = "sandero_stepway_iii_expression_ecog120_automatic"
TARGET_SOURCE = "src_pl_sandero_stepway_expression_ecog120_at_20260626"
TARGETS = {
    ("technical", "ground_clearance", ""),
    ("technical", "max_torque_rpm", "lpg"),
    ("technical", "max_torque_rpm", "petrol"),
    ("technical", "overall_height", ""),
    ("technical", "overall_width_with_mirrors", ""),
    ("technical", "wheel_finish", ""),
    ("equipment", "parking_assist_system", ""),
}


class DependencyError(RuntimeError):
    pass


def canonical(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\\n"


def load_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DependencyError(f"expected JSON object: {path}")
    return payload


def targeted_decision(decision: object) -> bool:
    if not isinstance(decision, dict):
        return False
    return (
        decision.get("source_code") == TARGET_SOURCE
        and decision.get("configuration_code") == TARGET_CONFIGURATION
        and (str(decision.get("domain", "")), str(decision.get("attribute_code", "")), str(decision.get("fuel_type_code", ""))) in TARGETS
    )


def targeted_key(key: object) -> bool:
    if not isinstance(key, str):
        return False
    parts = key.split("|")
    if len(parts) != 6:
        return False
    domain, source, configuration, _category, attribute, fuel = parts
    return source == TARGET_SOURCE and configuration == TARGET_CONFIGURATION and (domain, attribute, "" if fuel == "none" else fuel) in TARGETS


def filtered_evidence(payload: dict[str, object]) -> tuple[dict[str, object], int]:
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise DependencyError("unexpected evidence payload")
    output = dict(payload)
    output["decisions"] = [item for item in decisions if not targeted_decision(item)]
    return output, len(decisions) - len(output["decisions"])


def filtered_source_review(payload: dict[str, object]) -> tuple[dict[str, object], int]:
    keys = payload.get("review_triage_keys")
    if not isinstance(keys, list):
        raise DependencyError("unexpected configuration source-review payload")
    output = dict(payload)
    output["review_triage_keys"] = [item for item in keys if not targeted_key(item)]
    return output, len(keys) - len(output["review_triage_keys"])


def reconciliation_outputs() -> tuple[str, str]:
    payload, markdown = reconciliation.build_from_paths(ROOT, reconciliation.DEFAULT_LEDGER, reconciliation.DEFAULT_REVIEW)
    return reconciliation.canonical_json(payload), markdown


def apply() -> None:
    for path in EVIDENCE_PATHS:
        evidence, _removed = filtered_evidence(load_object(path))
        path.write_text(canonical(evidence), encoding="utf-8")
    source_review, review_removed = filtered_source_review(load_object(SOURCE_REVIEW))
    if review_removed not in {0, 1}:
        raise DependencyError(f"expected zero or one resolved source-review key, found {review_removed}")
    SOURCE_REVIEW.write_text(canonical(source_review), encoding="utf-8")
    json_text, markdown = reconciliation_outputs()
    (ROOT / reconciliation.DEFAULT_JSON).write_text(json_text, encoding="utf-8")
    (ROOT / reconciliation.DEFAULT_MARKDOWN).write_text(markdown, encoding="utf-8")


def check() -> None:
    for path in EVIDENCE_PATHS:
        _, remaining = filtered_evidence(load_object(path))
        if remaining:
            raise DependencyError(f"{remaining} resolved evidence decisions remain in {path}")
    _, review_remaining = filtered_source_review(load_object(SOURCE_REVIEW))
    if review_remaining:
        raise DependencyError(f"{review_remaining} resolved source-review keys remain")
    json_text, markdown = reconciliation_outputs()
    if (ROOT / reconciliation.DEFAULT_JSON).read_text(encoding="utf-8") != json_text:
        raise DependencyError("coverage reconciliation JSON is stale")
    if (ROOT / reconciliation.DEFAULT_MARKDOWN).read_text(encoding="utf-8") != markdown:
        raise DependencyError("coverage reconciliation Markdown is stale")
    print("Stepway Expression automatic reporting dependencies: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        check() if args.check else (apply(), check())
    except (DependencyError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def align_text() -> str:
    return r'''#!/usr/bin/env python3
"""Align deterministic snapshots after the Stepway Expression automatic import."""
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
AUTO_SPEC = ROOT / "data/reporting/sandero_stepway_ecog120_automatic_completeness.json"
AUTO_EVIDENCE = ROOT / "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json"
DEFAULT_COMPLETENESS = ROOT / comparison.DEFAULT_COMPLETENESS_SPEC
DEFAULT_EVIDENCE = ROOT / comparison.DEFAULT_EVIDENCE_SPEC
AVAILABILITY = ROOT / "data/master/configuration_attribute_availability.csv"
RANGES = ROOT / "data/master/configuration_attribute_value_ranges.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
RECONCILIATION = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
STATE = ROOT / "project/state.json"
CHANGED_PATHS = {
    "tools/align_sandero_stepway_expression_auto_snapshot_contracts_20260801.py",
    "tools/close_stepway_expression_auto_reporting_dependencies_20260801.py",
    "tools/import_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tools/import_sandero_stepway_extreme_source_gap_20260626.py",
    "tools/import_sandero_stepway_essential_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_source_gap_20260626.py",
    "tools/review_official_brochure_residual_evidence_20260726.py",
    "tests/test_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tests/test_sandero_stepway_ecog120_automatic_reporting_scope.py",
    "tests/test_sandero_stepway_extreme_source_gap_20260626.py",
    "tests/test_sandero_stepway_essential_source_gap_20260626.py",
    "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    "tests/test_configuration_value_ranges.py",
    "tests/test_jogger_payload_performance_ranges.py",
    "tests/test_sandero_equipment_availability.py",
    "tests/test_sandero_passive_safety_availability.py",
    "tests/configuration_comparison_context_filter_contract.py",
    "tests/configuration_comparison_pair_summary_contract.py",
    "tests/test_duster_ecog120_reporting_scope.py",
    "tests/test_official_brochure_residual_evidence_review.py",
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


def python_literal(value: object) -> str:
    return pprint.pformat(value, sort_dicts=False, width=120)


def automatic_reports() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    return (
        completeness.collect_report(ROOT, AUTO_SPEC, AS_OF),
        source_coverage.collect_report(ROOT, AUTO_SPEC, AS_OF),
        comparison.collect_report(ROOT, AUTO_SPEC, AUTO_EVIDENCE, AS_OF),
    )


def render_automatic_test(complete: dict[str, object], coverage: dict[str, object], compared: dict[str, object]) -> str:
    pair_types = Counter(pair["pair_type"] for pair in compared["pairs"])
    not_comparable = {
        domain: sum(pair["summary"][domain]["not_comparable"] for pair in compared["pairs"])
        for domain in ("technical", "equipment", "prices")
    }
    ranged = [item for pair in compared["pairs"] for item in pair["technical"] if "minimum_value" in item["left"] or "minimum_value" in item["right"]]
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
SPEC = REPOSITORY / "data/reporting/sandero_stepway_ecog120_automatic_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json"
CONFIGURATIONS = {{"sandero_stepway_iii_expression_ecog120_automatic", "sandero_stepway_iii_extreme_ecog120_automatic"}}
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


class SanderoStepwayEcoG120AutomaticReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_two_automatic_configurations(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 2)
        self.assertEqual(scope["technical_slots"], 54)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 2)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(self.completeness["technical"], EXPECTED_TECHNICAL)
        self.assertEqual(self.completeness["equipment"], EXPECTED_EQUIPMENT)
        self.assertEqual(len(self.completeness["gaps"]["technical"]), EXPECTED_TECHNICAL_GAPS)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), EXPECTED_EQUIPMENT_GAPS)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(self.coverage["source_registration"], EXPECTED_SOURCE_REGISTRATION)
        self.assertEqual(self.coverage["areas"], EXPECTED_AREAS)
        self.assertEqual(self.coverage["sections"], EXPECTED_SECTIONS)
        self.assertEqual(self.coverage["records"]["technical"]["present"], EXPECTED_TECHNICAL["present"])
        self.assertEqual(self.coverage["records"]["equipment"]["present"], EXPECTED_EQUIPMENT["recorded"])
        self.assertEqual(self.coverage["records"]["prices"]["present"], 2)
        self.assertEqual(len(self.coverage["gaps"]), EXPECTED_COVERAGE_GAPS)

    def test_single_pair_is_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(Counter(pair["pair_type"] for pair in pairs), Counter(EXPECTED_PAIR_TYPES))
        for domain, expected in EXPECTED_NOT_COMPARABLE.items():
            self.assertEqual(sum(pair["summary"][domain]["not_comparable"] for pair in pairs), expected)

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(self.comparison["summary"], EXPECTED_COMPARISON_SUMMARY)

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], EXPECTED_EVIDENCE_SUMMARY)
        ranged = [item for pair in self.comparison["pairs"] for item in pair["technical"] if "minimum_value" in item["left"] or "minimum_value" in item["right"]]
        self.assertEqual(len(ranged), EXPECTED_RANGED)

    def test_two_prices_are_present_and_the_pair_price_differs(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 2)
        self.assertEqual(self.comparison["summary"]["prices"]["different"], 1)


if __name__ == "__main__":
    unittest.main()
'''


def regex_update(path: str, pattern: str, replacement: str, *, count: int = 0) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    updated, changed = re.subn(pattern, replacement, text, count=count, flags=re.MULTILINE | re.DOTALL)
    if changed == 0 and replacement not in text:
        raise AlignmentError(f"snapshot pattern not found in {path}: {pattern}")
    write_text(target, updated if changed else text)


def align_previous_contracts() -> None:
    payload = analysis.collect(ROOT)
    missing = int(payload["summary"]["missing_technical_count"])
    exhausted = int(payload["summary"]["exhausted_source_candidate_count"])
    paths = (
        "tools/import_sandero_stepway_essential_source_gap_20260626.py",
        "tools/import_sandero_stepway_expression_source_gap_20260626.py",
        "tools/import_sandero_stepway_extreme_source_gap_20260626.py",
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
        "tests/test_sandero_stepway_extreme_source_gap_20260626.py",
    )
    for path in paths:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        text = re.sub(r'(missing_technical_count"\]\s*(?:!=|,))\s*\d+', rf'\g<1> {missing}', text)
        text = re.sub(r'(exhausted_source_candidate_count"\]\s*(?:!=|,))\s*\d+', rf'\g<1> {exhausted}', text)
        text = re.sub(r'expected exactly \w+ exhausted-source candidates', f'expected exactly {exhausted} exhausted-source candidates', text)
        write_text(target, text)

    target = ROOT / "tools/import_sandero_stepway_extreme_source_gap_20260626.py"
    text = target.read_text(encoding="utf-8")
    old = '''    state = json.loads(STATE.read_text(encoding="utf-8"))
    if (
        state["current_package"]["package_id"]
        != "sandero_stepway_extreme_source_gap_003"
    ):
        raise ContractError("project state does not identify the completed package")
'''
    new = '''    state = json.loads(STATE.read_text(encoding="utf-8"))
    if int(state["baseline"]["configuration_values"]) < EXPECTED_VALUE_LAST_ID:
        raise ContractError("project state baseline predates the completed package")
'''
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise AlignmentError("Extreme historical state contract not found")
    write_text(target, text)


def align_range_contracts(range_count: int) -> None:
    for path, patterns in {
        "tests/test_configuration_value_ranges.py": [r'(len\(rows\[1:\]\), )\d+', r'(checked, )\d+', r'(count, )\d+'],
        "tests/test_jogger_payload_performance_ranges.py": [r'(len\(self\.ranges\), )\d+'],
    }.items():
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        for pattern in patterns:
            text = re.sub(pattern, rf'\g<1>{range_count}', text)
        write_text(target, text)


def align_availability_contracts() -> None:
    configurations = {
        "sandero_iii_expression_ecog120_manual", "sandero_iii_journey_ecog120_manual",
        "sandero_stepway_iii_essential_ecog120_manual", "sandero_stepway_iii_expression_ecog120_automatic",
        "sandero_stepway_iii_expression_ecog120_manual", "sandero_stepway_iii_extreme_ecog120_automatic",
        "sandero_stepway_iii_extreme_ecog120_manual",
    }
    rows = [row for row in read_rows(AVAILABILITY) if row["configuration_code"] in configurations and row["observation_date"] == AS_OF]
    total = len(rows)
    previous = total - 1
    status_counts = Counter(row["availability_status"] for row in rows)
    configuration_counts = Counter(row["configuration_code"] for row in rows)
    paths = (
        "tests/test_sandero_50_kmh_noise_level_model.py", "tests/test_sandero_50_kmh_noise_level_values.py",
        "tests/test_sandero_euro_6e_bis_model.py", "tests/test_sandero_euro_6e_bis_values.py",
        "tests/test_sandero_exterior_colour_values.py", "tests/test_sandero_front_wheel_drive_values.py",
        "tests/test_sandero_maximum_payload_model.py", "tests/test_sandero_number_of_doors_values.py",
        "tests/test_sandero_standard_tyre_specification.py", "tests/test_sandero_total_valve_count_model.py",
    )
    for path in paths:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        if str(previous) in text:
            text = text.replace(str(previous), str(total))
        elif str(total) not in text:
            raise AlignmentError(f"availability snapshot not found in {path}")
        write_text(target, text)

    target = ROOT / "tests/test_sandero_passive_safety_availability.py"
    text = target.read_text(encoding="utf-8")
    text = text.replace(f'            ]),\n            {previous},\n        )\n        self.assertEqual(len(self.rows), 119)', f'            ]),\n            {total},\n        )\n        self.assertEqual(len(self.rows), 119)')
    write_text(target, text)

    target = ROOT / "tests/test_sandero_equipment_availability.py"
    text = target.read_text(encoding="utf-8")
    text = re.sub(r'("sandero_stepway_iii_expression_ecog120_automatic":)\s*\d+', rf'\g<1> {configuration_counts["sandero_stepway_iii_expression_ecog120_automatic"]}', text)
    text = re.sub(r'self\.assertEqual\(len\(self\.rows\),\s*\d+\)', f'self.assertEqual(len(self.rows), {total})', text)
    text = re.sub(r'Counter\(\{"standard":\s*\d+,\s*"not_available":\s*\d+\}\)', f'Counter({{"standard": {status_counts["standard"]}, "not_available": {status_counts["not_available"]}}})', text)
    write_text(target, text)


def align_comparison_contracts() -> None:
    report = comparison.collect_report(ROOT, DEFAULT_COMPLETENESS, DEFAULT_EVIDENCE)
    total = len(comparison.difference_csv_rows(report))
    regex_update("tests/test_duster_ecog120_reporting_scope.py", r'(default\["summary"\]\["total_differences"\], )\d+', rf'\g<1>{total}')
    target = ROOT / "tests/configuration_comparison_pair_summary_contract.py"
    text = target.read_text(encoding="utf-8")
    text = re.sub(r'(sum\(int\(row\["total_different"\]\) for row in rows\),\s*)\d+', rf'\g<1>{total}', text)
    write_text(target, text)

    target = ROOT / "tests/configuration_comparison_context_filter_contract.py"
    text = target.read_text(encoding="utf-8")
    text = re.sub(r'self\.assertEqual\(len\(core\.difference_csv_rows\(report\)\),\s*\d+\)', f'self.assertEqual(len(core.difference_csv_rows(report)), {total})', text)
    contexts = context_filter.difference_contexts(report)
    keys = ("", "fuel_type_code=", "fuel_type_code=lpg", "fuel_type_code=petrol", "market=PL;currency_code=PLN")
    expected_counts = {key: len(context_filter.difference_csv_rows(report, difference_context=key, known_contexts=contexts)) for key in keys}
    text, count = re.subn(r'expected_counts = \{.*?\n        \}', "expected_counts = " + python_literal(expected_counts), text, count=1, flags=re.DOTALL)
    if count != 1:
        raise AlignmentError("context-count snapshot block not found")
    write_text(target, text)
    rows = pair_summary.pair_summary_rows(report)
    if sum(int(row["total_different"]) for row in rows) != total:
        raise AlignmentError("pair-summary total differs from comparison total")


def align_dimension_contracts() -> None:
    versions = {row["code"]: row for row in read_rows(ROOT / "data/master/versions.csv")}
    models = {row["code"]: versions.get(row.get("version_code", ""), {}).get("model_code", "") for row in read_rows(ROOT / "data/master/configurations.csv") if row.get("status") == "active"}
    dimensions = {"overall_length", "overall_width", "overall_width_with_mirrors", "overall_height", "roof_height_with_rails", "wheelbase", "ground_clearance", "front_track", "rear_track", "front_overhang", "rear_overhang", "approach_angle", "departure_angle"}
    count = len([row for row in read_rows(VALUES) if models.get(row["configuration_code"]) == "sandero_stepway_iii" and row["attribute_code"] in dimensions])
    regex_update("tools/review_official_brochure_residual_evidence_20260726.py", r'(len\(selected\["sandero_stepway_iii"\]\) == )\d+', rf'\g<1>{count}')
    regex_update("tests/test_official_brochure_residual_evidence_review.py", r'(len\(selected\["sandero_stepway_iii"\]\), )\d+', rf'\g<1>{count}')


def align_spring_contracts(state: dict[str, object], range_count: int) -> None:
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    counts = reconciliation["summary"]["active_evidence_record_counts"]
    target = ROOT / "tests/test_spring_technical_20260219.py"
    text = target.read_text(encoding="utf-8")
    text = re.sub(r'(state\["baseline"\]\["configuration_values"\], )\d+', rf'\g<1>{state["baseline"]["configuration_values"]}', text)
    text = re.sub(r'(state\["baseline"\]\["configuration_value_ranges"\], )\d+', rf'\g<1>{range_count}', text)
    text = re.sub(r'(counts\["configuration_attribute_values"\], )\d+', rf'\g<1>{counts["configuration_attribute_values"]}', text)
    text = re.sub(r'(counts\["configuration_attribute_value_ranges"\], )\d+', rf'\g<1>{counts["configuration_attribute_value_ranges"]}', text)
    write_text(target, text)


def update_manifest() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    manifest = set(state["current_package"].get("manifest_paths", []))
    manifest.update(CHANGED_PATHS)
    state["current_package"]["manifest_paths"] = sorted(manifest)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply() -> None:
    complete, coverage, compared = automatic_reports()
    write_text(ROOT / "tests/test_sandero_stepway_ecog120_automatic_reporting_scope.py", render_automatic_test(complete, coverage, compared))
    align_previous_contracts()
    range_count = len(read_rows(RANGES))
    align_range_contracts(range_count)
    align_availability_contracts()
    align_comparison_contracts()
    align_dimension_contracts()
    state = json.loads(STATE.read_text(encoding="utf-8"))
    align_spring_contracts(state, range_count)
    update_manifest()
    report = comparison.collect_report(ROOT, DEFAULT_COMPLETENESS, DEFAULT_EVIDENCE)
    print(f"Sandero Stepway Expression automatic snapshot contracts aligned: ranges={range_count}, differences={len(comparison.difference_csv_rows(report))}")


if __name__ == "__main__":
    apply()
'''


def main() -> None:
    write(OUT_IMPORTER, importer_text())
    write(OUT_TEST, test_text())
    write(OUT_CLOSE, close_text())
    write(OUT_ALIGN, align_text())
    print("Generated Stepway Expression automatic source-gap package contracts.")


if __name__ == "__main__":
    main()
