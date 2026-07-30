#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib
import json
import pprint
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybrid155-system-voltage-20251210.json"
MASTER = ROOT / "data/master"
TARGETS = [
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def validate_targets() -> None:
    active = {
        row["code"]
        for row in rows(MASTER / "configurations.csv")
        if row["status"] == "active"
    }
    if not set(TARGETS) <= active:
        raise RuntimeError("Hybrid 155 target set is not fully active")


def write_spec() -> None:
    write_json(
        SPEC,
        {
            "version": 1,
            "kind": "configuration_attribute_values",
            "id_start": 3322,
            "attribute_code": "hybrid_system_voltage",
            "attribute_contract": {"data_type": "integer", "unit": "V", "status": "active"},
            "observation_date": "2025-12-10",
            "fuel_type_code": "",
            "source_page": 20,
            "source_section": "BATERIA",
            "notes_template": "Source page {page}, section {section}: {source_text}",
            "rows": [
                {
                    "configuration_code": code,
                    "source_code": SOURCE,
                    "value": "280",
                    "source_text": "280 V / 1,4 kWh",
                }
                for code in TARGETS
            ],
        },
    )


TEST_TEXT = r'''from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybrid155-system-voltage-20251210.json"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
BROCHURE_SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
TARGETS = {
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20Hybrid155VoltageConflictObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_preserves_source_and_integer_voltage_contract(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3322)
        self.assertEqual(self.spec["attribute_code"], "hybrid_system_voltage")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "integer", "unit": "V", "status": "active"})
        self.assertEqual(self.spec["source_page"], 20)
        self.assertEqual(self.spec["source_section"], "BATERIA")

    def test_exact_three_hybrid155_targets_are_in_spec_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.spec["rows"]]
        self.assertEqual(len(configurations), 3)
        self.assertEqual(set(configurations), TARGETS)
        self.assertEqual(len(configurations), len(set(configurations)))
        self.assertEqual({row["value"] for row in self.spec["rows"]}, {"280"})
        self.assertEqual({row["source_text"] for row in self.spec["rows"]}, {"280 V / 1,4 kWh"})

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"] == "hybrid_system_voltage"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], [3322, 3323, 3324])
        self.assertEqual({row["value"] for row in selected}, {"280"})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})

    def test_later_price_source_200v_rows_remain_unchanged(self) -> None:
        later = sorted(
            [
                row for row in self.values
                if row["source_code"] == PRICE_SOURCE
                and row["attribute_code"] == "hybrid_system_voltage"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in later], [1475, 1476, 1477])
        self.assertEqual({row["value"] for row in later}, {"200"})
        self.assertEqual({row["observation_date"] for row in later}, {"2026-07-03"})

    def test_both_registered_voltage_observations_coexist(self) -> None:
        selected = [
            row for row in self.values
            if row["attribute_code"] == "hybrid_system_voltage"
            and row["configuration_code"] in TARGETS
            and row["source_code"] in {BROCHURE_SOURCE, PRICE_SOURCE}
        ]
        self.assertEqual(len(selected), 6)
        by_configuration = {}
        for row in selected:
            by_configuration.setdefault(row["configuration_code"], set()).add((row["source_code"], row["value"]))
        expected = {(BROCHURE_SOURCE, "280"), (PRICE_SOURCE, "200")}
        self.assertEqual(set(by_configuration), TARGETS)
        self.assertTrue(all(values == expected for values in by_configuration.values()))

    def test_capacity_context_is_not_imported_by_this_package(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == BROCHURE_SOURCE
            and row["configuration_code"] in TARGETS
            and row["attribute_code"] in {"hybrid_battery_capacity", "hybrid_battery_capacity_source_stated"}
            and row["observation_date"] == "2025-12-10"
        ]
        self.assertEqual(selected, [])

    def test_all_targets_are_active_and_linked_to_source(self) -> None:
        active = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active"
        }
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(TARGETS <= active)
        self.assertTrue(TARGETS <= linked)

    def test_page_text_contains_exact_voltage_cell(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("280 V / 1,4 kWh"), page_text)


if __name__ == "__main__":
    unittest.main()
'''


def write_test() -> None:
    (ROOT / "tests/test_bigster_page20_hybrid155_voltage_conflict_observations.py").write_text(TEST_TEXT, encoding="utf-8", newline="\n")


def patch_coverage_contracts() -> None:
    run(sys.executable, "tools/verified_pdf_candidate_coverage_reconciliation.py")
    report = json.loads((ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json").read_text(encoding="utf-8"))
    summary = report["summary"]
    path = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    text = path.read_text(encoding="utf-8")
    marker = "class CoverageReconciliationRepositoryTests"
    prefix, suffix = text.split(marker, 1)
    suffix = re.sub(r'self\.assertEqual\(self\.payload\["summary"\]\["candidate_count"\], \d+\)', f'self.assertEqual(self.payload["summary"]["candidate_count"], {summary["candidate_count"]})', suffix, count=1)
    literal = pprint.pformat(summary["coverage_status_counts"], sort_dicts=False, width=100)
    suffix = re.sub(
        r'self\.assertEqual\(\n\s*self\.payload\["summary"\]\["coverage_status_counts"\],\n\s*\{.*?\},\n\s*\)',
        'self.assertEqual(\n            self.payload["summary"]["coverage_status_counts"],\n            ' + literal.replace("\n", "\n            ") + ',\n        )',
        suffix,
        count=1,
        flags=re.S,
    )
    path.write_text(prefix + marker + suffix, encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tools"))
    module = importlib.import_module("verified_pdf_candidate_residual_gap_prioritization")
    payload, _ = module.build_from_path(ROOT, module.DEFAULT_RECONCILIATION)
    path = ROOT / "tests/test_verified_pdf_candidate_residual_gap_prioritization.py"
    text = path.read_text(encoding="utf-8")
    marker = "class ResidualGapPrioritizationRepositoryTests"
    prefix, suffix = text.split(marker, 1)
    suffix = re.sub(r'self\.assertEqual\(payload\["summary"\]\["candidate_count"\], \d+\)', f'self.assertEqual(payload["summary"]["candidate_count"], {payload["summary"]["candidate_count"]})', suffix, count=1)
    literal = pprint.pformat(payload["summary"]["coverage_status_counts"], sort_dicts=False, width=100)
    suffix = re.sub(
        r'self\.assertEqual\(\n\s*payload\["summary"\]\["coverage_status_counts"\],\n\s*\{.*?\},\n\s*\)',
        'self.assertEqual(\n            payload["summary"]["coverage_status_counts"],\n            ' + literal.replace("\n", "\n            ") + ',\n        )',
        suffix,
        count=1,
        flags=re.S,
    )
    highest = pprint.pformat(payload["highest_priority_package"], sort_dicts=False, width=100)
    suffix = re.sub(
        r'self\.assertEqual\(\n\s*payload\["highest_priority_package"\],\n\s*\{.*?\},\n\s*\)\n\s*assigned =',
        'self.assertEqual(\n            payload["highest_priority_package"],\n            ' + highest.replace("\n", "\n            ") + ',\n        )\n        assigned =',
        suffix,
        count=1,
        flags=re.S,
    )
    path.write_text(prefix + marker + suffix, encoding="utf-8", newline="\n")


def patch_closure_contracts() -> None:
    verifier = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    text = verifier.read_text(encoding="utf-8")
    marker = '    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'
    if "Bigster Hybrid 155 voltage conflict-observation receipt differs" not in text:
        block = '''    voltage_conflicts = [\n        row\n        for row in scalar\n        if row.get("source_code") == "src_pl_bigster_brochure_20251210"\n        and row.get("attribute_code") == "hybrid_system_voltage"\n        and row.get("value") == "280"\n    ]\n    if voltage_conflicts:\n        ensure(len(voltage_conflicts) == 3, "Bigster Hybrid 155 voltage conflict-observation receipt differs")\n        ensure({row.get("configuration_code", "") for row in voltage_conflicts} == {\n            "bigster_expression_hybrid155_4x2_automatic",\n            "bigster_extreme_hybrid155_4x2_automatic",\n            "bigster_journey_hybrid155_4x2_automatic",\n        }, "Bigster Hybrid 155 voltage targets differ")\n        expected_scalar.update({"src_pl_bigster_brochure_20251210": 3})\n        expected_total += 3\n'''
        if text.count(marker) != 1:
            raise RuntimeError("closure verifier insertion marker differs")
        text = text.replace(marker, block + marker)
        verifier.write_text(text, encoding="utf-8", newline="\n")

    test_path = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    text = test_path.read_text(encoding="utf-8")
    current_marker = "EXPECTED_CURRENT_SCALAR = Counter("
    prefix, suffix = text.split(current_marker, 1)
    suffix = re.sub(r'("src_pl_bigster_brochure_20251210": )\d+', r'\g<1>237', suffix, count=1)
    text = prefix + current_marker + suffix
    text = text.replace("self.assertEqual(len(self.scalar), 1172)", "self.assertEqual(len(self.scalar), 1175)")
    test_path.write_text(text, encoding="utf-8", newline="\n")


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Bigster Page 20 Hybrid 155 Voltage Conflict Observation Import"
    state["current_package"] = {
        "package_id": "post_residual_bigster_page20_hybrid155_voltage_conflict_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Bigster Page 20 Hybrid 155 Voltage Conflict Observation Import",
        "status": "complete",
        "goal": "Add hybrid_system_voltage=280 V as a 2025-12-10 brochure observation for the three Hybrid 155 configurations while retaining and testing the later 200 V price-source observations and without importing the adjacent 1.4 kWh capacity context.",
        "manifest_paths": [
            "data/imports/configuration_values/bigster-page20-hybrid155-system-voltage-20251210.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_bigster_page20_hybrid155_voltage_conflict_observations.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "tests/test_verified_pdf_candidate_residual_gap_prioritization.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
        ],
    }
    state["next_package"] = {
        "package_id": "post_residual_bigster_page20_battery_capacity_conflict_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Bigster Page 20 Battery Capacity Conflict Observation Import",
        "status": "planned",
        "goal": "Add hybrid_battery_capacity_source_stated=0.84 kWh as a 2025-12-10 brochure observation for the eleven 48 V Bigster configurations while retaining and testing the later 0.839 kWh price-source observations and without changing the Hybrid 155 1.4 kWh context.",
        "manifest_paths": [
            "data/imports/configuration_values/bigster-page20-hybrid-battery-capacity-source-stated-20251210.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_bigster_page20_battery_capacity_conflict_observations.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "tests/test_verified_pdf_candidate_residual_gap_prioritization.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
        ],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")


def restore_quality() -> None:
    completed = subprocess.run(
        ["git", "show", "origin/main:.github/workflows/quality.yml"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    (ROOT / ".github/workflows/quality.yml").write_text(completed.stdout, encoding="utf-8", newline="\n")


def verify() -> None:
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC.relative_to(ROOT)), "--verify")
    run(
        sys.executable,
        "-m",
        "unittest",
        "tests.test_bigster_page20_hybrid155_voltage_conflict_observations",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
        "tests.test_verified_pdf_candidate_residual_gap_prioritization",
        "tests.test_official_brochure_technical_gap_resolution_closure",
        "tests.test_data_product_release",
        "tests.project_state_contract",
    )
    run(sys.executable, "tools/dkb.py", "project-state", "--check")


def main() -> None:
    if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise RuntimeError("Bigster brochure SHA differs")
    validate_targets()
    write_spec()
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC.relative_to(ROOT)), "--apply")
    write_test()
    patch_coverage_contracts()
    patch_closure_contracts()
    update_state()
    restore_quality()
    verify()


if __name__ == "__main__":
    main()
