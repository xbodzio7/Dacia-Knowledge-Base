from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


MATRIX_VERSION = 1
SOURCE_RELATIVE_PATH = Path("data/reporting/portfolio_model_family_summary.json")
CSV_COLUMNS = (
    "model_code",
    "model_name",
    "configuration_count",
    "version_count",
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
    "exclusive_scope_count",
    "shared_scope_count",
    "provenance_source_count",
    "provenance_relationship_count",
    "provenance_configuration_coverage_count",
    "provenance_missing_configuration_count",
    "provenance_earliest_document_date",
    "provenance_latest_document_date",
)


class PortfolioModelFamilyComparisonMatrixError(ValueError):
    """Raised when the family comparison cannot preserve source boundaries."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_source(repository: Path) -> dict[str, Any]:
    path = repository / SOURCE_RELATIVE_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortfolioModelFamilyComparisonMatrixError(
            f"cannot read verified family summary {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise PortfolioModelFamilyComparisonMatrixError(
            "verified family summary must be a JSON object"
        )
    return value


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PortfolioModelFamilyComparisonMatrixError(
            f"expected object for {field}"
        )
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise PortfolioModelFamilyComparisonMatrixError(
            f"expected list for {field}"
        )
    return list(value)


def collect_matrix(repository: Path) -> dict[str, Any]:
    source = _read_source(repository)
    source_summary = _mapping(source.get("summary"), "summary")
    if source.get("kind") != "portfolio_model_family_summary":
        raise PortfolioModelFamilyComparisonMatrixError(
            "unexpected source product kind"
        )
    if source.get("version") != 1:
        raise PortfolioModelFamilyComparisonMatrixError(
            "unsupported source product version"
        )
    for flag in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        if source_summary.get(flag) is not False:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"source product violates comparison boundary: {flag}"
            )

    raw_families = _list(source.get("families"), "families")
    projected: list[dict[str, Any]] = []
    for index, raw_family in enumerate(raw_families):
        family = _mapping(raw_family, f"families[{index}]")
        price = _mapping(
            family.get("catalog_price"),
            f"families[{index}].catalog_price",
        )
        provenance = _mapping(
            family.get("provenance"), f"families[{index}].provenance"
        )
        configuration_count = int(family["configuration_count"])
        recorded_seats = _list(
            family.get("recorded_seat_values"),
            f"families[{index}].recorded_seat_values",
        )
        seat_state = str(family.get("seat_summary_state"))
        if seat_state == "not_stated" and recorded_seats:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"not_stated seat state has values: {family.get('model_code')}"
            )
        if seat_state == "recorded" and not recorded_seats:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"recorded seat state has no values: {family.get('model_code')}"
            )
        reporting_scope_count = int(family["reporting_scope_count"])
        exclusive_scope_count = int(family["exclusive_scope_count"])
        shared_scope_count = int(family["shared_scope_count"])
        if reporting_scope_count != exclusive_scope_count + shared_scope_count:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"reporting scope decomposition differs: {family.get('model_code')}"
            )
        if int(provenance["configuration_coverage_count"]) != configuration_count:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"provenance coverage differs: {family.get('model_code')}"
            )
        if int(provenance["missing_configuration_count"]) != 0:
            raise PortfolioModelFamilyComparisonMatrixError(
                f"missing provenance coverage: {family.get('model_code')}"
            )
        projected.append(
            {
                "model_code": str(family["model_code"]),
                "model_name": str(family["model_name"]),
                "configuration_count": configuration_count,
                "version_count": int(family["version_count"]),
                "catalog_price": {
                    "state": str(price["state"]),
                    "currency": str(price["currency"]),
                    "minimum": price.get("minimum"),
                    "maximum": price.get("maximum"),
                    "recorded_count": int(price["recorded_count"]),
                    "missing_count": int(price["missing_count"]),
                },
                "recorded_seat_values": recorded_seats,
                "seat_summary_state": seat_state,
                "transmission_values": [
                    str(item)
                    for item in _list(
                        family.get("transmission_values"),
                        f"families[{index}].transmission_values",
                    )
                ],
                "powertrain_labels": [
                    str(item)
                    for item in _list(
                        family.get("powertrain_labels"),
                        f"families[{index}].powertrain_labels",
                    )
                ],
                "reporting_scope_count": reporting_scope_count,
                "exclusive_scope_count": exclusive_scope_count,
                "shared_scope_count": shared_scope_count,
                "provenance": {
                    "source_count": int(provenance["source_count"]),
                    "relationship_count": int(provenance["relationship_count"]),
                    "configuration_coverage_count": int(
                        provenance["configuration_coverage_count"]
                    ),
                    "missing_configuration_count": 0,
                    "earliest_document_date": str(
                        provenance["earliest_document_date"]
                    ),
                    "latest_document_date": str(
                        provenance["latest_document_date"]
                    ),
                },
            }
        )

    expected_family_count = int(source_summary["model_family_count"])
    if len(projected) != expected_family_count:
        raise PortfolioModelFamilyComparisonMatrixError(
            "model-family count differs from source summary"
        )
    if sum(item["configuration_count"] for item in projected) != int(
        source_summary["active_configuration_count"]
    ):
        raise PortfolioModelFamilyComparisonMatrixError(
            "active configuration total differs from source summary"
        )
    if sum(
        item["provenance"]["relationship_count"] for item in projected
    ) != int(source_summary["source_configuration_relationship_count"]):
        raise PortfolioModelFamilyComparisonMatrixError(
            "source relationship total differs from source summary"
        )

    return {
        "version": MATRIX_VERSION,
        "kind": "portfolio_model_family_comparison_matrix",
        "as_of": source.get("as_of"),
        "source_product": {
            "kind": source["kind"],
            "version": source["version"],
            "path": SOURCE_RELATIVE_PATH.as_posix(),
        },
        "summary": {
            "model_family_count": expected_family_count,
            "active_configuration_count": int(
                source_summary["active_configuration_count"]
            ),
            "reporting_scope_count": int(
                source_summary["reporting_scope_count"]
            ),
            "provenance_source_count": int(
                source_summary["provenance_source_count"]
            ),
            "source_configuration_relationship_count": int(
                source_summary["source_configuration_relationship_count"]
            ),
            "configurations_without_provenance_count": int(
                source_summary["configurations_without_provenance_count"]
            ),
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "families": projected,
    }


def render_json(matrix: Mapping[str, Any]) -> str:
    return json.dumps(matrix, ensure_ascii=False, indent=2) + "\n"


def _joined(values: Sequence[Any]) -> str:
    return "|".join(str(item) for item in values)


def _csv_row(family: Mapping[str, Any]) -> dict[str, Any]:
    price = _mapping(family["catalog_price"], "catalog_price")
    provenance = _mapping(family["provenance"], "provenance")
    return {
        "model_code": family["model_code"],
        "model_name": family["model_name"],
        "configuration_count": family["configuration_count"],
        "version_count": family["version_count"],
        "price_state": price["state"],
        "price_currency": price["currency"],
        "price_minimum": "" if price["minimum"] is None else price["minimum"],
        "price_maximum": "" if price["maximum"] is None else price["maximum"],
        "price_recorded_count": price["recorded_count"],
        "price_missing_count": price["missing_count"],
        "seat_summary_state": family["seat_summary_state"],
        "recorded_seat_values": _joined(family["recorded_seat_values"]),
        "transmission_values": _joined(family["transmission_values"]),
        "powertrain_labels": _joined(family["powertrain_labels"]),
        "reporting_scope_count": family["reporting_scope_count"],
        "exclusive_scope_count": family["exclusive_scope_count"],
        "shared_scope_count": family["shared_scope_count"],
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
    for family in matrix["families"]:
        writer.writerow(_csv_row(family))
    return output.getvalue()


def _price(price: Mapping[str, Any]) -> str:
    if price.get("state") != "recorded":
        return "not stated"
    minimum = f"{int(price['minimum']):,}".replace(",", " ")
    maximum = f"{int(price['maximum']):,}".replace(",", " ")
    return f"{minimum}–{maximum} {price['currency']}"


def _display(values: Sequence[Any], state: str = "recorded") -> str:
    if state == "not_stated" or not values:
        return '<span data-state="not_stated">not stated</span>'
    return html.escape(" / ".join(str(item) for item in values))


def render_html(matrix: Mapping[str, Any]) -> str:
    totals = _mapping(matrix["summary"], "summary")
    rows: list[str] = []
    for family in matrix["families"]:
        price = _mapping(family["catalog_price"], "catalog_price")
        provenance = _mapping(family["provenance"], "provenance")
        rows.append(
            "<tr>"
            f"<th scope=\"row\"><code>{html.escape(str(family['model_code']))}</code>"
            f"<strong>{html.escape(str(family['model_name']))}</strong></th>"
            f"<td>{family['configuration_count']}</td>"
            f"<td>{family['version_count']}</td>"
            f"<td>{html.escape(_price(price))}</td>"
            f"<td>{_display(family['recorded_seat_values'], str(family['seat_summary_state']))}</td>"
            f"<td>{_display(family['transmission_values'])}</td>"
            f"<td>{_display(family['powertrain_labels'])}</td>"
            f"<td>{family['reporting_scope_count']} "
            f"({family['exclusive_scope_count']} exclusive, "
            f"{family['shared_scope_count']} shared)</td>"
            f"<td>{provenance['source_count']} sources / "
            f"{provenance['relationship_count']} relationships / "
            f"{provenance['configuration_coverage_count']} configurations</td>"
            f"<td>{html.escape(str(provenance['earliest_document_date']))}–"
            f"{html.escape(str(provenance['latest_document_date']))}</td>"
            "</tr>"
        )
    body = "".join(rows)
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>Portfolio Model Family Comparison Matrix</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;color:#1f2937}"
        "h1{margin-bottom:.25rem}.boundary{max-width:72rem;color:#4b5563}"
        ".table-wrap{overflow-x:auto;margin-top:1.5rem}"
        "table{border-collapse:collapse;min-width:78rem;width:100%}"
        "th,td{border:1px solid #d1d5db;padding:.65rem;text-align:left;vertical-align:top}"
        "thead th{background:#f3f4f6}tbody th{min-width:12rem}"
        "tbody th code{display:block;font-size:.75rem;color:#6b7280}"
        "tbody th strong{display:block;margin-top:.25rem}"
        "[data-state=not_stated]{font-style:italic;color:#6b7280}"
        "footer{margin-top:1.5rem;color:#4b5563}"
        "</style></head><body>"
        "<main><h1>Portfolio Model Family Comparison Matrix</h1>"
        f"<p>Snapshot: <code>{html.escape(str(matrix.get('as_of')))}</code>. "
        f"{totals['model_family_count']} families, "
        f"{totals['active_configuration_count']} active configurations and "
        f"{totals['reporting_scope_count']} preserved reporting scopes.</p>"
        "<p class=\"boundary\">This standalone matrix projects only verified "
        "family-summary fields. It creates no configuration pair, cross-scope "
        "pair, ranking, recommendation or inferred value. Missing recorded "
        "states remain <em>not stated</em>.</p>"
        "<div class=\"table-wrap\"><table><thead><tr>"
        "<th>Family</th><th>Configurations</th><th>Versions</th>"
        "<th>Recorded price range</th><th>Recorded seats</th>"
        "<th>Transmissions</th><th>Powertrains</th><th>Reporting scopes</th>"
        "<th>Provenance coverage</th><th>Source dates</th>"
        "</tr></thead><tbody>"
        f"{body}</tbody></table></div></main>"
        "<footer>Source product: "
        f"<code>{html.escape(str(matrix['source_product']['path']))}</code>. "
        f"Explicit source relationships: "
        f"{totals['source_configuration_relationship_count']}.</footer>"
        "</body></html>\n"
    )
