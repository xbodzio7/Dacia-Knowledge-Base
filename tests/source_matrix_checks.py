from __future__ import annotations

import csv
import io
import json
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import portfolio_source_coverage_matrix as source_cli
from reporting.portfolio_source_coverage_matrix import (
    CSV_COLUMNS,
    collect_matrix,
    render_csv,
    render_html,
    render_json,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def run_source_matrix_checks(testcase: Any, repository: Path) -> None:
    matrix = collect_matrix(repository)
    summary = matrix["summary"]
    testcase.assertEqual(matrix["version"], 1)
    testcase.assertEqual(matrix["kind"], "portfolio_source_coverage_matrix")
    testcase.assertEqual(matrix["as_of"], "2026-08-02")
    testcase.assertEqual(
        summary,
        {
            "provenance_source_count": 33,
            "source_configuration_relationship_count": 254,
            "active_configuration_count": 84,
            "active_version_count": 22,
            "model_family_count": 6,
            "configurations_without_provenance_count": 0,
            "source_quality_scores_generated": False,
            "source_rankings_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
    )

    master = repository / "data/master"
    sources = {row["code"]: row for row in _read_csv(master / "sources.csv")}
    versions = {
        row["code"]: row
        for row in _read_csv(master / "versions.csv")
        if row.get("status") == "active"
    }
    configurations = {
        row["code"]: row
        for row in _read_csv(master / "configurations.csv")
        if row.get("status") == "active"
    }
    models = {row["code"]: row for row in _read_csv(master / "models.csv")}
    relationships = [
        row
        for row in _read_csv(master / "source_configurations.csv")
        if row.get("configuration_code") in configurations
    ]
    relations_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for relation in relationships:
        relations_by_source[relation["source_code"]].append(relation)

    records = matrix["sources"]
    testcase.assertEqual(len(records), 33)
    testcase.assertEqual(
        {record["source_code"] for record in records},
        set(relations_by_source),
    )

    relationship_total = 0
    covered_configurations: set[str] = set()
    covered_versions: set[str] = set()
    covered_models: set[str] = set()
    for record in records:
        source_code = record["source_code"]
        source = sources[source_code]
        source_relations = relations_by_source[source_code]
        expected_configurations = sorted(
            {row["configuration_code"] for row in source_relations}
        )
        expected_versions = sorted(
            {configurations[code]["version_code"] for code in expected_configurations}
        )
        expected_models = sorted(
            {versions[code]["model_code"] for code in expected_versions}
        )

        for field in (
            "source_type",
            "title",
            "publisher",
            "market",
            "document_date",
            "external_reference",
            "file_path",
            "sha256",
            "status",
            "notes",
        ):
            testcase.assertEqual(record[field], source[field])
        testcase.assertEqual(record["status"], "active")
        testcase.assertRegex(record["sha256"], r"^[0-9a-f]{64}$")
        testcase.assertTrue(record["external_reference"] or record["file_path"])
        testcase.assertEqual(record["relationship_count"], len(source_relations))
        testcase.assertEqual(
            record["relationship_types"],
            sorted({row["relationship"] for row in source_relations}),
        )
        testcase.assertEqual(record["configuration_codes"], expected_configurations)
        testcase.assertEqual(record["configuration_count"], len(expected_configurations))
        testcase.assertEqual(record["version_codes"], expected_versions)
        testcase.assertEqual(record["version_count"], len(expected_versions))
        testcase.assertEqual(record["model_codes"], expected_models)
        testcase.assertEqual(record["model_family_count"], len(expected_models))
        testcase.assertEqual(
            record["model_names"],
            [models[code]["name"] for code in expected_models],
        )

        relationship_total += record["relationship_count"]
        covered_configurations.update(expected_configurations)
        covered_versions.update(expected_versions)
        covered_models.update(expected_models)

    testcase.assertEqual(relationship_total, 254)
    testcase.assertEqual(covered_configurations, set(configurations))
    testcase.assertEqual(covered_versions, set(versions))
    testcase.assertEqual(
        covered_models,
        {version["model_code"] for version in versions.values()},
    )

    json_text = render_json(matrix)
    csv_text = render_csv(matrix)
    html_text = render_html(matrix)
    testcase.assertEqual(json_text, render_json(matrix))
    testcase.assertEqual(csv_text, render_csv(matrix))
    testcase.assertEqual(html_text, render_html(matrix))
    testcase.assertEqual(json.loads(json_text), matrix)
    csv_rows = list(csv.DictReader(io.StringIO(csv_text)))
    testcase.assertEqual(tuple(csv_rows[0]), CSV_COLUMNS)
    testcase.assertEqual(len(csv_rows), 33)
    testcase.assertEqual(
        sum(int(row["relationship_count"]) for row in csv_rows),
        254,
    )
    lowered = html_text.lower()
    testcase.assertTrue(html_text.startswith("<!doctype html>"))
    testcase.assertNotIn("<script", lowered)
    testcase.assertNotIn("<img", lowered)
    testcase.assertNotIn("<link", lowered)
    testcase.assertEqual(html_text.count("<tr>"), 34)
    testcase.assertEqual(html_text.count("SHA-256 "), 33)
    testcase.assertIn("creates no source quality score", html_text)
    testcase.assertIn("No source is preferred or rejected", html_text)

    base = repository / "data/reporting/portfolio_source_coverage_matrix"
    testcase.assertEqual(
        base.with_suffix(".json").read_text(encoding="utf-8"),
        json_text,
    )
    testcase.assertEqual(
        base.with_suffix(".csv").read_text(encoding="utf-8"),
        csv_text,
    )
    testcase.assertEqual(
        base.with_suffix(".html").read_text(encoding="utf-8"),
        html_text,
    )

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        json_path = root / "matrix.json"
        csv_path = root / "matrix.csv"
        html_path = root / "matrix.html"
        result = source_cli.main(
            [
                "--json",
                str(json_path),
                "--csv",
                str(csv_path),
                "--html",
                str(html_path),
            ],
            repository=repository,
        )
        testcase.assertEqual(result, 0)
        testcase.assertEqual(json_path.read_text(encoding="utf-8"), json_text)
        testcase.assertEqual(csv_path.read_text(encoding="utf-8"), csv_text)
        testcase.assertEqual(html_path.read_text(encoding="utf-8"), html_text)
