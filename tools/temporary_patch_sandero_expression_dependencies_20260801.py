#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(path: str, replacements: dict[str, str]) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for previous, current in replacements.items():
        if previous not in text:
            if current in text:
                continue
            raise SystemExit(f"missing dependency contract in {path}: {previous!r}")
        text = text.replace(previous, current)
    target.write_text(text, encoding="utf-8")


def main() -> int:
    patch(
        "tools/import_sandero_stepway_essential_source_gap_20260626.py",
        {
            'summary["missing_technical_count"] != 137': 'summary["missing_technical_count"] != 125',
            "expected 137 remaining technical records": "expected 125 remaining technical records",
            'summary["exhausted_source_candidate_count"] != 2': 'summary["exhausted_source_candidate_count"] != 3',
            "expected exactly two exhausted-source candidates": "expected exactly three exhausted-source candidates",
        },
    )
    patch(
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        {
            'payload["summary"]["missing_technical_count"], 137': 'payload["summary"]["missing_technical_count"], 125',
            'payload["summary"]["exhausted_source_candidate_count"], 2': 'payload["summary"]["exhausted_source_candidate_count"], 3',
        },
    )
    patch(
        "tests/test_duster_ecog120_reporting_scope.py",
        {'default["summary"]["total_differences"], 371': 'default["summary"]["total_differences"], 377'},
    )
    patch(
        "tests/test_jogger_payload_performance_ranges.py",
        {"self.assertEqual(len(self.ranges), 304)": "self.assertEqual(len(self.ranges), 307)"},
    )
    patch(
        "tests/test_official_brochure_residual_evidence_review.py",
        {'len(selected["sandero_stepway_iii"]), 54': 'len(selected["sandero_stepway_iii"]), 56'},
    )
    patch(
        "tools/review_official_brochure_residual_evidence_20260726.py",
        {'len(selected["sandero_stepway_iii"]) == 54': 'len(selected["sandero_stepway_iii"]) == 56'},
    )
    patch(
        "tests/test_sandero_ecog120_manual_reporting_scope.py",
        {
            '"coverage_percent": "91.67"': '"coverage_percent": "93.67"',
            '"missing": 25,': '"missing": 19,',
            '"present": 275,': '"present": 281,',
            'len(self.completeness["gaps"]["technical"]), 25': 'len(self.completeness["gaps"]["technical"]), 19',
            '"covered": 134,': '"covered": 135,',
            '"partial": 34,': '"partial": 33,',
            'self.coverage["records"]["technical"]["present"], 275': 'self.coverage["records"]["technical"]["present"], 281',
            'len(self.coverage["gaps"]), 72': 'len(self.coverage["gaps"]), 66',
            'pair["summary"]["technical"]["not_comparable"] for pair in pairs), 92': 'pair["summary"]["technical"]["not_comparable"] for pair in pairs), 75',
            '"technical": {"comparisons": 688, "different": 157, "equal": 439, "not_comparable": 92}': '"technical": {"comparisons": 688, "different": 162, "equal": 451, "not_comparable": 75}',
            '"total_differences": 181': '"total_differences": 186',
            '{"ambiguous": 0, "found": 0, "not_stated": 55, "out_of_scope": 17, "total": 72}': '{"ambiguous": 0, "found": 0, "not_stated": 49, "out_of_scope": 17, "total": 66}',
            "self.assertEqual(len(ranged), 36)": "self.assertEqual(len(ranged), 45)",
        },
    )
    patch(
        "tests/test_spring_technical_20260219.py",
        {
            'state["baseline"]["configuration_values"], 3555': 'state["baseline"]["configuration_values"], 3558',
            'state["baseline"]["configuration_value_ranges"], 304': 'state["baseline"]["configuration_value_ranges"], 307',
            'counts["configuration_attribute_values"], 3478': 'counts["configuration_attribute_values"], 3481',
            'counts["configuration_attribute_value_ranges"], 304': 'counts["configuration_attribute_value_ranges"], 307',
        },
    )
    patch(
        "tests/configuration_comparison_context_filter_contract.py",
        {
            "len(core.difference_csv_rows(report)), 371": "len(core.difference_csv_rows(report)), 377",
            '"fuel_type_code=": 164': '"fuel_type_code=": 168',
            '"fuel_type_code=lpg": 83': '"fuel_type_code=lpg": 84',
            '"fuel_type_code=petrol": 77': '"fuel_type_code=petrol": 78',
        },
    )
    patch(
        "tests/configuration_comparison_pair_summary_contract.py",
        {"            371,": "            377,"},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
