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
import source_coverage as coverage  # noqa: E402


class SourceCoverageTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def fixture(
        self,
        root: Path,
        *,
        include_second_source: bool = True,
        future_second_source: bool = False,
    ) -> tuple[Path, Path]:
        repository = root / 'repository'
        master = repository / 'data' / 'master'
        reporting = repository / 'data' / 'reporting'
        reporting.mkdir(parents=True)

        self.write_csv(
            master / 'configurations.csv',
            ['id', 'code', 'version_code', 'status'],
            [
                ['1', 'cfg_a', 'ver_a', 'active'],
                ['2', 'cfg_b', 'ver_b', 'active'],
            ],
        )
        self.write_csv(
            master / 'versions.csv',
            ['id', 'code', 'model_code', 'status'],
            [
                ['1', 'ver_a', 'model_a', 'active'],
                ['2', 'ver_b', 'model_b', 'active'],
            ],
        )
        self.write_csv(
            master / 'attributes.csv',
            ['id', 'code', 'category', 'status'],
            [
                ['1', 'engine_power', 'Engine', 'active'],
                ['2', 'vehicle_height', 'Dimensions', 'active'],
                ['3', 'fog_lights', 'Lighting', 'active'],
                ['4', 'heated_seat', 'Comfort', 'active'],
            ],
        )

        source_rows = [
            [
                '1',
                'src_a',
                'configuration_pdf',
                'Source A',
                'Dacia',
                'PL',
                '2026-06-01',
                'A',
                'PDF/a.pdf',
                'a' * 64,
                'active',
                '',
            ]
        ]
        if include_second_source:
            source_rows.append(
                [
                    '2',
                    'src_b',
                    'configuration_pdf',
                    'Source B',
                    'Dacia',
                    'PL',
                    '2027-01-01' if future_second_source else '2026-06-01',
                    'B',
                    'PDF/b.pdf',
                    'b' * 64,
                    'active',
                    '',
                ]
            )
        self.write_csv(
            master / 'sources.csv',
            [
                'id',
                'code',
                'source_type',
                'title',
                'publisher',
                'market',
                'document_date',
                'external_reference',
                'file_path',
                'sha256',
                'status',
                'notes',
            ],
            source_rows,
        )

        self.write_csv(
            master / 'source_models.csv',
            ['id', 'source_code', 'model_code', 'relationship', 'notes'],
            [
                ['1', 'src_a', 'model_a', 'configuration_for', ''],
                ['2', 'src_b', 'model_b', 'configuration_for', ''],
            ],
        )
        self.write_csv(
            master / 'source_versions.csv',
            ['id', 'source_code', 'version_code', 'relationship', 'notes'],
            [
                ['1', 'src_a', 'ver_a', 'documents', ''],
                ['2', 'src_b', 'ver_b', 'documents', ''],
            ],
        )
        self.write_csv(
            master / 'source_configurations.csv',
            [
                'id',
                'source_code',
                'configuration_code',
                'relationship',
                'notes',
            ],
            [
                ['1', 'src_a', 'cfg_a', 'documents', ''],
                ['2', 'src_b', 'cfg_b', 'documents', ''],
            ],
        )
        self.write_csv(
            master / 'configuration_prices.csv',
            [
                'id',
                'code',
                'configuration_code',
                'market',
                'price_type',
                'amount',
                'currency_code',
                'price_date',
                'source_code',
                'notes',
            ],
            [
                ['1', 'price_a', 'cfg_a', 'PL', 'catalog_gross', '1', 'PLN', '2026-06-01', 'src_a', ''],
                ['2', 'price_b', 'cfg_b', 'PL', 'catalog_gross', '2', 'PLN', '2026-06-01', 'src_b', ''],
            ],
        )
        self.write_csv(
            master / 'configuration_attribute_values.csv',
            [
                'id',
                'code',
                'configuration_code',
                'attribute_code',
                'fuel_type_code',
                'value',
                'observation_date',
                'source_code',
                'notes',
            ],
            [
                ['1', 'power_a', 'cfg_a', 'engine_power', '', '100', '2026-06-01', 'src_a', ''],
                ['2', 'power_b', 'cfg_b', 'engine_power', '', '100', '2026-06-01', 'src_b', ''],
            ],
        )
        self.write_csv(
            master / 'configuration_attribute_availability.csv',
            [
                'id',
                'code',
                'configuration_code',
                'attribute_code',
                'availability_status',
                'observation_date',
                'source_code',
                'notes',
            ],
            [
                ['1', 'fog_a', 'cfg_a', 'fog_lights', 'standard', '2026-06-01', 'src_a', ''],
                ['2', 'fog_b', 'cfg_b', 'fog_lights', 'unknown', '2026-06-01', 'src_b', ''],
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
                {'attribute_code': 'vehicle_height', 'fuel_type_code': ''},
            ],
            'equipment_attributes': ['fog_lights', 'heated_seat'],
            'not_applicable': {'technical': [], 'equipment': []},
        }
        spec_path = reporting / 'configuration_completeness.json'
        spec_path.write_text(
            json.dumps(spec, indent=2) + '\n',
            encoding='utf-8',
        )
        return repository, spec_path

    def test_reports_registered_sources_and_record_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = coverage.collect_report(repository, spec)

        self.assertEqual(report['source_registration']['registered'], 2)
        self.assertEqual(report['source_registration']['missing'], 0)
        self.assertEqual(report['records']['identity_links']['present'], 6)
        self.assertEqual(report['records']['prices']['present'], 2)
        self.assertEqual(report['records']['technical']['present'], 2)
        self.assertEqual(report['records']['technical']['missing'], 2)
        self.assertEqual(report['records']['equipment']['present'], 2)
        self.assertEqual(report['records']['equipment']['missing'], 2)
        self.assertEqual(len(report['gaps']), 4)

    def test_distinguishes_missing_source_from_missing_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(
                Path(directory),
                include_second_source=False,
            )
            report = coverage.collect_report(repository, spec)

        self.assertEqual(report['source_registration']['registered'], 1)
        self.assertEqual(report['source_registration']['missing'], 1)
        self.assertEqual(report['records']['technical']['missing'], 1)
        self.assertEqual(report['records']['technical']['source_missing'], 2)
        self.assertEqual(report['records']['equipment']['missing'], 1)
        self.assertEqual(report['records']['equipment']['source_missing'], 2)
        self.assertEqual(
            report['sources'][1]['registration_state'],
            'missing',
        )

    def test_future_source_is_separate_registration_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(
                Path(directory),
                future_second_source=True,
            )
            report = coverage.collect_report(
                repository,
                spec,
                '2026-06-01',
            )

        self.assertEqual(report['source_registration']['future'], 1)
        self.assertEqual(
            report['sources'][1]['registration_state'],
            'future',
        )

    def test_sections_distinguish_partial_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = coverage.collect_report(repository, spec)

        statuses = {
            (item['area'], item['section']): item['status']
            for item in report['sources'][0]['sections']
        }
        self.assertEqual(statuses[('technical', 'Dimensions')], 'missing')
        self.assertEqual(statuses[('technical', 'Engine')], 'covered')
        self.assertEqual(statuses[('equipment', 'Comfort')], 'missing')
        self.assertEqual(statuses[('equipment', 'Lighting')], 'covered')

    def test_json_and_markdown_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            report = coverage.collect_report(repository, spec)

        first = coverage.render_json(report)
        second = coverage.render_json(report)
        self.assertEqual(first, second)
        self.assertNotIn('generated_at', first)
        markdown = coverage.render_markdown(report)
        self.assertIn('# Source Coverage', markdown)
        self.assertIn('`src_a`', markdown)
        self.assertIn('`vehicle_height`', markdown)
        self.assertIn('a' * 64, markdown)

    def test_rejects_invalid_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            path = repository / 'data' / 'master' / 'sources.csv'
            text = path.read_text(encoding='utf-8')
            path.write_text(
                text.replace('a' * 64, 'invalid'),
                encoding='utf-8',
            )
            with self.assertRaisesRegex(
                coverage.SourceCoverageError,
                'invalid SHA-256',
            ):
                coverage.collect_report(repository, spec)

    def test_rejects_observation_source_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = self.fixture(Path(directory))
            path = (
                repository
                / 'data'
                / 'master'
                / 'configuration_attribute_values.csv'
            )
            text = path.read_text(encoding='utf-8')
            path.write_text(
                text.replace('power_a,cfg_a,engine_power,,100,2026-06-01,src_a',
                             'power_a,cfg_a,engine_power,,100,2026-06-01,src_b'),
                encoding='utf-8',
            )
            with self.assertRaisesRegex(
                coverage.SourceCoverageError,
                'source differs',
            ):
                coverage.collect_report(repository, spec)

    def test_range_observations_count_as_source_covered_technical_evidence(self) -> None:
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
            report = coverage.collect_report(repository, spec)
        self.assertEqual(report['records']['technical']['present'], 4)
        self.assertEqual(report['records']['technical']['missing'], 0)
        self.assertEqual(len(report['gaps']), 2)


if __name__ == '__main__':
    unittest.main()
