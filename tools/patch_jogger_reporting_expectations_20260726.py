#!/usr/bin/env python3
"""Refresh exact reporting expectations after adding contextual Jogger cargo."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"expectation anchor missing: {label}")
    return text.replace(old, new, 1)


def patch_scope(
    path: Path,
    *,
    old_slots: int,
    new_slots: int,
    old_present: int,
    new_present: int,
    old_summary: str,
    new_summary: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        f'        self.assertEqual(scope["technical_slots"], {old_slots})\n',
        f'        self.assertEqual(scope["technical_slots"], {new_slots})\n',
        f"{path.name} technical slots",
    )
    for field in ("applicable", "denominator", "present"):
        text = replace_once(
            text,
            f'                "{field}": {old_present},\n',
            f'                "{field}": {new_present},\n',
            f"{path.name} completeness {field}",
        )
    text = replace_once(
        text,
        f'        self.assertEqual(self.coverage["records"]["technical"]["present"], {old_present})\n',
        f'        self.assertEqual(self.coverage["records"]["technical"]["present"], {new_present})\n',
        f"{path.name} source coverage",
    )
    text = replace_once(
        text,
        '        self.assertEqual({pair["summary"]["technical"]["not_comparable"] for pair in pairs}, {0})\n',
        '        self.assertEqual({pair["summary"]["technical"]["not_comparable"] for pair in pairs}, {0, 10})\n',
        f"{path.name} pair comparability",
    )
    text = replace_once(
        text,
        old_summary,
        new_summary,
        f"{path.name} comparison summary",
    )
    path.write_text(text, encoding="utf-8")


patch_scope(
    ROOT / "tests" / "test_jogger_ecog120_automatic_reporting_scope.py",
    old_slots=34,
    new_slots=35,
    old_present=136,
    new_present=140,
    old_summary='                "technical": {"comparisons": 204, "equal": 172, "different": 32, "not_comparable": 0},\n',
    new_summary='                "technical": {"comparisons": 254, "equal": 182, "different": 32, "not_comparable": 40},\n',
)
patch_scope(
    ROOT / "tests" / "test_jogger_ecog120_manual_reporting_scope.py",
    old_slots=34,
    new_slots=35,
    old_present=204,
    new_present=210,
    old_summary='                "technical": {"comparisons": 510, "equal": 438, "different": 72, "not_comparable": 0},\n',
    new_summary='                "technical": {"comparisons": 630, "equal": 468, "different": 72, "not_comparable": 90},\n',
)
patch_scope(
    ROOT / "tests" / "test_jogger_hybrid155_automatic_reporting_scope.py",
    old_slots=27,
    new_slots=28,
    old_present=162,
    new_present=168,
    old_summary='                "technical": {"comparisons": 405, "equal": 351, "different": 54, "not_comparable": 0},\n',
    new_summary='                "technical": {"comparisons": 525, "equal": 381, "different": 54, "not_comparable": 90},\n',
)
patch_scope(
    ROOT / "tests" / "test_jogger_tce110_manual_reporting_scope.py",
    old_slots=24,
    new_slots=25,
    old_present=144,
    new_present=150,
    old_summary='                "technical": {"comparisons": 360, "equal": 297, "different": 63, "not_comparable": 0},\n',
    new_summary='                "technical": {"comparisons": 480, "equal": 327, "different": 63, "not_comparable": 90},\n',
)

workbook = ROOT / "tests" / "test_configuration_comparison_workbook.py"
text = workbook.read_text(encoding="utf-8")
text = replace_once(
    text,
    '            "A1:K10",\n',
    '            "A1:K11",\n',
    "workbook sources dimension",
)
workbook.write_text(text, encoding="utf-8")
print("PASS: Jogger reporting expectations refreshed")
