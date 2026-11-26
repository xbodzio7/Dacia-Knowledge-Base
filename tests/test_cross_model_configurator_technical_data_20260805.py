import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/reporting/cross_model_configurator_technical_data.json'
class CrossModelConfiguratorTechnicalDataTest(unittest.TestCase):
    def test_exact_technical_contract(self):
        data=json.loads(DATA.read_text(encoding='utf-8'))
        self.assertEqual(data['configuration_count'],18)
        self.assertEqual(data['total_category_count'],162)
        self.assertEqual(data['total_source_line_count'],349)
        self.assertEqual(len({d['configuration_code'] for d in data['documents']}),18)
        self.assertEqual(sum(d['source_line_count'] for d in data['documents']),349)
        by_code={d['configuration_code']:d for d in data['documents']}
        self.assertEqual(by_code['GGQ0LU']['source_line_count'],22)
        self.assertEqual(by_code['MEOHF3']['source_line_count'],20)
        self.assertEqual(by_code['ARKVJG']['source_line_count'],17)
        self.assertEqual(data['normalization_status'],'source_lines_preserved; semantic key-value parsing deferred')
if __name__=='__main__': unittest.main()
