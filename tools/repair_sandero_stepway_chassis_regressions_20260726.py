#!/usr/bin/env python3
"""Update historical contracts after Sandero/Stepway chassis observations."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected text not found: {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def prune_resolved_evidence() -> None:
    path = ROOT / "data" / "reporting" / "sandero_ecog120_automatic_gap_evidence.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise RuntimeError("Sandero automatic evidence decisions are missing")
    targets = {
        "sandero_iii_expression_ecog120_automatic",
        "sandero_iii_journey_ecog120_automatic",
    }
    retained = [
        item for item in decisions
        if not (
            item.get("domain") == "technical"
            and item.get("configuration_code") in targets
            and item.get("attribute_code") == "standard_tyre_specification"
            and item.get("fuel_type_code", "") == ""
        )
    ]
    removed = len(decisions) - len(retained)
    if removed not in {0, 2}:
        raise RuntimeError(f"unexpected resolved evidence count: {removed}")
    payload["decisions"] = retained
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_historical_import_boundary() -> None:
    importer = ROOT / "tools" / "import_sandero_ecog120_automatic_brochure_technical_20260726.py"
    test = ROOT / "tests" / "test_sandero_ecog120_automatic_brochure_technical_20260726.py"
    for path in (importer, test):
        text = path.read_text(encoding="utf-8")
        text = text.replace('    "standard_tyre_specification",\n', "")
        text = text.replace('    "maximum_kerb_weight",\n', "")
        path.write_text(text, encoding="utf-8")


def update_reporting_expectations() -> None:
    workbook = ROOT / "tests" / "test_configuration_comparison_workbook.py"
    replace_once(workbook, '            "A1:AS217",\n', '            "A1:AS221",\n')

    duster = ROOT / "tests" / "test_duster_ecog120_reporting_scope.py"
    replace_once(
        duster,
        '        self.assertEqual(default["summary"]["total_differences"], 349)\n',
        '        self.assertEqual(default["summary"]["total_differences"], 365)\n',
    )

    manual = ROOT / "tests" / "test_sandero_ecog120_manual_reporting_scope.py"
    replacements = {
        '        self.assertEqual(scope["technical_slots"], 47)\n': '        self.assertEqual(scope["technical_slots"], 51)\n',
        '                "applicable": 235,\n': '                "applicable": 255,\n',
        '                "coverage_percent": "98.30",\n': '                "coverage_percent": "98.43",\n',
        '                "denominator": 235,\n': '                "denominator": 255,\n',
        '                "present": 231,\n': '                "present": 251,\n',
        '                "covered": 134,\n': '                "covered": 139,\n',
        '                "denominator": 170,\n': '                "denominator": 175,\n',
        '        self.assertEqual(self.coverage["records"]["technical"]["present"], 231)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 251)\n',
        '                "technical": {"comparisons": 558, "different": 146, "equal": 390, "not_comparable": 22},\n': '                "technical": {"comparisons": 598, "different": 152, "equal": 424, "not_comparable": 22},\n',
        '                "total_differences": 170,\n': '                "total_differences": 176,\n',
    }
    for old, new in replacements.items():
        replace_once(manual, old, new)

    automatic = ROOT / "tests" / "test_sandero_stepway_ecog120_automatic_reporting_scope.py"
    replacements = {
        '        self.assertEqual(scope["technical_slots"], 47)\n': '        self.assertEqual(scope["technical_slots"], 51)\n',
        '                "applicable": 94,\n': '                "applicable": 102,\n',
        '                "coverage_percent": "98.94",\n': '                "coverage_percent": "99.02",\n',
        '                "denominator": 94,\n': '                "denominator": 102,\n',
        '                "present": 93,\n': '                "present": 101,\n',
        '                "covered": 58,\n': '                "covered": 60,\n',
        '                "denominator": 68,\n': '                "denominator": 70,\n',
        '        self.assertEqual(self.coverage["records"]["technical"]["present"], 93)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 101)\n',
        '                "technical": {"comparisons": 52, "different": 7, "equal": 44, "not_comparable": 1},\n': '                "technical": {"comparisons": 56, "different": 7, "equal": 48, "not_comparable": 1},\n',
    }
    for old, new in replacements.items():
        replace_once(automatic, old, new)


def main() -> int:
    prune_resolved_evidence()
    update_historical_import_boundary()
    update_reporting_expectations()
    print("PASS: Sandero and Stepway chassis regression contracts updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
