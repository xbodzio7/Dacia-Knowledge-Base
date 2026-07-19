#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if text.count(old) != 1:
        raise SystemExit(f"unexpected patch anchor in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


architecture = Path("tests/test_configuration_value_ranges.py")
replace_once(architecture, "        self.assertEqual(len(rows[1:]), 64)\n", "        self.assertEqual(len(rows[1:]), 144)\n")
replace_once(architecture, "        self.assertEqual(checked, 64)\n", "        self.assertEqual(checked, 144)\n")
replace_once(architecture, "            self.assertEqual(count, 64)\n", "            self.assertEqual(count, 144)\n")

wltp = Path("tests/test_jogger_wltp_efficiency_ranges.py")
replace_once(
    wltp,
    '        cls.range_rows = rows(MASTER / "configuration_attribute_value_ranges.csv")\n',
    '        cls.range_rows = [\n'
    '            row\n'
    '            for row in rows(MASTER / "configuration_attribute_value_ranges.csv")\n'
    '            if 1 <= int(row["id"]) <= 64\n'
    '        ]\n',
)
replace_once(
    wltp,
    '            for path in SPECS.glob("jogger-page6-*-range-20260401.json")\n'
    '        }\n',
    '            for path in SPECS.glob("jogger-page6-*-range-20260401.json")\n'
    '            if path.name in SPEC_NAMES\n'
    '        }\n',
)
replace_once(wltp, '        self.assertEqual(baseline["tests"], 528)\n', '        self.assertEqual(baseline["tests"], 536)\n')
replace_once(wltp, '        self.assertEqual(baseline["rows"], 3909)\n', '        self.assertEqual(baseline["rows"], 3989)\n')
replace_once(wltp, '        self.assertEqual(baseline["configuration_value_ranges"], 64)\n', '        self.assertEqual(baseline["configuration_value_ranges"], 144)\n')
replace_once(wltp, '        self.assertEqual(baseline["configuration_range_import_specs"], 8)\n', '        self.assertEqual(baseline["configuration_range_import_specs"], 19)\n')
