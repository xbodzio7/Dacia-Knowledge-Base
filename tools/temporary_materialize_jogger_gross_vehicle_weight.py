#!/usr/bin/env python3
"""Materialize the temporary Jogger page 19 gross-vehicle-weight package."""

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
SPEC_PATH = ROOT / "data/imports/configuration_values/jogger-brochure-gross-vehicle-weight-20251217.json"
TEST_PATH = ROOT / "tests/test_jogger_page19_gross_vehicle_weight_source_observations.py"
SOURCE = "src_pl_jogger_brochure_20251217"
LATER_SOURCE = "src_pl_jogger_price_my26_20260401"
SOURCE_LABEL = "Dopuszczalna masa całkowita (DMC)"
FIVE_ROW = "Wersja 5-miejscowa 1685 1765 1785 1830"
SEVEN_ROW = "Wersja 7-miejscowa 1855 1940 1960 2000"
EXPECTED = {
    "jogger_expression_5seat_tce110_manual": "1685",
    "jogger_extreme_5seat_tce110_manual": "1685",
    "jogger_journey_5seat_tce110_manual": "1685",
    "jogger_essential_5seat_ecog120_manual": "1765",
    "jogger_expression_5seat_ecog120_manual": "1765",
    "jogger_extreme_5seat_ecog120_manual": "1765",
    "jogger_extreme_5seat_ecog120_automatic": "1785",
    "jogger_journey_5seat_ecog120_automatic": "1785",
    "jogger_expression_5seat_hybrid155_automatic": "1830",
    "jogger_extreme_5seat_hybrid155_automatic": "1830",
    "jogger_journey_5seat_hybrid155_automatic": "1830",
    "jogger_expression_7seat_tce110_manual": "1855",
    "jogger_extreme_7seat_tce110_manual": "1855",
    "jogger_journey_7seat_tce110_manual": "1855",
    "jogger_essential_7seat_ecog120_manual": "1940",
    "jogger_expression_7seat_ecog120_manual": "1940",
    "jogger_extreme_7seat_ecog120_manual": "1940",
    "jogger_extreme_7seat_ecog120_automatic": "1960",
    "jogger_journey_7seat_ecog120_automatic": "1960",
    "jogger_expression_7seat_hybrid155_automatic": "2000",
    "jogger_extreme_7seat_hybrid155_automatic": "2000",
    "jogger_journey_7seat_hybrid155_automatic": "2000",
}


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: replacement target count for {old!r} is {count}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def write_spec() -> None:
    rows = []
    for configuration, value in EXPECTED.items():
        rows.append(
            {
                "configuration_code": configuration,
                "source_code": SOURCE,
                "value": value,
                "source_text": FIVE_ROW if "_5seat_" in configuration else SEVEN_ROW,
            }
        )
    payload = {
        "version": 1,
        "kind": "configuration_attribute_values",
        "id_start": 3426,
        "attribute_code": "gross_vehicle_weight",
        "attribute_contract": {"data_type": "integer", "unit": "kg", "status": "active"},
        "observation_date": "2025-12-17",
        "fuel_type_code": "",
        "source_page": 19,
        "source_section": SOURCE_LABEL,
        "notes_template": "Source page {page}, section {section}: {source_text}",
        "rows": rows,
    }
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_test() -> None:
    expected_literal = pprint.pformat(EXPECTED, sort_dicts=False, width=110)
    text = f'''"""Verify Jogger page 19 gross-vehicle-weight source observations."""

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
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-gross-vehicle-weight-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = {SOURCE!r}
LATER_SOURCE = {LATER_SOURCE!r}
SOURCE_LABEL = {SOURCE_LABEL!r}
FIVE_ROW = {FIVE_ROW!r}
SEVEN_ROW = {SEVEN_ROW!r}
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED = {expected_literal}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19GrossVehicleWeightSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3426)
        self.assertEqual(self.spec["attribute_code"], "gross_vehicle_weight")
        self.assertEqual(self.spec["attribute_contract"], {{"data_type": "integer", "unit": "kg", "status": "active"}})
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], SOURCE_LABEL)

    def test_exact_twenty_two_targets_are_in_spec_once(self) -> None:
        actual = {{row["configuration_code"]: row["value"] for row in self.spec["rows"]}}
        self.assertEqual(len(self.spec["rows"]), 22)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(actual), len(self.spec["rows"]))
        self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted([row for row in self.values if 3426 <= int(row["id"]) <= 3447], key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in selected], list(range(3426, 3448)))
        self.assertEqual({{row["configuration_code"]: row["value"] for row in selected}}, EXPECTED)
        self.assertEqual({{row["attribute_code"] for row in selected}}, {{"gross_vehicle_weight"}})
        self.assertEqual({{row["source_code"] for row in selected}}, {{SOURCE}})
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2025-12-17"}})

    def test_later_official_observations_coexist_unchanged(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "gross_vehicle_weight"
            and row["configuration_code"] in EXPECTED
        ]
        self.assertEqual(len(selected), 22)
        self.assertEqual({{row["configuration_code"]: row["value"] for row in selected}}, EXPECTED)
        self.assertEqual({{row["observation_date"] for row in selected}}, {{"2026-04-01"}})

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {{row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}}
        linked = {{
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }}
        self.assertTrue(set(EXPECTED) <= active)
        self.assertTrue(set(EXPECTED) <= linked)

    def test_page_text_contains_exact_label_and_target_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        candidates = [_compact_text(text) for _, text in extract_page_candidates(PDF, 19)]
        page_text = " ".join(candidates)
        self.assertGreaterEqual(page_text.count(_compact_text(SOURCE_LABEL)), 3)
        self.assertIn(_compact_text(FIVE_ROW), page_text)
        self.assertIn(_compact_text(SEVEN_ROW), page_text)

    def test_adjacent_mislabeled_mass_blocks_are_not_imported(self) -> None:
        selected = [row for row in self.values if 3426 <= int(row["id"]) <= 3447]
        self.assertEqual(Counter(row["attribute_code"] for row in selected), Counter({{"gross_vehicle_weight": 22}}))
        encoded = json.dumps(self.spec, ensure_ascii=False)
        self.assertNotIn("maximum_kerb_weight", encoded)
        self.assertNotIn("gross_train_weight", encoded)


if __name__ == "__main__":
    unittest.main()
'''
    TEST_PATH.write_text(text, encoding="utf-8", newline="\n")


