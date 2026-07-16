from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS_DIRECTORY = REPOSITORY / "tools"

sys.path.insert(0, str(TOOLS_DIRECTORY))
import dkb  # noqa: E402


class DkbCliTests(unittest.TestCase):
    def test_displays_help_without_arguments(
        self,
    ) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = dkb.main([])

        output = stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Dacia Knowledge Base", output)
        self.assertIn(
            "python tools/dkb.py <command>",
            output,
        )
        self.assertIn("sqlite-verify", output)
        self.assertIn("quality", output)
        self.assertIn("dictionary", output)
        self.assertIn("package-review", output)

    def test_accepts_all_help_aliases(
        self,
    ) -> None:
        for argument in ("help", "--help", "-h"):
            with self.subTest(argument=argument):
                stdout = io.StringIO()

                with redirect_stdout(stdout):
                    result = dkb.main([argument])

                self.assertEqual(result, 0)
                self.assertIn(
                    "Commands:",
                    stdout.getvalue(),
                )

    def test_rejects_unknown_command(
        self,
    ) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = dkb.main(["unknown-command"])

        self.assertEqual(result, 2)
        self.assertIn(
            "ERROR: unknown command: unknown-command",
            stderr.getvalue(),
        )
        self.assertIn("Usage:", stdout.getvalue())

    def test_rejects_arguments_for_report_command(
        self,
    ) -> None:
        stderr = io.StringIO()

        with (
            mock.patch.object(
                dkb,
                "generate_report",
            ) as generate_report,
            redirect_stderr(stderr),
        ):
            result = dkb.main(
                ["catalog", "unexpected"]
            )

        self.assertEqual(result, 2)
        generate_report.assert_not_called()
        self.assertIn(
            "does not accept arguments",
            stderr.getvalue(),
        )

    def test_forwards_script_arguments_and_exit_code(
        self,
    ) -> None:
        completed = SimpleNamespace(returncode=7)

        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "search",
                [
                    "Duster",
                    "--field",
                    "name",
                ],
            )

        self.assertEqual(result, 7)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "search.py"),
                "Duster",
                "--field",
                "name",
            ],
            check=False,
        )

    def test_forwards_workflow_arguments_and_exit_code(
        self,
    ) -> None:
        completed = SimpleNamespace(returncode=6)

        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_workflow(
                "package-review",
                ["--quality"],
            )

        self.assertEqual(result, 6)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "package_workflow.py"),
                "review",
                "--quality",
            ],
            check=False,
        )

    def test_main_dispatches_workflow_command(
        self,
    ) -> None:
        with mock.patch.object(
            dkb,
            "run_workflow",
            return_value=4,
        ) as run_workflow:
            result = dkb.main(
                ["package-finish", "--base-ref", "origin/main"]
            )

        self.assertEqual(result, 4)
        run_workflow.assert_called_once_with(
            "package-finish",
            ["--base-ref", "origin/main"],
        )

    def test_main_dispatches_script_command(
        self,
    ) -> None:
        with mock.patch.object(
            dkb,
            "run_script",
            return_value=5,
        ) as run_script:
            result = dkb.main(
                [
                    "search",
                    "Duster",
                    "--field",
                    "name",
                ]
            )

        self.assertEqual(result, 5)
        run_script.assert_called_once_with(
            "search",
            [
                "Duster",
                "--field",
                "name",
            ],
        )

    def test_main_dispatches_report_command(
        self,
    ) -> None:
        with mock.patch.object(
            dkb,
            "generate_report",
            return_value=0,
        ) as generate_report:
            result = dkb.main(["dictionary"])

        self.assertEqual(result, 0)
        generate_report.assert_called_once_with(
            "dictionary",
            REPOSITORY,
        )

    def test_reports_missing_command_script(
        self,
    ) -> None:
        stderr = io.StringIO()

        with (
            mock.patch.dict(
                dkb.SCRIPT_COMMANDS,
                {
                    "broken": (
                        "missing_script.py",
                        "Broken command.",
                        "",
                    ),
                },
            ),
            redirect_stderr(stderr),
        ):
            result = dkb.run_script(
                "broken",
                [],
            )

        self.assertEqual(result, 1)
        self.assertIn(
            "command script does not exist",
            stderr.getvalue(),
        )



    def test_configuration_gap_triage_help_and_forwarding(
        self,
    ) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            help_result = dkb.main([])
        self.assertEqual(help_result, 0)
        self.assertIn("configuration-gap-triage", stdout.getvalue())

        completed = SimpleNamespace(returncode=13)
        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "configuration-gap-triage",
                ["--json", "triage.json"],
            )
        self.assertEqual(result, 13)
        run.assert_called_once_with(
            [
                sys.executable,
                str(
                    TOOLS_DIRECTORY
                    / "configuration_gap_triage.py"
                ),
                "--json",
                "triage.json",
            ],
            check=False,
        )


    def test_source_coverage_help_and_forwarding(
        self,
    ) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            help_result = dkb.main([])
        self.assertEqual(help_result, 0)
        self.assertIn("source-coverage", stdout.getvalue())

        completed = SimpleNamespace(returncode=12)
        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "source-coverage",
                ["--json", "source-coverage.json"],
            )
        self.assertEqual(result, 12)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "source_coverage.py"),
                "--json",
                "source-coverage.json",
            ],
            check=False,
        )


    def test_configuration_completeness_help_and_forwarding(
        self,
    ) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            help_result = dkb.main([])
        self.assertEqual(help_result, 0)
        self.assertIn("configuration-completeness", stdout.getvalue())
        completed = SimpleNamespace(returncode=11)
        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "configuration-completeness",
                ["--json", "completeness.json"],
            )
        self.assertEqual(result, 11)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "configuration_completeness.py"),
                "--json",
                "completeness.json",
            ],
            check=False,
        )


    def test_documentation_baseline_help_and_forwarding(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            help_result = dkb.main([])

        self.assertEqual(help_result, 0)
        self.assertIn("documentation-baseline", stdout.getvalue())

        completed = SimpleNamespace(returncode=10)
        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "documentation-baseline",
                ["--check", "--json", "baseline.json"],
            )

        self.assertEqual(result, 10)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "documentation_baseline.py"),
                "--check",
                "--json",
                "baseline.json",
            ],
            check=False,
        )


    def test_help_includes_configuration_value_import(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = dkb.main([])

        self.assertEqual(result, 0)
        self.assertIn(
            "import-configuration-values",
            stdout.getvalue(),
        )

    def test_forwards_configuration_value_import_arguments(self) -> None:
        completed = SimpleNamespace(returncode=9)

        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "import-configuration-values",
                ["--spec", "spec.json", "--verify"],
            )

        self.assertEqual(result, 9)
        run.assert_called_once_with(
            [
                sys.executable,
                str(
                    TOOLS_DIRECTORY
                    / "import_configuration_values.py"
                ),
                "--spec",
                "spec.json",
                "--verify",
            ],
            check=False,
        )

    def test_help_includes_package_publish(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = dkb.main([])

        self.assertEqual(result, 0)
        self.assertIn("package-publish", stdout.getvalue())

    def test_forwards_package_publish_arguments_and_exit_code(self) -> None:
        completed = SimpleNamespace(returncode=8)

        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = dkb.run_script(
                "package-publish",
                ["--manifest", "package.json"],
            )

        self.assertEqual(result, 8)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "package_publish.py"),
                "--manifest",
                "package.json",
            ],
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
