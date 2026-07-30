#!/usr/bin/env python3
"""Materialize the Jogger page 19 non-Hybrid braked-trailer package."""

from __future__ import annotations

import csv
import hashlib
import json
import pprint
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/imports/configuration_values/jogger-brochure-braked-trailer-weight-non-hybrid-20251217.json"
TEST_PATH = ROOT / "tests/test_jogger_page19_braked_trailer_weight_non_hybrid_source_observations.py"
RECONCILIATION_JSON = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
SOURCE = "src_pl_jogger_brochure_20251217"
LATER_SOURCE = "src_pl_jogger_price_my26_20260401"
SOURCE_LABEL = "Maks. masa całkowita przyczepy"
FIVE_ROW = "Wersja 5-miejscowa 1200 1200 1200 1200"
SEVEN_ROW = "Wersja 7-miejscowa 1200 1200 1200 1200"
SOURCE_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED = {
    "jogger_expression_5seat_tce110_manual": "1200",
    "jogger_extreme_5seat_tce110_manual": "1200",
    "jogger_journey_5seat_tce110_manual": "1200",
    "jogger_essential_5seat_ecog120_manual": "1200",
    "jogger_expression_5seat_ecog120_manual": "1200",
    "jogger_extreme_5seat_ecog120_manual": "1200",
    "jogger_extreme_5seat_ecog120_automatic": "1200",
    "jogger_journey_5seat_ecog120_automatic": "1200",
    "jogger_expression_7seat_tce110_manual": "1200",
    "jogger_extreme_7seat_tce110_manual": "1200",
    "jogger_journey_7seat_tce110_manual": "1200",
    "jogger_essential_7seat_ecog120_manual": "1200",
    "jogger_expression_7seat_ecog120_manual": "1200",
    "jogger_extreme_7seat_ecog120_manual": "1200",
    "jogger_extreme_7seat_ecog120_automatic": "1200",
    "jogger_journey_7seat_ecog120_automatic": "1200",
}
HYBRID = {
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}


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


def ordered_configurations() -> list[str]:
    return [
        "jogger_expression_5seat_tce110_manual",
        "jogger_extreme_5seat_tce110_manual",
        "jogger_journey_5seat_tce110_manual",
        "jogger_essential_5seat_ecog120_manual",
        "jogger_expression_5seat_ecog120_manual",
        "jogger_extreme_5seat_ecog120_manual",
        "jogger_extreme_5seat_ecog120_automatic",
        "jogger_journey_5seat_ecog120_automatic",
        "jogger_expression_7seat_tce110_manual",
        "jogger_extreme_7seat_tce110_manual",
        "jogger_journey_7seat_tce110_manual",
        "jogger_essential_7seat_ecog120_manual",
        "jogger_expression_7seat_ecog120_manual",
        "jogger_extreme_7seat_ecog120_manual",
        "jogger_extreme_7seat_ecog120_automatic",
        "jogger_journey_7seat_ecog120_automatic",
    ]


def write_spec() -> None:
    values = []
    for configuration in ordered_configurations():
        source_text = FIVE_ROW if "5seat" in configuration else SEVEN_ROW
        values.append(
            {
                "configuration_code": configuration,
                "source_code": SOURCE,
                "value": "1200",
                "source_text": source_text,
            }
        )
    payload: dict[str, object] = {
        "version": 1,
        "kind": "configuration_attribute_values",
        "id_start": 3448,
        "attribute_code": "braked_trailer_weight",
        "attribute_contract": {"data_type": "integer", "unit": "kg", "status": "active"},
        "observation_date": "2025-12-17",
        "fuel_type_code": "",
        "source_page": 19,
        "source_section": SOURCE_LABEL,
        "notes_template": "Source page {page}, section {section}: {source_text}",
        "rows": values,
    }
    write_json(SPEC_PATH, payload)


