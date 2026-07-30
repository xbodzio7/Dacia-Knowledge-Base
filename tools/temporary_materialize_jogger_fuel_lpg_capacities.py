#!/usr/bin/env python3
"""Materialize the temporary Jogger page 19 fuel/LPG capacity package."""

from __future__ import annotations

import json
import pprint
import re
import subprocess
import sys
import textwrap
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_DIR = ROOT / "data/imports/configuration_values"
MASTER_VALUES = ROOT / "data/master/configuration_attribute_values.csv"
TEST_PATH = ROOT / "tests/test_jogger_page19_fuel_lpg_capacity_source_observations.py"
SOURCE = "src_pl_jogger_brochure_20251217"
LATER_SOURCE = "src_pl_jogger_price_my26_20260401"
SOURCE_ROW = "Pojemność zbiornika paliwa (l) 50 50/40(3) 50 50/40(3) 50 50"
FOOTNOTE = "(3) Poj. całkowita / poj. użyteczna."

ALL_CONFIGURATIONS = [
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
]
ECOG_CONFIGURATIONS = [code for code in ALL_CONFIGURATIONS if "_ecog120_" in code]
NON_ECOG_CONFIGURATIONS = [code for code in ALL_CONFIGURATIONS if code not in ECOG_CONFIGURATIONS]

SPECIFICATIONS = [
    (
        "jogger-brochure-fuel-tank-capacity-20251217.json",
        3384,
        "fuel_tank_capacity",
        {"data_type": "decimal", "unit": "L", "status": "active"},
        [
            {
                "configuration_code": code,
                "source_code": SOURCE,
                "fuel_type_code": "petrol" if code in ECOG_CONFIGURATIONS else "",
                "value": "50",
                "source_text": SOURCE_ROW,
            }
            for code in ALL_CONFIGURATIONS
        ],
    ),
    (
        "jogger-brochure-lpg-vessel-total-capacity-20251217.json",
        3406,
        "lpg_vessel_capacity_total",
        {"data_type": "decimal", "unit": "L", "status": "active"},
        [
            {
                "configuration_code": code,
                "source_code": SOURCE,
                "fuel_type_code": "lpg",
                "value": "50",
                "source_text": SOURCE_ROW,
            }
            for code in ECOG_CONFIGURATIONS
        ],
    ),
    (
        "jogger-brochure-lpg-vessel-filling-capacity-20251217.json",
        3416,
        "lpg_vessel_filling_capacity",
        {"data_type": "decimal", "unit": "L", "status": "active"},
        [
            {
                "configuration_code": code,
                "source_code": SOURCE,
                "fuel_type_code": "lpg",
                "value": "40",
                "source_text": SOURCE_ROW,
            }
            for code in ECOG_CONFIGURATIONS
        ],
    ),
]


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: replacement target count for {old!r} is {count}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def write_specs() -> list[Path]:
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, id_start, attribute_code, contract, rows in SPECIFICATIONS:
        payload = {
            "version": 1,
            "kind": "configuration_attribute_values",
            "id_start": id_start,
            "attribute_code": attribute_code,
            "attribute_contract": contract,
            "observation_date": "2025-12-17",
            "fuel_type_code": "",
            "source_page": 19,
            "source_section": "Pojemność zbiornika paliwa (l)",
            "notes_template": "Source page {page}, section {section}: {source_text}",
            "rows": rows,
        }
        path = IMPORT_DIR / filename
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        paths.append(path)
    return paths


