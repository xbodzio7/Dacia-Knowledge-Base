#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "data/imports/configuration_value_ranges"
SOURCE = "src_pl_sandero_brochure_20260202"
DATE = "2026-02-02"

TCE = [
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
]
MANUAL = [
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
]
AUTO = [
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
]


def row(code: str, fuel: str, lo: str, hi: str, text: str) -> dict:
    return {
        "configuration_code": code,
        "source_code": SOURCE,
        "fuel_type_code": fuel,
        "minimum_value": lo,
        "maximum_value": hi,
        "lower_inclusive": True,
        "upper_inclusive": True,
        "source_text": text,
    }


def spec(id_start: int, attribute: str, rows: list[dict]) -> dict:
    return {
        "version": 1,
        "kind": "configuration_attribute_value_ranges",
        "id_start": id_start,
        "attribute_code": attribute,
        "attribute_contract": {"data_type": "integer", "unit": "rpm", "status": "active"},
        "observation_date": DATE,
        "fuel_type_code": "",
        "source_page": 17,
        "source_section": "SILNIKI",
        "notes_template": "Source page {page}, section {section}: {source_text}. Inclusive engine-speed interval retained with source fuel context.",
        "rows": rows,
    }


power_rows = [row(code, "petrol", "5000", "5250", "74 (120 KM) od 5000 do 5250") for code in TCE]
power_rows += [row(code, "lpg", "4500", "5000", "90 (120 KM) od 4500 do 5000") for code in MANUAL + AUTO]
power_rows += [row(code, "petrol", "4500", "5750", "84 (114 KM) od 4500 do 5750") for code in MANUAL + AUTO]
torque_rows = [row(code, "petrol", "2900", "3500", "200 od 2900 do 3500") for code in TCE]
torque_rows += [row(code, "lpg", "1750", "3750", "197 od 1750 do 3750") for code in MANUAL + AUTO]
torque_rows += [row(code, "petrol", "2000", "4000", "190 od 2000 do 4000") for code in MANUAL]

spec_paths = [
    SPECS / "sandero-page17-max-power-rpm-ranges-20260202.json",
    SPECS / "sandero-page17-max-torque-rpm-ranges-20260202.json",
]
for path, payload in zip(spec_paths, [spec(279, "max_power_rpm", power_rows), spec(290, "max_torque_rpm", torque_rows)]):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

for path in spec_paths:
    subprocess.run(["python", "tools/import_configuration_value_ranges.py", "--spec", str(path), "--apply"], cwd=ROOT, check=True)
    subprocess.run(["python", "tools/import_configuration_value_ranges.py", "--spec", str(path), "--verify"], cwd=ROOT, check=True)

