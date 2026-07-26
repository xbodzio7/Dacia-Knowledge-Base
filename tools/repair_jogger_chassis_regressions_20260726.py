#!/usr/bin/env python3
"""Update Jogger reporting snapshots after four chassis slots."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected snapshot not found: {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_workbook() -> None:
    replace_once(
        ROOT / "tests" / "test_configuration_comparison_workbook.py",
        '            "A1:AS221",\n',
        '            "A1:AS225",\n',
    )


def update_scope(path: Path, replacements: dict[str, str]) -> None:
    for old, new in replacements.items():
        replace_once(path, old, new)


def main() -> int:
    update_workbook()

    update_scope(
        ROOT / "tests" / "test_jogger_ecog120_automatic_reporting_scope.py",
        {
            '        self.assertEqual(scope["technical_slots"], 37)\n': '        self.assertEqual(scope["technical_slots"], 41)\n',
            '                "applicable": 148,\n': '                "applicable": 164,\n',
            '                "denominator": 148,\n': '                "denominator": 164,\n',
            '                "present": 148,\n': '                "present": 164,\n',
            '        self.assertEqual(self.coverage["sections"], {"covered": 108, "denominator": 108, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n': '        self.assertEqual(self.coverage["sections"], {"covered": 116, "denominator": 116, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n',
            '        self.assertEqual(self.coverage["records"]["technical"]["present"], 148)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 164)\n',
            '                "technical": {"comparisons": 266, "equal": 186, "different": 40, "not_comparable": 40},\n': '                "technical": {"comparisons": 290, "equal": 210, "different": 40, "not_comparable": 40},\n',
        },
    )

    update_scope(
        ROOT / "tests" / "test_jogger_ecog120_manual_reporting_scope.py",
        {
            '        self.assertEqual(scope["technical_slots"], 37)\n': '        self.assertEqual(scope["technical_slots"], 41)\n',
            '                "applicable": 222,\n': '                "applicable": 246,\n',
            '                "denominator": 222,\n': '                "denominator": 246,\n',
            '                "present": 222,\n': '                "present": 246,\n',
            '        self.assertEqual(self.coverage["sections"], {"covered": 162, "denominator": 162, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n': '        self.assertEqual(self.coverage["sections"], {"covered": 174, "denominator": 174, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n',
            '        self.assertEqual(self.coverage["records"]["technical"]["present"], 222)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 246)\n',
            '                "technical": {"comparisons": 660, "equal": 480, "different": 90, "not_comparable": 90},\n': '                "technical": {"comparisons": 720, "equal": 540, "different": 90, "not_comparable": 90},\n',
        },
    )

    update_scope(
        ROOT / "tests" / "test_jogger_hybrid155_automatic_reporting_scope.py",
        {
            '        self.assertEqual(scope["technical_slots"], 31)\n': '        self.assertEqual(scope["technical_slots"], 35)\n',
            '                "applicable": 186,\n': '                "applicable": 210,\n',
            '                "denominator": 186,\n': '                "denominator": 210,\n',
            '                "present": 186,\n': '                "present": 210,\n',
            '        self.assertEqual(self.coverage["sections"], {"covered": 168, "denominator": 168, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n': '        self.assertEqual(self.coverage["sections"], {"covered": 180, "denominator": 180, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n',
            '        self.assertEqual(self.coverage["records"]["technical"]["present"], 186)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 210)\n',
            '                "technical": {"comparisons": 570, "equal": 417, "different": 63, "not_comparable": 90},\n': '                "technical": {"comparisons": 630, "equal": 477, "different": 63, "not_comparable": 90},\n',
        },
    )

    update_scope(
        ROOT / "tests" / "test_jogger_tce110_manual_reporting_scope.py",
        {
            '        self.assertEqual(scope["technical_slots"], 26)\n': '        self.assertEqual(scope["technical_slots"], 30)\n',
            '                "applicable": 156,\n': '                "applicable": 180,\n',
            '                "denominator": 156,\n': '                "denominator": 180,\n',
            '                "present": 156,\n': '                "present": 180,\n',
            '        self.assertEqual(self.coverage["sections"], {"covered": 162, "denominator": 162, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n': '        self.assertEqual(self.coverage["sections"], {"covered": 174, "denominator": 174, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})\n',
            '        self.assertEqual(self.coverage["records"]["technical"]["present"], 156)\n': '        self.assertEqual(self.coverage["records"]["technical"]["present"], 180)\n',
            '                "technical": {"comparisons": 495, "equal": 333, "different": 72, "not_comparable": 90},\n': '                "technical": {"comparisons": 555, "equal": 393, "different": 72, "not_comparable": 90},\n',
        },
    )

    print("PASS: Jogger chassis reporting contracts updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
