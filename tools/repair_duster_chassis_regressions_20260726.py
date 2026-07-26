#!/usr/bin/env python3
"""Update historical range totals and Duster reporting snapshots."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_all(path: Path, old: str, new: str, expected_count: int) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        return
    count = text.count(old)
    if count != expected_count:
        raise RuntimeError(f"unexpected occurrence count in {path}: {old!r}: {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    replace_all(path, old, new, 1)


def update_range_totals() -> None:
    ranges = ROOT / "tests" / "test_configuration_value_ranges.py"
    replace_all(ranges, "        self.assertEqual(len(rows[1:]), 234)\n", "        self.assertEqual(len(rows[1:]), 244)\n", 1)
    replace_all(ranges, "        self.assertEqual(checked, 234)\n", "        self.assertEqual(checked, 244)\n", 1)
    replace_all(ranges, "            self.assertEqual(count, 234)\n", "            self.assertEqual(count, 244)\n", 1)

    jogger = ROOT / "tests" / "test_jogger_payload_performance_ranges.py"
    replace_once(jogger, "        self.assertEqual(len(self.ranges), 234)\n", "        self.assertEqual(len(self.ranges), 244)\n")


def update_duster_scope_snapshots() -> None:
    path = ROOT / "tests" / "test_duster_ecog120_reporting_scope.py"
    replacements = {
        '        "technical_slots": 20,\n': '        "technical_slots": 27,\n',
        '        "technical_records": 80,\n': '        "technical_records": 108,\n',
        '        "technical_comparisons": 138,\n': '        "technical_comparisons": 180,\n',
        '        "technical_slots": 19,\n': '        "technical_slots": 26,\n',
        '        "technical_records": 57,\n': '        "technical_records": 78,\n',
        '        "technical_comparisons": 78,\n': '        "technical_comparisons": 99,\n',
        '        "technical_slots": 17,\n': '        "technical_slots": 24,\n',
        '        "technical_records": 51,\n': '        "technical_records": 72,\n',
        '        "technical_comparisons": 72,\n': '        "technical_comparisons": 93,\n',
    }
    for old, new in replacements.items():
        replace_once(path, old, new)


def main() -> int:
    update_range_totals()
    update_duster_scope_snapshots()
    print("PASS: Duster chassis regression contracts updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