def patch_ambiguity_boundary() -> None:
    checker = ROOT / "tools/import_jogger_chassis_20260726.py"
    replace_once(
        checker,
        '{"maximum_kerb_weight", "gross_vehicle_weight", "gross_train_weight"}',
        '{"maximum_kerb_weight", "gross_train_weight"}',
    )
    test = ROOT / "tests/test_jogger_chassis_20260726.py"
    replace_once(
        test,
        '                "maximum_kerb_weight",\n                "gross_vehicle_weight",\n                "gross_train_weight",\n',
        '                "maximum_kerb_weight",\n                "gross_train_weight",\n',
    )


def patch_global_contracts() -> None:
    verifier = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    old = '    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'
    block = '''jogger_gross_vehicle_weight = [
        row
        for row in scalar
        if row.get("source_code") == "src_pl_jogger_brochure_20251217"
        and row.get("attribute_code") == "gross_vehicle_weight"
        and 3426 <= int(row.get("id", "0")) <= 3447
    ]
    if jogger_gross_vehicle_weight:
        ensure(len(jogger_gross_vehicle_weight) == 22, "Jogger gross-vehicle-weight source-observation receipt differs")
        ensure([int(row["id"]) for row in jogger_gross_vehicle_weight] == list(range(3426, 3448)), "Jogger gross-vehicle-weight source-observation IDs differ")
        ensure(
            Counter(row.get("value", "") for row in jogger_gross_vehicle_weight)
            == Counter({"1685": 3, "1765": 3, "1785": 2, "1830": 3, "1855": 3, "1940": 3, "1960": 2, "2000": 3}),
            "Jogger gross-vehicle-weight source-observation values differ",
        )
        expected_scalar.update({"src_pl_jogger_brochure_20251217": 22})
        expected_total += 22
    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")
    '''
    block_lines = block.splitlines()
    replacement = "    " + block_lines[0] + "\n" + textwrap.indent(textwrap.dedent("\n".join(block_lines[1:])), "    ") + "\n"
    replace_once(verifier, old, replacement)

    closure_test = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    replace_once(closure_test, '        "src_pl_jogger_brochure_20251217": 580,\n', '        "src_pl_jogger_brochure_20251217": 602,\n')
    replace_once(closure_test, '        self.assertEqual(len(self.scalar), 1276)\n', '        self.assertEqual(len(self.scalar), 1298)\n')


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Jogger Page 19 Gross Vehicle Weight Source Observations"
    state["baseline"].update({
        "tests": 1655,
        "csv_files": 46,
        "rows": 11306,
        "configuration_values": 3447,
        "configuration_import_specs": 132,
        "configuration_value_ranges": 278,
        "configuration_range_import_specs": 22,
        "availability_records": 5770,
        "attributes": 385,
        "attribute_categories": 30,
    })
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_gross_vehicle_weight_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Gross Vehicle Weight Source Observations",
        "status": "complete",
        "goal": "Add 22 source-specific gross vehicle weight observations from Jogger brochure page 19 where every printed kilogram value exactly matches the later official source, without importing either adjacent mislabeled mass block.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-gross-vehicle-weight-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_gross_vehicle_weight_source_observations.py",
            "tools/import_jogger_chassis_20260726.py",
            "tests/test_jogger_chassis_20260726.py",
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
        "package_id": "post_residual_jogger_page19_braked_trailer_weight_non_hybrid_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Non-Hybrid Braked Trailer Weight Source Observations",
        "status": "planned",
        "source_code": SOURCE,
        "target_configuration_count": 16,
        "planned_observation_count": 16,
        "goal": "Add the matching 1200 kg brochure-source braked trailer observations for the 16 current TCe 110 and Eco-G 120 configurations while explicitly excluding all six Hybrid 155 configurations because their later official value is 1000 kg.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-braked-trailer-weight-non-hybrid-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_braked_trailer_weight_non_hybrid_source_observations.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def refresh_generated_contracts() -> None:
    run(sys.executable, "tools/verified_pdf_candidate_coverage_reconciliation.py")
    artifact = json.loads((ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json").read_text(encoding="utf-8"))
    counts = artifact["summary"]["coverage_status_counts"]

    coverage_test = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    text = coverage_test.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"(?m)^            \{'already_covered': \d+, 'ambiguous': \d+, 'explicit_non_import': \d+, 'unresolved': \d+\},$",
        "            " + repr(counts) + ",",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"coverage-count replacement count is {count}")
    coverage_test.write_text(updated, encoding="utf-8", newline="\n")

    priority_test = ROOT / "tests/test_verified_pdf_candidate_residual_gap_prioritization.py"
    text = priority_test.read_text(encoding="utf-8")
    residual = {"ambiguous": counts["ambiguous"], "unresolved": counts["unresolved"]}
    updated, count = re.subn(
        r"(?m)^            \{'ambiguous': \d+, 'unresolved': \d+\},$",
        "            " + repr(residual) + ",",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"priority-count replacement count is {count}")
    priority_test.write_text(updated, encoding="utf-8", newline="\n")


def main() -> int:
    write_spec()
    write_test()
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC_PATH.relative_to(ROOT)), "--apply")
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC_PATH.relative_to(ROOT)), "--verify")
    patch_ambiguity_boundary()
    patch_global_contracts()
    update_state()
    refresh_generated_contracts()
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--apply")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py", "--check")
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC_PATH.relative_to(ROOT)), "--verify")
    run(sys.executable, "-m", "unittest", "-v", "tests.test_jogger_page19_gross_vehicle_weight_source_observations", "tests.test_jogger_chassis_20260726", "tests.test_official_brochure_technical_gap_resolution_closure", "tests.test_verified_pdf_candidate_coverage_reconciliation", "tests.test_verified_pdf_candidate_residual_gap_prioritization")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q")
    print("PASS: Jogger gross-vehicle-weight package materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
