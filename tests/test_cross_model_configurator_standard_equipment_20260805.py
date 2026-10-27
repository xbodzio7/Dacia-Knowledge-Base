import json
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
        self.assertIn('16" felgi aluminiowe TAMIA BLACK', lines('5WZLHM'))

if __name__ == '__main__':
    unittest.main()