def write_test() -> None:
    all_literal = pprint.pformat(ALL_CONFIGURATIONS, width=110)
    ecog_literal = pprint.pformat(ECOG_CONFIGURATIONS, width=110)
    non_ecog_literal = pprint.pformat(NON_ECOG_CONFIGURATIONS, width=110)
    text = f'''"""Verify Jogger page 19 fuel and LPG capacity source observations."""

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
IMPORT_DIR = ROOT / "data/imports/configuration_values"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = "{SOURCE}"
LATER_SOURCE = "{LATER_SOURCE}"
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
SOURCE_ROW = {SOURCE_ROW!r}
FOOTNOTE = {FOOTNOTE!r}
ALL_CONFIGURATIONS = {all_literal}
ECOG_CONFIGURATIONS = {ecog_literal}
NON_ECOG_CONFIGURATIONS = {non_ecog_literal}
SPEC_PATHS = [
    IMPORT_DIR / "jogger-brochure-fuel-tank-capacity-20251217.json",
    IMPORT_DIR / "jogger-brochure-lpg-vessel-total-capacity-20251217.json",
    IMPORT_DIR / "jogger-brochure-lpg-vessel-filling-capacity-20251217.json",
]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19FuelLpgCapacitySourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = [json.loads(path.read_text(encoding="utf-8")) for path in SPEC_PATHS]
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_specs_are_strict_source_bounded_and_contiguous(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual([spec["id_start"] for spec in self.specs], [3384, 3406, 3416])
        self.assertEqual(
            [spec["attribute_code"] for spec in self.specs],
            ["fuel_tank_capacity", "lpg_vessel_capacity_total", "lpg_vessel_filling_capacity"],
        )
        self.assertEqual([len(spec["rows"]) for spec in self.specs], [22, 10, 10])
        self.assertTrue(all(spec["observation_date"] == "2025-12-17" for spec in self.specs))
        self.assertTrue(all(spec["source_page"] == 19 for spec in self.specs))
        self.assertTrue(all(spec["source_section"] == "Pojemność zbiornika paliwa (l)" for spec in self.specs))

    def test_fuel_tank_targets_preserve_petrol_context(self) -> None:
        spec = self.specs[0]
        actual = {{row["configuration_code"]: row.get("fuel_type_code", "") for row in spec["rows"]}}
        self.assertEqual(set(actual), set(ALL_CONFIGURATIONS))
        self.assertEqual({{code for code, fuel in actual.items() if fuel == "petrol"}}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({{code for code, fuel in actual.items() if fuel == ""}}, set(NON_ECOG_CONFIGURATIONS))
        self.assertEqual({{row["value"] for row in spec["rows"]}}, {{"50"}})

    def test_lpg_total_and_filling_targets_are_separate(self) -> None:
        total, filling = self.specs[1], self.specs[2]
        self.assertEqual({{row["configuration_code"] for row in total["rows"]}}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({{row["configuration_code"] for row in filling["rows"]}}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({{row.get("fuel_type_code", "") for row in total["rows"] + filling["rows"]}}, {{"lpg"}})
        self.assertEqual({{row["value"] for row in total["rows"]}}, {{"50"}})
        self.assertEqual({{row["value"] for row in filling["rows"]}}, {{"40"}})

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3384 <= int(row["id"]) <= 3425],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3384, 3426)))
        self.assertEqual(
            Counter((row["attribute_code"], row["fuel_type_code"], row["value"]) for row in selected),
            Counter({{
                ("fuel_tank_capacity", "petrol", "50"): 10,
                ("fuel_tank_capacity", "", "50"): 12,
                ("lpg_vessel_capacity_total", "lpg", "50"): 10,
                ("lpg_vessel_filling_capacity", "lpg", "40"): 10,
            }}),
        )
        self.assertEqual({{row["source_code"] for row in selected}}, {{SOURCE}})
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2025-12-17"}})

    def test_later_official_observations_coexist_unchanged(self) -> None:
        selected = [
            row
            for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["configuration_code"] in ALL_CONFIGURATIONS
            and row["attribute_code"] in {{
                "fuel_tank_capacity",
                "lpg_vessel_capacity_total",
                "lpg_vessel_filling_capacity",
            }}
        ]
        self.assertEqual(len(selected), 42)
        self.assertEqual(
            Counter((row["attribute_code"], row["fuel_type_code"], row["value"]) for row in selected),
            Counter({{
                ("fuel_tank_capacity", "petrol", "50"): 10,
                ("fuel_tank_capacity", "", "50"): 12,
                ("lpg_vessel_capacity_total", "lpg", "50"): 10,
                ("lpg_vessel_filling_capacity", "lpg", "40"): 10,
            }}),
        )
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2026-04-01"}})

    def test_source_page_contains_row_and_capacity_footnote(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 19))
        self.assertIn(_compact_text(SOURCE_ROW), page_text)
        self.assertIn(_compact_text(FOOTNOTE), page_text)

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {{row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}}
        linked = {{
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }}
        self.assertTrue(set(ALL_CONFIGURATIONS) <= active)
        self.assertTrue(set(ALL_CONFIGURATIONS) <= linked)

    def test_capacity_semantics_are_not_collapsed(self) -> None:
        selected = [row for row in self.values if 3384 <= int(row["id"]) <= 3425]
        self.assertEqual(
            {{row["attribute_code"] for row in selected}},
            {{"fuel_tank_capacity", "lpg_vessel_capacity_total", "lpg_vessel_filling_capacity"}},
        )
        self.assertFalse(any(row["attribute_code"] == "fuel_tank_capacity" and row["fuel_type_code"] == "lpg" for row in selected))


if __name__ == "__main__":
    unittest.main()
'''
    TEST_PATH.write_text(text, encoding="utf-8", newline="\n")