TEST = ROOT / "tests/test_sandero_page17_power_torque_rpm_ranges.py"
TEST.write_text(r'''from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPECS = ROOT / "data/imports/configuration_value_ranges"
PDF = ROOT / "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
SOURCE = "src_pl_sandero_brochure_20260202"
SHA = "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97"
SPEC_NAMES = {
    "sandero-page17-max-power-rpm-ranges-20260202.json",
    "sandero-page17-max-torque-rpm-ranges-20260202.json",
}
TARGETS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoPage17PowerTorqueRpmRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
        cls.selected = sorted([r for r in cls.ranges if 279 <= int(r["id"]) <= 298], key=lambda r: int(r["id"]))
        cls.specs = {name: json.loads((SPECS / name).read_text(encoding="utf-8")) for name in SPEC_NAMES}

    def test_two_specs_and_contiguous_exact_receipt(self) -> None:
        self.assertEqual(sum(len(s["rows"]) for s in self.specs.values()), 20)
        self.assertEqual([int(r["id"]) for r in self.selected], list(range(279, 299)))
        self.assertEqual(Counter(r["attribute_code"] for r in self.selected), Counter({"max_power_rpm": 11, "max_torque_rpm": 9}))

    def test_source_date_unit_and_closed_intervals(self) -> None:
        self.assertEqual({r["source_code"] for r in self.selected}, {SOURCE})
        self.assertEqual({r["observation_date"] for r in self.selected}, {"2026-02-02"})
        self.assertEqual({(r["lower_inclusive"], r["upper_inclusive"]) for r in self.selected}, {("true", "true")})
        for payload in self.specs.values():
            self.assertEqual(payload["attribute_contract"], {"data_type": "integer", "unit": "rpm", "status": "active"})
            self.assertEqual(payload["source_page"], 17)
            self.assertEqual(payload["source_section"], "SILNIKI")

    def test_power_ranges_preserve_exact_fuel_context(self) -> None:
        actual = Counter((r["fuel_type_code"], r["minimum_value"], r["maximum_value"]) for r in self.selected if r["attribute_code"] == "max_power_rpm")
        self.assertEqual(actual, Counter({("petrol", "5000", "5250"): 3, ("lpg", "4500", "5000"): 4, ("petrol", "4500", "5750"): 4}))

    def test_torque_ranges_preserve_missing_automatic_petrol_boundary(self) -> None:
        torque = [r for r in self.selected if r["attribute_code"] == "max_torque_rpm"]
        actual = Counter((r["fuel_type_code"], r["minimum_value"], r["maximum_value"]) for r in torque)
        self.assertEqual(actual, Counter({("petrol", "2900", "3500"): 3, ("lpg", "1750", "3750"): 4, ("petrol", "2000", "4000"): 2}))
        self.assertFalse(any(r["fuel_type_code"] == "petrol" and r["configuration_code"].endswith("ecog120_automatic") for r in torque))

    def test_exact_active_targets_are_linked_to_source(self) -> None:
        configurations = {r["code"]: r for r in rows(MASTER / "configurations.csv")}
        linked = {r["configuration_code"] for r in rows(MASTER / "source_configurations.csv") if r["source_code"] == SOURCE and r["relationship"] == "brochure_technical_data_for"}
        self.assertEqual({r["configuration_code"] for r in self.selected}, TARGETS)
        self.assertTrue(all(configurations[c]["status"] == "active" for c in TARGETS))
        self.assertTrue(TARGETS <= linked)

    def test_registered_pdf_and_exact_source_fragments(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SHA)
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 17))
        fragments = {r["source_text"] for payload in self.specs.values() for r in payload["rows"]}
        for fragment in fragments:
            self.assertIn(_compact_text(fragment), page)

    def test_reconciliation_non_import_boundaries_remain_absent(self) -> None:
        self.assertEqual(len(self.selected), 20)
        self.assertFalse(any(r["attribute_code"] not in {"max_power_rpm", "max_torque_rpm"} for r in self.selected))
        self.assertFalse(any(r["configuration_code"].endswith("ecog120_automatic") and r["attribute_code"] == "max_torque_rpm" and r["fuel_type_code"] == "petrol" for r in self.selected))


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

# Live range-count contracts.
path = ROOT / "tests/test_configuration_value_ranges.py"
text = path.read_text(encoding="utf-8")
text = text.replace("self.assertEqual(len(rows[1:]), 278)", "self.assertEqual(len(rows[1:]), 298)")
text = text.replace("self.assertEqual(checked, 278)", "self.assertEqual(checked, 298)")
text = text.replace("self.assertEqual(count, 278)", "self.assertEqual(count, 298)")
path.write_text(text, encoding="utf-8")

path = ROOT / "tests/test_jogger_payload_performance_ranges.py"
text = path.read_text(encoding="utf-8").replace("self.assertEqual(len(self.ranges), 278)", "self.assertEqual(len(self.ranges), 298)")
path.write_text(text, encoding="utf-8")

path = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
text = path.read_text(encoding="utf-8")
old = 'EXPECTED_CURRENT_RANGE_BY_SOURCE = EXPECTED_RANGE_BY_SOURCE + Counter(\n    {"src_pl_bigster_brochure_20251210": 30}\n)'
new = 'EXPECTED_CURRENT_RANGE_BY_SOURCE = EXPECTED_RANGE_BY_SOURCE + Counter(\n    {"src_pl_bigster_brochure_20251210": 30, "src_pl_sandero_brochure_20260202": 20}\n)'
if old not in text:
    raise RuntimeError("current range-source counter block not found")
path.write_text(text.replace(old, new), encoding="utf-8")

# Refresh generated evidence products before synchronizing state and docs.
subprocess.run(["python", "tools/dkb.py", "pdf-candidate-coverage-reconciliation"], cwd=ROOT, check=True)
subprocess.run(["python", "tools/dkb.py", "pdf-candidate-residual-gap-prioritization"], cwd=ROOT, check=True)
subprocess.run(["python", "tools/dkb.py", "documentation-baseline", "--apply"], cwd=ROOT, check=True)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["phase"] = "Sandero Page 17 Power and Torque RPM Range Import"
state["current_package"] = {
    "package_id": "post_residual_sandero_page17_power_torque_rpm_range_import_001",
    "kind": "configuration_value_range_import",
    "name": "Sandero Page 17 Power and Torque RPM Range Import",
    "status": "complete",
    "goal": "Add 20 exact closed max-power and max-torque engine-speed ranges across the seven active Sandero III configurations while preserving fuel context and every reconciliation non-import boundary.",
    "manifest_paths": [],
}
state["next_package"] = {
    "package_id": "post_residual_sandero_page17_power_torque_rpm_range_import_closure_001",
    "kind": "review_closure",
    "name": "Sandero Page 17 Power and Torque RPM Range Import Closure",
    "status": "planned",
    "source_code": SOURCE,
    "source_page": 17,
    "goal": "Verify the exact 20-range receipt, close the only import-ready Sandero page-17 gap, preserve every scalar, fuel-context and non-import boundary, then publish data-products-v1.9.0.",
    "manifest_paths": [
        "data/reporting/sandero_page17_power_torque_rpm_range_import_closure.json",
        "data/reporting/sandero_page17_power_torque_rpm_range_import_closure.md",
        "project/reviews/sandero-page17-power-torque-rpm-range-import-closure-2026-07-31.md",
        "project/state.json",
        "project/STATE_SUMMARY.md",
    ],
}
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
subprocess.run(["python", "tools/dkb.py", "project-state", "--apply"], cwd=ROOT, check=True)

# Record the actual package surface after all generators have run.
changed = []
for line in subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines():
    changed.append(line[3:])
state = json.loads(state_path.read_text(encoding="utf-8"))
state["current_package"]["manifest_paths"] = sorted(set(changed) | {"project/state.json", "project/STATE_SUMMARY.md"})
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
subprocess.run(["python", "tools/dkb.py", "project-state", "--apply"], cwd=ROOT, check=True)
subprocess.run(["python", "-m", "unittest", "discover", "-s", "tests"], cwd=ROOT, check=True)
subprocess.run(["python", "tools/dkb.py", "project-state", "--check"], cwd=ROOT, check=True)
subprocess.run(["python", "tools/dkb.py", "documentation-baseline", "--check"], cwd=ROOT, check=True)
print("MATERIALIZATION PASS")
