from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path
from typing import Any

from source_matrix_checks import run_source_matrix_checks

import portfolio_model_version_comparison_matrix as version_cli
from reporting.portfolio_model_version_comparison_matrix import (
    CSV_COLUMNS,
    collect_matrix,
    render_csv,
    render_html,
    render_json,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def run_version_matrix_checks(testcase: Any, repository: Path) -> None:
    matrix = collect_matrix(repository)
    summary = matrix["summary"]
    testcase.assertEqual(matrix["version"], 1)
    testcase.assertEqual(
        matrix["kind"],
        "portfolio_model_version_comparison_matrix",
    )
    testcase.assertEqual(matrix["as_of"], "2026-08-09")
    testcase.assertEqual(
        summary,
        {
            "model_family_count": 6,
            "active_version_count": 22,
            "active_configuration_count": 84,
            "reporting_scope_count": 23,
            "provenance_source_count": 35,
            "source_configuration_relationship_count": 284,
            "configurations_without_provenance_count": 0,
            "configuration_pairs_generated": False,
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
    )

    active_versions = [
        row
        for row in _read_csv(repository / "data/master/versions.csv")
        if row.get("status") == "active"
    ]
    active_configurations = [
        row
        for row in _read_csv(repository / "data/master/configurations.csv")
        if row.get("status") == "active"
    ]
    records = matrix["versions"]
    testcase.assertEqual(len(records), 22)
    testcase.assertEqual(
        {record["version_code"] for record in records},
        {row["code"] for row in active_versions},
    )

    configuration_codes: list[str] = []
    relation_total = 0
    used_models: set[str] = set()
    for record in records:
        codes = record["configuration_codes"]
        configuration_codes.extend(codes)
        used_models.add(record["model_code"])
        testcase.assertEqual(record["configuration_count"], len(codes))
        price = record["catalog_price"]
        testcase.assertEqual(
            price["recorded_count"] + price["missing_count"],
            record["configuration_count"],
        )
        if price["state"] == "recorded":
            testcase.assertEqual(price["currency"], "PLN")
            testcase.assertIsNotNone(price["minimum"])
            testcase.assertIsNotNone(price["maximum"])
            testcase.assertLessEqual(price["minimum"], price["maximum"])
        else:
            testcase.assertEqual(price["state"], "not_stated")
            testcase.assertEqual(price["currency"], "")
            testcase.assertIsNone(price["minimum"])
            testcase.assertIsNone(price["maximum"])

        seats = record["recorded_seat_values"]
        if record["seat_summary_state"] == "recorded":
            testcase.assertTrue(seats)
        else:
            testcase.assertEqual(record["seat_summary_state"], "not_stated")
            testcase.assertEqual(seats, [])

        testcase.assertEqual(
            record["reporting_scope_count"],
            record["single_model_scope_count"]
            + record["mixed_model_scope_count"],
        )
        testcase.assertEqual(
            record["reporting_scope_count"],
            len(record["scope_slugs"]),
        )
        testcase.assertEqual(
            record["single_model_scope_count"],
            len(record["single_model_scope_slugs"]),
        )
        testcase.assertEqual(
            record["mixed_model_scope_count"],
            len(record["mixed_model_scope_slugs"]),
        )

        provenance = record["provenance"]
        testcase.assertEqual(
            provenance["configuration_coverage_count"],
            record["configuration_count"],
        )
        testcase.assertEqual(provenance["missing_configuration_count"], 0)
        testcase.assertGreater(provenance["source_count"], 0)
        testcase.assertGreater(provenance["relationship_count"], 0)
        testcase.assertLessEqual(
            provenance["earliest_document_date"],
            provenance["latest_document_date"],
        )
        relation_total += provenance["relationship_count"]

    testcase.assertEqual(used_models, {
        "sandero_iii",
        "sandero_stepway_iii",
        "jogger",
        "duster_iii",
        "bigster",
        "spring",
    })
    testcase.assertEqual(len(configuration_codes), 84)
    testcase.assertEqual(len(set(configuration_codes)), 84)
    testcase.assertEqual(
        set(configuration_codes),
        {row["code"] for row in active_configurations},
    )
    testcase.assertEqual(relation_total, 284)

    anchors = {record["version_code"]: record for record in records}
    testcase.assertEqual(
        anchors["duster_iii_journey_plus"]["configuration_count"], 1
    )
    testcase.assertEqual(
        anchors["spring_essential"]["configuration_count"], 1
    )
    testcase.assertEqual(
        anchors["sandero_iii_essential"]["powertrain_labels"],
        ["TCe 100"],
    )
    testcase.assertEqual(
        anchors["spring_extreme"]["transmission_values"],
        ["automatic"],
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
    testcase.assertEqual(len(csv_rows), 22)
    lowered = html_text.lower()
    testcase.assertTrue(html_text.startswith("<!doctype html>"))
    testcase.assertNotIn("<script", lowered)
    testcase.assertNotIn("<img", lowered)
    testcase.assertNotIn("http://", lowered)
    testcase.assertNotIn("https://", lowered)
    testcase.assertEqual(html_text.count("<tr>"), 23)
    testcase.assertIn("creates no configuration pair", html_text)
    testcase.assertIn("No version is ranked or recommended", html_text)

    base = repository / "data/reporting/portfolio_model_version_comparison_matrix"
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
        result = version_cli.main(
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

    run_source_matrix_checks(testcase, repository)
