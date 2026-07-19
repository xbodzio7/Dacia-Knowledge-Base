from __future__ import annotations

import csv
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from reporting.deterministic_xlsx_model import Cell, Sheet, WorkbookError

WORKBOOK_VERSION = 1
DOMAIN_ORDER = ("prices", "technical", "equipment")
STATE_FIELDS = (
    "state",
    "data_type",
    "value",
    "minimum_value",
    "maximum_value",
    "lower_inclusive",
    "upper_inclusive",
    "source_code",
    "observation_date",
    "reason_code",
    "reviewed_pages",
    "evidence_basis_json",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise WorkbookError(f"cannot read workbook source table {path}: {exc}") from exc


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkbookError(f"cannot read workbook JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkbookError(f"workbook JSON root must be an object: {path}")
    return value


def _date(value: object) -> object:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return str(value)


def _typed(value: object, data_type: str) -> object:
    if value is None or value == "":
        return None
    if data_type == "integer":
        try:
            return int(Decimal(str(value)))
        except (InvalidOperation, ValueError) as exc:
            raise WorkbookError(f"invalid integer workbook value: {value!r}") from exc
    if data_type == "decimal":
        try:
            number = Decimal(str(value))
        except InvalidOperation as exc:
            raise WorkbookError(f"invalid decimal workbook value: {value!r}") from exc
        if not number.is_finite():
            raise WorkbookError(f"non-finite workbook value: {value!r}")
        return number
    if data_type == "boolean":
        if isinstance(value, bool):
            return value
        if str(value) not in {"true", "false"}:
            raise WorkbookError(f"invalid boolean workbook value: {value!r}")
        return str(value) == "true"
    return str(value)


def _state_values(state: Mapping[str, Any], domain: str) -> tuple[object, ...]:
    data_type = str(state.get("data_type", ""))
    scalar: object = None
    minimum: object = None
    maximum: object = None
    if domain == "prices":
        data_type = "decimal"
        scalar = _typed(state.get("amount"), data_type)
    elif domain == "technical":
        if "minimum_value" in state:
            minimum = _typed(state.get("minimum_value"), data_type)
            maximum = _typed(state.get("maximum_value"), data_type)
        else:
            scalar = _typed(
                state.get("normalized_value", state.get("value")),
                data_type,
            )
    else:
        data_type = "text"
        scalar = state.get("availability_status") or None
    reviewed = state.get("reviewed_pages", [])
    reviewed_text = ";".join(str(item) for item in reviewed) if isinstance(reviewed, list) else ""
    basis = state.get("basis")
    basis_text = (
        json.dumps(basis, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if isinstance(basis, dict)
        else ""
    )
    observation_key = "price_date" if domain == "prices" else "observation_date"
    return (
        str(state.get("state", "")),
        data_type,
        scalar,
        minimum,
        maximum,
        state.get("lower_inclusive") if "lower_inclusive" in state else None,
        state.get("upper_inclusive") if "upper_inclusive" in state else None,
        str(state.get("source_code", "")),
        _date(state.get(observation_key)),
        str(state.get("reason_code", "")),
        reviewed_text,
        basis_text,
    )


def _item_identity(item: Mapping[str, Any], domain: str) -> tuple[str, str, str, str, str]:
    if domain == "prices":
        context = (
            f"market={item.get('market', '')};"
            f"price_type={item.get('price_type', '')};"
            f"currency_code={item.get('currency_code', '')}"
        )
        return (
            str(item.get("price_type", "")),
            "",
            "",
            context,
            str(item.get("currency_code", "")),
        )
    context = (
        f"fuel_type_code={item.get('fuel_type_code', '')}"
        if domain == "technical" and item.get("fuel_type_code")
        else ""
    )
    return (
        str(item.get("attribute_code", "")),
        str(item.get("attribute_name", "")),
        str(item.get("category", "")),
        context,
        str(item.get("unit", "")),
    )


def _comparison_headers() -> tuple[str, ...]:
    common = (
        "scope",
        "report_as_of",
        "pair_code",
        "pair_type",
        "domain",
        "comparison",
        "item_code",
        "item_name",
        "category",
        "context",
        "unit",
        "range_relation",
    )
    identity = ("configuration_code", "version_code", "transmission_type")
    left = tuple(f"left_{field}" for field in (*identity, *STATE_FIELDS))
    right = tuple(f"right_{field}" for field in (*identity, *STATE_FIELDS))
    return (*common, *left, *right, "delta_right_minus_left")


def _comparison_rows(reports: Mapping[str, Mapping[str, Any]]) -> list[tuple[object, ...]]:
    rows: list[tuple[object, ...]] = [_comparison_headers()]
    for scope in sorted(reports):
        report = reports[scope]
        for pair in report.get("pairs", []):
            left_configuration = pair["left_configuration"]
            right_configuration = pair["right_configuration"]
            for domain in DOMAIN_ORDER:
                for item in pair.get(domain, []):
                    item_code, item_name, category, context, unit = _item_identity(item, domain)
                    delta = (
                        _typed(item.get("amount_delta_right_minus_left"), "decimal")
                        if domain == "prices"
                        else None
                    )
                    rows.append(
                        (
                            scope,
                            _date(report.get("as_of")),
                            str(pair.get("pair_code", "")),
                            str(pair.get("pair_type", "")),
                            domain,
                            str(item.get("comparison", "")),
                            item_code,
                            item_name,
                            category,
                            context,
                            unit,
                            str(item.get("range_relation", "")),
                            str(left_configuration.get("configuration_code", "")),
                            str(left_configuration.get("version_code", "")),
                            str(left_configuration.get("transmission_type", "")),
                            *_state_values(item.get("left", {}), domain),
                            str(right_configuration.get("configuration_code", "")),
                            str(right_configuration.get("version_code", "")),
                            str(right_configuration.get("transmission_type", "")),
                            *_state_values(item.get("right", {}), domain),
                            delta,
                        )
                    )
    return rows


def _load_reports(build_root: Path, manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for group in manifest.get("groups", []):
        if group.get("status") != "comparable":
            continue
        record = group.get("files", {}).get("json")
        if not isinstance(record, dict):
            raise WorkbookError(f"comparable scope has no JSON report: {group.get('scope')}")
        reports[str(group["scope"])] = _read_json(build_root / str(record["path"]))
    return reports


def _scope_rows(manifest: Mapping[str, Any], reports: Mapping[str, Mapping[str, Any]]) -> list[tuple[object, ...]]:
    headers = (
        "scope", "status", "source_completeness_spec", "source_evidence_spec",
        "report_as_of", "configuration_count", "configuration_codes", "pair_count",
        "total_differences", "prices_comparisons", "prices_equal", "prices_different",
        "prices_not_comparable", "technical_comparisons", "technical_equal",
        "technical_different", "technical_not_comparable", "equipment_comparisons",
        "equipment_equal", "equipment_different", "equipment_not_comparable",
        "evidence_total", "evidence_ambiguous", "evidence_found",
        "evidence_not_stated", "evidence_out_of_scope", "json_path", "json_sha256",
        "markdown_path", "markdown_sha256", "csv_path", "csv_sha256", "html_path",
        "html_sha256",
    )
    rows: list[tuple[object, ...]] = [headers]
    for group in sorted(manifest.get("groups", []), key=lambda item: str(item["scope"])):
        scope = str(group["scope"])
        report = reports.get(scope, {})
        summary = report.get("summary", {})
        evidence = group.get("evidence_summary", report.get("evidence_summary", {}))
        files = group.get("files", {})
        domain_values: list[object] = []
        for domain in DOMAIN_ORDER:
            current = summary.get(domain, {})
            domain_values.extend(
                current.get(key, 0) for key in ("comparisons", "equal", "different", "not_comparable")
            )
        file_values: list[object] = []
        for kind in ("json", "markdown", "csv", "html"):
            record = files.get(kind, {})
            file_values.extend((record.get("path", ""), record.get("sha256", "")))
        codes = list(group.get("configuration_codes", []))
        rows.append(
            (
                scope, str(group.get("status", "")),
                str(group.get("source_completeness_spec", "")),
                str(group.get("source_evidence_spec", "")),
                _date(group.get("report_as_of")), len(codes),
                Cell(";".join(str(code) for code in codes), "wrap"),
                int(group.get("pair_count", 0)), int(group.get("total_differences", 0)),
                *domain_values,
                int(evidence.get("total", 0)), int(evidence.get("ambiguous", 0)),
                int(evidence.get("found", 0)), int(evidence.get("not_stated", 0)),
                int(evidence.get("out_of_scope", 0)), *file_values,
            )
        )
    return rows


def _configuration_rows(repository: Path, manifest: Mapping[str, Any]) -> tuple[list[tuple[object, ...]], set[str]]:
    master = repository / "data" / "master"
    configurations = {row["code"]: row for row in _read_csv(master / "configurations.csv")}
    versions = {row["code"]: row for row in _read_csv(master / "versions.csv")}
    models = {row["code"]: row for row in _read_csv(master / "models.csv")}
    source_by_code: dict[str, str] = {}
    group_by_code: dict[str, tuple[str, str]] = {}
    for group in manifest.get("groups", []):
        spec = _read_json(repository / "data" / "reporting" / str(group["source_completeness_spec"]))
        for item in spec.get("configurations", []):
            source_by_code[str(item["configuration_code"])] = str(item["source_code"])
        for code in group.get("configuration_codes", []):
            group_by_code[str(code)] = (str(group["scope"]), str(group["status"]))
    headers = (
        "scope", "group_status", "configuration_code", "model_code", "model_name",
        "version_code", "version_name", "powertrain_label", "transmission_type",
        "source_code",
    )
    rows: list[tuple[object, ...]] = [headers]
    sources: set[str] = set()
    for code in sorted(group_by_code, key=lambda item: (group_by_code[item][0], item)):
        configuration = configurations.get(code)
        if configuration is None:
            raise WorkbookError(f"workbook configuration missing from master data: {code}")
        version = versions.get(str(configuration.get("version_code", "")))
        if version is None:
            raise WorkbookError(f"workbook configuration has unknown version: {code}")
        model = models.get(str(version.get("model_code", "")))
        if model is None:
            raise WorkbookError(f"workbook version has unknown model: {version.get('code')}")
        source = source_by_code.get(code, "")
        if not source:
            raise WorkbookError(f"workbook configuration has no source mapping: {code}")
        sources.add(source)
        scope, status = group_by_code[code]
        rows.append(
            (
                scope, status, code, str(model.get("code", "")),
                str(model.get("name", "")), str(version.get("code", "")),
                str(version.get("name", "")), str(configuration.get("powertrain_label", "")),
                str(configuration.get("transmission_type", "")), source,
            )
        )
    return rows, sources


def _source_rows(repository: Path, source_codes: set[str]) -> list[tuple[object, ...]]:
    headers = (
        "source_code", "source_type", "title", "publisher", "market", "document_date",
        "external_reference", "file_path", "sha256", "status", "notes",
    )
    indexed = {row["code"]: row for row in _read_csv(repository / "data" / "master" / "sources.csv")}
    missing = sorted(source_codes - set(indexed))
    if missing:
        raise WorkbookError(f"workbook references unknown source codes: {missing}")
    rows: list[tuple[object, ...]] = [headers]
    for code in sorted(source_codes):
        row = indexed[code]
        rows.append(
            (
                code, row.get("source_type", ""), Cell(row.get("title", ""), "wrap"),
                row.get("publisher", ""), row.get("market", ""), _date(row.get("document_date")),
                row.get("external_reference", ""), Cell(row.get("file_path", ""), "wrap"),
                row.get("sha256", ""), row.get("status", ""), Cell(row.get("notes", ""), "wrap"),
            )
        )
    return rows


def _artifact_rows(manifest: Mapping[str, Any]) -> list[tuple[object, ...]]:
    records: list[tuple[str, str, str, int, str]] = []
    for group in manifest.get("groups", []):
        for kind, record in group.get("files", {}).items():
            records.append(
                (
                    str(group["scope"]), str(kind), str(record["path"]),
                    int(record["size_bytes"]), str(record["sha256"]),
                )
            )
    records.sort(key=lambda item: item[2])
    return [("owner", "artifact_kind", "path", "size_bytes", "sha256"), *records]


def _overview_rows(manifest: Mapping[str, Any], reports: Mapping[str, Mapping[str, Any]]) -> list[tuple[object, ...]]:
    dates = sorted({str(report.get("as_of", "")) for report in reports.values() if report.get("as_of")})
    total_pairs = sum(int(group.get("pair_count", 0)) for group in manifest.get("groups", []))
    total_differences = sum(int(group.get("total_differences", 0)) for group in manifest.get("groups", []))
    values = (
        ("workbook_version", WORKBOOK_VERSION),
        ("bundle_version", int(manifest.get("version", 0))),
        ("selected_configuration_count", int(manifest.get("selected_configuration_count", 0))),
        ("scope_group_count", int(manifest.get("scope_group_count", 0))),
        ("comparable_scope_count", int(manifest.get("comparable_scope_count", 0))),
        ("singleton_scope_count", int(manifest.get("singleton_scope_count", 0))),
        ("cross_scope_pairs_generated", bool(manifest.get("cross_scope_pairs_generated", False))),
        ("total_pair_count", total_pairs),
        ("total_difference_count", total_differences),
        ("report_snapshot_dates", ";".join(dates)),
        ("manifest_path", "comparison-bundle-manifest.json"),
        ("ranking_generated", False),
        ("recommendations_generated", False),
        ("inferred_values_generated", False),
    )
    return [("key", "value"), *values]


def _comparison_sources(rows: Sequence[Sequence[object]]) -> set[str]:
    headers = list(rows[0])
    indexes = [headers.index("left_source_code"), headers.index("right_source_code")]
    return {
        str(row[index])
        for row in rows[1:]
        for index in indexes
        if row[index]
    }


def _widths(headers: Sequence[str]) -> tuple[float, ...]:
    widths: list[float] = []
    for header in headers:
        if any(token in header for token in ("configuration_code", "sha256", "evidence_basis")):
            widths.append(32)
        elif any(token in header for token in ("title", "file_path", "configuration_codes")):
            widths.append(40)
        elif any(token in header for token in ("item_name", "powertrain", "reviewed_pages", "notes")):
            widths.append(24)
        elif any(token in header for token in ("date", "state", "status", "comparison", "scope")):
            widths.append(18)
        else:
            widths.append(16)
    return tuple(widths)


def build_sheets(repository: Path, build_root: Path, manifest: Mapping[str, Any]) -> tuple[Sheet, ...]:
    reports = _load_reports(build_root, manifest)
    comparison_rows = _comparison_rows(reports)
    configuration_rows, source_codes = _configuration_rows(repository, manifest)
    source_codes.update(_comparison_sources(comparison_rows))
    scope_rows = _scope_rows(manifest, reports)
    source_rows = _source_rows(repository, source_codes)
    artifact_rows = _artifact_rows(manifest)
    overview_rows = _overview_rows(manifest, reports)
    definitions = (
        ("Overview", overview_rows, False),
        ("Scopes", scope_rows, True),
        ("Configurations", configuration_rows, True),
        ("Comparisons", comparison_rows, True),
        ("Sources", source_rows, True),
        ("Artifacts", artifact_rows, True),
    )
    return tuple(
        Sheet(
            name=name,
            rows=rows,
            widths=_widths(tuple(str(item) for item in rows[0])),
            freeze_header=True,
            auto_filter=filtered,
        )
        for name, rows, filtered in definitions
    )
