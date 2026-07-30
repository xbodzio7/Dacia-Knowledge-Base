#!/usr/bin/env python3
"""Materialize the Duster mini page 20 exact scalar gap import."""

from __future__ import annotations

import csv
import json
import pprint
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SOURCE = "src_pl_duster_mini_brochure_20251020"
SOURCE_SHA = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
PDF = ROOT / "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf"
TEST_PATH = ROOT / "tests/test_duster_mini_page20_exact_scalar_gap_import.py"
RECONCILIATION_JSON = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"

ECOG = [
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
]
MHEV = [
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
]
TARGETS = ECOG + MHEV
SPECS = [
    {
        "filename": "duster-mini-page20-emission-standard-20251020.json",
        "id_start": 3464,
        "attribute": "emission_standard",
        "contract": {"data_type": "enum", "unit": "", "status": "active"},
        "source_section": "SILNIKI",
        "source_text": "Norma emisji spalin Euro 6E bis Euro 6E bis",
        "values": {code: "euro_6e_bis" for code in TARGETS},
    },
    {
        "filename": "duster-mini-page20-particulate-filter-20251020.json",
        "id_start": 3471,
        "attribute": "particulate_filter",
        "contract": {"data_type": "boolean", "unit": "", "status": "active"},
        "source_section": "SILNIKI",
        "source_text": "Filtr cząstek stałych Da Da",
        "values": {code: "true" for code in TARGETS},
    },
    {
        "filename": "duster-mini-page20-start-stop-20251020.json",
        "id_start": 3478,
        "attribute": "start_stop_system",
        "contract": {"data_type": "boolean", "unit": "", "status": "active"},
        "source_section": "SILNIKI",
        "source_text": "Stop & Start Da Da",
        "values": {code: "true" for code in TARGETS},
    },
    {
        "filename": "duster-mini-page20-eco-mode-20251020.json",
        "id_start": 3485,
        "attribute": "eco_mode",
        "contract": {"data_type": "boolean", "unit": "", "status": "active"},
        "source_section": "OSIĄGI I ZUŻYCIE PALIWA",
        "source_text": "Tryb Eco Da Da",
        "values": {code: "true" for code in TARGETS},
    },
    {
        "filename": "duster-mini-page20-gross-vehicle-weight-20251020.json",
        "id_start": 3492,
        "attribute": "gross_vehicle_weight",
        "contract": {"data_type": "integer", "unit": "kg", "status": "active"},
        "source_section": "MASY",
        "source_text": "Dopuszczalna masa całkowita pojazdu (DMC) 1805 1830",
        "values": {**{code: "1805" for code in ECOG}, **{code: "1830" for code in MHEV}},
    },
]


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def replace_pattern(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{path}: replacement target count is {count}")
    path.write_text(updated, encoding="utf-8", newline="\n")


def write_specs() -> None:
    for spec in SPECS:
        payload = {
            "version": 1,
            "kind": "configuration_attribute_values",
            "id_start": spec["id_start"],
            "attribute_code": spec["attribute"],
            "attribute_contract": spec["contract"],
            "observation_date": "2025-10-20",
            "fuel_type_code": "",
            "source_page": 20,
            "source_section": spec["source_section"],
            "notes_template": "Source page {page}, section {section}: {source_text}",
            "rows": [
                {
                    "configuration_code": code,
                    "source_code": SOURCE,
                    "value": spec["values"][code],
                    "source_text": spec["source_text"],
                }
                for code in TARGETS
            ],
        }
        write_json(ROOT / "data/imports/configuration_values" / spec["filename"], payload)


def write_test() -> None:
    specs_literal = pprint.pformat(
        {
            spec["filename"]: {
                "id_start": spec["id_start"],
                "attribute": spec["attribute"],
                "contract": spec["contract"],
                "source_text": spec["source_text"],
                "values": spec["values"],
            }
            for spec in SPECS
        },
        sort_dicts=False,
        width=120,
    )
    targets_literal = pprint.pformat(set(TARGETS), sort_dicts=True, width=120)
    text = f'''"""Verify the Duster mini page 20 exact scalar gap import."""

from __future__ import annotations

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
IMPORTS = ROOT / "data/imports/configuration_values"
PDF = ROOT / "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf"
SOURCE = {SOURCE!r}
SOURCE_SHA = {SOURCE_SHA!r}
TARGETS = {targets_literal}
SPECS = {specs_literal}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterMiniPage20ExactScalarGapImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.payloads = {{name: json.loads((IMPORTS / name).read_text(encoding="utf-8")) for name in SPECS}}

    def test_source_hash_and_spec_contracts(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SOURCE_SHA)
        for name, expected in SPECS.items():
            payload = self.payloads[name]
            self.assertEqual(payload["id_start"], expected["id_start"])
            self.assertEqual(payload["attribute_code"], expected["attribute"])
            self.assertEqual(payload["attribute_contract"], expected["contract"])
            self.assertEqual(payload["observation_date"], "2025-10-20")
            self.assertEqual(payload["source_page"], 20)

    def test_each_spec_targets_exactly_seven_manual_configurations(self) -> None:
        for name, expected in SPECS.items():
            payload = self.payloads[name]
            actual = {{row["configuration_code"]: row["value"] for row in payload["rows"]}}
            self.assertEqual(actual, expected["values"])
            self.assertEqual(set(actual), TARGETS)
            self.assertEqual(len(payload["rows"]), 7)
            self.assertEqual({{row["source_code"] for row in payload["rows"]}}, {{SOURCE}})
            self.assertFalse(any(row.get("fuel_type_code") for row in payload["rows"]))

    def test_master_receipt_is_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3464 <= int(row["id"]) <= 3498],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3464, 3499)))
        self.assertEqual(
            Counter(row["attribute_code"] for row in selected),
            Counter({{
                "emission_standard": 7,
                "particulate_filter": 7,
                "start_stop_system": 7,
                "eco_mode": 7,
                "gross_vehicle_weight": 7,
            }}),
        )
        self.assertEqual({{row["source_code"] for row in selected}}, {{SOURCE}})
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2025-10-20"}})
        self.assertEqual({{row["configuration_code"] for row in selected}}, TARGETS)

    def test_master_values_match_reviewed_handoff(self) -> None:
        selected = [row for row in self.values if 3464 <= int(row["id"]) <= 3498]
        by_attribute = {{}}
        for row in selected:
            by_attribute.setdefault(row["attribute_code"], {{}})[row["configuration_code"]] = row["value"]
        for expected in SPECS.values():
            self.assertEqual(by_attribute[expected["attribute"]], expected["values"])

    def test_targets_are_active_manual_duster_and_source_linked(self) -> None:
        configurations = {{row["code"]: row for row in rows(MASTER / "configurations.csv")}}
        versions = {{row["code"]: row for row in rows(MASTER / "versions.csv")}}
        linked = {{
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }}
        for code in TARGETS:
            row = configurations[code]
            self.assertEqual(row["status"], "active")
            self.assertEqual(row["transmission_type"], "manual")
            self.assertEqual(versions[row["version_code"]]["model_code"], "duster_iii")
        self.assertTrue(TARGETS <= linked)

    def test_page_text_contains_every_reviewed_source_row(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        candidates = [_compact_text(text) for _, text in extract_page_candidates(PDF, 20)]
        page_text = " ".join(candidates)
        for expected in SPECS.values():
            self.assertIn(_compact_text(expected["source_text"]), page_text)

    def test_injection_context_and_non_import_boundaries_remain_preserved(self) -> None:
        selected = [row for row in self.values if row["configuration_code"] in TARGETS]
        self.assertFalse(any(row["attribute_code"] == "injection_type" and row["source_code"] == SOURCE for row in selected))
        imported_attributes = {{row["attribute_code"] for row in self.values if 3464 <= int(row["id"]) <= 3498}}
        self.assertEqual(
            imported_attributes,
            {{"emission_standard", "particulate_filter", "start_stop_system", "eco_mode", "gross_vehicle_weight"}},
        )


if __name__ == "__main__":
    unittest.main()
'''
    TEST_PATH.write_text(text, encoding="utf-8", newline="\n")


def patch_global_receipt() -> None:
    checker = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    text = checker.read_text(encoding="utf-8")
    anchor = '    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'
    block = '''    duster_page20_exact_scalar_gap = [
        row
        for row in scalar
        if row.get("source_code") == "src_pl_duster_mini_brochure_20251020"
        and 3464 <= int(row.get("id", "0")) <= 3498
    ]
    if duster_page20_exact_scalar_gap:
        ensure(len(duster_page20_exact_scalar_gap) == 35, "Duster page-20 exact scalar gap receipt differs")
        ensure([int(row["id"]) for row in duster_page20_exact_scalar_gap] == list(range(3464, 3499)), "Duster page-20 exact scalar gap IDs differ")
        ensure(
            Counter(row.get("attribute_code", "") for row in duster_page20_exact_scalar_gap)
            == Counter({
                "emission_standard": 7,
                "particulate_filter": 7,
                "start_stop_system": 7,
                "eco_mode": 7,
                "gross_vehicle_weight": 7,
            }),
            "Duster page-20 exact scalar gap attribute distribution differs",
        )
        ensure(
            {row.get("configuration_code", "") for row in duster_page20_exact_scalar_gap}
            == {
                "duster_iii_essential_ecog120_4x2_manual",
                "duster_iii_expression_ecog120_4x2_manual",
                "duster_iii_extreme_ecog120_4x2_manual",
                "duster_iii_journey_ecog120_4x2_manual",
                "duster_iii_expression_mildhybrid140_4x2_manual",
                "duster_iii_extreme_mildhybrid140_4x2_manual",
                "duster_iii_journey_mildhybrid140_4x2_manual",
            },
            "Duster page-20 exact scalar gap target set differs",
        )
        ensure(not any(row.get("attribute_code") == "injection_type" for row in duster_page20_exact_scalar_gap), "Duster unscoped injection entered the package")
        expected_scalar.update({"src_pl_duster_mini_brochure_20251020": 35})
        expected_total += 35
'''
    if text.count(anchor) != 1:
        raise RuntimeError(f"global receipt anchor count is {text.count(anchor)}")
    checker.write_text(text.replace(anchor, block + anchor), encoding="utf-8", newline="\n")

    test = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    text = test.read_text(encoding="utf-8")
    replacements = [
        ('        "src_pl_duster_mini_brochure_20251020": 244,\n', '        "src_pl_duster_mini_brochure_20251020": 279,\n'),
        ('        self.assertEqual(len(self.scalar), 1314)\n', '        self.assertEqual(len(self.scalar), 1349)\n'),
    ]
    for old, new in replacements:
        if text.count(old) != 1:
            raise RuntimeError(f"global test replacement target count is {text.count(old)}: {old!r}")
        text = text.replace(old, new)
    test.write_text(text, encoding="utf-8", newline="\n")


def refresh_reconciliation_expectations() -> None:
    run(sys.executable, "tools/dkb.py", "pdf-candidate-coverage-reconciliation")
    payload = json.loads(RECONCILIATION_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    counts = {
        key: summary["coverage_status_counts"][key]
        for key in ("already_covered", "ambiguous", "explicit_non_import", "unresolved")
    }
    reconciliation_test = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    pattern = (
        r'(    def test_real_reconciliation_has_expected_candidate_partition\(self\) -> None:\n'
        r'        self\.assertEqual\(self\.payload\["summary"\]\["target_groups"\], 10\)\n)'
        r'        self\.assertEqual\(self\.payload\["summary"\]\["candidate_count"\], \d+\)\n'
        r'        self\.assertEqual\(\n'
        r'            self\.payload\["summary"\]\["coverage_status_counts"\],\n'
        r'            \{[^\n]+\},\n'
        r'        \)\n'
    )
    replacement = (
        r'\1'
        f'        self.assertEqual(self.payload["summary"]["candidate_count"], {summary["candidate_count"]})\n'
        '        self.assertEqual(\n'
        '            self.payload["summary"]["coverage_status_counts"],\n'
        f'            {counts!r},\n'
        '        )\n'
    )
    replace_pattern(reconciliation_test, pattern, replacement)

    sys.path.insert(0, str(ROOT / "tools"))
    import verified_pdf_candidate_residual_gap_prioritization as prioritization

    priority, _ = prioritization.build_from_path(ROOT, prioritization.DEFAULT_RECONCILIATION)
    priority_counts = {
        key: priority["summary"]["coverage_status_counts"][key]
        for key in ("ambiguous", "unresolved")
    }
    priority_test = ROOT / "tests/test_verified_pdf_candidate_residual_gap_prioritization.py"
    priority_pattern = (
        r'(    def test_real_repository_partition_and_highest_priority\(self\) -> None:\n'
        r'        payload, markdown = prioritization\.build_from_path\(\n'
        r'            ROOT, prioritization\.DEFAULT_RECONCILIATION\n'
        r'        \)\n)'
        r'        self\.assertEqual\(payload\["summary"\]\["candidate_count"\], \d+\)\n'
        r'        self\.assertEqual\(\n'
        r'            payload\["summary"\]\["coverage_status_counts"\],\n'
        r'            \{[^\n]+\},\n'
        r'        \)\n'
        r'        self\.assertEqual\(payload\["summary"\]\["package_count"\], \d+\)\n'
    )
    priority_replacement = (
        r'\1'
        f'        self.assertEqual(payload["summary"]["candidate_count"], {priority["summary"]["candidate_count"]})\n'
        '        self.assertEqual(\n'
        '            payload["summary"]["coverage_status_counts"],\n'
        f'            {priority_counts!r},\n'
        '        )\n'
        f'        self.assertEqual(payload["summary"]["package_count"], {priority["summary"]["package_count"]})\n'
    )
    replace_pattern(priority_test, priority_pattern, priority_replacement)


def write_state() -> None:
    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Duster Mini Page 20 Exact Scalar Gap Import"
    state["baseline"].update(
        {
            "tests": 1669,
            "csv_files": 46,
            "rows": 11357,
            "configuration_values": 3498,
            "configuration_import_specs": 138,
            "configuration_value_ranges": 278,
            "configuration_range_import_specs": 22,
            "availability_records": 5770,
            "attributes": 385,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "package_id": "post_residual_duster_mini_page20_exact_scalar_gap_import_001",
        "kind": "configuration_value_import",
        "name": "Duster Mini Page 20 Exact Scalar Gap Import",
        "status": "complete",
        "goal": "Add 35 append-only source-specific Euro 6E bis, particulate-filter, Start & Stop, Eco-mode and gross-vehicle-weight observations across the seven exact manual Duster 4x2 configurations while preserving injection and context boundaries.",
        "manifest_paths": [
            "data/imports/configuration_values/duster-mini-page20-emission-standard-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-particulate-filter-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-start-stop-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-eco-mode-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-gross-vehicle-weight-20251020.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_duster_mini_page20_exact_scalar_gap_import.py",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "tests/test_verified_pdf_candidate_residual_gap_prioritization.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = {
        "package_id": "post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001",
        "kind": "review_closure",
        "name": "Duster Mini Page 20 Exact Scalar Import Closure Review",
        "status": "planned",
        "source_code": SOURCE,
        "source_page": 20,
        "goal": "Verify the 35-row exact scalar receipt, confirm all reconciliation import-ready gaps are closed, preserve injection/context deferrals and return the completed Duster page-20 boundary to global residual-queue selection.",
        "manifest_paths": [
            "data/reporting/duster_mini_page20_exact_scalar_import_closure.json",
            "data/reporting/duster_mini_page20_exact_scalar_import_closure.md",
            "project/reviews/duster-mini-page20-exact-scalar-import-closure-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    write_json(state_path, state)


def verify_receipt() -> None:
    values = rows(MASTER / "configuration_attribute_values.csv")
    selected = sorted([row for row in values if 3464 <= int(row["id"]) <= 3498], key=lambda row: int(row["id"]))
    if len(selected) != 35:
        raise RuntimeError(f"expected 35 rows, found {len(selected)}")
    if [int(row["id"]) for row in selected] != list(range(3464, 3499)):
        raise RuntimeError("import IDs are not contiguous")
    if Counter(row["attribute_code"] for row in selected) != Counter({spec["attribute"]: 7 for spec in SPECS}):
        raise RuntimeError("import attribute distribution differs")
    if {row["configuration_code"] for row in selected} != set(TARGETS):
        raise RuntimeError("import target set differs")
    if any(row["attribute_code"] == "injection_type" for row in selected):
        raise RuntimeError("unscoped injection entered the import")


def main() -> int:
    write_specs()
    write_test()
    patch_global_receipt()
    for spec in SPECS:
        path = ROOT / "data/imports/configuration_values" / spec["filename"]
        run(sys.executable, "tools/dkb.py", "import-configuration-values", "--spec", str(path), "--apply")
        run(sys.executable, "tools/dkb.py", "import-configuration-values", "--spec", str(path), "--verify")
    verify_receipt()
    refresh_reconciliation_expectations()
    write_state()
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--apply")
    run(sys.executable, "tools/dkb.py", "pdf-candidate-coverage-reconciliation", "--verify")
    run(
        sys.executable,
        "-m",
        "unittest",
        "-v",
        "tests.test_duster_mini_page20_exact_scalar_gap_import",
        "tests.test_official_brochure_technical_gap_resolution_closure",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
        "tests.test_verified_pdf_candidate_residual_gap_prioritization",
    )
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
