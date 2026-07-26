#!/usr/bin/env python3
"""Update exact post-import snapshot contracts for generic brochure dimensions."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepairError(RuntimeError):
    """Raised when an expected historical snapshot cannot be normalized."""


def replace_once_or_done(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return True
    if old_count == 0 and new_count == 1:
        return False
    raise RepairError(
        f"unexpected replacement state for {path}: old={old_count}, new={new_count}"
    )


def repair_semantic_mapping_review() -> None:
    path = ROOT / "tests/test_brochure_generic_dimensions_semantic_mapping_review.py"
    replace_once_or_done(
        path,
        '''        self.assertEqual(max(int(row["id"]) for row in self.values), 2567)\n        brochure_sources = set(self.sources)\n        self.assertFalse(any(\n            row["source_code"] in brochure_sources and row["attribute_code"] in ATTRIBUTE_CODES\n            for row in self.values\n        ))''',
        '''        self.assertEqual(max(int(row["id"]) for row in self.values), 2949)\n        brochure_sources = set(self.sources)\n        approved = [\n            row\n            for row in self.values\n            if row["source_code"] in brochure_sources\n            and row["attribute_code"] in ATTRIBUTE_CODES\n            and 2568 <= int(row["id"]) <= 2949\n        ]\n        self.assertEqual(len(approved), 382)\n        self.assertEqual(\n            [int(row["id"]) for row in approved],\n            list(range(2568, 2950)),\n        )\n        self.assertEqual(\n            Counter(row["source_code"] for row in approved),\n            Counter({\n                "src_pl_sandero_brochure_20260202": 40,\n                "src_pl_jogger_brochure_20251217": 242,\n                "src_pl_duster_mini_brochure_20251020": 100,\n            }),\n        )''',
    )
    replace_once_or_done(
        path,
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Semantic Mapping Review")\n        self.assertEqual(state["current_package"]["status"], "complete")\n        self.assertEqual(state["next_package"]["name"], "Brochure Generic Dimensions Observation Import")\n        self.assertEqual(state["baseline"]["tests"], 939)\n        self.assertEqual(state["baseline"]["rows"], 9306)\n        self.assertEqual(state["baseline"]["configuration_values"], 2567)\n        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)\n        self.assertEqual(state["baseline"]["attributes"], 385)''',
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Observation Import")\n        self.assertEqual(state["current_package"]["status"], "complete")\n        self.assertEqual(state["next_package"]["name"], "Brochure Generic Dimensions Import Closure Review")\n        self.assertEqual(state["baseline"]["tests"], 947)\n        self.assertEqual(state["baseline"]["rows"], 9688)\n        self.assertEqual(state["baseline"]["configuration_values"], 2949)\n        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)\n        self.assertEqual(state["baseline"]["attributes"], 385)''',
    )


def repair_workbook() -> None:
    path = ROOT / "tests/test_configuration_comparison_workbook.py"
    replace_once_or_done(path, '            "A1:AS225",', '            "A1:AS236",')


def repair_duster_reporting() -> None:
    path = ROOT / "tests/test_duster_ecog120_reporting_scope.py"
    for old, new in (
        (
            '''        "technical_slots": 27,\n        "technical_records": 108,\n        "technical_comparisons": 180,''',
            '''        "technical_slots": 37,\n        "technical_records": 148,\n        "technical_comparisons": 240,''',
        ),
        (
            '''        "technical_slots": 26,\n        "technical_records": 78,\n        "technical_comparisons": 99,''',
            '''        "technical_slots": 36,\n        "technical_records": 108,\n        "technical_comparisons": 129,''',
        ),
        (
            '''        "technical_slots": 24,\n        "technical_records": 72,\n        "technical_comparisons": 93,''',
            '''        "technical_slots": 34,\n        "technical_records": 102,\n        "technical_comparisons": 123,''',
        ),
    ):
        replace_once_or_done(path, old, new)


def repair_jogger_reporting() -> None:
    cases = (
        (
            "tests/test_jogger_ecog120_automatic_reporting_scope.py",
            (
                ('        self.assertEqual(scope["technical_slots"], 41)', '        self.assertEqual(scope["technical_slots"], 52)'),
                ('                "applicable": 164,\n                "coverage_percent": "100.00",\n                "denominator": 164,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 164,', '                "applicable": 208,\n                "coverage_percent": "100.00",\n                "denominator": 208,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 208,'),
                ('{"covered": 116, "denominator": 116, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}', '{"covered": 120, "denominator": 120, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}'),
                ('self.assertEqual(self.coverage["records"]["technical"]["present"], 164)', 'self.assertEqual(self.coverage["records"]["technical"]["present"], 208)'),
                ('"technical": {"comparisons": 290, "equal": 210, "different": 40, "not_comparable": 40}', '"technical": {"comparisons": 356, "equal": 276, "different": 40, "not_comparable": 40}'),
            ),
        ),
        (
            "tests/test_jogger_ecog120_manual_reporting_scope.py",
            (
                ('        self.assertEqual(scope["technical_slots"], 41)', '        self.assertEqual(scope["technical_slots"], 52)'),
                ('                "applicable": 246,\n                "coverage_percent": "100.00",\n                "denominator": 246,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 246,', '                "applicable": 312,\n                "coverage_percent": "100.00",\n                "denominator": 312,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 312,'),
                ('{"covered": 174, "denominator": 174, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}', '{"covered": 180, "denominator": 180, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}'),
                ('self.assertEqual(self.coverage["records"]["technical"]["present"], 246)', 'self.assertEqual(self.coverage["records"]["technical"]["present"], 312)'),
                ('"technical": {"comparisons": 720, "equal": 540, "different": 90, "not_comparable": 90}', '"technical": {"comparisons": 885, "equal": 705, "different": 90, "not_comparable": 90}'),
            ),
        ),
        (
            "tests/test_jogger_hybrid155_automatic_reporting_scope.py",
            (
                ('        self.assertEqual(scope["technical_slots"], 35)', '        self.assertEqual(scope["technical_slots"], 46)'),
                ('                "applicable": 210,\n                "coverage_percent": "100.00",\n                "denominator": 210,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 210,', '                "applicable": 276,\n                "coverage_percent": "100.00",\n                "denominator": 276,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 276,'),
                ('{"covered": 180, "denominator": 180, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}', '{"covered": 186, "denominator": 186, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}'),
                ('self.assertEqual(self.coverage["records"]["technical"]["present"], 210)', 'self.assertEqual(self.coverage["records"]["technical"]["present"], 276)'),
                ('"technical": {"comparisons": 630, "equal": 477, "different": 63, "not_comparable": 90}', '"technical": {"comparisons": 795, "equal": 642, "different": 63, "not_comparable": 90}'),
            ),
        ),
        (
            "tests/test_jogger_tce110_manual_reporting_scope.py",
            (
                ('        self.assertEqual(scope["technical_slots"], 30)', '        self.assertEqual(scope["technical_slots"], 41)'),
                ('                "applicable": 180,\n                "coverage_percent": "100.00",\n                "denominator": 180,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 180,', '                "applicable": 246,\n                "coverage_percent": "100.00",\n                "denominator": 246,\n                "missing": 0,\n                "not_applicable": 0,\n                "present": 246,'),
                ('{"covered": 174, "denominator": 174, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}', '{"covered": 180, "denominator": 180, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0}'),
                ('self.assertEqual(self.coverage["records"]["technical"]["present"], 180)', 'self.assertEqual(self.coverage["records"]["technical"]["present"], 246)'),
                ('"technical": {"comparisons": 555, "equal": 393, "different": 72, "not_comparable": 90}', '"technical": {"comparisons": 720, "equal": 558, "different": 72, "not_comparable": 90}'),
            ),
        ),
    )
    for relative, replacements in cases:
        path = ROOT / relative
        for old, new in replacements:
            replace_once_or_done(path, old, new)


def repair_sandero_manual_reporting() -> None:
    path = ROOT / "tests/test_sandero_ecog120_manual_reporting_scope.py"
    replacements = (
        ('        self.assertEqual(scope["technical_slots"], 51)', '        self.assertEqual(scope["technical_slots"], 56)'),
        ('''                "applicable": 255,\n                "coverage_percent": "98.43",\n                "denominator": 255,\n                "missing": 4,\n                "not_applicable": 0,\n                "present": 251,''', '''                "applicable": 280,\n                "coverage_percent": "93.21",\n                "denominator": 280,\n                "missing": 19,\n                "not_applicable": 0,\n                "present": 261,'''),
        ('        self.assertEqual(len(self.completeness["gaps"]["technical"]), 4)', '        self.assertEqual(len(self.completeness["gaps"]["technical"]), 19)'),
        ('{"covered": 11, "denominator": 20, "missing": 0, "partial": 9, "source_missing": 0}', '{"covered": 10, "denominator": 20, "missing": 0, "partial": 10, "source_missing": 0}'),
        ('''                "covered": 139,\n                "denominator": 175,\n                "missing": 7,\n                "not_applicable": 0,\n                "partial": 29,''', '''                "covered": 136,\n                "denominator": 175,\n                "missing": 7,\n                "not_applicable": 0,\n                "partial": 32,'''),
        ('self.assertEqual(self.coverage["records"]["technical"]["present"], 251)', 'self.assertEqual(self.coverage["records"]["technical"]["present"], 261)'),
        ('self.assertEqual(len(self.coverage["gaps"]), 51)', 'self.assertEqual(len(self.coverage["gaps"]), 66)'),
        ('sum(pair["summary"]["technical"]["not_comparable"] for pair in pairs), 22', 'sum(pair["summary"]["technical"]["not_comparable"] for pair in pairs), 67'),
        ('"technical": {"comparisons": 598, "different": 152, "equal": 424, "not_comparable": 22}', '"technical": {"comparisons": 648, "different": 152, "equal": 429, "not_comparable": 67}'),
        ('{"ambiguous": 0, "found": 0, "not_stated": 34, "out_of_scope": 17, "total": 51}', '{"ambiguous": 0, "found": 0, "not_stated": 49, "out_of_scope": 17, "total": 66}'),
    )
    for old, new in replacements:
        replace_once_or_done(path, old, new)


def repair_residual_review() -> None:
    path = ROOT / "tests/test_official_brochure_residual_evidence_review.py"
    replace_once_or_done(
        path,
        '''        self.assertEqual(len(selected["sandero_iii"]), 10)\n        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_iii"]}), 2)\n        self.assertEqual(len(selected["sandero_stepway_iii"]), 25)\n        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}), 5)\n        self.assertEqual(selected["jogger"], [])\n        self.assertEqual(len(selected["bigster"]), 140)\n        self.assertEqual(len({row["configuration_code"] for row in selected["bigster"]}), 14)\n        self.assertEqual(selected["duster_iii"], [])''',
        '''        self.assertEqual(len(selected["sandero_iii"]), 50)\n        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_iii"]}), 4)\n        self.assertEqual(len(selected["sandero_stepway_iii"]), 25)\n        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}), 5)\n        self.assertEqual(len(selected["jogger"]), 242)\n        self.assertEqual(len({row["configuration_code"] for row in selected["jogger"]}), 22)\n        self.assertEqual(len(selected["bigster"]), 140)\n        self.assertEqual(len({row["configuration_code"] for row in selected["bigster"]}), 14)\n        self.assertEqual(len(selected["duster_iii"]), 100)\n        self.assertEqual(len({row["configuration_code"] for row in selected["duster_iii"]}), 10)''',
    )
    replace_once_or_done(
        path,
        '''    def test_no_generic_dimension_was_imported_from_brochures(self) -> None:\n        brochure_sources = {\n            "src_pl_sandero_brochure_20260202",\n            "src_pl_sandero_stepway_brochure_20260202",\n            "src_pl_jogger_brochure_20251217",\n            "src_pl_bigster_brochure_20251210",\n            "src_pl_duster_mini_brochure_20251020",\n        }\n        self.assertFalse(any(\n            row["source_code"] in brochure_sources and row["attribute_code"] in CORE_DIMENSIONS\n            for row in self.values\n        ))\n        turning = [\n            row for row in self.values\n            if row["source_code"] == "src_pl_duster_mini_brochure_20251020"\n            and row["attribute_code"] == "turning_circle_wheel_track"\n        ]\n        self.assertEqual(len(turning), 10)''',
        '''    def test_only_approved_generic_dimensions_were_imported_from_brochures(self) -> None:\n        brochure_sources = {\n            "src_pl_sandero_brochure_20260202",\n            "src_pl_sandero_stepway_brochure_20260202",\n            "src_pl_jogger_brochure_20251217",\n            "src_pl_bigster_brochure_20251210",\n            "src_pl_duster_mini_brochure_20251020",\n        }\n        generic = [\n            row\n            for row in self.values\n            if row["source_code"] in brochure_sources\n            and row["attribute_code"] in CORE_DIMENSIONS\n        ]\n        approved = [row for row in generic if 2568 <= int(row["id"]) <= 2949]\n        self.assertEqual(len(generic), 382)\n        self.assertEqual(len(approved), 382)\n        self.assertEqual(\n            [int(row["id"]) for row in approved],\n            list(range(2568, 2950)),\n        )\n        self.assertEqual(\n            Counter(row["source_code"] for row in approved),\n            Counter({\n                "src_pl_sandero_brochure_20260202": 40,\n                "src_pl_jogger_brochure_20251217": 242,\n                "src_pl_duster_mini_brochure_20251020": 100,\n            }),\n        )\n        self.assertFalse(any(\n            row["attribute_code"] in {"approach_angle", "departure_angle"}\n            for row in approved\n        ))\n        turning = [\n            row for row in self.values\n            if row["source_code"] == "src_pl_duster_mini_brochure_20251020"\n            and row["attribute_code"] == "turning_circle_wheel_track"\n        ]\n        self.assertEqual(len(turning), 10)''',
    )


def repair_technical_closure() -> None:
    path = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    replace_once_or_done(
        path,
        '''EXPECTED_RANGES = Counter(''',
        '''EXPECTED_CURRENT_SCALAR = Counter(\n    {\n        "src_pl_sandero_brochure_20260202": 132,\n        "src_pl_sandero_stepway_brochure_20260202": 72,\n        "src_pl_jogger_brochure_20251217": 490,\n        "src_pl_bigster_brochure_20251210": 180,\n        "src_pl_duster_mini_brochure_20251020": 244,\n    }\n)\nEXPECTED_RANGES = Counter(''',
    )
    replace_once_or_done(
        path,
        '''        self.assertEqual(len(self.scalar), 736)\n        self.assertEqual(len(self.ranges), 68)\n        self.assertEqual(Counter(row["source_code"] for row in self.scalar), EXPECTED_SCALAR)''',
        '''        self.assertEqual(len(self.scalar), 1118)\n        self.assertEqual(len(self.ranges), 68)\n        self.assertEqual(\n            Counter(row["source_code"] for row in self.scalar),\n            EXPECTED_CURRENT_SCALAR,\n        )''',
    )
    replace_once_or_done(
        path,
        '''        self.assertFalse(any(\n            row["attribute_code"] in {"overall_length", "overall_width", "overall_height", "wheelbase", "ground_clearance"}\n            for row in self.scalar\n        ))''',
        '''        approved = [\n            row\n            for row in self.scalar\n            if 2568 <= int(row["id"]) <= 2949\n        ]\n        self.assertEqual(len(approved), 382)\n        self.assertEqual(\n            [int(row["id"]) for row in approved],\n            list(range(2568, 2950)),\n        )\n        self.assertEqual(\n            Counter(row["source_code"] for row in approved),\n            Counter({\n                "src_pl_sandero_brochure_20260202": 40,\n                "src_pl_jogger_brochure_20251217": 242,\n                "src_pl_duster_mini_brochure_20251020": 100,\n            }),\n        )\n        self.assertFalse(any(\n            row["attribute_code"] in {"approach_angle", "departure_angle"}\n            for row in approved\n        ))''',
    )


def main() -> int:
    repair_semantic_mapping_review()
    repair_workbook()
    repair_duster_reporting()
    repair_jogger_reporting()
    repair_sandero_manual_reporting()
    repair_residual_review()
    repair_technical_closure()
    print("PASS: generic dimension snapshot tests normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
