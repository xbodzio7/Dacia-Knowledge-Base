#!/usr/bin/env python3
from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = "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"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    raw = gzip.decompress(base64.b64decode(PAYLOAD)).decode("utf-8")
    data = json.loads(raw)
    target = ROOT / "data/reporting/cross_model_configurator_standard_equipment.json"
    write(target, json.dumps(data, ensure_ascii=False, indent=2))

    write(ROOT / "data/reporting/cross_model_configurator_standard_equipment.md", f"""# Cross-model Configurator Standard Equipment

Observed: 2026-08-04

- exact configurations: {data['configuration_count']}
- source pages per configuration: 3-4
- category blocks: {data['total_category_count']}
- preserved source lines: {data['total_source_line_count']}

The report preserves the exact extracted source lines under each configurator code. Line wrapping from the official PDF is retained deliberately; semantic joining is deferred to a later bounded normalization step rather than inferred here.

No equipment item is transferred between grades, powertrains, phases, seat counts or model families.
""")

    write(ROOT / "project/packages/cross-model-configurator-standard-equipment-migration-20260805.md", """# Cross-model Configurator Standard Equipment Migration

## Package

- Package ID: `cross_model_configurator_standard_equipment_migration_001`
- Kind: `source_backed_equipment_migration`
- Status: complete
- Source date: 2026-08-04

## Result

All standard-equipment source lines from pages 3 and 4 of the 18 registered configurator PDFs are persisted under their exact configurator codes. The package covers Bigster, Duster, new Jogger 5-seat, Sandero F.2 and Sandero Stepway F.2.

## Evidence boundary

- exact configurator-code scope only;
- source wording and PDF line wrapping preserved;
- no cross-grade, cross-powertrain, cross-phase or cross-seat-count transfer;
- no semantic joining of wrapped source lines is inferred.

## Next package

`cross_model_configurator_technical_data_migration_001` will persist exact technical-data observations from the dedicated technical pages of all 18 PDFs.
""")

    write(ROOT / "tests/test_cross_model_configurator_standard_equipment_20260805.py", """import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'data/reporting/cross_model_configurator_standard_equipment.json'

class CrossModelConfiguratorStandardEquipmentTest(unittest.TestCase):
    def test_exact_standard_equipment_contract(self):
        data = json.loads(REPORT.read_text(encoding='utf-8'))
        self.assertEqual(data['configuration_count'], 18)
        self.assertEqual(data['document_count'], 18)
        self.assertEqual(data['total_category_count'], 156)
        self.assertEqual(data['total_source_line_count'], 1355)
        docs = {d['configuration_code']: d for d in data['documents']}
        self.assertEqual(len(docs), 18)
        self.assertEqual(docs['4TJTWN']['phase'], 'F.2')
        self.assertEqual(docs['I23FGG']['seat_count'], 5)
        self.assertEqual(docs['MEOHF3']['powertrain'], 'Eco-G 120')
        self.assertTrue(data['evidence_boundary']['source_wording_preserved'])
        self.assertTrue(data['evidence_boundary']['no_semantic_line_joining_inferred'])
        def lines(code):
            return [line for group in docs[code]['categories'] for line in group['source_lines']]
        self.assertIn('fabryczna instalacja LPG', lines('GGQ0LU'))
        self.assertIn('system kontroli martwego pola', lines('HJISLB'))
        self.assertIn('16\" felgi aluminiowe TAMIA BLACK', lines('5WZLHM'))

if __name__ == '__main__':
    unittest.main()
""")

    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state["next_package"]["package_id"] != "cross_model_configurator_standard_equipment_migration_001":
        raise RuntimeError("canonical next package changed")
    state["updated_on"] = "2026-08-05"
    state["baseline"]["tests"] = 1866
    state["current_package"] = {
        "package_id": "cross_model_configurator_standard_equipment_migration_001",
        "kind": "source_backed_equipment_migration",
        "name": "Cross-model Configurator Standard Equipment Migration",
        "status": "complete",
        "goal": "Persist exact standard-equipment source lines from pages 3-4 of all 18 saved configurator PDFs while preserving configuration boundaries.",
        "manifest_paths": [
            "data/reporting/cross_model_configurator_standard_equipment.json",
            "data/reporting/cross_model_configurator_standard_equipment.md",
            "project/STATE_SUMMARY.md",
            "project/packages/cross-model-configurator-standard-equipment-migration-20260805.md",
            "project/state.json",
            "tests/test_cross_model_configurator_standard_equipment_20260805.py"
        ]
    }
    state["next_package"] = {
        "package_id": "cross_model_configurator_technical_data_migration_001",
        "kind": "source_backed_technical_observation_migration",
        "name": "Cross-model Configurator Technical Data Migration",
        "status": "planned",
        "goal": "Extract and persist exact technical-data observations from all 18 saved configurator PDFs without cross-identity propagation.",
        "manifest_paths": []
    }
    write(state_path, json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
