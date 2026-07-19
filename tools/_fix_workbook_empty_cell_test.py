from __future__ import annotations

from pathlib import Path

path = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "test_configuration_comparison_workbook.py"
)
text = path.read_text(encoding="utf-8")
old = '''        comparable = [row for row in rows if row["status"] == "comparable"]
        self.assertTrue(
            all(
                row["report_as_of"] == date(2026, 6, 26)
                for row in comparable
            )
        )
'''
new = '''        comparable = [row for row in rows if row["status"] == "comparable"]
        self.assertEqual(
            {row["report_as_of"] for row in comparable},
            {date(2026, 4, 1), date(2026, 6, 26)},
        )
'''
if old not in text and new not in text:
    raise RuntimeError("workbook scope date assertion marker not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
