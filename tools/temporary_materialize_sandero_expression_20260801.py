#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_replace(text: str, old: str, new: str) -> str:
    found = text.count(old)
    if found == 0:
        raise SystemExit(f"missing replacement contract: {old!r}")
    return text.replace(old, new)


def build_importer() -> None:
    source = ROOT / "tools/import_sandero_stepway_essential_source_gap_20260626.py"
    target = ROOT / "tools/import_sandero_stepway_expression_source_gap_20260626.py"
    text = source.read_text(encoding="utf-8")
    text = text.replace("Essential", "Expression").replace("essential", "expression")
    replacements = {
        'SOURCE_SHA256 = "14dbd68fc58d63bc81595f64784e37089ef25ed0103e2a74768477e602b29ea1"': 'SOURCE_SHA256 = "7cbca5f16e74c5bce10cdf1d099573b6ace40e905d79325676fdd5753d14f130"',
        "EXPECTED_VALUE_FIRST_ID = 3553": "EXPECTED_VALUE_FIRST_ID = 3556",
        "EXPECTED_VALUE_LAST_ID = 3555": "EXPECTED_VALUE_LAST_ID = 3558",
        "EXPECTED_RANGE_FIRST_ID = 302": "EXPECTED_RANGE_FIRST_ID = 305",
        "EXPECTED_RANGE_LAST_ID = 304": "EXPECTED_RANGE_LAST_ID = 307",
        '"reported_records": 24': '"reported_records": 20',
        '"unique_slots": 12': '"unique_slots": 10',
        '"resolved_unique_slots": 8': '"resolved_unique_slots": 6',
        '"maximum_value": "3750", "source_page": 5': '"maximum_value": "3750", "source_page": 6',
        '"maximum_value": "4000", "source_page": 5': '"maximum_value": "4000", "source_page": 6',
        '"package_id": "sandero_stepway_expression_source_gap_001"': '"package_id": "sandero_stepway_expression_source_gap_002"',
        'f"{analysis.slug(model)}_highest_impact_eligible_gap_002"': 'f"{analysis.slug(model)}_highest_impact_eligible_gap_003"',
        'summary["missing_technical_count"] != 137': 'summary["missing_technical_count"] != 125',
        "expected 137 remaining technical records": "expected 125 remaining technical records",
        'summary["exhausted_source_candidate_count"] != 2': 'summary["exhausted_source_candidate_count"] != 3',
        "expected exactly two exhausted-source candidates": "expected exactly three exhausted-source candidates",
        "scalar IDs are not the exact contiguous suffix 3553-3555": "scalar IDs are not the exact contiguous suffix 3556-3558",
        "range IDs are not the exact contiguous suffix 302-304": "range IDs are not the exact contiguous suffix 305-307",
        "Stepway Expression source-gap observations: PASS (3 values + 3 ranges + 2 scope corrections)": "Stepway Expression source-gap observations: PASS (3 values + 3 ranges)",
    }
    for old, new in replacements.items():
        text = require_replace(text, old, new)

    pattern = re.compile(
        r'            "reporting_context_corrections": \[.*?            \],\n        },\n        "excluded_alternatives"',
        re.S,
    )
    text, count = pattern.subn(
        '            "reporting_context_corrections": [],\n        },\n        "excluded_alternatives"',
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("could not replace reporting-context correction block")

    review_function = '''def render_review_markdown(payload: dict[str, object]) -> str:
    return (
        "# Sandero Stepway Expression Source-Gap Review\\n\\n"
        "Status: complete\\n\\n"
        f"Source `{SOURCE_CODE}` was inspected page by page against the 20 reported "
        "scope records for `sandero_stepway_iii_expression_ecog120_manual`. The two "
        "scope records describe 10 unique technical slots.\\n\\n"
        "## Imported observations\\n\\n"
        "- `overall_height = 1586 mm` for the exact standard configuration with roof rails.\\n"
        "- `overall_width_with_mirrors = 2012 mm` with mirrors unfolded, matching the repository convention.\\n"
        "- `wheel_finish = stalowe`; ATARA remains the separate existing wheel-design observation.\\n"
        "- `ground_clearance = 170-200 mm`.\\n"
        "- `max_torque_rpm = 1750-3750` for LPG and `2000-4000` for petrol.\\n\\n"
        "## Remaining boundary\\n\\n"
        "`front_track`, `rear_track`, and `max_power_rpm` for LPG and petrol are not "
        "stated in this PDF. The source is therefore classified "
        "`source_exhausted_not_stated` after the six exact imports. Equipment decisions "
        "remain governed by their existing direct-evidence or explicit-alternative reviews.\\n"
    )
'''
    start = text.index("def render_review_markdown(")
    end = text.index("\ndef package_text()", start)
    text = text[:start] + review_function + text[end + 1 :]

    package_function = '''def package_text() -> str:
    return (
        "# Sandero Stepway Expression Source Gap\\n\\n"
        "Status: complete\\n\\n"
        "Imported three exact scalar observations and three inclusive ranges from "
        "the configuration-specific Polish PDF dated 2026-06-26, regenerated the "
        "missing-data analysis and formally exhausted the source for the four technical "
        "slots it does not state.\\n\\n"
        "No value was projected from another trim, fuel, diagram or document. Alternative "
        "no-rails and folded-mirror dimensions remain excluded, and existing ATARA "
        "wheel-design evidence is not duplicated. Equipment evidence boundaries remain unchanged.\\n"
    )
'''
    start = text.index("def package_text()")
    end = text.index("\ndef update_analysis_outputs()", start)
    text = text[:start] + package_function + text[end + 1 :]
    target.write_text(text, encoding="utf-8")


def build_test() -> None:
    source = ROOT / "tests/test_sandero_stepway_essential_source_gap_20260626.py"
    target = ROOT / "tests/test_sandero_stepway_expression_source_gap_20260626.py"
    text = source.read_text(encoding="utf-8")
    text = text.replace("Essential", "Expression").replace("essential", "expression")
    replacements = {
        "[3553, 3554, 3555]": "[3556, 3557, 3558]",
        "[302, 303, 304]": "[305, 306, 307]",
        'review["reconciliation"]["resolved_unique_slots"], 8': 'review["reconciliation"]["resolved_unique_slots"], 6',
        'payload["summary"]["missing_technical_count"], 137': 'payload["summary"]["missing_technical_count"], 125',
        'payload["summary"]["exhausted_source_candidate_count"], 2': 'payload["summary"]["exhausted_source_candidate_count"], 3',
    }
    for old, new in replacements.items():
        text = require_replace(text, old, new)
    target.write_text(text, encoding="utf-8")


def build_closer() -> None:
    source = ROOT / "tools/close_stepway_essential_reporting_dependencies_20260801.py"
    target = ROOT / "tools/close_stepway_expression_reporting_dependencies_20260801.py"
    text = source.read_text(encoding="utf-8")
    text = text.replace("Essential", "Expression").replace("essential", "expression")
    target.write_text(text, encoding="utf-8")


def build_spec() -> None:
    target = ROOT / "data/imports/sandero_stepway_expression_source_gap_20260626.csv"
    fields = (
        "record_type",
        "configuration_code",
        "attribute_code",
        "fuel_type_code",
        "value",
        "minimum_value",
        "maximum_value",
        "source_page",
        "source_label",
        "normalization_notes",
    )
    configuration = "sandero_stepway_iii_expression_ecog120_manual"
    rows = [
        {
            "record_type": "value",
            "configuration_code": configuration,
            "attribute_code": "overall_height",
            "fuel_type_code": "",
            "value": "1586",
            "minimum_value": "",
            "maximum_value": "",
            "source_page": "6",
            "source_label": "Wysokość Pojazdu Nieobciążonego Z Relingami (Mm): 1586 (Stepway)",
            "normalization_notes": "Exact Expression Stepway configuration has roof rails as standard; the alternative 1535 mm height without roof rails is excluded.",
        },
        {
            "record_type": "value",
            "configuration_code": configuration,
            "attribute_code": "overall_width_with_mirrors",
            "fuel_type_code": "",
            "value": "2012",
            "minimum_value": "",
            "maximum_value": "",
            "source_page": "6",
            "source_label": "Szerokość Całkowita Z Lusterkami Zewnętrznymi: 1853/2012 (złożone/rozłożone)",
            "normalization_notes": "Store the unfolded-mirror width used by the repository comparison convention; the folded-mirror width 1853 mm is excluded.",
        },
        {
            "record_type": "value",
            "configuration_code": configuration,
            "attribute_code": "wheel_finish",
            "fuel_type_code": "",
            "value": "stalowe",
            "minimum_value": "",
            "maximum_value": "",
            "source_page": "2",
            "source_label": "16\" felgi stalowe ATARA",
            "normalization_notes": "Normalize only the wheel finish; the ATARA design is already represented by the separate wheel_design observation.",
        },
        {
            "record_type": "range",
            "configuration_code": configuration,
            "attribute_code": "ground_clearance",
            "fuel_type_code": "",
            "value": "",
            "minimum_value": "170",
            "maximum_value": "200",
            "source_page": "6",
            "source_label": "Prześwit Pojazdu: 130-160 (Sandero) / 170-200 (Stepway)",
            "normalization_notes": "Preserve the printed Stepway interval without selecting either endpoint as a scalar value.",
        },
        {
            "record_type": "range",
            "configuration_code": configuration,
            "attribute_code": "max_torque_rpm",
            "fuel_type_code": "lpg",
            "value": "",
            "minimum_value": "1750",
            "maximum_value": "3750",
            "source_page": "6",
            "source_label": "Maksymalny Moment Obrotowy W Nm: 197 przy 1750-3750 (LPG)",
            "normalization_notes": "Preserve the exact LPG engine-speed interval.",
        },
        {
            "record_type": "range",
            "configuration_code": configuration,
            "attribute_code": "max_torque_rpm",
            "fuel_type_code": "petrol",
            "value": "",
            "minimum_value": "2000",
            "maximum_value": "4000",
            "source_page": "6",
            "source_label": "Maksymalny Moment Obrotowy W Nm: 190 przy 2000-4000",
            "normalization_notes": "Preserve the exact petrol engine-speed interval.",
        },
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    build_importer()
    build_test()
    build_closer()
    build_spec()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
