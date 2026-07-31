#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANUAL_STEPWAY = [
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_manual",
]
AUTO_STEPWAY = [
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
]
MANUAL_SLOTS = [
    ("max_power_rpm", "lpg"),
    ("max_power_rpm", "petrol"),
    ("max_torque_rpm", "lpg"),
    ("max_torque_rpm", "petrol"),
]
AUTO_SLOTS = [
    ("max_power_rpm", "lpg"),
    ("max_power_rpm", "petrol"),
    ("max_torque_rpm", "lpg"),
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_slots(path_name: str, slots: list[tuple[str, str]]) -> None:
    path = ROOT / path_name
    payload = read_json(path)
    existing = {
        (item["attribute_code"], item.get("fuel_type_code", ""))
        for item in payload["technical_slots"]
    }
    for attribute, fuel in slots:
        if (attribute, fuel) not in existing:
            payload["technical_slots"].append(
                {"attribute_code": attribute, "fuel_type_code": fuel}
            )
    payload["technical_slots"].sort(
        key=lambda item: (item["attribute_code"], item.get("fuel_type_code", ""))
    )
    write_json(path, payload)


def template_for(
    decisions: list[dict], configuration: str, attribute: str, fuel: str
) -> dict:
    preferred_attribute = "engine_power" if attribute == "max_power_rpm" else "engine_torque"
    metadata = [
        item for item in decisions if item.get("configuration_code") == configuration
    ]
    if not metadata:
        raise RuntimeError(f"no evidence metadata for {configuration}")
    base = copy.deepcopy(sorted(metadata, key=lambda item: item.get("triage_key", ""))[0])
    source_code = base.get("source_code", "")
    technical = [
        item
        for item in decisions
        if item.get("domain") == "technical"
        and item.get("source_code", "") == source_code
    ]
    if not technical:
        technical = [item for item in decisions if item.get("domain") == "technical"]
    ordered = sorted(
        technical,
        key=lambda item: (
            item.get("attribute_code") != preferred_attribute,
            item.get("fuel_type_code", "") != fuel,
            item.get("fuel_type_code", "") not in {fuel, ""},
            item.get("triage_key", ""),
        ),
    )
    if not ordered:
        raise RuntimeError(f"no technical category template in evidence file for {configuration}")
    technical_template = ordered[0]
    base["category"] = technical_template.get("category", base.get("category", "Engine"))
    base["reviewed_pages"] = technical_template.get("reviewed_pages", base.get("reviewed_pages", []))
    return base


def add_not_stated_decisions(
    path_name: str,
    configurations: list[str],
    slots: list[tuple[str, str]],
) -> None:
    path = ROOT / path_name
    payload = read_json(path)
    decisions = payload["decisions"]
    existing = {
        (
            item.get("domain", ""),
            item.get("configuration_code", ""),
            item.get("attribute_code", ""),
            item.get("fuel_type_code", ""),
        )
        for item in decisions
    }
    for configuration in configurations:
        for attribute, fuel in slots:
            signature = ("technical", configuration, attribute, fuel)
            if signature in existing:
                continue
            item = template_for(decisions, configuration, attribute, fuel)
            item.update(
                {
                    "attribute_code": attribute,
                    "auto_import": False,
                    "basis": None,
                    "candidate_value": "",
                    "classification": "not_stated",
                    "configuration_code": configuration,
                    "domain": "technical",
                    "fuel_type_code": fuel,
                    "manual_source_review_required": False,
                    "reason_code": "not_stated_on_relevant_pages",
                    "review_note": "No direct configured source statement was found for this engine-speed range in the registered configuration source.",
                    "source_page": None,
                    "source_section": "",
                    "source_text": "",
                }
            )
            fuel_key = fuel or "none"
            item["triage_key"] = "|".join(
                [
                    "technical",
                    str(item.get("source_code", "")),
                    configuration,
                    str(item.get("category", "")),
                    attribute,
                    fuel_key,
                ]
            )
            decisions.append(item)
            existing.add(signature)
    decisions.sort(key=lambda item: item.get("triage_key", ""))
    write_json(path, payload)


def replace(path_name: str, old: str, new: str) -> None:
    path = ROOT / path_name
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected contract not found in {path_name}: {old}")
    path.write_text(text.replace(old, new), encoding="utf-8")


# Direct Sandero Eco-G 120 automatic observations need a reporting denominator.
add_slots(
    "data/reporting/sandero_ecog120_automatic_completeness.json",
    AUTO_SLOTS,
)

# Stepway configurations remain explicit gaps in scopes that now expose the RPM slots.
add_not_stated_decisions(
    "data/reporting/configuration_gap_evidence.json",
    MANUAL_STEPWAY,
    MANUAL_SLOTS,
)
add_not_stated_decisions(
    "data/reporting/configuration_gap_evidence.json",
    AUTO_STEPWAY,
    MANUAL_SLOTS,
)
add_not_stated_decisions(
    "data/reporting/sandero_ecog120_manual_gap_evidence.json",
    MANUAL_STEPWAY,
    MANUAL_SLOTS,
)
add_not_stated_decisions(
    "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json",
    AUTO_STEPWAY,
    AUTO_SLOTS,
)

# Rebuild the versioned resolution plan after evidence expansion.
subprocess.run(
    [
        "python",
        "tools/configuration_gap_resolution_plan.py",
        "--write-plan-spec",
        "data/reporting/configuration_gap_resolution_plan.json",
    ],
    cwd=ROOT,
    check=True,
)

# Current official-brochure receipts include the 20 Sandero RPM ranges.
replace(
    "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
    "expected_range_total = 98",
    "expected_range_total = 118",
)
replace(
    "tests/test_official_brochure_technical_gap_resolution_closure.py",
    '    {"src_pl_bigster_brochure_20251210": 34}\n',
    '    {"src_pl_bigster_brochure_20251210": 34, "src_pl_sandero_brochure_20260202": 20}\n',
)
replace(
    "tests/test_cross_model_comparison_view.py",
    'self.assertEqual(scope["technical_slot_count"], 56)',
    'self.assertEqual(scope["technical_slot_count"], 60)',
)
replace(
    "tests/test_configuration_comparison_workbook.py",
    '            "A1:AS236",',
    '            "A1:AS239",',
)

# Manual Sandero/Stepway Eco-G 120 reporting expectations.
manual_test = "tests/test_sandero_ecog120_manual_reporting_scope.py"
replace(manual_test, 'self.assertEqual(scope["technical_slots"], 56)', 'self.assertEqual(scope["technical_slots"], 60)')
replace(
    manual_test,
    '''                "applicable": 280,\n                "coverage_percent": "93.21",\n                "denominator": 280,\n                "missing": 19,\n                "not_applicable": 0,\n                "present": 261,''',
    '''                "applicable": 300,\n                "coverage_percent": "89.67",\n                "denominator": 300,\n                "missing": 31,\n                "not_applicable": 0,\n                "present": 269,''',
)
replace(manual_test, 'len(self.completeness["gaps"]["technical"]), 19', 'len(self.completeness["gaps"]["technical"]), 31')
replace(
    manual_test,
    '''                "covered": 136,\n                "denominator": 175,\n                "missing": 7,\n                "not_applicable": 0,\n                "partial": 32,\n                "source_missing": 0,''',
    '''                "covered": 133,\n                "denominator": 175,\n                "missing": 7,\n                "not_applicable": 0,\n                "partial": 35,\n                "source_missing": 0,''',
)
replace(manual_test, 'self.coverage["records"]["technical"]["present"], 261', 'self.coverage["records"]["technical"]["present"], 269')
replace(manual_test, 'len(self.coverage["gaps"]), 66', 'len(self.coverage["gaps"]), 78')
replace(manual_test, 'sum(pair["summary"]["technical"]["not_comparable"] for pair in pairs), 67', 'sum(pair["summary"]["technical"]["not_comparable"] for pair in pairs), 103')
replace(
    manual_test,
    '"technical": {"comparisons": 648, "different": 152, "equal": 429, "not_comparable": 67}',
    '"technical": {"comparisons": 688, "different": 152, "equal": 433, "not_comparable": 103}',
)
replace(
    manual_test,
    '{"ambiguous": 0, "found": 0, "not_stated": 49, "out_of_scope": 17, "total": 66}',
    '{"ambiguous": 0, "found": 0, "not_stated": 61, "out_of_scope": 17, "total": 78}',
)
replace(manual_test, 'self.assertEqual(ranged, [])', 'self.assertEqual(len(ranged), 40)')

# Stepway Eco-G 120 automatic reporting expectations.
auto_test = "tests/test_sandero_stepway_ecog120_automatic_reporting_scope.py"
replace(auto_test, 'self.assertEqual(scope["technical_slots"], 51)', 'self.assertEqual(scope["technical_slots"], 54)')
replace(
    auto_test,
    '''                "applicable": 102,\n                "coverage_percent": "99.02",\n                "denominator": 102,\n                "missing": 1,\n                "not_applicable": 0,\n                "present": 101,''',
    '''                "applicable": 108,\n                "coverage_percent": "93.52",\n                "denominator": 108,\n                "missing": 7,\n                "not_applicable": 0,\n                "present": 101,''',
)
replace(auto_test, 'len(self.completeness["gaps"]["technical"]), 1', 'len(self.completeness["gaps"]["technical"]), 7')
replace(
    auto_test,
    '{"covered": 5, "denominator": 8, "missing": 0, "partial": 3, "source_missing": 0}',
    '{"covered": 4, "denominator": 8, "missing": 0, "partial": 4, "source_missing": 0}',
)
replace(auto_test, 'len(self.coverage["gaps"]), 18', 'len(self.coverage["gaps"]), 24')
replace(auto_test, 'pair["summary"]["technical"]["not_comparable"], 1', 'pair["summary"]["technical"]["not_comparable"], 4')
replace(
    auto_test,
    '"technical": {"comparisons": 56, "different": 7, "equal": 48, "not_comparable": 1}',
    '"technical": {"comparisons": 59, "different": 7, "equal": 48, "not_comparable": 4}',
)
replace(
    auto_test,
    '{"ambiguous": 0, "found": 0, "not_stated": 10, "out_of_scope": 8, "total": 18}',
    '{"ambiguous": 0, "found": 0, "not_stated": 16, "out_of_scope": 8, "total": 24}',
)

print("PASS: completed Sandero RPM range dependent contracts")
