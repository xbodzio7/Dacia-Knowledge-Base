#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGE_LAYOUT = {
  "bigster": {"documents": 4, "summary": [2], "standard_equipment": [3,4], "technical_data": [5], "remaining": [6,7,8,9]},
  "duster": {"documents": 4, "summary": [2], "standard_equipment": [3,4], "technical_data": [5], "remaining": [6,7,8,9]},
  "jogger": {"documents": 4, "summary": [2], "standard_equipment": [3,4], "technical_data": [5], "remaining": [6,7,8,9,10]},
  "sandero": {"documents": 3, "summary": [2], "standard_equipment": [3,4], "technical_data": [5], "remaining": [6,7,8,9]},
  "sandero_stepway": {"documents": 3, "summary": [2], "standard_equipment": [3,4], "technical_data": [5], "remaining": [6,7,8,9,10]}
}

RECONCILIATION = {
  "package_id": "cross_model_configurator_data_reconciliation_001",
  "source_code": "src_pl_dacia_configurator_cross_model_pdf_bundle_20260804",
  "observed_on": "2026-08-04",
  "document_count": 18,
  "page_layout": PAGE_LAYOUT,
  "verified_content": {
    "configuration_identity": 18,
    "configuration_summary_pages": 18,
    "standard_equipment_page_sets": 18,
    "technical_data_pages": 18,
    "commercial_followup_page_sets": 18
  },
  "canonical_mapping": {
    "exact_existing_scope": [
      "duster Eco-G 120 manual: essential, expression, extreme, journey"
    ],
    "new_or_phase_bounded_scope": [
      "Bigster mild hybrid-G 140 and mild hybrid 140 saved states",
      "new Jogger 5-seat saved states dated 2026-08-04",
      "new Sandero F.2 TCe 100 saved states",
      "new Sandero Stepway F.2 TCe 110 and Eco-G 120 saved states"
    ],
    "rule": "No value may be copied across grade, powertrain, transmission, seat-count or phase boundaries."
  },
  "migration_selection": {
    "selected_now": [],
    "reason": "The reconciliation proves complete page-level evidence coverage but master-data mutation requires per-domain exact-row comparison. Mixing source extraction and canonical writes in one package would hide conflicts and phase changes.",
    "next_packages": [
      "cross_model_configurator_commercial_data_migration_001",
      "cross_model_configurator_standard_equipment_migration_001",
      "cross_model_configurator_technical_data_migration_001",
      "cross_model_configurator_options_packages_migration_001",
      "cross_model_configurator_conflict_closure_001"
    ]
  },
  "status": "complete"
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    write(ROOT / "data/reporting/cross_model_configurator_data_reconciliation.json", json.dumps(RECONCILIATION, ensure_ascii=False, indent=2))
    write(ROOT / "data/reporting/cross_model_configurator_data_reconciliation.md", """# Cross-model Configurator Data Reconciliation

Observed: 2026-08-04

## Coverage

All 18 registered PDFs were inspected page by page. Every document contains an exact configuration summary, standard-equipment pages, a technical-data page and later commercial/legal pages.

## Mapping result

- Duster Eco-G 120 manual maps to existing exact canonical scopes for essential, expression, extreme and journey.
- Bigster states remain powertrain-exact and grade-exact.
- new Jogger is preserved as a 2026-08-04 5-seat phase-bound scope.
- new Sandero and new Sandero Stepway are preserved as F.2 scopes and are not merged into older phase records.

## Migration decision

No master row is changed in this reconciliation package. The evidence is complete enough to continue, but the writes must be split by domain so that price, equipment, technical and option conflicts remain reviewable. The next package is commercial-data migration, followed by standard equipment, technical data, options/packages and final conflict closure.
""")
    write(ROOT / "project/packages/cross-model-configurator-data-reconciliation-20260805.md", """# Cross-model Configurator Data Reconciliation

- Package ID: `cross_model_configurator_data_reconciliation_001`
- Kind: `source_reconciliation`
- Status: complete

The package confirms page-level evidence coverage for all 18 exact configurator states, preserves F.2/new-phase boundaries, maps Duster Eco-G 120 manual states to existing canonical scopes and selects bounded domain migrations. No source-backed value is inferred or propagated between configurations.
""")
    write(ROOT / "tests/test_cross_model_configurator_data_reconciliation_20260805.py", """import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'data/reporting/cross_model_configurator_data_reconciliation.json'

class CrossModelConfiguratorDataReconciliationTest(unittest.TestCase):
    def test_reconciliation_contract(self):
        data = json.loads(REPORT.read_text(encoding='utf-8'))
        self.assertEqual(data['document_count'], 18)
        self.assertEqual(sum(v['documents'] for v in data['page_layout'].values()), 18)
        self.assertEqual(data['verified_content']['technical_data_pages'], 18)
        self.assertEqual(data['migration_selection']['selected_now'], [])
        self.assertEqual(len(data['migration_selection']['next_packages']), 5)
        self.assertIn('No value may be copied', data['canonical_mapping']['rule'])

if __name__ == '__main__':
    unittest.main()
""")
    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-08-05"
    state["phase"] = "Cross-model Configurator Data Assimilation"
    state["current_package"] = {
      "package_id": "cross_model_configurator_data_reconciliation_001",
      "kind": "source_reconciliation",
      "name": "Cross-model Configurator Data Reconciliation",
      "status": "complete",
      "goal": "Verify page-level evidence coverage for all 18 exact configurator states, map canonical identities and select bounded non-inferred domain migrations.",
      "manifest_paths": [
        "data/reporting/cross_model_configurator_data_reconciliation.json",
        "data/reporting/cross_model_configurator_data_reconciliation.md",
        "project/STATE_SUMMARY.md",
        "project/packages/cross-model-configurator-data-reconciliation-20260805.md",
        "project/state.json",
        "tests/test_cross_model_configurator_data_reconciliation_20260805.py"
      ]
    }
    state["next_package"] = {
      "package_id": "cross_model_configurator_commercial_data_migration_001",
      "kind": "data_migration",
      "name": "Cross-model Configurator Commercial Data Migration",
      "status": "planned",
      "goal": "Import exact displayed configuration prices, colours, wheels and upholstery from all 18 saved states while preserving phase, grade, powertrain, transmission and seat-count boundaries.",
      "manifest_paths": []
    }
    write(state_path, json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
