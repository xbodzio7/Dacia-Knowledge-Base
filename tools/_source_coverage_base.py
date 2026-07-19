#!/usr/bin/env python3
"""Generate deterministic source-coverage reports for Dacia Knowledge Base."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from configuration_value_range_reporting import (
    combine_latest_observations,
    read_optional_ranges,
)


DEFAULT_SPEC = Path("data/reporting/configuration_completeness.json")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class SourceCoverageError(RuntimeError):
    """Controlled source-coverage failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise SourceCoverageError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise SourceCoverageError(f"cannot read UTF-8 CSV {path}: {exc}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceCoverageError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SourceCoverageError(f"JSON root must be an object: {path}")
    return value


def iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SourceCoverageError(
            f"invalid ISO date for {label}: {value!r}"
        ) from exc


def percentage(complete: int, applicable: int) -> str:
    if applicable == 0:
        return "100.00"
    return f"{complete * 100 / applicable:.2f}"


def latest_records(
    rows: Iterable[dict[str, str]],
    key_fields: Sequence[str],
    date_field: str,
    as_of: date,
    label: str,
) -> dict[tuple[str, ...], dict[str, str]]:
    chosen: dict[tuple[str, ...], tuple[date, dict[str, str]]] = {}
    for row in rows:
        observed = iso_date(row.get(date_field, ""), label)
        if observed > as_of:
            continue
        key = tuple(row.get(field, "") for field in key_fields)
        for field, item in zip(key_fields, key):
            if not item and field != "fuel_type_code":
                raise SourceCoverageError(f"{label} has incomplete key: {key}")
        previous = chosen.get(key)
        if previous is None or observed > previous[0]:
            chosen[key] = (observed, row)
        elif observed == previous[0]:
            raise SourceCoverageError(
                f"{label} has duplicate current records for {key} on {observed}"
            )
    return {key: item[1] for key, item in chosen.items()}


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SourceCoverageError(f"{label} must be a list")
    return value


def parse_scope(
    repository: Path,
    spec_path: Path,
) -> tuple[
    dict[str, str],
    dict[str, tuple[str, str]],
    list[tuple[str, str]],
    list[str],
    set[tuple[str, str, str]],
    set[tuple[str, str]],
    dict[str, dict[str, str]],
]:
    spec = read_json(spec_path)
    if spec.get("version") != 1:
        raise SourceCoverageError("configuration completeness spec version must be 1")
    status = spec.get("configuration_status")
    if not isinstance(status, str) or not status:
        raise SourceCoverageError("configuration_status must be non-empty")

    master = repository / "data" / "master"
    configurations = read_csv(master / "configurations.csv")
    versions = read_csv(master / "versions.csv")
    attributes = read_csv(master / "attributes.csv")

    active_configurations = {
        row["code"]: row
        for row in configurations
        if row.get("status") == status
    }
    version_models = {
        row["code"]: row.get("model_code", "")
        for row in versions
    }
    attribute_rows = {
        row["code"]: row
        for row in attributes
        if row.get("status") == "active"
    }

    configuration_sources: dict[str, str] = {}
    configuration_entities: dict[str, tuple[str, str]] = {}
    for item in require_list(spec.get("configurations"), "configurations"):
        if not isinstance(item, dict):
            raise SourceCoverageError("configuration entries must be objects")
        configuration_code = item.get("configuration_code")
        source_code = item.get("source_code")
        if not isinstance(configuration_code, str) or not configuration_code:
            raise SourceCoverageError("configuration_code must be non-empty")
        if not isinstance(source_code, str) or not source_code:
            raise SourceCoverageError("source_code must be non-empty")
        if configuration_code in configuration_sources:
            raise SourceCoverageError(
                f"duplicate configuration in spec: {configuration_code}"
            )
        configuration_sources[configuration_code] = source_code

        configuration = active_configurations.get(configuration_code)
        if configuration is None:
            raise SourceCoverageError(
                "spec configurations differ from current active configuration scope"
            )
        version_code = configuration.get("version_code", "")
        model_code = version_models.get(version_code, "")
        if not version_code or not model_code:
            raise SourceCoverageError(
                f"cannot resolve version/model for {configuration_code}"
            )
        configuration_entities[configuration_code] = (
            version_code,
            model_code,
        )

    if sorted(configuration_sources) != sorted(active_configurations):
        raise SourceCoverageError(
            "spec configurations differ from current active configuration scope"
        )

    technical_slots: list[tuple[str, str]] = []
    for item in require_list(spec.get("technical_slots"), "technical_slots"):
        if not isinstance(item, dict):
            raise SourceCoverageError("technical slot entries must be objects")
        attribute_code = item.get("attribute_code")
        fuel_type_code = item.get("fuel_type_code", "")
        if not isinstance(attribute_code, str) or not attribute_code:
            raise SourceCoverageError("technical attribute_code must be non-empty")
        if not isinstance(fuel_type_code, str):
            raise SourceCoverageError("technical fuel_type_code must be a string")
        slot = (attribute_code, fuel_type_code)
        if slot in technical_slots:
            raise SourceCoverageError(f"duplicate technical slot: {slot}")
        technical_slots.append(slot)
    technical_slots.sort()

    raw_equipment = require_list(
        spec.get("equipment_attributes"),
        "equipment_attributes",
    )
    if any(not isinstance(item, str) or not item for item in raw_equipment):
        raise SourceCoverageError("equipment_attributes contains an invalid value")
    equipment_attributes = sorted(raw_equipment)
    if len(equipment_attributes) != len(set(equipment_attributes)):
        raise SourceCoverageError("equipment_attributes contains duplicates")

    scoped_attributes = {
        attribute_code for attribute_code, _ in technical_slots
    } | set(equipment_attributes)
    missing_attributes = sorted(scoped_attributes - set(attribute_rows))
    if missing_attributes:
        raise SourceCoverageError(
            f"spec references inactive or missing attributes: {missing_attributes}"
        )

    raw_not_applicable = spec.get("not_applicable", {})
    if not isinstance(raw_not_applicable, dict):
        raise SourceCoverageError("not_applicable must be an object")

    technical_not_applicable: set[tuple[str, str, str]] = set()
    for item in require_list(
        raw_not_applicable.get("technical", []),
        "not_applicable.technical",
    ):
        if not isinstance(item, dict):
            raise SourceCoverageError(
                "technical not_applicable entries must be objects"
            )
        key = (
            str(item.get("configuration_code", "")),
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
        )
        if not key[0] or not key[1] or key in technical_not_applicable:
            raise SourceCoverageError(
                f"invalid technical not_applicable entry: {key}"
            )
        technical_not_applicable.add(key)

    equipment_not_applicable: set[tuple[str, str]] = set()
    for item in require_list(
        raw_not_applicable.get("equipment", []),
        "not_applicable.equipment",
    ):
        if not isinstance(item, dict):
            raise SourceCoverageError(
                "equipment not_applicable entries must be objects"
            )
        key = (
            str(item.get("configuration_code", "")),
            str(item.get("attribute_code", "")),
        )
        if not key[0] or not key[1] or key in equipment_not_applicable:
            raise SourceCoverageError(
                f"invalid equipment not_applicable entry: {key}"
            )
        equipment_not_applicable.add(key)

    return (
        configuration_sources,
        configuration_entities,
        technical_slots,
        equipment_attributes,
        technical_not_applicable,
        equipment_not_applicable,
        attribute_rows,
    )


def section_status(
    expected: int,
    present: int,
    source_registered: bool,
) -> str:
    if not source_registered:
        return "source_missing"
    if expected == 0:
        return "not_applicable"
    if present == 0:
        return "missing"
    if present < expected:
        return "partial"
    return "covered"


def collect_report(
    repository: Path,
    spec_path: Path,
    as_of_value: str | None = None,
) -> dict[str, Any]:
    master = repository / "data" / "master"
    sources = read_csv(master / "sources.csv")
    source_models = read_csv(master / "source_models.csv")
    source_versions = read_csv(master / "source_versions.csv")
    source_configurations = read_csv(master / "source_configurations.csv")
    prices = read_csv(master / "configuration_prices.csv")
    values = read_csv(master / "configuration_attribute_values.csv")
    ranges = read_optional_ranges(master, read_csv)
    availability = read_csv(
        master / "configuration_attribute_availability.csv"
    )

    (
        configuration_sources,
        configuration_entities,
        technical_slots,
        equipment_attributes,
        technical_not_applicable,
        equipment_not_applicable,
        attribute_rows,
    ) = parse_scope(repository, spec_path)

    scoped_source_codes = sorted(set(configuration_sources.values()))
    source_rows = {row.get("code", ""): row for row in sources if row.get("code")}

    if as_of_value is None:
        dated_values: list[date] = []
        for row in sources:
            if row.get("code") in scoped_source_codes and row.get("document_date"):
                dated_values.append(
                    iso_date(row["document_date"], "source document_date")
                )
        for rows, field, label in (
            (prices, "price_date", "configuration price"),
            (values, "observation_date", "configuration value"),
            (ranges, "observation_date", "configuration value range"),
            (
                availability,
                "observation_date",
                "configuration availability",
            ),
        ):
            for row in rows:
                if (
                    row.get("configuration_code") in configuration_sources
                    and row.get(field)
                ):
                    dated_values.append(iso_date(row[field], label))
        if not dated_values:
            raise SourceCoverageError("no dated source-backed records found")
        as_of = max(dated_values)
    else:
        as_of = iso_date(as_of_value, "--as-of")

    source_registration = {
        "expected": len(scoped_source_codes),
        "registered": 0,
        "missing": 0,
        "inactive": 0,
        "future": 0,
        "metadata_complete": 0,
    }
    registration_state: dict[str, str] = {}
    metadata_by_source: dict[str, dict[str, str]] = {}

    for source_code in scoped_source_codes:
        row = source_rows.get(source_code)
        if row is None:
            registration_state[source_code] = "missing"
            source_registration["missing"] += 1
            continue
        if row.get("status") != "active":
            registration_state[source_code] = "inactive"
            source_registration["inactive"] += 1
            continue
        document_date = iso_date(
            row.get("document_date", ""),
            f"source {source_code} document_date",
        )
        if document_date > as_of:
            registration_state[source_code] = "future"
            source_registration["future"] += 1
            continue
        sha256 = row.get("sha256", "")
        file_path = row.get("file_path", "")
        if not SHA256_PATTERN.fullmatch(sha256):
            raise SourceCoverageError(
                f"source {source_code} has invalid SHA-256: {sha256!r}"
            )
        if not file_path:
            raise SourceCoverageError(
                f"source {source_code} has empty file_path"
            )
        registration_state[source_code] = "registered"
        source_registration["registered"] += 1
        source_registration["metadata_complete"] += 1
        metadata_by_source[source_code] = {
            "title": row.get("title", ""),
            "publisher": row.get("publisher", ""),
            "market": row.get("market", ""),
            "document_date": document_date.isoformat(),
            "external_reference": row.get("external_reference", ""),
            "file_path": file_path,
            "sha256": sha256,
        }

    scoped_configurations = set(configuration_sources)
    scoped_values = [
        row for row in values
        if row.get("configuration_code") in scoped_configurations
    ]
    scoped_ranges = [
        row for row in ranges
        if row.get("configuration_code") in scoped_configurations
    ]
    scoped_availability = [
        row for row in availability
        if row.get("configuration_code") in scoped_configurations
    ]
    scoped_prices = [
        row for row in prices
        if row.get("configuration_code") in scoped_configurations
    ]

    current_scalar_values = latest_records(
        scoped_values,
        ("configuration_code", "attribute_code", "fuel_type_code"),
        "observation_date",
        as_of,
        "configuration values",
    )
    current_range_values = latest_records(
        scoped_ranges,
        ("configuration_code", "attribute_code", "fuel_type_code"),
        "observation_date",
        as_of,
        "configuration value ranges",
    )
    current_values = combine_latest_observations(
        current_scalar_values, current_range_values, SourceCoverageError
    )
    current_availability = latest_records(
        scoped_availability,
        ("configuration_code", "attribute_code"),
        "observation_date",
        as_of,
        "configuration availability",
    )
    current_prices = latest_records(
        scoped_prices,
        ("configuration_code", "market", "price_type"),
        "price_date",
        as_of,
        "configuration prices",
    )

    for key, row in current_values.items():
        configuration_code = key[0]
        expected_source = configuration_sources[configuration_code]
        if row.get("source_code") != expected_source:
            raise SourceCoverageError(
                "technical record source differs from scope mapping: "
                f"{key} -> {row.get('source_code')!r}"
            )
    for key, row in current_availability.items():
        configuration_code = key[0]
        expected_source = configuration_sources[configuration_code]
        if row.get("source_code") != expected_source:
            raise SourceCoverageError(
                "equipment record source differs from scope mapping: "
                f"{key} -> {row.get('source_code')!r}"
            )
    for key, row in current_prices.items():
        configuration_code = key[0]
        expected_source = configuration_sources[configuration_code]
        if row.get("source_code") != expected_source:
            raise SourceCoverageError(
                "price record source differs from scope mapping: "
                f"{key} -> {row.get('source_code')!r}"
            )

    source_model_pairs = {
        (row.get("source_code", ""), row.get("model_code", ""))
        for row in source_models
    }
    source_version_pairs = {
        (row.get("source_code", ""), row.get("version_code", ""))
        for row in source_versions
    }
    source_configuration_pairs = {
        (
            row.get("source_code", ""),
            row.get("configuration_code", ""),
        )
        for row in source_configurations
    }

    technical_categories: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for slot in technical_slots:
        technical_categories[attribute_rows[slot[0]]["category"]].append(slot)
    equipment_categories: dict[str, list[str]] = defaultdict(list)
    for attribute_code in equipment_attributes:
        equipment_categories[attribute_rows[attribute_code]["category"]].append(
            attribute_code
        )

    record_summary = {
        "identity_links": {
            "expected": 3 * len(configuration_sources),
            "present": 0,
            "missing": 0,
            "source_missing": 0,
        },
        "prices": {
            "expected": len(configuration_sources),
            "present": 0,
            "missing": 0,
            "source_missing": 0,
            "records": 0,
        },
        "technical": {
            "expected": 0,
            "present": 0,
            "missing": 0,
            "not_applicable": 0,
            "source_missing": 0,
        },
        "equipment": {
            "expected": 0,
            "present": 0,
            "missing": 0,
            "not_applicable": 0,
            "source_missing": 0,
        },
    }
    area_summary = {
        "denominator": 4 * len(configuration_sources),
        "covered": 0,
        "partial": 0,
        "missing": 0,
        "source_missing": 0,
    }
    section_summary = {
        "denominator": 0,
        "covered": 0,
        "partial": 0,
        "missing": 0,
        "not_applicable": 0,
        "source_missing": 0,
    }

    source_reports: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []

    for configuration_code in sorted(configuration_sources):
        source_code = configuration_sources[configuration_code]
        version_code, model_code = configuration_entities[configuration_code]
        registered = registration_state[source_code] == "registered"

        model_present = (source_code, model_code) in source_model_pairs
        version_present = (source_code, version_code) in source_version_pairs
        configuration_present = (
            source_code,
            configuration_code,
        ) in source_configuration_pairs
        identity_present_count = sum(
            (model_present, version_present, configuration_present)
        )

        if not registered:
            record_summary["identity_links"]["source_missing"] += 3
        else:
            record_summary["identity_links"]["present"] += identity_present_count
            record_summary["identity_links"]["missing"] += 3 - identity_present_count

        source_price_rows = [
            row
            for key, row in current_prices.items()
            if key[0] == configuration_code
        ]
        price_present = bool(source_price_rows)
        record_summary["prices"]["records"] += len(source_price_rows)
        if not registered:
            record_summary["prices"]["source_missing"] += 1
        elif price_present:
            record_summary["prices"]["present"] += 1
        else:
            record_summary["prices"]["missing"] += 1

        sections: list[dict[str, Any]] = []

        def add_section(
            area: str,
            section: str,
            expected: int,
            present: int,
        ) -> None:
            status = section_status(expected, present, registered)
            section_summary["denominator"] += 1
            section_summary[status] += 1
            sections.append(
                {
                    "area": area,
                    "section": section,
                    "expected": expected,
                    "present": present,
                    "missing": max(expected - present, 0),
                    "status": status,
                }
            )

        add_section("identity", "model", 1, int(model_present))
        add_section("identity", "version", 1, int(version_present))
        add_section(
            "identity",
            "configuration",
            1,
            int(configuration_present),
        )
        add_section("commercial", "prices", 1, int(price_present))

        technical_expected = 0
        technical_present = 0
        technical_not_applicable_count = 0
        for category in sorted(technical_categories):
            expected = 0
            present = 0
            for attribute_code, fuel_type_code in technical_categories[category]:
                key = (
                    configuration_code,
                    attribute_code,
                    fuel_type_code,
                )
                if key in technical_not_applicable:
                    technical_not_applicable_count += 1
                    record_summary["technical"]["not_applicable"] += 1
                    continue
                expected += 1
                technical_expected += 1
                record_summary["technical"]["expected"] += 1
                if not registered:
                    record_summary["technical"]["source_missing"] += 1
                    continue
                if key in current_values:
                    present += 1
                    technical_present += 1
                    record_summary["technical"]["present"] += 1
                else:
                    record_summary["technical"]["missing"] += 1
                    gaps.append(
                        {
                            "source_code": source_code,
                            "configuration_code": configuration_code,
                            "area": "technical",
                            "section": category,
                            "attribute_code": attribute_code,
                            "fuel_type_code": fuel_type_code,
                            "state": "record_missing",
                        }
                    )
            add_section("technical", category, expected, present)

        equipment_expected = 0
        equipment_present = 0
        equipment_not_applicable_count = 0
        for category in sorted(equipment_categories):
            expected = 0
            present = 0
            for attribute_code in equipment_categories[category]:
                key = (configuration_code, attribute_code)
                if key in equipment_not_applicable:
                    equipment_not_applicable_count += 1
                    record_summary["equipment"]["not_applicable"] += 1
                    continue
                expected += 1
                equipment_expected += 1
                record_summary["equipment"]["expected"] += 1
                if not registered:
                    record_summary["equipment"]["source_missing"] += 1
                    continue
                if key in current_availability:
                    present += 1
                    equipment_present += 1
                    record_summary["equipment"]["present"] += 1
                else:
                    record_summary["equipment"]["missing"] += 1
                    gaps.append(
                        {
                            "source_code": source_code,
                            "configuration_code": configuration_code,
                            "area": "equipment",
                            "section": category,
                            "attribute_code": attribute_code,
                            "fuel_type_code": "",
                            "state": "record_missing",
                        }
                    )
            add_section("equipment", category, expected, present)

        area_rows = [
            {
                "area": "identity",
                "expected": 3,
                "present": identity_present_count,
                "missing": 3 - identity_present_count,
                "status": section_status(3, identity_present_count, registered),
            },
            {
                "area": "commercial",
                "expected": 1,
                "present": int(price_present),
                "missing": int(not price_present),
                "status": section_status(1, int(price_present), registered),
            },
            {
                "area": "technical",
                "expected": technical_expected,
                "present": technical_present,
                "missing": max(technical_expected - technical_present, 0),
                "not_applicable": technical_not_applicable_count,
                "status": section_status(
                    technical_expected,
                    technical_present,
                    registered,
                ),
            },
            {
                "area": "equipment",
                "expected": equipment_expected,
                "present": equipment_present,
                "missing": max(equipment_expected - equipment_present, 0),
                "not_applicable": equipment_not_applicable_count,
                "status": section_status(
                    equipment_expected,
                    equipment_present,
                    registered,
                ),
            },
        ]
        for area in area_rows:
            area_summary[area["status"]] += 1

        observation_dates: dict[str, list[str]] = {}
        for label, rows, field in (
            ("prices", source_price_rows, "price_date"),
            (
                "technical",
                [
                    row
                    for key, row in current_values.items()
                    if key[0] == configuration_code
                ],
                "observation_date",
            ),
            (
                "equipment",
                [
                    row
                    for key, row in current_availability.items()
                    if key[0] == configuration_code
                ],
                "observation_date",
            ),
        ):
            observation_dates[label] = sorted(
                {row.get(field, "") for row in rows if row.get(field)}
            )

        source_report: dict[str, Any] = {
            "source_code": source_code,
            "registration_state": registration_state[source_code],
            "configuration_code": configuration_code,
            "version_code": version_code,
            "model_code": model_code,
            "areas": area_rows,
            "sections": sections,
            "observation_dates": observation_dates,
        }
        source_report.update(metadata_by_source.get(source_code, {}))
        source_reports.append(source_report)

    for domain in ("technical", "equipment"):
        counts = record_summary[domain]
        counts["coverage_percent"] = percentage(
            counts["present"],
            counts["expected"] - counts["source_missing"],
        )

    out_of_scope: dict[str, dict[str, Any]] = {}
    for label, rows in (
        ("source_models", source_models),
        ("source_versions", source_versions),
        ("source_configurations", source_configurations),
        ("configuration_prices", prices),
        ("configuration_attribute_values", values),
        ("configuration_attribute_value_ranges", ranges),
        ("configuration_attribute_availability", availability),
    ):
        codes = sorted(
            {
                row.get("source_code", "")
                for row in rows
                if row.get("source_code")
                and row.get("source_code") not in scoped_source_codes
            }
        )
        out_of_scope[label] = {
            "records": sum(
                1
                for row in rows
                if row.get("source_code")
                and row.get("source_code") not in scoped_source_codes
            ),
            "source_codes": codes,
        }

    return {
        "version": 1,
        "as_of": as_of.isoformat(),
        "scope": {
            "configurations": len(configuration_sources),
            "expected_sources": len(scoped_source_codes),
            "technical_slots_per_configuration": len(technical_slots),
            "equipment_attributes_per_configuration": len(
                equipment_attributes
            ),
        },
        "source_registration": dict(sorted(source_registration.items())),
        "areas": dict(sorted(area_summary.items())),
        "sections": dict(sorted(section_summary.items())),
        "records": {
            key: dict(sorted(value.items()))
            for key, value in sorted(record_summary.items())
        },
        "sources": source_reports,
        "gaps": gaps,
        "out_of_scope": out_of_scope,
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    registration = report["source_registration"]
    records = report["records"]
    sections = report["sections"]
    lines = [
        "# Source Coverage",
        "",
        f"As of: `{report['as_of']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Expected sources | {registration['expected']} |",
        f"| Registered sources | {registration['registered']} |",
        f"| Missing sources | {registration['missing']} |",
        f"| Inactive sources | {registration['inactive']} |",
        f"| Future sources | {registration['future']} |",
        f"| Identity links | {records['identity_links']['present']}/{records['identity_links']['expected']} |",
        f"| Sources with prices | {records['prices']['present']}/{records['prices']['expected']} |",
        f"| Technical records | {records['technical']['present']}/{records['technical']['expected']} ({records['technical']['coverage_percent']}%) |",
        f"| Equipment records | {records['equipment']['present']}/{records['equipment']['expected']} ({records['equipment']['coverage_percent']}%) |",
        f"| Partial sections | {sections['partial']} |",
        f"| Missing sections | {sections['missing']} |",
        "",
        "## Sources",
        "",
        "| Source | Date | SHA-256 | Configuration | Identity | Price | Technical | Equipment |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for source in report["sources"]:
        areas = {item["area"]: item for item in source["areas"]}
        sha256 = source.get("sha256", "—")
        source_date = source.get("document_date", "—")
        lines.append(
            f"| `{source['source_code']}` | `{source_date}` | `{sha256}` | "
            f"`{source['configuration_code']}` | "
            f"{areas['identity']['present']}/{areas['identity']['expected']} | "
            f"{areas['commercial']['present']}/{areas['commercial']['expected']} | "
            f"{areas['technical']['present']}/{areas['technical']['expected']} | "
            f"{areas['equipment']['present']}/{areas['equipment']['expected']} |"
        )

    lines.extend(
        [
            "",
            "## Incomplete sections",
            "",
            "| Source | Area | Section | Present | Expected | Status |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    incomplete = [
        (source, section)
        for source in report["sources"]
        for section in source["sections"]
        if section["status"] not in {"covered", "not_applicable"}
    ]
    if not incomplete:
        lines.append("| — | — | — | — | — | — |")
    else:
        for source, section in incomplete:
            lines.append(
                f"| `{source['source_code']}` | {section['area']} | "
                f"{section['section']} | {section['present']} | "
                f"{section['expected']} | `{section['status']}` |"
            )

    lines.extend(
        [
            "",
            "## Missing records in registered sources",
            "",
            "| Source | Configuration | Area | Section | Attribute | Fuel context |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if not report["gaps"]:
        lines.append("| — | — | — | — | — | — |")
    else:
        for gap in report["gaps"]:
            fuel = gap["fuel_type_code"] or "none"
            lines.append(
                f"| `{gap['source_code']}` | `{gap['configuration_code']}` | "
                f"{gap['area']} | {gap['section']} | "
                f"`{gap['attribute_code']}` | `{fuel}` |"
            )

    lines.append("")
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic source-registration, area and record "
            "coverage reports."
        )
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=DEFAULT_SPEC,
        help="Configuration completeness denominator specification.",
    )
    parser.add_argument(
        "--as-of",
        help="Optional inclusive snapshot date in YYYY-MM-DD form.",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    spec_path = arguments.spec
    if not spec_path.is_absolute():
        spec_path = repository / spec_path
    try:
        report = collect_report(repository, spec_path, arguments.as_of)
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(f"JSON source coverage report written to {arguments.json_path}")
        if arguments.markdown is not None:
            write_atomic(arguments.markdown, render_markdown(report))
            print(
                "Markdown source coverage report written to "
                f"{arguments.markdown}"
            )
        registration = report["source_registration"]
        technical = report["records"]["technical"]
        equipment = report["records"]["equipment"]
        print("Source coverage")
        print("---------------")
        print(f"As of                  : {report['as_of']}")
        print(
            "Registered sources     : "
            f"{registration['registered']}/{registration['expected']}"
        )
        print(
            "Missing sources        : "
            f"{registration['missing'] + registration['inactive'] + registration['future']}"
        )
        print(
            "Technical coverage     : "
            f"{technical['coverage_percent']}%"
        )
        print(f"Technical record gaps  : {technical['missing']}")
        print(
            "Equipment coverage     : "
            f"{equipment['coverage_percent']}%"
        )
        print(f"Equipment record gaps  : {equipment['missing']}")
        print(f"Missing sections       : {report['sections']['missing']}")
        return 0
    except SourceCoverageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
