from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.change_impact_matrix import (
    REQUIRED_AREAS,
    requires_matrix,
    validate_change_impact,
    validate_matrix_text,
)


def matrix_text(result: str = "PASS") -> str:
    rows = [
        "| Area | Required evidence | Result (PASS / FAIL / N/A) | Exact command or artifact | Notes / unresolved items |",
        "|---|---|---|---|---|",
    ]
    for area in REQUIRED_AREAS:
        note = "Not applicable: no affected surface in this package" if result == "N/A" else "Verified against candidate tree"
        rows.append(f"| {area} | required evidence | {result} | tests/quality.log | {note} |")
    return "\n".join([
        "# Change-impact matrix",
        "## Package identity",
        "- Package: test-package",
        "## Change inventory",
        "| Entity type | Exact IDs |",
        "## Change-impact matrix",
        *rows,
        "## Test-contract review",
        "- [x] reviewed",
        "## Failure classification",
        "| Failure | Category |",
        "## Closure",
        "- Final tested head SHA: recorded in PR review",
    ])


class ChangeImpactMatrixTests(unittest.TestCase):
    def test_master_data_and_source_paths_require_matrix(self) -> None:
        self.assertTrue(requires_matrix("data/master/configurations.csv"))
        self.assertTrue(requires_matrix("data/master/sources.csv"))
        self.assertTrue(requires_matrix("data/source_intake/manifest.json"))
        self.assertTrue(requires_matrix("PDF/Cenniki/striker.pdf"))
        self.assertTrue(requires_matrix("data/reporting/striker_completeness.json"))
        self.assertFalse(requires_matrix("data/reporting/report_registry.json"))
        self.assertFalse(requires_matrix("project/ROADMAP.md"))

    def test_non_data_change_does_not_require_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(
                validate_change_impact(["tools/new_tool.py"], Path(temporary)),
                [],
            )

    def test_master_data_change_without_matrix_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            errors = validate_change_impact(["data/master/configurations.csv"], Path(temporary))
        self.assertTrue(any("require exactly one added or updated" in error for error in errors))

    def test_complete_matrix_passes_for_master_data_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            matrix = root / "project/packages/CHANGE_IMPACT_MATRIX_test.md"
            matrix.parent.mkdir(parents=True)
            matrix.write_text(matrix_text(), encoding="utf-8")
            self.assertEqual(
                validate_change_impact(
                    ["data/master/configurations.csv", "project/packages/CHANGE_IMPACT_MATRIX_test.md"],
                    root,
                ),
                [],
            )

    def test_missing_area_and_missing_evidence_fail(self) -> None:
        content = matrix_text().replace(
            "| Portfolio summaries | required evidence | PASS | tests/quality.log | Verified against candidate tree |\n",
            "",
        ).replace(
            "| Canonical registries | required evidence | PASS | tests/quality.log | Verified against candidate tree |",
            "| Canonical registries | required evidence | PASS | | Verified against candidate tree |",
        )
        errors = validate_matrix_text(content)
        self.assertTrue(any("missing required area: Portfolio summaries" in error for error in errors))
        self.assertTrue(any("exact command or artifact evidence is required" in error for error in errors))

    def test_failed_or_unjustified_not_applicable_rows_fail(self) -> None:
        content = matrix_text().replace(
            "| Tooling | required evidence | PASS | tests/quality.log | Verified against candidate tree |",
            "| Tooling | required evidence | FAIL | tests/quality.log | Failure unresolved |",
        ).replace(
            "| CI | required evidence | PASS | tests/quality.log | Verified against candidate tree |",
            "| CI | required evidence | N/A | tests/quality.log | |",
        )
        errors = validate_matrix_text(content)
        self.assertTrue(any("Tooling: result must be PASS or justified N/A" in error for error in errors))
        self.assertTrue(any("CI: N/A requires a reason" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
