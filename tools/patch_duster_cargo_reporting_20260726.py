#!/usr/bin/env python3
"""Add Duster cargo coverage and update durable reporting contracts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
IMPORTER = ROOT / "tools" / "import_duster_brochure_cargo_20260726.py"
REPORTING_TEST = ROOT / "tests" / "test_duster_ecog120_reporting_scope.py"
TARGETS = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
    "duster_iii_expression_hybrid155_4x2_automatic",
    "duster_iii_extreme_hybrid155_4x2_automatic",
    "duster_iii_journey_hybrid155_4x2_automatic",
}
SLOT = {"attribute_code": "boot_capacity", "fuel_type_code": ""}

text = IMPORTER.read_text(encoding="utf-8")
old = 'ensure(not any(row.get("powertrain_label") == "hybrid-G 150 4x4" for row in rows.values()), "unreviewed exact 4x4 configuration now exists")'
new = 'ensure(not any(code.startswith("duster_iii_") and row.get("powertrain_label") == "hybrid-G 150 4x4" for code, row in rows.items()), "unreviewed exact Duster 4x4 configuration now exists")'
if old in text:
    IMPORTER.write_text(text.replace(old, new), encoding="utf-8")
elif new not in text:
    raise RuntimeError("Duster 4x4 guard anchor missing")

changed: list[str] = []
for path in sorted(REPORTING.glob("*completeness.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    configurations = payload.get("configurations")
    slots = payload.get("technical_slots")
    if not isinstance(configurations, list) or not isinstance(slots, list):
        continue
    codes = {str(item.get("configuration_code", "")) for item in configurations if isinstance(item, dict)}
    if not (codes & TARGETS) or SLOT in slots:
        continue
    slots.append(SLOT.copy())
    slots.sort(key=lambda item: (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", ""))))
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed.append(path.relative_to(ROOT).as_posix())

text = REPORTING_TEST.read_text(encoding="utf-8")
replacements = {
    '"ecog120": {\n': '"ecog120": {\n',
    '        "technical_slots": 17,\n        "technical_records": 68,\n        "technical_comparisons": 102,': '        "technical_slots": 18,\n        "technical_records": 72,\n        "technical_comparisons": 126,',
    '        "technical_slots": 16,\n        "technical_records": 48,\n        "technical_comparisons": 48,': '        "technical_slots": 17,\n        "technical_records": 51,\n        "technical_comparisons": 72,',
    '        "technical_slots": 14,\n        "technical_records": 42,\n        "technical_comparisons": 42,': '        "technical_slots": 15,\n        "technical_records": 45,\n        "technical_comparisons": 66,',
}
for before, after in replacements.items():
    if before in text:
        text = text.replace(before, after, 1)
    elif after not in text:
        raise RuntimeError(f"reporting test anchor missing: {before!r}")
REPORTING_TEST.write_text(text, encoding="utf-8")

print(f"PASS: Duster cargo reporting scopes updated ({len(changed)})")
for path in changed:
    print(f"  {path}")
