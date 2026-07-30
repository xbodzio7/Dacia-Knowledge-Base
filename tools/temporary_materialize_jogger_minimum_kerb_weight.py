#!/usr/bin/env python3
"""Materialize the temporary Jogger page 19 minimum-kerb-weight package."""

from __future__ import annotations

import json
import pprint
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/imports/configuration_values/jogger-brochure-minimum-kerb-weight-20251217.json"
TEST_PATH = ROOT / "tests/test_jogger_page19_minimum_kerb_weight_source_observations.py"
EXPECTED = {
    "jogger_expression_5seat_tce110_manual": "1193",
    "jogger_extreme_5seat_tce110_manual": "1193",
    "jogger_journey_5seat_tce110_manual": "1193",
    "jogger_essential_5seat_ecog120_manual": "1292",
    "jogger_expression_5seat_ecog120_manual": "1292",
    "jogger_extreme_5seat_ecog120_manual": "1292",
    "jogger_extreme_5seat_ecog120_automatic": "1326",
    "jogger_journey_5seat_ecog120_automatic": "1326",
    "jogger_expression_5seat_hybrid155_automatic": "1359",
    "jogger_extreme_5seat_hybrid155_automatic": "1359",
    "jogger_journey_5seat_hybrid155_automatic": "1359",
    "jogger_expression_7seat_tce110_manual": "1221",
    "jogger_extreme_7seat_tce110_manual": "1221",
    "jogger_journey_7seat_tce110_manual": "1221",
    "jogger_essential_7seat_ecog120_manual": "1321",
    "jogger_expression_7seat_ecog120_manual": "1321",
    "jogger_extreme_7seat_ecog120_manual": "1321",
    "jogger_extreme_7seat_ecog120_automatic": "1354",
    "jogger_journey_7seat_ecog120_automatic": "1354",
    "jogger_expression_7seat_hybrid155_automatic": "1388",
    "jogger_extreme_7seat_hybrid155_automatic": "1388",
    "jogger_journey_7seat_hybrid155_automatic": "1388",
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
        source_text = (
            "Wersja 5-miejscowa 1193 1292 1326 1359"
            if "_5seat_" in configuration
            else "Wersja 7-miejscowa 1221 1321 1354 1388"
        )
        rows.append(
            {
                "configuration_code": configuration,
                "source_code": "src_pl_jogger_brochure_20251217",
                "value": value,
                "source_text": source_text,
            }
        )
    payload = {
        "version": 1,
        "kind": "configuration_attribute_values",
        "id_start": 3362,
        "attribute_code": "minimum_kerb_weight",
        "attribute_contract": {"data_type": "integer", "unit": "kg", "status": "active"},
        "observation_date": "2025-12-17",
        "fuel_type_code": "",
        "source_page": 19,
        "source_section": "Minimalna masa własna",
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
    header = textwrap.dedent(
        '''\
        """Verify Jogger page 19 minimum-kerb-weight source observations."""

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
        SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-minimum-kerb-weight-20251217.json"
        PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
        BROCHURE_SOURCE = "src_pl_jogger_brochure_20251217"
        PRICE_SOURCE = "src_pl_jogger_price_my26_20260401"
        EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
        EXPECTED = '''
    )
    body = textwrap.dedent(
        '''


        def rows(path: Path) -> list[dict[str, str]]:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))


        class JoggerPage19MinimumKerbWeightSourceObservationTests(unittest.TestCase):
            @classmethod
            def setUpClass(cls) -> None:
                cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
                cls.values = rows(MASTER / "configuration_attribute_values.csv")

            def test_spec_is_strict_and_source_bounded(self) -> None:
                self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
                self.assertEqual(self.spec["id_start"], 3362)
                self.assertEqual(self.spec["attribute_code"], "minimum_kerb_weight")
                self.assertEqual(
                    self.spec["attribute_contract"],
                    {"data_type": "integer", "unit": "kg", "status": "active"},
                )
                self.assertEqual(self.spec["observation_date"], "2025-12-17")
                self.assertEqual(self.spec["source_page"], 19)
                self.assertEqual(self.spec["source_section"], "Minimalna masa własna")

            def test_exact_twenty_two_targets_are_in_spec_once(self) -> None:
                actual = {row["configuration_code"]: row["value"] for row in self.spec["rows"]}
                self.assertEqual(len(self.spec["rows"]), 22)
                self.assertEqual(actual, EXPECTED)
                self.assertEqual(len(actual), len(self.spec["rows"]))
                self.assertEqual({row["source_code"] for row in self.spec["rows"]}, {BROCHURE_SOURCE})
                self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

            def test_brochure_rows_are_contiguous_and_exact(self) -> None:
                selected = sorted(
                    [
                        row
                        for row in self.values
                        if row["source_code"] == BROCHURE_SOURCE
                        and row["attribute_code"] == "minimum_kerb_weight"
                        and row["configuration_code"] in EXPECTED
                    ],
                    key=lambda row: int(row["id"]),
                )
                self.assertEqual([int(row["id"]) for row in selected], list(range(3362, 3384)))
                self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
                self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-17"})

            def test_later_official_source_observations_coexist_unchanged(self) -> None:
                selected = [
                    row
                    for row in self.values
                    if row["source_code"] == PRICE_SOURCE
                    and row["attribute_code"] == "minimum_kerb_weight"
                    and row["configuration_code"] in EXPECTED
                ]
                self.assertEqual(len(selected), 22)
                self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
                self.assertEqual({row["observation_date"] for row in selected}, {"2026-04-01"})

            def test_targets_are_active_and_linked_to_brochure(self) -> None:
                active = {
                    row["code"]
                    for row in rows(MASTER / "configurations.csv")
                    if row["status"] == "active"
                }
                linked = {
                    row["configuration_code"]
                    for row in rows(MASTER / "source_configurations.csv")
                    if row["source_code"] == BROCHURE_SOURCE
                    and row["relationship"] == "brochure_technical_data_for"
                }
                self.assertTrue(set(EXPECTED) <= active)
                self.assertTrue(set(EXPECTED) <= linked)

            def test_page_text_contains_exact_label_and_rows(self) -> None:
                if shutil.which("pdftotext") is None:
                    self.skipTest("pdftotext unavailable")
                page_text = " ".join(
                    _compact_text(text)
                    for _, text in extract_page_candidates(PDF, 19)
                )
                self.assertIn(_compact_text("Minimalna masa własna"), page_text)
                self.assertIn(
                    _compact_text("Wersja 5-miejscowa 1193 1292 1326 1359"),
                    page_text,
                )
                self.assertIn(
                    _compact_text("Wersja 7-miejscowa 1221 1321 1354 1388"),
                    page_text,
                )

            def test_mislabeled_mass_blocks_are_not_part_of_this_import(self) -> None:
                selected = [row for row in self.values if 3362 <= int(row["id"]) <= 3383]
                self.assertEqual({row["attribute_code"] for row in selected}, {"minimum_kerb_weight"})
                encoded = json.dumps(self.spec, ensure_ascii=False)
                self.assertNotIn("maximum_kerb_weight", encoded)
                self.assertNotIn("gross_train_weight", encoded)
                self.assertNotIn("gross_vehicle_weight", encoded)


        if __name__ == "__main__":
            unittest.main()
        '''
    )
    TEST_PATH.write_text(header + expected_literal + body, encoding="utf-8", newline="\n")


def patch_live_contracts() -> None:
    verifier = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    old = '    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'
    block = '''jogger_minimum_kerb_weight = [
        row
        for row in scalar
        if row.get("source_code") == "src_pl_jogger_brochure_20251217"
        and row.get("attribute_code") == "minimum_kerb_weight"
        and 3362 <= int(row.get("id", "0")) <= 3383
    ]
    if jogger_minimum_kerb_weight:
        ensure(len(jogger_minimum_kerb_weight) == 22, "Jogger minimum-kerb-weight source-observation receipt differs")
        ensure(
            [int(row["id"]) for row in jogger_minimum_kerb_weight] == list(range(3362, 3384)),
            "Jogger minimum-kerb-weight source-observation IDs differ",
        )
        ensure(
            Counter(row.get("value", "") for row in jogger_minimum_kerb_weight)
            == Counter({"1193": 3, "1292": 3, "1326": 2, "1359": 3, "1221": 3, "1321": 3, "1354": 2, "1388": 3}),
            "Jogger minimum-kerb-weight source-observation values differ",
        )
        expected_scalar.update({"src_pl_jogger_brochure_20251217": 22})
        expected_total += 22
    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")
    '''
    replace_once(verifier, old, textwrap.indent(textwrap.dedent(block), "    "))

    closure_test = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    replace_once(
        closure_test,
        '        "src_pl_jogger_brochure_20251217": 516,\n',
        '        "src_pl_jogger_brochure_20251217": 538,\n',
    )
    replace_once(
        closure_test,
        '        self.assertEqual(len(self.scalar), 1212)\n',
        '        self.assertEqual(len(self.scalar), 1234)\n',
    )


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Jogger Page 19 Minimum Kerb Weight Source Observations"
    state["baseline"].update(
        {
            "tests": 1640,
            "csv_files": 46,
            "rows": 11242,
            "configuration_values": 3383,
            "configuration_import_specs": 128,
            "configuration_value_ranges": 278,
            "configuration_range_import_specs": 22,
            "availability_records": 5770,
            "attributes": 385,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_minimum_kerb_weight_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Minimum Kerb Weight Source Observations",
        "status": "complete",
        "goal": "Add 22 source-specific minimum kerb weight observations from Jogger brochure page 19 for all current five- and seven-seat configurations where the printed values exactly match later official observations, without importing either mislabeled mass block.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-minimum-kerb-weight-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_minimum_kerb_weight_source_observations.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = {
        "package_id": "post_residual_jogger_page19_fuel_lpg_capacity_source_observation_import_001",
        "kind": "configuration_value_import",
        "name": "Jogger Page 19 Fuel and LPG Capacity Source Observations",
        "status": "planned",
        "source_code": "src_pl_jogger_brochure_20251217",
        "target_configuration_count": 22,
        "planned_observation_count": 42,
        "goal": "Preserve source-specific 50 L petrol-tank observations for all 22 current Jogger configurations and separate 50 L total plus 40 L filling-capacity LPG observations for the ten current Eco-G 120 configurations, without collapsing distinct capacity semantics.",
        "manifest_paths": [
            "data/imports/configuration_values/jogger-brochure-fuel-lpg-capacities-20251217.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_jogger_page19_fuel_lpg_capacity_source_observations.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def update_reconciliation_test() -> None:
    artifact_path = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    expected = repr(artifact["summary"]["coverage_status_counts"])
    path = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    text = path.read_text(encoding="utf-8")
    pattern = r"(?m)^            \{'already_covered': \d+, 'ambiguous': \d+, 'explicit_non_import': \d+, 'unresolved': \d+\},$"
    updated, count = re.subn(pattern, "            " + expected + ",", text, count=1)
    if count != 1:
        raise RuntimeError(f"coverage-count replacement count is {count}")
    path.write_text(updated, encoding="utf-8", newline="\n")


def main() -> int:
    write_spec()
    write_test()
    run(
        sys.executable,
        "tools/import_configuration_values.py",
        "--spec",
        str(SPEC_PATH.relative_to(ROOT)),
        "--apply",
    )
    run(
        sys.executable,
        "tools/import_configuration_values.py",
        "--spec",
        str(SPEC_PATH.relative_to(ROOT)),
        "--verify",
    )
    patch_live_contracts()
    update_state()
    run(sys.executable, "tools/verified_pdf_candidate_coverage_reconciliation.py")
    update_reconciliation_test()
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--apply")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py", "--check")
    run(
        sys.executable,
        "tools/import_configuration_values.py",
        "--spec",
        str(SPEC_PATH.relative_to(ROOT)),
        "--verify",
    )
    run(
        sys.executable,
        "-m",
        "unittest",
        "-v",
        "tests.test_jogger_page19_minimum_kerb_weight_source_observations",
        "tests.test_official_brochure_technical_gap_resolution_closure",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
    )
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q")
    print("PASS: Jogger minimum-kerb-weight package materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
