from __future__ import annotations

import csv
import html
import io
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from reporting.configuration_shortlist import ShortlistCriteria
from reporting.configuration_shortlist_html import collect_browser_catalog
from reporting.cross_model_comparison_view import collect_view


MATRIX_VERSION = 1
_MODEL_ORDER = {
    "sandero_iii": 10,
    "sandero_stepway_iii": 20,
    "jogger": 30,
    "duster_iii": 40,
    "bigster": 50,
    "spring": 60,
}
CSV_COLUMNS = (
    "version_code",
    "version_name",
    "model_code",
    "model_name",
    "configuration_count",
    "configuration_codes",
    "price_state",
    "price_currency",
    "price_minimum",
    "price_maximum",
    "price_recorded_count",
    "price_missing_count",
    "seat_summary_state",
    "recorded_seat_values",
    "transmission_values",
    "powertrain_labels",
    "reporting_scope_count",
    "single_model_scope_count",
    "mixed_model_scope_count",
    "scope_slugs",
    "provenance_source_count",
    "provenance_relationship_count",
    "provenance_configuration_coverage_count",
    "provenance_missing_configuration_count",
    "provenance_earliest_document_date",
    "provenance_latest_document_date",
)


class PortfolioModelVersionComparisonMatrixError(ValueError):
    """Raised when a source-preserving version matrix cannot be built."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise PortfolioModelVersionComparisonMatrixError(
                    f"missing CSV header: {path}"
                )
            return list(reader)
    except OSError as exc:
        raise PortfolioModelVersionComparisonMatrixError(
            f"cannot read CSV file {path}: {exc}"
        ) from exc


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PortfolioModelVersionComparisonMatrixError(
            f"expected object for {field}"
        )
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise PortfolioModelVersionComparisonMatrixError(
            f"expected string list for {field}"
        )
    return list(value)


def _price_amount(item: Mapping[str, Any]) -> int | None:
    state = item.get("catalog_price")
    if not isinstance(state, Mapping) or state.get("state") != "recorded":
        return None
    raw = state.get("amount")
    try:
        return int(str(raw))
    except (TypeError, ValueError) as exc:
        raise PortfolioModelVersionComparisonMatrixError(
            f"invalid price for {item.get('configuration_code')}: {raw!r}"
        ) from exc


def _seat_value(item: Mapping[str, Any]) -> int | None:
    state = item.get("number_of_seats")
    if not isinstance(state, Mapping) or state.get("state") != "recorded":
        return None
    raw = state.get("value")
    try:
        return int(str(raw))
    except (TypeError, ValueError) as exc:
        raise PortfolioModelVersionComparisonMatrixError(
            f"invalid seat value for {item.get('configuration_code')}: {raw!r}"
        ) from exc


def _version_sort_key(
    version: Mapping[str, str],
) -> tuple[int, int, str]:
    raw_id = version.get("id", "")
    try:
        identifier = int(raw_id)
    except ValueError:
        identifier = 999999
    return (
        _MODEL_ORDER.get(version.get("model_code", ""), 999),
        identifier,
        version.get("code", ""),
    )


def collect_matrix(repository: Path) -> dict[str, Any]:
    master = repository / "data" / "master"
    models = {row["code"]: row for row in _read_csv(master / "models.csv")}
    version_rows = [
        row
        for row in _read_csv(master / "versions.csv")
        if row.get("status") == "active"
    ]
    versions = {row["code"]: row for row in version_rows}
    configurations = {
        row["code"]: row
        for row in _read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    }
    sources = {
        row["code"]: row for row in _read_csv(master / "sources.csv")
    }
    relationship_rows = _read_csv(master / "source_configurations.csv")

    catalog = collect_browser_catalog(repository, ShortlistCriteria())
    raw_catalog = catalog.get("configurations")
    if not isinstance(raw_catalog, list) or not all(
        isinstance(item, Mapping) for item in raw_catalog
    ):
        raise PortfolioModelVersionComparisonMatrixError(
            "browser catalog configurations are missing"
        )
    catalog_index = {
        str(item.get("configuration_code", "")): item
        for item in raw_catalog
    }
    if set(catalog_index) != set(configurations):
        raise PortfolioModelVersionComparisonMatrixError(
            "browser catalog does not cover every active configuration exactly once"
        )

    configurations_by_version: dict[str, list[str]] = defaultdict(list)
    for code, configuration in configurations.items():
        version_code = configuration.get("version_code", "")
        version = versions.get(version_code)
        if version is None:
            raise PortfolioModelVersionComparisonMatrixError(
                f"configuration references inactive or unknown version: "
                f"{code} -> {version_code}"
            )
        model_code = version.get("model_code", "")
        if model_code not in models:
            raise PortfolioModelVersionComparisonMatrixError(
                f"version references unknown model: {version_code} -> {model_code}"
            )
        configurations_by_version[version_code].append(code)
    if set(configurations_by_version) != set(versions):
        missing = sorted(set(versions) - set(configurations_by_version))
        raise PortfolioModelVersionComparisonMatrixError(
            f"active versions without active configurations: {missing}"
        )

    view = collect_view(repository)
    view_summary = _mapping(view.get("summary"), "cross-model summary")
    raw_scopes = view.get("scopes")
    if not isinstance(raw_scopes, list) or not all(
        isinstance(scope, Mapping) for scope in raw_scopes
    ):
        raise PortfolioModelVersionComparisonMatrixError(
            "cross-model reporting scopes are missing"
        )
    for flag in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        if view_summary.get(flag) is not False:
            raise PortfolioModelVersionComparisonMatrixError(
                f"cross-model view violates version boundary: {flag}"
            )

    scope_by_configuration: dict[str, Mapping[str, Any]] = {}
    for scope in raw_scopes:
        slug = str(scope.get("slug", ""))
        if not slug:
            raise PortfolioModelVersionComparisonMatrixError(
                "reporting scope has no slug"
            )
        for code in _string_list(
            scope.get("configuration_codes"),
            f"scope {slug} configuration_codes",
        ):
            if code in scope_by_configuration:
                raise PortfolioModelVersionComparisonMatrixError(
                    f"configuration belongs to multiple scopes: {code}"
                )
            scope_by_configuration[code] = scope
    if set(scope_by_configuration) != set(configurations):
        raise PortfolioModelVersionComparisonMatrixError(
            "reporting scopes do not cover every active configuration exactly once"
        )

    relations_by_version: dict[str, list[dict[str, str]]] = defaultdict(list)
    covered_configurations: set[str] = set()
    used_sources: set[str] = set()
    relationship_count = 0
    for relation in relationship_rows:
        configuration_code = relation.get("configuration_code", "")
        configuration = configurations.get(configuration_code)
        if configuration is None:
            continue
        source_code = relation.get("source_code", "")
        if source_code not in sources:
            raise PortfolioModelVersionComparisonMatrixError(
                f"source relationship references unknown source: {source_code}"
            )
        version_code = configuration["version_code"]
        relations_by_version[version_code].append(relation)
        covered_configurations.add(configuration_code)
        used_sources.add(source_code)
        relationship_count += 1
    if covered_configurations != set(configurations):
        missing = sorted(set(configurations) - covered_configurations)
        raise PortfolioModelVersionComparisonMatrixError(
            f"active configurations without source provenance: {missing}"
        )

    records: list[dict[str, Any]] = []
    for version in sorted(version_rows, key=_version_sort_key):
        version_code = version["code"]
        model_code = version.get("model_code", "")
        model = models[model_code]
        configuration_codes = sorted(configurations_by_version[version_code])
        items = [catalog_index[code] for code in configuration_codes]
        prices = [
            value
            for item in items
            if (value := _price_amount(item)) is not None
        ]
        seats = sorted(
            {
                value
                for item in items
                if (value := _seat_value(item)) is not None
            }
        )
        scopes = {
            str(scope_by_configuration[code]["slug"]): scope_by_configuration[code]
            for code in configuration_codes
        }
        single_model_scope_slugs = sorted(
            slug
            for slug, scope in scopes.items()
            if scope.get("mixed_model") is False
        )
        mixed_model_scope_slugs = sorted(
            slug
            for slug, scope in scopes.items()
            if scope.get("mixed_model") is True
        )

        relations = relations_by_version[version_code]
        version_source_codes = sorted({row["source_code"] for row in relations})
        source_dates = [
            sources[code].get("document_date", "")
            for code in version_source_codes
            if sources[code].get("document_date", "")
        ]
        relation_configuration_codes = {
            row["configuration_code"] for row in relations
        }
        missing_provenance = sorted(
            set(configuration_codes) - relation_configuration_codes
        )
        if missing_provenance:
            raise PortfolioModelVersionComparisonMatrixError(
                f"version configurations without provenance: "
                f"{version_code} -> {missing_provenance}"
            )
        records.append(
            {
                "version_code": version_code,
                "version_name": version.get("name", ""),
                "model_code": model_code,
                "model_name": model.get("name", model_code),
                "configuration_count": len(configuration_codes),
                "configuration_codes": configuration_codes,
                "catalog_price": {
                    "state": "recorded" if prices else "not_stated",
                    "currency": "PLN" if prices else "",
                    "minimum": min(prices) if prices else None,
                    "maximum": max(prices) if prices else None,
                    "recorded_count": len(prices),
                    "missing_count": len(configuration_codes) - len(prices),
                },
                "recorded_seat_values": seats,
                "seat_summary_state": "recorded" if seats else "not_stated",
                "transmission_values": sorted(
                    {
                        str(item.get("transmission_type", ""))
                        for item in items
                        if str(item.get("transmission_type", ""))
                    }
                ),
                "powertrain_labels": sorted(
                    {
                        str(item.get("powertrain_label", ""))
                        for item in items
                        if str(item.get("powertrain_label", ""))
                    }
                ),
                "reporting_scope_count": len(scopes),
                "single_model_scope_count": len(single_model_scope_slugs),
                "mixed_model_scope_count": len(mixed_model_scope_slugs),
                "scope_slugs": sorted(scopes),
                "single_model_scope_slugs": single_model_scope_slugs,
                "mixed_model_scope_slugs": mixed_model_scope_slugs,
                "provenance": {
                    "source_count": len(version_source_codes),
                    "relationship_count": len(relations),
                    "configuration_coverage_count": len(configuration_codes),
                    "missing_configuration_count": 0,
                    "earliest_document_date": min(source_dates),
                    "latest_document_date": max(source_dates),
                },
            }
        )

    if len(records) != 22:
        raise PortfolioModelVersionComparisonMatrixError(
            f"expected 22 active versions, found {len(records)}"
        )
    if sum(record["configuration_count"] for record in records) != 81:
        raise PortfolioModelVersionComparisonMatrixError(
            "version rows do not preserve all 81 active configurations"
        )
    if relationship_count != int(
        view_summary.get("active_configuration_count", -1)
    ) and relationship_count <= 0:
        raise PortfolioModelVersionComparisonMatrixError(
            "source relationship count is invalid"
        )

    return {
        "version": MATRIX_VERSION,
        "kind": "portfolio_model_version_comparison_matrix",
        "as_of": catalog.get("as_of"),
        "summary": {
            "model_family_count": len({row["model_code"] for row in records}),
            "active_version_count": len(records),
            "active_configuration_count": len(configurations),
            "reporting_scope_count": len(raw_scopes),
            "provenance_source_count": len(used_sources),
            "source_configuration_relationship_count": relationship_count,
            "configurations_without_provenance_count": 0,
            "configuration_pairs_generated": False,
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "methodology": {
            "version_boundary": (
                "Each row is one active canonical version_code and includes only "
                "active configurations assigned to that version."
            ),
            "scope_boundary": (
                "Every configuration keeps its single existing reporting scope; "
                "scope memberships are aggregated but never expanded into pairs."
            ),
            "provenance_boundary": (
                "Only explicit source_configurations relationships are counted."
            ),
            "unknown_handling": (
                "Unstated values remain not_stated and are never replaced with "
                "zero, false, unavailable or an inferred value."
            ),
        },
        "versions": records,
    }


def render_json(matrix: Mapping[str, Any]) -> str:
    return json.dumps(matrix, ensure_ascii=False, indent=2) + "\n"


def _joined(values: Sequence[Any]) -> str:
    return "|".join(str(item) for item in values)


def _csv_row(record: Mapping[str, Any]) -> dict[str, Any]:
    price = _mapping(record["catalog_price"], "catalog_price")
    provenance = _mapping(record["provenance"], "provenance")
    return {
        "version_code": record["version_code"],
        "version_name": record["version_name"],
        "model_code": record["model_code"],
        "model_name": record["model_name"],
        "configuration_count": record["configuration_count"],
        "configuration_codes": _joined(record["configuration_codes"]),
        "price_state": price["state"],
        "price_currency": price["currency"],
        "price_minimum": "" if price["minimum"] is None else price["minimum"],
        "price_maximum": "" if price["maximum"] is None else price["maximum"],
        "price_recorded_count": price["recorded_count"],
        "price_missing_count": price["missing_count"],
        "seat_summary_state": record["seat_summary_state"],
        "recorded_seat_values": _joined(record["recorded_seat_values"]),
        "transmission_values": _joined(record["transmission_values"]),
        "powertrain_labels": _joined(record["powertrain_labels"]),
        "reporting_scope_count": record["reporting_scope_count"],
        "single_model_scope_count": record["single_model_scope_count"],
        "mixed_model_scope_count": record["mixed_model_scope_count"],
        "scope_slugs": _joined(record["scope_slugs"]),
        "provenance_source_count": provenance["source_count"],
        "provenance_relationship_count": provenance["relationship_count"],
        "provenance_configuration_coverage_count": provenance[
            "configuration_coverage_count"
        ],
        "provenance_missing_configuration_count": provenance[
            "missing_configuration_count"
        ],
        "provenance_earliest_document_date": provenance[
            "earliest_document_date"
        ],
        "provenance_latest_document_date": provenance[
            "latest_document_date"
        ],
    }


def render_csv(matrix: Mapping[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=CSV_COLUMNS,
        lineterminator="\n",
    )
    writer.writeheader()
    for record in matrix["versions"]:
        writer.writerow(_csv_row(record))
    return output.getvalue()


def _display(values: Sequence[Any], state: str = "recorded") -> str:
    if state == "not_stated" or not values:
        return '<span data-state="not_stated">not stated</span>'
    return html.escape(" / ".join(str(item) for item in values))


def _price(price: Mapping[str, Any]) -> str:
    if price.get("state") != "recorded":
        return "not stated"
    minimum = f"{int(price['minimum']):,}".replace(",", " ")
    maximum = f"{int(price['maximum']):,}".replace(",", " ")
    return f"{minimum}–{maximum} {price['currency']}"


def render_html(matrix: Mapping[str, Any]) -> str:
    summary = _mapping(matrix["summary"], "summary")
    rows: list[str] = []
    for record in matrix["versions"]:
        price = _mapping(record["catalog_price"], "catalog_price")
        provenance = _mapping(record["provenance"], "provenance")
        rows.append(
            "<tr>"
            f"<th scope=\"row\"><code>{html.escape(str(record['version_code']))}</code>"
            f"<strong>{html.escape(str(record['model_name']))} — "
            f"{html.escape(str(record['version_name']))}</strong></th>"
            f"<td>{record['configuration_count']}</td>"
            f"<td>{html.escape(_price(price))}</td>"
            f"<td>{_display(record['recorded_seat_values'], str(record['seat_summary_state']))}</td>"
            f"<td>{_display(record['transmission_values'])}</td>"
            f"<td>{_display(record['powertrain_labels'])}</td>"
            f"<td>{record['reporting_scope_count']} "
            f"({record['single_model_scope_count']} single-model, "
            f"{record['mixed_model_scope_count']} mixed-model)</td>"
            f"<td>{provenance['source_count']} sources / "
            f"{provenance['relationship_count']} relationships / "
            f"{provenance['configuration_coverage_count']} configurations</td>"
            f"<td>{html.escape(str(provenance['earliest_document_date']))}–"
            f"{html.escape(str(provenance['latest_document_date']))}</td>"
            "</tr>"
        )
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>Portfolio Model Version Comparison Matrix</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;color:#1f2937}"
        "h1{margin-bottom:.25rem}.boundary{max-width:72rem;color:#4b5563}"
        ".table-wrap{overflow-x:auto;margin-top:1.5rem}"
        "table{border-collapse:collapse;min-width:72rem;width:100%}"
        "th,td{border:1px solid #d1d5db;padding:.65rem;text-align:left;vertical-align:top}"
        "thead th{background:#f3f4f6}tbody th{min-width:16rem}"
        "tbody th code{display:block;font-size:.72rem;color:#6b7280}"
        "tbody th strong{display:block;margin-top:.25rem}"
        "[data-state=not_stated]{font-style:italic;color:#6b7280}"
        "footer{margin-top:1.5rem;color:#4b5563}"
        "</style></head><body><main>"
        "<h1>Portfolio Model Version Comparison Matrix</h1>"
        f"<p>Snapshot: <code>{html.escape(str(matrix.get('as_of')))}</code>. "
        f"{summary['active_version_count']} active versions, "
        f"{summary['active_configuration_count']} active configurations and "
        f"{summary['reporting_scope_count']} preserved reporting scopes.</p>"
        "<p class=\"boundary\">This standalone matrix projects only verified "
        "version-bounded canonical fields. It creates no configuration pair, "
        "cross-scope pair, ranking, recommendation or inferred value. Missing "
        "recorded states remain <em>not stated</em>.</p>"
        "<div class=\"table-wrap\"><table><thead><tr>"
        "<th>Model version</th><th>Configurations</th>"
        "<th>Recorded price range</th><th>Recorded seats</th>"
        "<th>Transmissions</th><th>Powertrains</th>"
        "<th>Reporting scopes</th><th>Provenance coverage</th>"
        "<th>Source dates</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div></main>"
        "<footer>Explicit source relationships: "
        f"{summary['source_configuration_relationship_count']}. "
        "No version is ranked or recommended.</footer>"
        "</body></html>\n"
    )
