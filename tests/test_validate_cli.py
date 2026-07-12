from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.validators.references import REFERENCE_RULES


class ValidateCliIntegrationTests(unittest.TestCase):
    def test_validate_command_executes_complete_validator(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"

        completed = subprocess.run(
            [
                sys.executable,
                "tools/dkb.py",
                "validate",
            ],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        combined_output = (
            completed.stdout
            + "\n"
            + completed.stderr
        )

        self.assertEqual(
            completed.returncode,
            0,
            msg=combined_output,
        )

        expected_fragments = (
            "DKB Validator v0.10",
            "1. Sprawdzanie struktury repozytorium",
            "2. Walidacja plików CSV",
            "3. Walidacja unikalności kluczy",
            "4. Walidacja relacji między tabelami",
            "5. Walidacja zakresów lat",
            "6. Walidacja statusów i cyklu życia",
            "7. Walidacja okresów dostępności powiązań",
            "8. Walidacja nakładających się okresów powiązań",
            "9. Walidacja kontraktu reguł danych",
            "10. Wykonywanie reguł danych",
            "11. Zbieranie statystyk",
            "12. Generowanie raportu",
            f"{len(REFERENCE_RULES)} relacji",
        )

        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    completed.stdout,
                )

        report_path = (
            repository
            / "reports"
            / "validation_report.md"
        )

        self.assertTrue(
            report_path.is_file(),
            msg="Validation report was not generated.",
        )

        report = report_path.read_text(
            encoding="utf-8",
        )

        self.assertIn(
            "- Overall validation: **PASS**",
            report,
        )
        self.assertIn(
            "- Key uniqueness: **PASS**",
            report,
        )
        self.assertIn(
            "- Cross-file references: **PASS**",
            report,
        )
        self.assertIn(
            "- Year ranges: **PASS**",
            report,
        )
        self.assertIn(
            "- Lifecycle statuses: **PASS**",
            report,
        )
        self.assertIn(
            "- Association ranges: **PASS**",
            report,
        )
        self.assertIn(
            "- Association interval uniqueness: **PASS**",
            report,
        )
        self.assertIn(
            "- Validation rule contracts: **PASS**",
            report,
        )
        self.assertIn(
            "- Data rule execution: **PASS**",
            report,
        )


if __name__ == "__main__":
    unittest.main()
