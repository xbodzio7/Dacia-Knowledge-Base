from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


run(sys.executable, "tools/import_jogger_equipment_availability.py", "--apply")

for path in sorted((ROOT / "tests").rglob("*.py")):
    text = path.read_text(encoding="utf-8")
    text = text.replace('baseline["tests"], 536', 'baseline["tests"], 544')
    text = text.replace('baseline["rows"], 3989', 'baseline["rows"], 5155')
    text = text.replace('baseline["availability_records"], 1811', 'baseline["availability_records"], 2977')
    text = text.replace('"tests": 536', '"tests": 544')
    text = text.replace('"rows": 3989', '"rows": 5155')
    text = text.replace('"availability_records": 1811', '"availability_records": 2977')
    path.write_text(text, encoding="utf-8")

path = ROOT / "tests/test_duster_equipment_availability_import.py"
replace(
    path,
    '''    def test_existing_non_duster_availability_is_preserved(self) -> None:\n        actual = rows("configuration_attribute_availability.csv")\n        non_duster = [\n            row for row in actual\n            if not row["configuration_code"].startswith("duster_iii_")\n        ]\n        self.assertEqual(len(actual), 1811)\n        self.assertEqual(len(non_duster), 419)\n''',
    '''    def test_existing_sandero_availability_is_preserved(self) -> None:\n        actual = rows("configuration_attribute_availability.csv")\n        sandero = [\n            row for row in actual\n            if not row["configuration_code"].startswith(("duster_iii_", "jogger_"))\n        ]\n        self.assertEqual(len(actual), 2977)\n        self.assertEqual(len(sandero), 419)\n''',
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["reference_delivery"] = {
    "name": "Jogger Equipment Matrix Intake Selection",
    "pull_request": 128,
    "head_sha": "56fbefc78e7f83225b5374b11b8dd1a562eef681",
    "quality_run": 589,
}
state["baseline"].update({"tests": 544, "rows": 5155, "availability_records": 2977})
state["current_package"] = {
    "name": "Jogger Equipment Availability Import",
    "status": "active",
    "goal": "Materialize 53 selected pages 4-5 equipment attributes as 1166 dated availability records for all 22 active Jogger configurations.",
}
state["next_package"] = {
    "name": "Jogger Technical Reporting Scope Selection",
    "status": "planned",
    "goal": "Select the first bounded homogeneous Jogger reporting group after technical, price and equipment source coverage is complete.",
}
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

review = ROOT / "project/reviews/jogger-equipment-availability-import.md"
review.write_text(
    """# Jogger Equipment Availability Import\n\n## Status\n\n`IMPLEMENTING`\n\nThis package materializes the denominator selected in PR #128 without changing scalar values, ranges, prices or existing availability rows.\n\n## Denominator\n\nTwo versioned pages 4-5 matrices define 53 active boolean attributes for all 22 active Jogger configurations. The importer creates exactly 1,166 records: 920 `standard`, 84 `optional` and 162 `not_available`.\n\n## Storage contract\n\nThe records form the contiguous availability-ID suffix `1812-2977`. Every row is dated `2026-04-01`, references `src_pl_jogger_price_my26_20260401`, retains the printed source label and preserves package or powertrain qualifiers in notes.\n\nThe existing 419 Sandero and 1,392 Duster records remain byte-for-byte semantically unchanged.\n\n## Evidence boundary\n\n`start_stop_system` remains a scalar page-6 observation. Conflicting rain-wiper evidence, descriptive appearance values, package prices and features without a selected dedicated contract remain outside this package.\n\n## Expected baseline\n\n- 544 tests;\n- 37 master CSV files and 5,155 rows;\n- 1,204 scalar values and 71 scalar specifications;\n- 144 range values and 19 range specifications;\n- 2,977 availability records;\n- 357 attributes in 30 categories.\n\n## Next package\n\n**Jogger Technical Reporting Scope Selection** will select the first homogeneous Jogger reporting denominator.\n""",
    encoding="utf-8",
)

changelog = ROOT / "CHANGELOG.md"
text = changelog.read_text(encoding="utf-8")
entry = "* Source-backed Jogger equipment availability with 1,166 records across 53 canonical attributes and explicit standard, optional and unavailable semantics.\n"
if entry not in text:
    text = text.replace("### Added\n\n", "### Added\n\n" + entry, 1)
    changelog.write_text(text, encoding="utf-8")

readme = ROOT / "README.md"
text = readme.read_text(encoding="utf-8")
paragraph = "Macierze wyposażenia Jogger ze stron 4-5 dostarczają 1 166 datowanych rekordów dostępności dla 53 kanonicznych atrybutów i 22 konfiguracji. Import zachowuje statusy seryjne, opcjonalne i niedostępne oraz kwalifikatory pakietów i napędów.\n\n"
marker = "<!-- dkb:documentation-baseline:readme:start -->"
if paragraph not in text:
    text = text.replace(marker, paragraph + marker, 1)
    readme.write_text(text, encoding="utf-8")

run(sys.executable, "tools/dkb.py", "project-state", "--apply")
run(sys.executable, "tools/dkb.py", "documentation-baseline", "--apply")
run(sys.executable, "tools/import_jogger_equipment_availability.py", "--check")
