from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


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
            "DKB Validator v0.5",
            "1. Sprawdzanie struktury repozytorium",
            "2. Walidacja plików CSV",
            "3. Walidacja unikalności kluczy",
            "4. Walidacja relacji między tabelami",
            "5. Walidacja zakresów lat",
            "6. Zbieranie statystyk",
            "7. Generowanie raportu",
            "13 relacji",
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


if __name__ == "__main__":
    unittest.main()
