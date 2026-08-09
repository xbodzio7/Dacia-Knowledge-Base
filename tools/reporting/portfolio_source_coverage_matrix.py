from __future__ import annotations

import csv
import html
import io
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


MATRIX_VERSION = 1
CSV_COLUMNS = (
    "source_code",
    "source_type",
    "title",
    "publisher",
    "market",
    "document_date",
    "external_reference",
    "file_path",
    "sha256",
    "status",
    "relationship_count",
    "relationship_types",
    "configuration_count",
    "configuration_codes",
    "version_count",
    "version_codes",
    "model_family_count",
    "model_codes",
    "model_names",
    "notes",
)


class PortfolioSourceCoverageMatrixError(ValueError):
    """Raised when an exact source-coverage projection cannot be built."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise PortfolioSourceCoverageMatrixError(
                    f"missing CSV header: {path}"
                )
            return list(reader)
    except OSError as exc:
        raise PortfolioSourceCoverageMatrixError(
            f"cannot read CSV file {path}: {exc}"
        ) from exc


def _numeric_id(row: Mapping[str, str]) -> tuple[int, str]:
    try:
        identifier = int(row.get("id", ""))
    except ValueError:
        identifier = 999999999
    return identifier, row.get("code", "")


def _joined(values: Sequence[Any]) -> str:
    return "|".join(str(item) for item in values)


def collect_matrix(repository: Path) -> dict[str, Any]:
    master = repository / "data" / "master"
    model_rows = _read_csv(master / "models.csv")
    version_rows = _read_csv(master / "versions.csv")
    configuration_rows = _read_csv(master / "configurations.csv")
    source_rows = _read_csv(master / "sources.csv")
    relationship_rows = _read_csv(master / "source_configurations.csv")

    models = {row["code"]: row for row in model_rows}
    versions = {
        row["code"]: row
        for row in version_rows
        if row.get("status") == "active"
    }
    configurations = {
        row["code"]: row
        for row in configuration_rows
        if row.get("status") == "active"
    }
    sources = {row["code"]: row for row in source_rows}

    if len(configurations) != 84:
        raise PortfolioSourceCoverageMatrixError(
            f"expected 84 active configurations, found {len(configurations)}"
        )
    if len(versions) != 22:
        raise PortfolioSourceCoverageMatrixError(
            f"expected 22 active versions, found {len(versions)}"
        )

    configuration_context: dict[str, dict[str, str]] = {}
    active_model_codes: set[str] = set()
    for configuration_code, configuration in configurations.items():
        version_code = configuration.get("version_code", "")
        version = versions.get(version_code)
        if version is None:
            raise PortfolioSourceCoverageMatrixError(
                "active configuration references inactive or unknown version: "
                f"{configuration_code} -> {version_code}"
            )
        model_code = version.get("model_code", "")
        model = models.get(model_code)
        if model is None:
            raise PortfolioSourceCoverageMatrixError(
                f"active version references unknown model: {version_code} -> {model_code}"
            )
        active_model_codes.add(model_code)
        configuration_context[configuration_code] = {
            "configuration_code": configuration_code,
            "version_code": version_code,
            "version_name": version.get("name", ""),
            "model_code": model_code,
            "model_name": model.get("name", model_code),
        }

    if len(active_model_codes) != 6:
        raise PortfolioSourceCoverageMatrixError(
            f"expected six active model families, found {len(active_model_codes)}"
        )

    relations_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    covered_configurations: set[str] = set()
    relationship_ids: set[str] = set()
    relationship_identities: set[tuple[str, str, str]] = set()
    active_relationship_count = 0

    for relation in relationship_rows:
        configuration_code = relation.get("configuration_code", "")
        if configuration_code not in configurations:
            continue
        source_code = relation.get("source_code", "")
        source = sources.get(source_code)
        if source is None:
            raise PortfolioSourceCoverageMatrixError(
                f"relationship references unknown source: {source_code}"
            )
        if source.get("status") != "active":
            raise PortfolioSourceCoverageMatrixError(
                f"used provenance source is not active: {source_code}"
            )
        relation_id = relation.get("id", "")
        if not relation_id or relation_id in relationship_ids:
            raise PortfolioSourceCoverageMatrixError(
                f"duplicate or missing source relationship id: {relation_id!r}"
            )
        relationship_ids.add(relation_id)
        identity = (
            source_code,
            configuration_code,
            relation.get("relationship", ""),
        )
        if identity in relationship_identities:
            raise PortfolioSourceCoverageMatrixError(
                f"duplicate source relationship identity: {identity}"
            )
        relationship_identities.add(identity)
        relations_by_source[source_code].append(relation)
        covered_configurations.add(configuration_code)
        active_relationship_count += 1

    if active_relationship_count != 284:
        raise PortfolioSourceCoverageMatrixError(
            "expected 284 active source-to-configuration relationships, "
            f"found {active_relationship_count}"
        )
    if covered_configurations != set(configurations):
        missing = sorted(set(configurations) - covered_configurations)
        raise PortfolioSourceCoverageMatrixError(
            f"active configurations without provenance: {missing}"
        )
    if len(relations_by_source) != 35:
        raise PortfolioSourceCoverageMatrixError(
            f"expected 35 used provenance sources, found {len(relations_by_source)}"
        )

    records: list[dict[str, Any]] = []
    for source_code in sorted(
        relations_by_source,
        key=lambda code: _numeric_id(sources[code]),
    ):
        source = sources[source_code]
        relations = sorted(
            relations_by_source[source_code],
            key=lambda row: (
                configuration_context[row["configuration_code"]]["model_code"],
                configuration_context[row["configuration_code"]]["version_code"],
                row["configuration_code"],
                row.get("relationship", ""),
                int(row["id"]),
            ),
        )
        configuration_codes = sorted(
            {row["configuration_code"] for row in relations}
        )
        version_codes = sorted(
            {
                configuration_context[code]["version_code"]
                for code in configuration_codes
            }
        )
        model_codes = sorted(
            {
                configuration_context[code]["model_code"]
                for code in configuration_codes
            }
        )
        model_names = [models[code].get("name", code) for code in model_codes]
        relationship_types = sorted(
            {row.get("relationship", "") for row in relations}
        )
        if "" in relationship_types:
            raise PortfolioSourceCoverageMatrixError(
                f"source relationship type is missing for {source_code}"
            )
        sha256 = source.get("sha256", "")
        if len(sha256) != 64 or any(
            character not in "0123456789abcdef" for character in sha256
        ):
            raise PortfolioSourceCoverageMatrixError(
                f"invalid source SHA-256 for {source_code}: {sha256!r}"
            )
        if not source.get("external_reference") and not source.get("file_path"):
            raise PortfolioSourceCoverageMatrixError(
                f"used source has no external or local identity: {source_code}"
            )

        records.append(
            {
                "source_code": source_code,
                "source_type": source.get("source_type", ""),
                "title": source.get("title", ""),
                "publisher": source.get("publisher", ""),
                "market": source.get("market", ""),
                "document_date": source.get("document_date", ""),
                "external_reference": source.get("external_reference", ""),
                "file_path": source.get("file_path", ""),
                "sha256": sha256,
                "status": source.get("status", ""),
                "notes": source.get("notes", ""),
                "relationship_count": len(relations),
                "relationship_types": relationship_types,
                "configuration_count": len(configuration_codes),
                "configuration_codes": configuration_codes,
                "version_count": len(version_codes),
                "version_codes": version_codes,
                "model_family_count": len(model_codes),
                "model_codes": model_codes,
                "model_names": model_names,
            }
        )

    if sum(record["relationship_count"] for record in records) != 284:
        raise PortfolioSourceCoverageMatrixError(
            "source rows do not preserve all 284 relationships exactly once"
        )
    if {
        code
        for record in records
        for code in record["configuration_codes"]
    } != set(configurations):
        raise PortfolioSourceCoverageMatrixError(
            "source rows do not preserve all active configuration identities"
        )
    if {
        code for record in records for code in record["version_codes"]
    } != set(versions):
        raise PortfolioSourceCoverageMatrixError(
            "source rows do not preserve all active version identities"
        )
    if {
        code for record in records for code in record["model_codes"]
    } != active_model_codes:
        raise PortfolioSourceCoverageMatrixError(
            "source rows do not preserve all active model-family identities"
        )

    document_dates = [
        record["document_date"] for record in records if record["document_date"]
    ]
    return {
        "version": MATRIX_VERSION,
        "kind": "portfolio_source_coverage_matrix",
        "as_of": max(document_dates) if document_dates else None,
        "summary": {
            "provenance_source_count": len(records),
            "source_configuration_relationship_count": active_relationship_count,
            "active_configuration_count": len(configurations),
            "active_version_count": len(versions),
            "model_family_count": len(active_model_codes),
            "configurations_without_provenance_count": 0,
            "source_quality_scores_generated": False,
            "source_rankings_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "methodology": {
            "source_boundary": (
                "Each row is one active registered source used by at least one "
                "active configuration."
            ),
            "relationship_boundary": (
                "Coverage is projected only from explicit source_configurations "
                "rows; every active relationship is counted exactly once."
            ),
            "identity_boundary": (
                "Registered external_reference, file_path and SHA-256 values are "
                "preserved without reconstruction."
            ),
            "evaluation_boundary": (
                "The product does not score, rank, recommend or infer source "
                "quality, authority, preference or missing values."
            ),
        },
        "sources": records,
    }


def render_json(matrix: Mapping[str, Any]) -> str:
    return json.dumps(matrix, ensure_ascii=False, indent=2) + "\n"


def _csv_row(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_code": record["source_code"],
        "source_type": record["source_type"],
        "title": record["title"],
        "publisher": record["publisher"],
        "market": record["market"],
        "document_date": record["document_date"],
        "external_reference": record["external_reference"],
        "file_path": record["file_path"],
        "sha256": record["sha256"],
        "status": record["status"],
        "relationship_count": record["relationship_count"],
        "relationship_types": _joined(record["relationship_types"]),
        "configuration_count": record["configuration_count"],
        "configuration_codes": _joined(record["configuration_codes"]),
        "version_count": record["version_count"],
        "version_codes": _joined(record["version_codes"]),
        "model_family_count": record["model_family_count"],
        "model_codes": _joined(record["model_codes"]),
        "model_names": _joined(record["model_names"]),
        "notes": record["notes"],
    }


def render_csv(matrix: Mapping[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=CSV_COLUMNS,
        lineterminator="\n",
    )
    writer.writeheader()
    for record in matrix["sources"]:
        writer.writerow(_csv_row(record))
    return output.getvalue()


def _list_text(values: Sequence[Any]) -> str:
    return " / ".join(str(value) for value in values)


def render_html(matrix: Mapping[str, Any]) -> str:
    summary = matrix["summary"]
    rows: list[str] = []
    for record in matrix["sources"]:
        identity_parts = []
        if record["external_reference"]:
            identity_parts.append(
                "external: " + html.escape(str(record["external_reference"]))
            )
        if record["file_path"]:
            identity_parts.append(
                "local: " + html.escape(str(record["file_path"]))
            )
        identity_parts.append("SHA-256 " + html.escape(str(record["sha256"])))
        rows.append(
            "<tr>"
            f"<th scope=\"row\"><code>{html.escape(str(record['source_code']))}</code>"
            f"<strong>{html.escape(str(record['title']))}</strong></th>"
            f"<td>{html.escape(str(record['source_type']))}<br>"
            f"{html.escape(str(record['publisher']))} / "
            f"{html.escape(str(record['market']))}</td>"
            f"<td>{html.escape(str(record['document_date']))}<br>"
            f"status: {html.escape(str(record['status']))}</td>"
            f"<td>{'<br>'.join(identity_parts)}</td>"
            f"<td>{record['model_family_count']}: "
            f"{html.escape(_list_text(record['model_names']))}</td>"
            f"<td>{record['version_count']}<br>"
            f"{html.escape(_list_text(record['version_codes']))}</td>"
            f"<td>{record['configuration_count']}<br>"
            f"{html.escape(_list_text(record['configuration_codes']))}</td>"
            f"<td>{record['relationship_count']}<br>"
            f"{html.escape(_list_text(record['relationship_types']))}</td>"
            "</tr>"
        )
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>Portfolio Source Coverage Matrix</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;color:#1f2937}"
        "h1{margin-bottom:.25rem}.boundary{max-width:76rem;color:#4b5563}"
        ".table-wrap{overflow-x:auto;margin-top:1.5rem}"
        "table{border-collapse:collapse;min-width:110rem;width:100%}"
        "th,td{border:1px solid #d1d5db;padding:.65rem;text-align:left;vertical-align:top}"
        "thead th{background:#f3f4f6}tbody th{min-width:20rem}"
        "tbody th code{display:block;font-size:.72rem;color:#6b7280}"
        "tbody th strong{display:block;margin-top:.25rem}"
        "td{overflow-wrap:anywhere}footer{margin-top:1.5rem;color:#4b5563}"
        "</style></head><body><main>"
        "<h1>Portfolio Source Coverage Matrix</h1>"
        f"<p>Snapshot: <code>{html.escape(str(matrix.get('as_of')))}</code>. "
        f"{summary['provenance_source_count']} used provenance sources, "
        f"{summary['source_configuration_relationship_count']} explicit relationships, "
        f"{summary['active_configuration_count']} active configurations, "
        f"{summary['active_version_count']} active versions and "
        f"{summary['model_family_count']} model families.</p>"
        "<p class=\"boundary\">Every row preserves registered source metadata and "
        "exact canonical coverage derived only from explicit source relationships. "
        "The matrix creates no source quality score, ranking, recommendation or "
        "inferred value.</p>"
        "<div class=\"table-wrap\"><table><thead><tr>"
        "<th>Source</th><th>Type and publisher</th><th>Date and status</th>"
        "<th>Registered identity</th><th>Model families</th><th>Versions</th>"
        "<th>Configurations</th><th>Relationships</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div></main>"
        "<footer>Coverage is descriptive only. No source is preferred or rejected "
        "by this product.</footer></body></html>\n"
    )
