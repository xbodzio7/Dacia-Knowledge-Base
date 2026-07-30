#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_bigster_brochure_20251210"
SPEC_PATH = ROOT / "data/imports/configuration_values/bigster-page20-eco-mode-20251210.json"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected one occurrence in {path}: {old!r}; found {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def active_bigster() -> list[str]:
    with (ROOT / "data/master/configurations.csv").open(encoding="utf-8-sig", newline="") as handle:
        values = [row["code"] for row in csv.DictReader(handle) if row["status"] == "active" and row["code"].startswith("bigster_")]
    values.sort()
    if len(values) != 14:
        raise RuntimeError(f"expected 14 active Bigster configurations, found {len(values)}")
    return values


def write_spec(configurations: list[str]) -> None:
    payload = {
        "version": 1,
        "kind": "configuration_attribute_values",
        "id_start": 3268,
        "attribute_code": "eco_mode",
        "attribute_contract": {"data_type": "boolean", "unit": "", "status": "active"},
        "observation_date": "2025-12-10",
        "fuel_type_code": "",
        "source_page": 20,
        "source_section": "ZUŻYCIE PALIWA I EMISJA CO2",
        "notes_template": "Source page {page}, section {section}: {source_text}",
        "rows": [{"configuration_code": code, "source_code": SOURCE, "value": "true", "source_text": "Tryb Eco Tak"} for code in configurations],
    }
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


ECO_TEST = '''from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "imports" / "configuration_values" / "bigster-page20-eco-mode-20251210.json"
MASTER = ROOT / "data" / "master"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE = "src_pl_bigster_brochure_20251210"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20EcoModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.rows = cls.spec["rows"]
        cls.codes = {row["code"]: row for row in read_csv(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] == "eco_mode" and row["source_code"] == SOURCE}
        cls.active_bigster = {row["code"] for row in read_csv(MASTER / "configurations.csv") if row["status"] == "active" and row["code"].startswith("bigster_")}

    def test_spec_preserves_the_verified_source_receipt(self) -> None:
        self.assertEqual(self.spec["kind"], "configuration_attribute_values")
        self.assertEqual(self.spec["id_start"], 3268)
        self.assertEqual(self.spec["attribute_code"], "eco_mode")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "boolean", "unit": "", "status": "active"})
        self.assertEqual((self.spec["source_page"], self.spec["source_section"]), (20, "ZUŻYCIE PALIWA I EMISJA CO2"))
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)

    def test_all_fourteen_current_bigster_configurations_are_imported_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.rows]
        self.assertEqual(len(configurations), 14)
        self.assertEqual(set(configurations), self.active_bigster)
        self.assertEqual(len(configurations), len(set(configurations)))

    def test_master_rows_are_contiguous_and_match_the_spec(self) -> None:
        selected = sorted(self.codes.values(), key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in selected], list(range(3268, 3282)))
        expected = {(row["configuration_code"], "eco_mode", "", "2025-12-10", SOURCE): "true" for row in self.rows}
        actual = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"], row["source_code"]): row["value"] for row in selected}
        self.assertEqual(actual, expected)

    def test_values_are_boolean_source_backed_and_do_not_replace_other_observations(self) -> None:
        selected = list(self.codes.values())
        self.assertEqual({row["value"] for row in selected}, {"true"})
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})
        self.assertTrue(all("Tryb Eco Tak" in row["notes"] for row in selected))
        all_eco = [row for row in read_csv(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] == "eco_mode"]
        self.assertEqual(len(all_eco), 14)

    def test_every_imported_configuration_has_the_registered_source_relationship(self) -> None:
        linked = {row["configuration_code"] for row in read_csv(MASTER / "source_configurations.csv") if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"}
        self.assertTrue(self.active_bigster <= linked)

    def test_source_page_contains_the_shared_eco_mode_value(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("Tryb Eco Tak"), page_text)


if __name__ == "__main__":
    unittest.main()
'''


def write_test() -> None:
    (ROOT / "tests/test_bigster_page20_eco_mode.py").write_text(ECO_TEST, encoding="utf-8", newline="\n")


def refresh_live_contracts() -> None:
    run(sys.executable, "tools/verified_pdf_candidate_coverage_reconciliation.py")
    coverage_test = ROOT / "tests/test_verified_pdf_candidate_coverage_reconciliation.py"
    replace_once(coverage_test, '"already_covered": 122', '"already_covered": 123')
    replace_once(coverage_test, '"unresolved": 1157', '"unresolved": 1156')
    priority_test = ROOT / "tests/test_verified_pdf_candidate_residual_gap_prioritization.py"
    replace_once(priority_test, 'self.assertEqual(payload["summary"]["candidate_count"], 1266)', 'self.assertEqual(payload["summary"]["candidate_count"], 1265)')
    replace_once(priority_test, '{"ambiguous": 109, "unresolved": 1157}', '{"ambiguous": 109, "unresolved": 1156}')
    verifier = ROOT / "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py"
    old = '''        expected_total = 1118\n    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'''
    new = '''        expected_total = 1118\n    eco_mode = [\n        row\n        for row in scalar\n        if row.get("source_code") == "src_pl_bigster_brochure_20251210"\n        and row.get("attribute_code") == "eco_mode"\n    ]\n    if eco_mode:\n        ensure(len(eco_mode) == 14, "Bigster eco-mode receipt differs")\n        expected_scalar.update({"src_pl_bigster_brochure_20251210": 14})\n        expected_total += 14\n    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")\n'''
    replace_once(verifier, old, new)
    closure_test = ROOT / "tests/test_official_brochure_technical_gap_resolution_closure.py"
    replace_once(closure_test, '"src_pl_bigster_brochure_20251210": 180,', '"src_pl_bigster_brochure_20251210": 194,')
    replace_once(closure_test, 'self.assertEqual(len(self.scalar), 1118)', 'self.assertEqual(len(self.scalar), 1132)')


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["phase"] = "Bigster Page 20 Eco Mode Import"
    state["current_package"] = {
        "package_id": "post_residual_bigster_page20_eco_mode_import_001",
        "kind": "configuration_value_import",
        "name": "Bigster Page 20 Eco Mode Import",
        "status": "complete",
        "goal": "Add eco_mode=true for all 14 current Bigster configurations from the shared page-20 Tak source value, preserving exact source-to-configuration relationships and without touching any deferred technical conflict.",
        "manifest_paths": [
            "data/imports/configuration_values/bigster-page20-eco-mode-20251210.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_bigster_page20_eco_mode.py",
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
            "tests/test_official_brochure_technical_gap_resolution_closure.py"
        ],
    }
    state["next_package"] = {
        "package_id": "post_residual_bigster_page20_deferred_import_gap_review_001",
        "kind": "review",
        "name": "Bigster Page 20 Deferred Import Gap Review",
        "status": "planned",
        "goal": "Review the three non-conflicting subfacts embedded in page-20 rows that also contain deferred conflicts: Hybrid-G 150 4x4 total system power 113 kW, traction-motor torque 87 Nm, and lithium-ion battery type. Verify existing attribute semantics and source relationships, preserve every RPM, capacity and voltage conflict, and select only a narrow evidence-safe follow-up package.",
        "manifest_paths": [
            "data/reporting/bigster_page20_deferred_import_gap_review.json",
            "data/reporting/bigster_page20_deferred_import_gap_review.md",
            "project/reviews/bigster-page20-deferred-import-gap-review-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md"
        ],
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")


def verify() -> None:
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC_PATH.relative_to(ROOT)), "--verify")
    run(sys.executable, "-m", "unittest", "tests.test_bigster_page20_eco_mode", "tests.test_verified_pdf_candidate_coverage_reconciliation", "tests.test_verified_pdf_candidate_residual_gap_prioritization", "tests.test_official_brochure_technical_gap_resolution_closure", "tests.test_official_brochure_residual_evidence_review", "tests.project_state_contract")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")


def main() -> None:
    write_spec(active_bigster())
    run(sys.executable, "tools/import_configuration_values.py", "--spec", str(SPEC_PATH.relative_to(ROOT)), "--apply")
    write_test()
    refresh_live_contracts()
    update_state()
    verify()


if __name__ == "__main__":
    main()