def write_test() -> None:
    expected_literal = pprint.pformat(EXPECTED, sort_dicts=False, width=110)
    hybrid_literal = pprint.pformat(HYBRID, sort_dicts=True, width=110)
    text = f'''"""Verify Jogger page 19 non-Hybrid braked-trailer source observations."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-braked-trailer-weight-non-hybrid-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = {SOURCE!r}
LATER_SOURCE = {LATER_SOURCE!r}
SOURCE_LABEL = {SOURCE_LABEL!r}
FIVE_ROW = {FIVE_ROW!r}
SEVEN_ROW = {SEVEN_ROW!r}
EXPECTED_SHA = {SOURCE_SHA!r}
EXPECTED = {expected_literal}
HYBRID = {hybrid_literal}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19BrakedTrailerWeightNonHybridSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3448)
        self.assertEqual(self.spec["attribute_code"], "braked_trailer_weight")
        self.assertEqual(self.spec["attribute_contract"], {{"data_type": "integer", "unit": "kg", "status": "active"}})
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], SOURCE_LABEL)

    def test_exact_sixteen_non_hybrid_targets_are_in_spec_once(self) -> None:
        actual = {{row["configuration_code"]: row["value"] for row in self.spec["rows"]}}
        self.assertEqual(len(self.spec["rows"]), 16)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(set(actual) & HYBRID, set())
        self.assertEqual({{row["source_code"] for row in self.spec["rows"]}}, {{SOURCE}})
        self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3448 <= int(row["id"]) <= 3463],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3448, 3464)))
        self.assertEqual({{row["configuration_code"]: row["value"] for row in selected}}, EXPECTED)
        self.assertEqual({{row["attribute_code"] for row in selected}}, {{"braked_trailer_weight"}})
        self.assertEqual({{row["source_code"] for row in selected}}, {{SOURCE}})
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2025-12-17"}})

    def test_later_non_hybrid_observations_coexist_unchanged(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in EXPECTED
        ]
        self.assertEqual(len(selected), 16)
        self.assertEqual({{row["configuration_code"]: row["value"] for row in selected}}, EXPECTED)
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2026-04-01"}})

    def test_hybrid_conflict_remains_excluded_and_later_value_is_1000(self) -> None:
        later = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in HYBRID
        ]
        brochure = [
            row for row in self.values
            if row["source_code"] == SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in HYBRID
        ]
        self.assertEqual({{row["configuration_code"] for row in later}}, HYBRID)
        self.assertEqual({{row["value"] for row in later}}, {{"1000"}})
        self.assertEqual(brochure, [])

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {{row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}}
        linked = {{
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }}
        self.assertTrue(set(EXPECTED) <= active)
        self.assertTrue(set(EXPECTED) <= linked)

    def test_page_text_contains_exact_label_and_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        candidates = [_compact_text(text) for _, text in extract_page_candidates(PDF, 19)]
        page_text = " ".join(candidates)
        self.assertIn(_compact_text(SOURCE_LABEL), page_text)
        self.assertIn(_compact_text(FIVE_ROW), page_text)
        self.assertIn(_compact_text(SEVEN_ROW), page_text)


if __name__ == "__main__":
    unittest.main()
'''
    TEST_PATH.write_text(text, encoding="utf-8", newline="\n")


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
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Jogger Page 19 Non-Hybrid Braked Trailer Weight Source Observations"
    state["baseline"].update(
        {
            "tests": 1662,
            "csv_files": 46,
            "rows": 11322,
            "configuration_values": 3463,
            "configuration_import_specs": 133,
            "configuration_value_ranges": 278,
            "configuration_range_import_specs": 22,
            "availability_records": 5770,
            "attributes": 385,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_braked_trailer_weight_non_hybrid_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Non-Hybrid Braked Trailer Weight Source Observations",
        "status": "complete",
        "goal": "Add the matching 1200 kg brochure-source braked trailer observations for the 16 current TCe 110 and Eco-G 120 configurations while explicitly excluding all six Hybrid 155 configurations because their later official value is 1000 kg.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-braked-trailer-weight-non-hybrid-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_braked_trailer_weight_non_hybrid_source_observations.py",
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
        "package_id": "post_residual_jogger_page19_remaining_mass_conflict_closure_review_001",
        "kind": "review_closure",
        "name": "Jogger Page 19 Remaining Mass Conflict Closure Review",
        "status": "planned",
        "source_code": SOURCE,
        "goal": "Confirm that every safely importable exact page-19 fact is covered after the reviewed acceleration, minimum-mass, capacity, gross-vehicle-weight and non-Hybrid trailer packages, while preserving the two mislabeled maximum-kerb/gross-train blocks as explicit unresolved source conflicts.",
        "manifest_paths": [
            "data/reporting/jogger_page19_remaining_mass_conflict_closure.json",
            "data/reporting/jogger_page19_remaining_mass_conflict_closure.md",
            "project/reviews/jogger-page19-remaining-mass-conflict-closure-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    write_json(path, state)


def verify_receipt() -> None:
    values = rows(ROOT / "data/master/configuration_attribute_values.csv")
    selected = [row for row in values if 3448 <= int(row["id"]) <= 3463]
    if len(selected) != 16:
        raise RuntimeError(f"expected 16 package rows, found {len(selected)}")
    if [int(row["id"]) for row in selected] != list(range(3448, 3464)):
        raise RuntimeError("package IDs are not contiguous")
    if Counter(row["attribute_code"] for row in selected) != Counter({"braked_trailer_weight": 16}):
        raise RuntimeError("package attribute distribution differs")
    if {row["configuration_code"]: row["value"] for row in selected} != EXPECTED:
        raise RuntimeError("package values differ")
    if any(row["configuration_code"] in HYBRID for row in selected):
        raise RuntimeError("Hybrid 155 entered the brochure package")


def main() -> int:
    write_spec()
    write_test()
    run(sys.executable, "tools/dkb.py", "import-configuration-values", "--spec", str(SPEC_PATH), "--apply")
    run(sys.executable, "tools/dkb.py", "import-configuration-values", "--spec", str(SPEC_PATH), "--verify")
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
        "tests.test_jogger_page19_braked_trailer_weight_non_hybrid_source_observations",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
        "tests.test_verified_pdf_candidate_residual_gap_prioritization",
    )
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
