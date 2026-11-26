import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'data/reporting/cross_model_configurator_commercial_data.json'

class CrossModelConfiguratorCommercialDataTest(unittest.TestCase):
    def test_exact_commercial_contract(self):
        data = json.loads(PATH.read_text(encoding='utf-8'))
        rows = data['rows']
        self.assertEqual(data['record_count'], 18)
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({r['configuration_code'] for r in rows}), 18)
        self.assertEqual(sum(r['price_pln'] for r in rows), 1593400)
        self.assertTrue(all(r['colour'] == 'biel alpejska' for r in rows))
        self.assertTrue(all(r['colour_price_pln'] == 0 for r in rows))
        self.assertTrue(all(r['wheels_price_pln'] == 0 for r in rows))
        self.assertTrue(all(r['upholstery_price_pln'] == 0 for r in rows))
        by_code = {r['configuration_code']: r for r in rows}
        self.assertEqual(by_code['GGQ0LU']['wheels'], 'aluminiowe obręcze kół 17" 215 TERGAN')
        self.assertEqual(by_code['MEOHF3']['price_pln'], 82000)
        self.assertEqual(by_code['I23FGG']['phase'], 'new')
        self.assertEqual(by_code['4TJTWN']['phase'], 'F.2')
        self.assertEqual(by_code['5WZLHM']['wheels'], '16" felgi aluminiowe TAMIA BLACK')
        self.assertFalse(data['migration_boundary']['master_data_mutated'])

if __name__ == '__main__':
    unittest.main()
