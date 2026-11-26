import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'project/sources/dacia-pl-configurator-cross-model-pdf-bundle-20260804.json'

class CrossModelConfiguratorPdfIntakeTest(unittest.TestCase):
    def test_exact_intake_contract(self):
        data = json.loads(SOURCE.read_text(encoding='utf-8'))
        docs = data['documents']
        self.assertEqual(data['document_count'], 18)
        self.assertEqual(len(docs), 18)
        self.assertEqual(set(data['model_families']), {'bigster','duster','jogger','sandero','sandero_stepway'})
        self.assertEqual(len({d['sha256'] for d in docs}), 18)
        self.assertEqual(len({d['configuration_code'] for d in docs}), 18)
        self.assertTrue(all(len(d['sha256']) == 64 for d in docs))
        self.assertEqual(sum(d['price_pln'] for d in docs), 1593400)
        by_code = {d['configuration_code']: d for d in docs}
        self.assertEqual(by_code['GGQ0LU']['price_pln'], 101400)
        self.assertEqual(by_code['MEOHF3']['price_pln'], 82000)
        self.assertEqual(by_code['I23FGG']['seat_count'], 5)
        self.assertEqual(by_code['4TJTWN']['phase'], 'F.2')
        self.assertEqual(by_code['5WZLHM']['powertrain'], 'Eco-G 120')
        self.assertTrue(data['evidence_boundary']['no_cross_phase_transfer'])

if __name__ == '__main__':
    unittest.main()
