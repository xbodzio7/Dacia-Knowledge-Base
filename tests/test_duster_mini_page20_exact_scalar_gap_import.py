"""Verify the Duster mini page 20 exact scalar gap import."""

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
SOURCE = 'src_pl_duster_mini_brochure_20251020'
SOURCE_SHA = '84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8'
TARGETS = {'duster_iii_essential_ecog120_4x2_manual',
 'duster_iii_expression_ecog120_4x2_manual',
 'duster_iii_expression_mildhybrid140_4x2_manual',
 'duster_iii_extreme_ecog120_4x2_manual',
 'duster_iii_extreme_mildhybrid140_4x2_manual',
 'duster_iii_journey_ecog120_4x2_manual',
 'duster_iii_journey_mildhybrid140_4x2_manual'}
SPECS = {'duster-mini-page20-emission-standard-20251020.json': {'id_start': 3464,
                                                        'attribute': 'emission_standard',
                                                        'contract': {'data_type': 'enum',
                                                                     'unit': '',
                                                                     'status': 'active'},
                                                        'source_text': 'Norma emisji spalin Euro 6E bis Euro 6E bis',
                                                        'values': {'duster_iii_essential_ecog120_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_expression_ecog120_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_extreme_ecog120_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_journey_ecog120_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_expression_mildhybrid140_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_extreme_mildhybrid140_4x2_manual': 'euro_6e_bis',
                                                                   'duster_iii_journey_mildhybrid140_4x2_manual': 'euro_6e_bis'}},
 'duster-mini-page20-particulate-filter-20251020.json': {'id_start': 3471,
                                                         'attribute': 'particulate_filter',
                                                         'contract': {'data_type': 'boolean',
                                                                      'unit': '',
                                                                      'status': 'active'},
                                                         'source_text': 'Filtr cząstek stałych(1) Tak Tak',
                                                         'values': {'duster_iii_essential_ecog120_4x2_manual': 'true',
                                                                    'duster_iii_expression_ecog120_4x2_manual': 'true',
                                                                    'duster_iii_extreme_ecog120_4x2_manual': 'true',
                                                                    'duster_iii_journey_ecog120_4x2_manual': 'true',
                                                                    'duster_iii_expression_mildhybrid140_4x2_manual': 'true',
                                                                    'duster_iii_extreme_mildhybrid140_4x2_manual': 'true',
                                                                    'duster_iii_journey_mildhybrid140_4x2_manual': 'true'}},
 'duster-mini-page20-start-stop-20251020.json': {'id_start': 3478,
                                                 'attribute': 'start_stop_system',
                                                 'contract': {'data_type': 'boolean', 'unit': '', 'status': 'active'},
                                                 'source_text': 'Stop & Start(2) Tak Tak',
                                                 'values': {'duster_iii_essential_ecog120_4x2_manual': 'true',
                                                            'duster_iii_expression_ecog120_4x2_manual': 'true',
                                                            'duster_iii_extreme_ecog120_4x2_manual': 'true',
                                                            'duster_iii_journey_ecog120_4x2_manual': 'true',
                                                            'duster_iii_expression_mildhybrid140_4x2_manual': 'true',
                                                            'duster_iii_extreme_mildhybrid140_4x2_manual': 'true',
                                                            'duster_iii_journey_mildhybrid140_4x2_manual': 'true'}},
 'duster-mini-page20-eco-mode-20251020.json': {'id_start': 3485,
                                               'attribute': 'eco_mode',
                                               'contract': {'data_type': 'boolean', 'unit': '', 'status': 'active'},
                                               'source_text': 'Tryb Eco Tak',
                                               'values': {'duster_iii_essential_ecog120_4x2_manual': 'true',
                                                          'duster_iii_expression_ecog120_4x2_manual': 'true',
                                                          'duster_iii_extreme_ecog120_4x2_manual': 'true',
                                                          'duster_iii_journey_ecog120_4x2_manual': 'true',
                                                          'duster_iii_expression_mildhybrid140_4x2_manual': 'true',
                                                          'duster_iii_extreme_mildhybrid140_4x2_manual': 'true',
                                                          'duster_iii_journey_mildhybrid140_4x2_manual': 'true'}},
 'duster-mini-page20-gross-vehicle-weight-20251020.json': {'id_start': 3492,
                                                           'attribute': 'gross_vehicle_weight',
                                                           'contract': {'data_type': 'integer',
                                                                        'unit': 'kg',
                                                                        'status': 'active'},
                                                           'source_text': 'Dopuszczalna masa całkowita (DMC) pojazdu '
                                                                          '1805 1830',
                                                           'values': {'duster_iii_essential_ecog120_4x2_manual': '1805',
                                                                      'duster_iii_expression_ecog120_4x2_manual': '1805',
                                                                      'duster_iii_extreme_ecog120_4x2_manual': '1805',
                                                                      'duster_iii_journey_ecog120_4x2_manual': '1805',
                                                                      'duster_iii_expression_mildhybrid140_4x2_manual': '1830',
                                                                      'duster_iii_extreme_mildhybrid140_4x2_manual': '1830',
                                                                      'duster_iii_journey_mildhybrid140_4x2_manual': '1830'}}}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterMiniPage20ExactScalarGapImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.payloads = {name: json.loads((IMPORTS / name).read_text(encoding="utf-8")) for name in SPECS}

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
            actual = {row["configuration_code"]: row["value"] for row in payload["rows"]}
            self.assertEqual(actual, expected["values"])
            self.assertEqual(set(actual), TARGETS)
            self.assertEqual(len(payload["rows"]), 7)
            self.assertEqual({row["source_code"] for row in payload["rows"]}, {SOURCE})
            self.assertFalse(any(row.get("fuel_type_code") for row in payload["rows"]))

    def test_master_receipt_is_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3464 <= int(row["id"]) <= 3498],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3464, 3499)))
        self.assertEqual(
            Counter(row["attribute_code"] for row in selected),
            Counter({
                "emission_standard": 7,
                "particulate_filter": 7,
                "start_stop_system": 7,
                "eco_mode": 7,
                "gross_vehicle_weight": 7,
            }),
        )
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-10-20"})
        self.assertEqual({row["configuration_code"] for row in selected}, TARGETS)

    def test_master_values_match_reviewed_handoff(self) -> None:
        selected = [row for row in self.values if 3464 <= int(row["id"]) <= 3498]
        by_attribute = {}
        for row in selected:
            by_attribute.setdefault(row["attribute_code"], {})[row["configuration_code"]] = row["value"]
        for expected in SPECS.values():
            self.assertEqual(by_attribute[expected["attribute"]], expected["values"])

    def test_targets_are_active_manual_duster_and_source_linked(self) -> None:
        configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
        versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
        linked = {
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
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
        imported_attributes = {row["attribute_code"] for row in self.values if 3464 <= int(row["id"]) <= 3498}
        self.assertEqual(
            imported_attributes,
            {"emission_standard", "particulate_filter", "start_stop_system", "eco_mode", "gross_vehicle_weight"},
        )


if __name__ == "__main__":
    unittest.main()
