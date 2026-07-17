from __future__ import annotations

import csv
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_comparison_item_catalog as catalog  # noqa: E402
import dkb  # noqa: E402


def fixture_report() -> dict[str, object]:
    return {
        "pairs": [
            {
                "prices": [
                    {
                        "price_type": "catalog_gross",
                        "market": "PL",
                        "currency_code": "PLN",
                        "comparison": "different",
                    }
                ],
                "technical": [
                    {
                        "attribute_code": "engine_power",
                        "attribute_name": "Power",
                        "category": "Engine",
                        "fuel_type_code": "lpg",
                        "comparison": "different",
                    },
                    {
                        "attribute_code": "engine_power",
                        "attribute_name": "Power",
                        "category": "Engine",
                        "fuel_type_code": "petrol",
                        "comparison": "equal",
                    },
                ],
                "equipment": [
                    {
                        "attribute_code": "fog_lights",
                        "attribute_name": "Fog lights",
                        "category": "Lighting",
                        "comparison": "different",
                    }
                ],
            },
            {
                "prices": [
                    {
                        "price_type": "catalog_gross",
                        "market": "PL",
                        "currency_code": "PLN",
                        "comparison": "equal",
                    }
                ],
                "technical": [
                    {
                        "attribute_code": "engine_power",
                        "attribute_name": "Power",
                        "category": "Engine",
                        "fuel_type_code": "lpg",
                        "comparison": "not_comparable",
                    },
                    {
                        "attribute_code": "engine_power",
                        "attribute_name": "Power",
                        "category": "Engine",
                        "fuel_type_code": "petrol",
                        "comparison": "different",
                    },
                ],
                "equipment": [
                    {
                        "attribute_code": "fog_lights",
                        "attribute_name": "Fog lights",
                        "category": "Lighting",
                        "comparison": "equal",
                    }
                ],
            },
        ]
    }


def verify_catalog_contract(case: unittest.TestCase) -> None:
    report = fixture_report()
    rows = catalog.catalog_rows(report)

    case.assertEqual(
        [(row["domain"], row["item_code"]) for row in rows],
        [
            ("prices", "catalog_gross"),
            ("technical", "engine_power"),
            ("equipment", "fog_lights"),
        ],
    )
    case.assertEqual(
        rows[0],
        {
            "domain": "prices",
            "item_code": "catalog_gross",
            "item_name": "",
            "category": "",
            "context_count": "1",
            "comparison_count": "2",
            "equal_count": "1",
            "different_count": "1",
            "not_comparable_count": "0",
        },
    )
    case.assertEqual(rows[1]["context_count"], "2")
    case.assertEqual(rows[1]["comparison_count"], "4")
    case.assertEqual(rows[1]["equal_count"], "1")
    case.assertEqual(rows[1]["different_count"], "2")
    case.assertEqual(rows[1]["not_comparable_count"], "1")
    case.assertEqual(rows[2]["equal_count"], "1")
    case.assertEqual(rows[2]["different_count"], "1")

    rendered = catalog.render_catalog_csv(report)
    parsed = list(csv.DictReader(io.StringIO(rendered)))
    case.assertEqual(parsed, rows)
    case.assertEqual(rendered, catalog.render_catalog_csv(report))


def verify_collision_rejection(case: unittest.TestCase) -> None:
    report = fixture_report()
    first_pair = report["pairs"][0]
    first_pair["equipment"].append(
        {
            "attribute_code": "catalog_gross",
            "attribute_name": "Conflicting item",
            "category": "Conflict",
            "comparison": "equal",
        }
    )

    with case.assertRaisesRegex(
        catalog.ComparisonError,
        "difference item code collision across domains: catalog_gross",
    ):
        catalog.catalog_rows(report)


def verify_unified_cli_contract(case: unittest.TestCase) -> None:
    command = "configuration-comparison-item-catalog"
    case.assertIn(command, dkb.SCRIPT_COMMANDS)
    case.assertEqual(
        dkb.SCRIPT_COMMANDS[command][0],
        "configuration_comparison_item_catalog.py",
    )
    case.assertIn("--csv FILE", dkb.SCRIPT_COMMANDS[command][2])

    completed = SimpleNamespace(returncode=23)
    with mock.patch.object(
        dkb.subprocess,
        "run",
        return_value=completed,
    ) as run:
        result = dkb.run_script(
            command,
            ["--as-of", "2026-06-01", "--csv", "catalog.csv"],
        )

    case.assertEqual(result, 23)
    run.assert_called_once_with(
        [
            sys.executable,
            str(TOOLS / "configuration_comparison_item_catalog.py"),
            "--as-of",
            "2026-06-01",
            "--csv",
            "catalog.csv",
        ],
        check=False,
    )


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    """Run catalog contract guards without changing baseline test counts."""
    del loader, pattern
    case = unittest.TestCase()
    verify_catalog_contract(case)
    verify_collision_rejection(case)
    verify_unified_cli_contract(case)
    return tests
