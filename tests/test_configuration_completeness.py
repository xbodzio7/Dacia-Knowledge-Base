from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / 'tools'
sys.path.insert(0, str(TOOLS))
import configuration_completeness as completeness  # noqa: E402


class ConfigurationCompletenessTests(unittest.TestCase):
    def write_csv(self, path: Path, header: list[str], rows: list[list[str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def fixture(self, root: Path) -> tuple[Path, Path]:
        repository = root / 'repository'
        master = repository / 'data' / 'master'
        reporting = repository / 'data' / 'reporting'
        reporting.mkdir(parents=True)
        self.write_csv(
            master / 'configurations.csv',
            ['id', 'code', 'status'],
            [['1', 'cfg_a', 'active'], ['2', 'cfg_b', 'active'], ['3', 'old', 'archived']],
        )
        self.write_csv(
            master / 'sources.csv',
            ['id', 'code', 'status'],
            [['1', 'src_a', 'active'], ['2', 'src_b', 'active']],
        )
        self.write_csv(
            master / 'attributes.csv',
            ['id', 'code', 'category', 'status'],
            [
                ['1', 'engine_power', 'Engine', 'active'],
                ['2', 'engine_torque', 'Engine', 'active'],
                ['3', 'vehicle_height', 'Dimensions', 'active'],
                ['4', 'fog_lights', 'Lighting', 'active'],
                ['5', 'heated_seat', 'Comfort', 'active'],
            ],
        )
        value_header = [
            'id', 'code', 'configuration_code', 'attribute_code',
            'fuel_type_code', 'value', 'observation_date', 'source_code', 'notes',
        ]
        self.write_csv(
            master / 'configuration_attribute_values.csv',
            value_header,
            [
                ['1', 'a_power_old', 'cfg_a', 'engine_power', '', '90', '2026-01-01', 'src_a', ''],
                ['2', 'a_power', 'cfg_a', 'engine_power', '', '100', '2026-06-01', 'src_a', ''],
                ['3', 'a_torque', 'cfg_a', 'engine_torque', 'petrol', '180', '2026-06-01', 'src_a', ''],
                ['4', 'b_power', 'cfg_b', 'engine_power', '', '100', '2026-06-01', 'src_b', ''],
            ],
        )
        availability_header = [
            'id', 'code', 'configuration_code', 'attribute_code',
            'availability_status', 'observation_date', 'source_code', 'notes',
        ]
        self.write_csv(
            master / 'configuration_attribute_availability.csv',
            availability_header,
            [
                ['1', 'a_fog', 'cfg_a', 'fog_lights', 'standard', '2026-06-01', 'src_a', ''],
                ['2', 'a_heated', 'cfg_a', 'heated_seat', 'not_available', '2026-06-01', 'src_a', ''],
                ['3', 'b_fog', 'cfg_b', 'fog_lights', 'unknown', '2026-06-01', 'src_b', ''],
            ],
        )
        spec = {
            'version': 1,
            'configuration_status': 'active',
            'configurations': [
                {'configuration_code': 'cfg_a', 'source_code': 'src_a'},
                {'configuration_code': 'cfg_b', 'source_code': 'src_b'},
            ],
            'technical_slots': [
                {'attribute_code': 'engine_power', 'fuel_type_code': ''},
                {'attribute_code': 'engine_torque', 'fuel_type_code': 'petrol'},
                {'attribute_code': 'vehicle_height', 'fuel_type_code': ''},
            ],
            'equipment_attributes': ['fog_lights', 'heated_seat'],
            'not_applicable': {
                'technical': [
                    {
                        'configuration_code': 'cfg_b',
                        'attribute_code': 'engine_torque',
                        'fuel_type_code': 'petrol',
                    }
                ],
                'equipment': [],
            },
        }
        spec_path = reporting / 'configuration_completeness.json'
        spec_path.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
        return repository, spec_path

    def test_distinguishes_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = completeness.collect_report(repository, spec)
        self.assertEqual(report['technical']['denominator'], 6)
        self.assertEqual(report['technical']['applicable'], 5)
        self.assertEqual(report['technical']['present'], 3)
        self.assertEqual(report['technical']['missing'], 2)
        self.assertEqual(report['technical']['not_applicable'], 1)
        self.assertEqual(report['equipment']['recorded'], 3)
        self.assertEqual(report['equipment']['missing'], 1)
        self.assertEqual(report['equipment']['standard'], 1)
        self.assertEqual(report['equipment']['not_available'], 1)
        self.assertEqual(report['equipment']['unknown'], 1)

    def test_deterministic_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = completeness.collect_report(repository, spec)
        self.assertEqual(completeness.render_json(report), completeness.render_json(report))
        self.assertNotIn('generated_at', completeness.render_json(report))
        markdown = completeness.render_markdown(report)
        self.assertIn('`vehicle_height`', markdown)
        self.assertIn('`heated_seat`', markdown)
        self.assertIn('`src_b`', markdown)

    def test_as_of(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = completeness.collect_report(repository, spec, '2026-02-01')
        self.assertEqual(report['technical']['present'], 1)
        self.assertEqual(report['equipment']['recorded'], 0)

    def test_rejects_scope_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            payload = json.loads(spec.read_text(encoding='utf-8'))
            payload['configurations'].pop()
            spec.write_text(json.dumps(payload), encoding='utf-8')
            with self.assertRaisesRegex(completeness.CompletenessError, 'spec configurations differ'):
                completeness.collect_report(repository, spec)

    def test_rejects_unregistered_slot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            payload = json.loads(spec.read_text(encoding='utf-8'))
            payload['technical_slots'] = payload['technical_slots'][1:]
            spec.write_text(json.dumps(payload), encoding='utf-8')
            with self.assertRaisesRegex(completeness.CompletenessError, 'absent from spec'):
                completeness.collect_report(repository, spec)

    def test_rejects_record_for_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            path = repository / 'data' / 'master' / 'configuration_attribute_values.csv'
            with path.open('a', encoding='utf-8', newline='') as handle:
                csv.writer(handle).writerow(
                    ['5', 'b_torque', 'cfg_b', 'engine_torque', 'petrol', '180', '2026-06-01', 'src_b', '']
                )
            with self.assertRaisesRegex(completeness.CompletenessError, 'not_applicable slot has a record'):
                completeness.collect_report(repository, spec)

    def test_range_observations_satisfy_technical_slots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            master = repository / 'data' / 'master'
            self.write_csv(
                master / 'configuration_attribute_value_ranges.csv',
                ['id', 'code', 'configuration_code', 'attribute_code',
                 'fuel_type_code', 'minimum_value', 'maximum_value',
                 'lower_inclusive', 'upper_inclusive', 'observation_date',
                 'source_code', 'notes'],
                [
                    ['1', 'a_height', 'cfg_a', 'vehicle_height', '', '1600', '1650', 'true', 'true', '2026-06-01', 'src_a', ''],
                    ['2', 'b_height', 'cfg_b', 'vehicle_height', '', '1640', '1700', 'true', 'true', '2026-06-01', 'src_b', ''],
                ],
            )
            report = completeness.collect_report(repository, spec)
        self.assertEqual(report['technical']['present'], 5)
        self.assertEqual(report['technical']['missing'], 0)


if __name__ == '__main__':
    unittest.main()
