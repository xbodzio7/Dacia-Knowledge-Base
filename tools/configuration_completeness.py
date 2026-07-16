#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

DEFAULT_SPEC = Path('data/reporting/configuration_completeness.json')
AVAILABILITY_STATES = {'standard', 'optional', 'not_available', 'unknown'}


class CompletenessError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise CompletenessError(f'missing CSV header: {path}')
            return list(reader)
    except (OSError, UnicodeDecodeError) as exc:
        raise CompletenessError(f'cannot read UTF-8 CSV {path}: {exc}') from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CompletenessError(f'cannot read JSON {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise CompletenessError(f'JSON root must be an object: {path}')
    return value


def iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CompletenessError(f'invalid ISO date for {label}: {value!r}') from exc


def latest(
    rows: Iterable[dict[str, str]],
    key_fields: Sequence[str],
    as_of: date,
    label: str,
) -> dict[tuple[str, ...], dict[str, str]]:
    chosen: dict[tuple[str, ...], tuple[date, dict[str, str]]] = {}
    for row in rows:
        observed = iso_date(row.get('observation_date', ''), label)
        if observed > as_of:
            continue
        key = tuple(row.get(field, '') for field in key_fields)
        for field, item in zip(key_fields, key):
            if not item and field != 'fuel_type_code':
                raise CompletenessError(f'{label} has incomplete key: {key}')
        previous = chosen.get(key)
        if previous is None or observed > previous[0]:
            chosen[key] = (observed, row)
        elif observed == previous[0]:
            raise CompletenessError(
                f'{label} has duplicate current records for {key} on {observed}'
            )
    return {key: item[1] for key, item in chosen.items()}


def percentage(complete: int, applicable: int) -> str:
    return '100.00' if applicable == 0 else f'{complete * 100 / applicable:.2f}'


def parse_spec(path: Path) -> dict[str, Any]:
    spec = read_json(path)
    if spec.get('version') != 1:
        raise CompletenessError('completeness spec version must be 1')
    required = (
        'configuration_status',
        'configurations',
        'technical_slots',
        'equipment_attributes',
        'not_applicable',
    )
    missing = [key for key in required if key not in spec]
    if missing:
        raise CompletenessError(f'completeness spec keys missing: {missing}')
    return spec


def collect_report(
    repository: Path,
    spec_path: Path,
    as_of_value: str | None = None,
) -> dict[str, Any]:
    master = repository / 'data' / 'master'
    configurations = read_csv(master / 'configurations.csv')
    sources = read_csv(master / 'sources.csv')
    attributes = read_csv(master / 'attributes.csv')
    values = read_csv(master / 'configuration_attribute_values.csv')
    availability = read_csv(master / 'configuration_attribute_availability.csv')
    spec = parse_spec(spec_path)

    status = spec['configuration_status']
    active_configurations = sorted(
        row['code'] for row in configurations if row.get('status') == status
    )
    configuration_sources: dict[str, str] = {}
    for item in spec['configurations']:
        code = item.get('configuration_code', '')
        source = item.get('source_code', '')
        if not code or not source or code in configuration_sources:
            raise CompletenessError('invalid configuration/source mapping in spec')
        configuration_sources[code] = source
    if sorted(configuration_sources) != active_configurations:
        raise CompletenessError(
            'spec configurations differ from current active configuration scope'
        )

    active_sources = {
        row['code'] for row in sources if row.get('status') == 'active'
    }
    bad_sources = sorted(set(configuration_sources.values()) - active_sources)
    if bad_sources:
        raise CompletenessError(f'inactive or missing sources in spec: {bad_sources}')

    active_attributes = {
        row['code']: row for row in attributes if row.get('status') == 'active'
    }
    slots: list[tuple[str, str]] = []
    for item in spec['technical_slots']:
        slot = (item.get('attribute_code', ''), item.get('fuel_type_code', ''))
        if not slot[0] or slot in slots:
            raise CompletenessError('invalid or duplicate technical slot in spec')
        slots.append(slot)
    slots.sort()
    equipment = sorted(spec['equipment_attributes'])
    if len(equipment) != len(set(equipment)) or any(not item for item in equipment):
        raise CompletenessError('invalid or duplicate equipment attribute in spec')
    missing_attributes = sorted(
        ({item[0] for item in slots} | set(equipment)) - set(active_attributes)
    )
    if missing_attributes:
        raise CompletenessError(
            f'inactive or missing attributes in spec: {missing_attributes}'
        )

    raw_na = spec['not_applicable']
    technical_na = {
        (
            item.get('configuration_code', ''),
            item.get('attribute_code', ''),
            item.get('fuel_type_code', ''),
        )
        for item in raw_na.get('technical', [])
    }
    equipment_na = {
        (item.get('configuration_code', ''), item.get('attribute_code', ''))
        for item in raw_na.get('equipment', [])
    }

    if as_of_value is None:
        dates = [
            iso_date(row['observation_date'], 'observation')
            for row in values + availability
            if row.get('observation_date')
        ]
        if not dates:
            raise CompletenessError('no dated configuration observations found')
        as_of = max(dates)
    else:
        as_of = iso_date(as_of_value, '--as-of')

    scoped_values = [
        row for row in values if row.get('configuration_code') in configuration_sources
    ]
    scoped_availability = [
        row
        for row in availability
        if row.get('configuration_code') in configuration_sources
    ]
    current_values = latest(
        scoped_values,
        ('configuration_code', 'attribute_code', 'fuel_type_code'),
        as_of,
        'configuration values',
    )
    current_availability = latest(
        scoped_availability,
        ('configuration_code', 'attribute_code'),
        as_of,
        'configuration availability',
    )

    allowed_slots = set(slots)
    extra_slots = sorted({(key[1], key[2]) for key in current_values} - allowed_slots)
    if extra_slots:
        raise CompletenessError(
            f'observed technical slots are absent from spec: {extra_slots}'
        )
    extra_equipment = sorted(
        {key[1] for key in current_availability} - set(equipment)
    )
    if extra_equipment:
        raise CompletenessError(
            f'observed equipment attributes are absent from spec: {extra_equipment}'
        )

    technical_scope = {
        (configuration, attribute, fuel)
        for configuration in active_configurations
        for attribute, fuel in slots
    }
    equipment_scope = {
        (configuration, attribute)
        for configuration in active_configurations
        for attribute in equipment
    }
    if not technical_na <= technical_scope:
        raise CompletenessError('technical not_applicable outside denominator')
    if not equipment_na <= equipment_scope:
        raise CompletenessError('equipment not_applicable outside denominator')

    technical = {
        'denominator': len(technical_scope),
        'applicable': 0,
        'present': 0,
        'missing': 0,
        'not_applicable': 0,
    }
    equipment_counts = {
        'denominator': len(equipment_scope),
        'applicable': 0,
        'recorded': 0,
        'missing': 0,
        'not_applicable': 0,
        'standard': 0,
        'optional': 0,
        'not_available': 0,
        'unknown': 0,
    }
    by_configuration: dict[str, dict[str, Any]] = defaultdict(dict)
    by_category: dict[str, dict[str, Any]] = defaultdict(dict)
    by_source: dict[str, dict[str, Any]] = defaultdict(dict)
    technical_gaps: list[dict[str, str]] = []
    equipment_gaps: list[dict[str, str]] = []

    def add(bucket: dict[str, Any], key: str) -> None:
        bucket[key] = int(bucket.get(key, 0)) + 1

    for key in sorted(technical_scope):
        configuration, attribute, fuel = key
        category = active_attributes[attribute]['category']
        source = configuration_sources[configuration]
        if key in technical_na:
            if key in current_values:
                raise CompletenessError(f'not_applicable slot has a record: {key}')
            technical['not_applicable'] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'technical_not_applicable')
            continue
        technical['applicable'] += 1
        for bucket in (
            by_configuration[configuration],
            by_category[category],
            by_source[source],
        ):
            add(bucket, 'technical_applicable')
        row = current_values.get(key)
        if row is None:
            technical['missing'] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'technical_missing')
            technical_gaps.append(
                {
                    'configuration_code': configuration,
                    'source_code': source,
                    'category': category,
                    'attribute_code': attribute,
                    'fuel_type_code': fuel,
                    'state': 'missing',
                }
            )
        else:
            if row.get('source_code') != source:
                raise CompletenessError(
                    f'technical record source differs from spec mapping: {key}'
                )
            technical['present'] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'technical_present')

    for key in sorted(equipment_scope):
        configuration, attribute = key
        category = active_attributes[attribute]['category']
        source = configuration_sources[configuration]
        if key in equipment_na:
            if key in current_availability:
                raise CompletenessError(f'not_applicable pair has a record: {key}')
            equipment_counts['not_applicable'] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'equipment_not_applicable')
            continue
        equipment_counts['applicable'] += 1
        for bucket in (
            by_configuration[configuration],
            by_category[category],
            by_source[source],
        ):
            add(bucket, 'equipment_applicable')
        row = current_availability.get(key)
        if row is None:
            equipment_counts['missing'] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'equipment_missing')
            equipment_gaps.append(
                {
                    'configuration_code': configuration,
                    'source_code': source,
                    'category': category,
                    'attribute_code': attribute,
                    'state': 'missing',
                }
            )
        else:
            if row.get('source_code') != source:
                raise CompletenessError(
                    f'equipment record source differs from spec mapping: {key}'
                )
            state = row.get('availability_status', '')
            if state not in AVAILABILITY_STATES:
                raise CompletenessError(
                    f'unexpected availability status for {key}: {state!r}'
                )
            equipment_counts['recorded'] += 1
            equipment_counts[state] += 1
            for bucket in (
                by_configuration[configuration],
                by_category[category],
                by_source[source],
            ):
                add(bucket, 'equipment_recorded')
                add(bucket, state)

    technical['coverage_percent'] = percentage(
        technical['present'], technical['applicable']
    )
    equipment_counts['coverage_percent'] = percentage(
        equipment_counts['recorded'], equipment_counts['applicable']
    )

    configuration_rows = []
    for code in active_configurations:
        row = dict(by_configuration[code])
        row['configuration_code'] = code
        row['source_code'] = configuration_sources[code]
        row['technical_coverage_percent'] = percentage(
            int(row.get('technical_present', 0)),
            int(row.get('technical_applicable', 0)),
        )
        row['equipment_coverage_percent'] = percentage(
            int(row.get('equipment_recorded', 0)),
            int(row.get('equipment_applicable', 0)),
        )
        configuration_rows.append(dict(sorted(row.items())))

    category_rows = []
    for category in sorted(by_category):
        row = dict(by_category[category])
        row['category'] = category
        row['technical_coverage_percent'] = percentage(
            int(row.get('technical_present', 0)),
            int(row.get('technical_applicable', 0)),
        )
        row['equipment_coverage_percent'] = percentage(
            int(row.get('equipment_recorded', 0)),
            int(row.get('equipment_applicable', 0)),
        )
        category_rows.append(dict(sorted(row.items())))

    source_rows = []
    for source in sorted(by_source):
        row = dict(by_source[source])
        row['source_code'] = source
        row['configuration_codes'] = sorted(
            code for code, mapped in configuration_sources.items() if mapped == source
        )
        row['technical_coverage_percent'] = percentage(
            int(row.get('technical_present', 0)),
            int(row.get('technical_applicable', 0)),
        )
        row['equipment_coverage_percent'] = percentage(
            int(row.get('equipment_recorded', 0)),
            int(row.get('equipment_applicable', 0)),
        )
        source_rows.append(dict(sorted(row.items())))

    return {
        'version': 1,
        'as_of': as_of.isoformat(),
        'scope': {
            'configuration_status': status,
            'active_configurations': len(active_configurations),
            'sources': len(set(configuration_sources.values())),
            'technical_slots': len(slots),
            'equipment_attributes': len(equipment),
        },
        'technical': dict(sorted(technical.items())),
        'equipment': dict(sorted(equipment_counts.items())),
        'by_configuration': configuration_rows,
        'by_category': category_rows,
        'by_source': source_rows,
        'gaps': {
            'technical': technical_gaps,
            'equipment': equipment_gaps,
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def render_markdown(report: Mapping[str, Any]) -> str:
    technical = report['technical']
    equipment = report['equipment']
    scope = report['scope']
    lines = [
        '# Configuration Data Completeness',
        '',
        f"As of: `{report['as_of']}`",
        '',
        '## Scope',
        '',
        '| Metric | Value |',
        '| --- | ---: |',
        f"| Active configurations | {scope['active_configurations']} |",
        f"| Sources | {scope['sources']} |",
        f"| Technical slots | {scope['technical_slots']} |",
        f"| Equipment attributes | {scope['equipment_attributes']} |",
        '',
        '## Summary',
        '',
        '| Domain | Applicable | Complete | Missing | Not applicable | Coverage |',
        '| --- | ---: | ---: | ---: | ---: | ---: |',
        (
            f"| Technical values | {technical['applicable']} | "
            f"{technical['present']} | {technical['missing']} | "
            f"{technical['not_applicable']} | {technical['coverage_percent']}% |"
        ),
        (
            f"| Equipment availability | {equipment['applicable']} | "
            f"{equipment['recorded']} | {equipment['missing']} | "
            f"{equipment['not_applicable']} | {equipment['coverage_percent']}% |"
        ),
        '',
        (
            'Equipment states: '
            f"`standard={equipment['standard']}`, "
            f"`optional={equipment['optional']}`, "
            f"`not_available={equipment['not_available']}`, "
            f"`unknown={equipment['unknown']}`."
        ),
        '',
        '## By configuration',
        '',
        '| Configuration | Source | Technical | Equipment |',
        '| --- | --- | ---: | ---: |',
    ]
    for row in report['by_configuration']:
        lines.append(
            f"| `{row['configuration_code']}` | `{row['source_code']}` | "
            f"{row['technical_coverage_percent']}% | "
            f"{row['equipment_coverage_percent']}% |"
        )
    lines.extend(
        [
            '',
            '## By category',
            '',
            '| Category | Technical | Equipment |',
            '| --- | ---: | ---: |',
        ]
    )
    for row in report['by_category']:
        lines.append(
            f"| {row['category']} | {row['technical_coverage_percent']}% | "
            f"{row['equipment_coverage_percent']}% |"
        )
    lines.extend(
        [
            '',
            '## Technical gaps',
            '',
            '| Configuration | Source | Category | Attribute | Fuel context |',
            '| --- | --- | --- | --- | --- |',
        ]
    )
    if report['gaps']['technical']:
        for gap in report['gaps']['technical']:
            fuel = gap['fuel_type_code'] or 'none'
            lines.append(
                f"| `{gap['configuration_code']}` | `{gap['source_code']}` | "
                f"{gap['category']} | `{gap['attribute_code']}` | `{fuel}` |"
            )
    else:
        lines.append('| — | — | — | — | — |')
    lines.extend(
        [
            '',
            '## Equipment gaps',
            '',
            '| Configuration | Source | Category | Attribute |',
            '| --- | --- | --- | --- |',
        ]
    )
    if report['gaps']['equipment']:
        for gap in report['gaps']['equipment']:
            lines.append(
                f"| `{gap['configuration_code']}` | `{gap['source_code']}` | "
                f"{gap['category']} | `{gap['attribute_code']}` |"
            )
    else:
        lines.append('| — | — | — | — |')
    lines.append('')
    return '\n'.join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.tmp-{os.getpid()}')
    try:
        temporary.write_text(content, encoding='utf-8', newline='\n')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Generate deterministic configuration-data completeness reports '
            'from an explicit denominator spec.'
        )
    )
    parser.add_argument('--spec', type=Path, default=DEFAULT_SPEC)
    parser.add_argument('--as-of')
    parser.add_argument('--json', dest='json_path', type=Path)
    parser.add_argument('--markdown', type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    spec = arguments.spec
    if not spec.is_absolute():
        spec = repository / spec
    try:
        report = collect_report(repository, spec, arguments.as_of)
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(f'JSON completeness report written to {arguments.json_path}')
        if arguments.markdown is not None:
            write_atomic(arguments.markdown, render_markdown(report))
            print(f'Markdown completeness report written to {arguments.markdown}')
        print('Configuration data completeness')
        print('-------------------------------')
        print(f"As of                  : {report['as_of']}")
        print(f"Active configurations  : {report['scope']['active_configurations']}")
        print(f"Technical coverage      : {report['technical']['coverage_percent']}%")
        print(f"Technical gaps          : {report['technical']['missing']}")
        print(f"Equipment coverage      : {report['equipment']['coverage_percent']}%")
        print(f"Equipment gaps          : {report['equipment']['missing']}")
        return 0
    except CompletenessError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
