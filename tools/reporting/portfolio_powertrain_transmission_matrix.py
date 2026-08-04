from __future__ import annotations

import csv
import html
import io
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

MATRIX_VERSION = 1
CSV_COLUMNS = (
    "powertrain_label",
    "transmission_type",
    "configuration_count",
    "model_count",
    "version_count",
    "model_codes",
    "version_codes",
    "configuration_codes",
)


class PortfolioPowertrainTransmissionMatrixError(ValueError):
    """Raised when the deterministic matrix cannot be built."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise PortfolioPowertrainTransmissionMatrixError(
                    f"missing CSV header: {path}"
                )
            return list(reader)
    except OSError as exc:
        raise PortfolioPowertrainTransmissionMatrixError(
            f"cannot read CSV file {path}: {exc}"
        ) from exc


def collect_matrix(repository: Path) -> dict[str, Any]:
    master = repository / "data" / "master"
    models = {
        row["code"]: row
        for row in _read_csv(master / "models.csv")
        if row.get("status") == "active"
    }
    versions = {
        row["code"]: row
        for row in _read_csv(master / "versions.csv")
        if row.get("status") == "active"
    }
    configurations = [
        row
        for row in _read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    ]
    if not configurations:
        raise PortfolioPowertrainTransmissionMatrixError(
            "no active configurations"
        )

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    seen_codes: set[str] = set()
    for configuration in configurations:
        code = configuration.get("code", "")
        if not code or code in seen_codes:
            raise PortfolioPowertrainTransmissionMatrixError(
                f"invalid or duplicate configuration code: {code!r}"
            )
        seen_codes.add(code)
        version_code = configuration.get("version_code", "")
        version = versions.get(version_code)
        if version is None:
            raise PortfolioPowertrainTransmissionMatrixError(
                f"configuration references unknown active version: {code} -> {version_code}"
            )
        model_code = version.get("model_code", "")
        if model_code not in models:
            raise PortfolioPowertrainTransmissionMatrixError(
                f"version references unknown active model: {version_code} -> {model_code}"
            )
        powertrain = configuration.get("powertrain_label", "").strip()
        transmission = configuration.get("transmission_type", "").strip()
        if not powertrain or not transmission:
            raise PortfolioPowertrainTransmissionMatrixError(
                f"missing exact powertrain/transmission value: {code}"
            )
        groups[(powertrain, transmission)].append(
            {
                "configuration_code": code,
                "version_code": version_code,
                "version_name": version.get("name", ""),
                "model_code": model_code,
                "model_name": models[model_code].get("name", ""),
            }
        )

    records: list[dict[str, Any]] = []
    for (powertrain, transmission), members in sorted(
        groups.items(), key=lambda item: (item[0][0].casefold(), item[0][1].casefold())
    ):
        ordered = sorted(
            members,
            key=lambda item: (
                item["model_code"],
                item["version_code"],
                item["configuration_code"],
            ),
        )
        records.append(
            {
                "powertrain_label": powertrain,
                "transmission_type": transmission,
                "configuration_count": len(ordered),
                "model_count": len({item["model_code"] for item in ordered}),
                "version_count": len({item["version_code"] for item in ordered}),
                "model_codes": sorted({item["model_code"] for item in ordered}),
                "version_codes": sorted({item["version_code"] for item in ordered}),
                "configuration_codes": [
                    item["configuration_code"] for item in ordered
                ],
                "configurations": ordered,
            }
        )

    return {
        "matrix_version": MATRIX_VERSION,
        "summary": {
            "active_configuration_count": len(configurations),
            "powertrain_transmission_group_count": len(records),
            "active_model_count": len(
                {item["model_code"] for record in records for item in record["configurations"]}
            ),
            "active_version_count": len(
                {item["version_code"] for record in records for item in record["configurations"]}
            ),
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "records": records,
    }


def render_json(matrix: dict[str, Any]) -> str:
    return json.dumps(matrix, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_csv(matrix: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in matrix["records"]:
        writer.writerow(
            {
                "powertrain_label": record["powertrain_label"],
                "transmission_type": record["transmission_type"],
                "configuration_count": record["configuration_count"],
                "model_count": record["model_count"],
                "version_count": record["version_count"],
                "model_codes": "|".join(record["model_codes"]),
                "version_codes": "|".join(record["version_codes"]),
                "configuration_codes": "|".join(record["configuration_codes"]),
            }
        )
    return output.getvalue()


def render_html(matrix: dict[str, Any]) -> str:
    rows = []
    for record in matrix["records"]:
        configurations = "<br>".join(
            html.escape(code) for code in record["configuration_codes"]
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(record['powertrain_label'])}</td>"
            f"<td>{html.escape(record['transmission_type'])}</td>"
            f"<td>{record['configuration_count']}</td>"
            f"<td>{record['model_count']}</td>"
            f"<td>{record['version_count']}</td>"
            f"<td>{configurations}</td>"
            "</tr>"
        )
    summary = matrix["summary"]
    return """<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Macierz układów napędowych i skrzyń Dacia</title>
<style>body{font-family:system-ui,sans-serif;margin:2rem;background:#161a18;color:#f2f4f2}h1{margin-bottom:.3rem}.summary{color:#bac1bc;margin-bottom:1.2rem}table{border-collapse:collapse;width:100%;background:#202522}th,td{border:1px solid #465049;padding:.55rem;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#303732}tr:nth-child(even){background:#262c28}code{white-space:nowrap}</style>
</head><body><h1>Macierz układów napędowych i skrzyń biegów</h1>
<p class="summary">Aktywne konfiguracje: %s · grupy: %s · modele: %s · wersje: %s</p>
<table><thead><tr><th>Układ napędowy</th><th>Skrzynia</th><th>Konfiguracje</th><th>Modele</th><th>Wersje</th><th>Kody konfiguracji</th></tr></thead><tbody>%s</tbody></table>
<p>Widok grupuje wyłącznie dokładnie zapisane wartości. Nie tworzy rankingu, rekomendacji ani wartości domyślnych.</p></body></html>
""" % (
        summary["active_configuration_count"],
        summary["powertrain_transmission_group_count"],
        summary["active_model_count"],
        summary["active_version_count"],
        "".join(rows),
    )


def write_outputs(repository: Path, output_dir: Path) -> dict[str, Path]:
    matrix = collect_matrix(repository)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / "portfolio-powertrain-transmission-matrix.json",
        "csv": output_dir / "portfolio-powertrain-transmission-matrix.csv",
        "html": output_dir / "portfolio-powertrain-transmission-matrix.html",
    }
    paths["json"].write_text(render_json(matrix), encoding="utf-8", newline="\n")
    paths["csv"].write_text(render_csv(matrix), encoding="utf-8", newline="\n")
    paths["html"].write_text(render_html(matrix), encoding="utf-8", newline="\n")
    return paths


if __name__ == "__main__":
    write_outputs(repository_root(), repository_root() / "output" / "portfolio-powertrain-transmission-matrix")