def patch_global_contracts() -> None:
    verifier = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    old = '    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'
    block = '''jogger_fuel_lpg_capacities = [
        row
        for row in scalar
        if row.get("source_code") == "src_pl_jogger_brochure_20251217"
        and 3384 <= int(row.get("id", "0")) <= 3425
    ]
    if jogger_fuel_lpg_capacities:
        ensure(len(jogger_fuel_lpg_capacities) == 42, "Jogger fuel/LPG capacity source-observation receipt differs")
        ensure(
            [int(row["id"]) for row in jogger_fuel_lpg_capacities] == list(range(3384, 3426)),
            "Jogger fuel/LPG capacity source-observation IDs differ",
        )
        ensure(
            Counter((row.get("attribute_code", ""), row.get("fuel_type_code", ""), row.get("value", "")) for row in jogger_fuel_lpg_capacities)
            == Counter({
                ("fuel_tank_capacity", "petrol", "50"): 10,
                ("fuel_tank_capacity", "", "50"): 12,
                ("lpg_vessel_capacity_total", "lpg", "50"): 10,
                ("lpg_vessel_filling_capacity", "lpg", "40"): 10,
            }),
            "Jogger fuel/LPG capacity source-observation semantics differ",
        )
        expected_scalar.update({"src_pl_jogger_brochure_20251217": 42})
        expected_total += 42
    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")
    '''
    block_lines = block.splitlines()
    replacement = (
        "    " + block_lines[0] + "\n"
        + textwrap.indent(textwrap.dedent("\n".join(block_lines[1:])), "    ")
        + "\n"
    )
    replace_once(verifier, old, replacement)

    closure_test = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    replace_once(
        closure_test,
        '        "src_pl_jogger_brochure_20251217": 538,\n',
        '        "src_pl_jogger_brochure_20251217": 580,\n',
    )
    replace_once(
        closure_test,
        '        self.assertEqual(len(self.scalar), 1234)\n',
        '        self.assertEqual(len(self.scalar), 1276)\n',
    )


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Jogger Page 19 Fuel and LPG Capacity Source Observations"
    state["baseline"].update(
        {
            "tests": 1648,
            "csv_files": 46,
            "rows": 11284,
            "configuration_values": 3425,
            "configuration_import_specs": 131,
            "configuration_value_ranges": 278,
            "configuration_range_import_specs": 22,
            "availability_records": 5770,
            "attributes": 385,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_fuel_lpg_capacity_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Fuel and LPG Capacity Source Observations",
        "status": "complete",
        "goal": "Preserve 22 source-specific 50 L petrol-tank observations and separate 50 L total plus 40 L usable/filling LPG observations for the ten current Eco-G 120 configurations without collapsing capacity semantics.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-fuel-tank-capacity-20251217.json",
            "data/imports/configuration_values/jogger-brochure-lpg-vessel-total-capacity-20251217.json",
            "data/imports/configuration_values/jogger-brochure-lpg-vessel-filling-capacity-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_fuel_lpg_capacity_source_observations.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "tests/test_verified_pdf_candidate_residual_gap_prioritization.py",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = {
        "package_id": "post_residual_jogger_page19_source_observation_import_closure_001",
        "kind": "review",
        "name": "Jogger Page 19 Source Observation Import Closure",
        "status": "planned",
        "source_code": SOURCE,
        "goal": "Reconcile the completed acceleration, minimum-kerb-weight and fuel/LPG-capacity source-observation imports against the page 19 review, verify whether any safe exact import remains, and preserve all unresolved source conflicts and context-model requirements without changing master data.",
        "manifest_paths": [
            "data/reporting/jogger_page19_source_observation_import_closure.json",
            "data/reporting/jogger_page19_source_observation_import_closure.md",
            "project/reviews/jogger-page19-source-observation-import-closure-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def update_generated_contract_tests() -> None:
    artifact_path = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    status_counts = artifact["summary"]["coverage_status_counts"]

    coverage_test = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    text = coverage_test.read_text(encoding="utf-8")
    pattern = r"(?m)^            \{'already_covered': \d+, 'ambiguous': \d+, 'explicit_non_import': \d+, 'unresolved': \d+\},$"
    replacement = "            " + repr(status_counts) + ","
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"coverage-count replacement count is {count}")
    coverage_test.write_text(updated, encoding="utf-8", newline="\n")

    priority_test = ROOT / "tests/test_verified_pdf_candidate_residual_gap_prioritization.py"
    text = priority_test.read_text(encoding="utf-8")
    pattern = r"(?m)^            \{'ambiguous': \d+, 'unresolved': \d+\},$"
    residual_counts = {
        "ambiguous": status_counts["ambiguous"],
        "unresolved": status_counts["unresolved"],
    }
    updated, count = re.subn(pattern, "            " + repr(residual_counts) + ",", text, count=1)
    if count != 1:
        raise RuntimeError(f"priority-count replacement count is {count}")
    priority_test.write_text(updated, encoding="utf-8", newline="\n")


def main() -> int:
    spec_paths = write_specs()
    write_test()
    for path in spec_paths:
        relative = str(path.relative_to(ROOT))
        run(sys.executable, "tools/import_configuration_values.py", "--spec", relative, "--apply")
        run(sys.executable, "tools/import_configuration_values.py", "--spec", relative, "--verify")
    patch_global_contracts()
    update_state()
    run(sys.executable, "tools/verified_pdf_candidate_coverage_reconciliation.py")
    update_generated_contract_tests()
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--apply")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py", "--check")
    for path in spec_paths:
        run(
            sys.executable,
            "tools/import_configuration_values.py",
            "--spec",
            str(path.relative_to(ROOT)),
            "--verify",
        )
    run(
        sys.executable,
        "-m",
        "unittest",
        "-v",
        "tests.test_jogger_page19_fuel_lpg_capacity_source_observations",
        "tests.test_official_brochure_technical_gap_resolution_closure",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
        "tests.test_verified_pdf_candidate_residual_gap_prioritization",
    )
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q")
    print("PASS: Jogger fuel/LPG capacity package materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
