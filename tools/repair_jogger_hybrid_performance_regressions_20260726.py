#!/usr/bin/env python3
"""Update historical regression expectations after Jogger performance import."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    range_test = ROOT / "tests" / "test_configuration_value_ranges.py"
    replace_once(range_test, "self.assertEqual(len(rows[1:]), 176)", "self.assertEqual(len(rows[1:]), 234)")
    replace_once(range_test, "self.assertEqual(checked, 176)", "self.assertEqual(checked, 234)")
    replace_once(range_test, "self.assertEqual(count, 176)", "self.assertEqual(count, 234)")

    payload_test = ROOT / "tests" / "test_jogger_payload_performance_ranges.py"
    replace_once(payload_test, "self.assertEqual(len(self.ranges), 176)", "self.assertEqual(len(self.ranges), 234)")

    hybrid_test = ROOT / "tests" / "test_jogger_hybrid155_automatic_reporting_scope.py"
    replace_once(hybrid_test, 'self.assertEqual(scope["technical_slots"], 29)', 'self.assertEqual(scope["technical_slots"], 31)')
    replace_once(
        hybrid_test,
        '''                "applicable": 174,
                "coverage_percent": "100.00",
                "denominator": 174,
                "missing": 0,
                "not_applicable": 0,
                "present": 174,''',
        '''                "applicable": 186,
                "coverage_percent": "100.00",
                "denominator": 186,
                "missing": 0,
                "not_applicable": 0,
                "present": 186,''',
    )
    replace_once(
        hybrid_test,
        'self.assertEqual(self.coverage["records"]["technical"]["present"], 174)',
        'self.assertEqual(self.coverage["records"]["technical"]["present"], 186)',
    )
    replace_once(
        hybrid_test,
        '"technical": {"comparisons": 540, "equal": 387, "different": 63, "not_comparable": 90}',
        '"technical": {"comparisons": 570, "equal": 417, "different": 63, "not_comparable": 90}',
    )

    print("PASS: Jogger hybrid performance regression expectations updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
