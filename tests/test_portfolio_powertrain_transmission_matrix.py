from __future__ import annotations

import csv
import io
import json
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from reporting.portfolio_powertrain_transmission_matrix import (  # noqa: E402
    collect_matrix,
    render_csv,
    render_html,
    render_json,
)


class PortfolioPowertrainTransmissionMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = collect_matrix(REPOSITORY)

    def test_every_active_configuration_is_covered_once(self) -> None:
        with (REPOSITORY / "data/master/configurations.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            active = {
                row["code"]
                for row in csv.DictReader(handle)
                if row["status"] == "active"
            }
        covered = [
            code
            for record in self.matrix["records"]
            for code in record["configuration_codes"]
        ]
        self.assertEqual(set(covered), active)
        self.assertEqual(len(covered), len(active))

    def test_group_identity_uses_exact_recorded_values(self) -> None:
        identities = [
            (record["powertrain_label"], record["transmission_type"])
            for record in self.matrix["records"]
        ]
        self.assertEqual(
            identities,
            sorted(
                identities,
                key=lambda value: (value[0].casefold(), value[1].casefold()),
            ),
        )
        self.assertEqual(len(identities), len(set(identities)))

    def test_no_inference_or_recommendation_flags(self) -> None:
        summary = self.matrix["summary"]
        self.assertFalse(summary["ranking_generated"])
        self.assertFalse(summary["recommendations_generated"])
        self.assertFalse(summary["inferred_values_generated"])

    def test_json_csv_and_html_are_deterministic_and_self_describing(self) -> None:
        json_text = render_json(self.matrix)
        self.assertEqual(json.loads(json_text), self.matrix)
        csv_text = render_csv(self.matrix)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        self.assertEqual(len(rows), len(self.matrix["records"]))
        html_text = render_html(self.matrix)
        self.assertIn("<!doctype html>", html_text.lower())
        self.assertIn("Macierz układów napędowych", html_text)
        self.assertIn("Nie tworzy rankingu", html_text)
        self.assertEqual(json_text, render_json(collect_matrix(REPOSITORY)))
        self.assertEqual(csv_text, render_csv(collect_matrix(REPOSITORY)))
        self.assertEqual(html_text, render_html(collect_matrix(REPOSITORY)))


if __name__ == "__main__":
    unittest.main()
