import json
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
