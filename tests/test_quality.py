from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS_DIRECTORY = REPOSITORY / "tools"

sys.path.insert(0, str(TOOLS_DIRECTORY))
import quality  # noqa: E402


class QualityTests(unittest.TestCase):
    def test_builds_ci_equivalent_steps(
        self,
    ) -> None:
        database = REPOSITORY / "quality.sqlite"

        steps = quality.quality_steps(
            REPOSITORY,
            database,
        )

        self.assertEqual(
            [label for label, _ in steps],
            [
                "Compile Python sources",
                "Run unit tests",
                "Check CSV encoding",
                "Validate repository data",
                "Build SQLite database",
                "Verify SQLite database",
                "Check documentation baseline",
                "Generate configuration completeness report",
                "Generate source coverage report",
            ],
        )

        self.assertEqual(
            steps[0][1],
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "tools",
                "scripts",
                "tests",
            ],
        )
        self.assertEqual(
            steps[1][1],
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_*.py",
                "-v",
            ],
        )
        self.assertEqual(
            steps[-5][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "sqlite",
                "--output",
                str(database),
            ],
        )
        self.assertEqual(
            steps[-4][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "sqlite-verify",
                str(database),
            ],
        )
        self.assertEqual(
            steps[-3][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "documentation-baseline",
                "--check",
                "--database",
                str(database),
                "--json",
                str(database.with_name("documentation-baseline.json")),
                "--markdown",
                str(database.with_name("documentation-baseline.md")),
            ],
        )
        self.assertEqual(
            steps[-2][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "configuration-completeness",
                "--json",
                str(database.with_name("configuration-completeness.json")),
                "--markdown",
                str(database.with_name("configuration-completeness.md")),
            ],
        )
        self.assertEqual(
            steps[-1][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "source-coverage",
                "--json",
                str(database.with_name("source-coverage.json")),
                "--markdown",
                str(database.with_name("source-coverage.md")),
            ],
        )

    def test_quality_environment_forces_utf8(self) -> None:
        with mock.patch.dict(
            quality.os.environ,
            {
                "PYTHONUTF8": "0",
                "PYTHONIOENCODING": "cp1250",
                "LANG": "pl_PL.cp1250",
                "LC_ALL": "pl_PL.cp1250",
            },
            clear=False,
        ):
            environment = quality.quality_environment()

        self.assertEqual(environment["PYTHONUTF8"], "1")
        self.assertEqual(
            environment["PYTHONIOENCODING"],
            "utf-8",
        )
        self.assertEqual(environment["LANG"], "C.UTF-8")
        self.assertEqual(environment["LC_ALL"], "C.UTF-8")

    def test_run_step_propagates_exit_code(
        self,
    ) -> None:
        completed = SimpleNamespace(returncode=7)
        stdout = io.StringIO()

        with (
            mock.patch.object(
                quality.subprocess,
                "run",
                return_value=completed,
            ) as run,
            redirect_stdout(stdout),
        ):
            result = quality.run_step(
                "Example",
                ["example", "--flag"],
                REPOSITORY,
            )

        self.assertEqual(result, 7)
        run.assert_called_once_with(
            ["example", "--flag"],
            cwd=REPOSITORY,
            env=mock.ANY,
            check=False,
        )
        self.assertIn("==> Example", stdout.getvalue())

    def test_run_step_handles_operating_system_error(
        self,
    ) -> None:
        stderr = io.StringIO()

        with (
            mock.patch.object(
                quality.subprocess,
                "run",
                side_effect=OSError("boom"),
            ),
            redirect_stderr(stderr),
        ):
            result = quality.run_step(
                "Broken",
                ["broken"],
                REPOSITORY,
            )

        self.assertEqual(result, 1)
        self.assertIn(
            "cannot run quality step 'Broken'",
            stderr.getvalue(),
        )

    def test_runs_all_steps_and_reports_success(
        self,
    ) -> None:
        steps = [
            ("First", ["first"]),
            ("Second", ["second"]),
        ]
        stdout = io.StringIO()

        with (
            mock.patch.object(
                quality,
                "quality_steps",
                return_value=steps,
            ),
            mock.patch.object(
                quality,
                "run_step",
                return_value=0,
            ) as run_step,
            redirect_stdout(stdout),
        ):
            result = quality.run_quality_checks(
                REPOSITORY
            )

        self.assertEqual(result, 0)
        self.assertEqual(run_step.call_count, 2)
        run_step.assert_has_calls(
            [
                mock.call(
                    "First",
                    ["first"],
                    REPOSITORY,
                ),
                mock.call(
                    "Second",
                    ["second"],
                    REPOSITORY,
                ),
            ]
        )
        self.assertIn(
            "Quality checks passed.",
            stdout.getvalue(),
        )

    def test_stops_after_first_failed_step(
        self,
    ) -> None:
        steps = [
            ("First", ["first"]),
            ("Second", ["second"]),
            ("Third", ["third"]),
        ]
        stderr = io.StringIO()

        with (
            mock.patch.object(
                quality,
                "quality_steps",
                return_value=steps,
            ),
            mock.patch.object(
                quality,
                "run_step",
                side_effect=[0, 5],
            ) as run_step,
            redirect_stderr(stderr),
        ):
            result = quality.run_quality_checks(
                REPOSITORY
            )

        self.assertEqual(result, 5)
        self.assertEqual(run_step.call_count, 2)
        self.assertIn(
            "Quality checks failed at: Second "
            "(exit code 5)",
            stderr.getvalue(),
        )


    def test_concise_success_writes_full_log_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            log = root / "quality.log"
            summary = root / "summary.json"
            database = root / "quality.sqlite"
            steps = [
                ("Run unit tests", ["tests"]),
                ("Validate", ["validate"]),
            ]
            results = [
                SimpleNamespace(
                    returncode=0,
                    stdout="",
                    stderr=(
                        "test_x ... ok\\n"
                        "Ran 298 tests in 1.0s\\n"
                        "OK\\n"
                    ),
                ),
                SimpleNamespace(
                    returncode=0,
                    stdout="validated\\n",
                    stderr="",
                ),
            ]
            stdout = io.StringIO()

            with (
                mock.patch.object(
                    quality,
                    "quality_steps",
                    return_value=steps,
                ),
                mock.patch.object(
                    quality.subprocess,
                    "run",
                    side_effect=results,
                ),
                redirect_stdout(stdout),
            ):
                result = quality.run_quality_checks(
                    REPOSITORY,
                    database=database,
                    concise=True,
                    log_file=log,
                    summary_file=summary,
                )

            self.assertEqual(result, 0)
            self.assertIn("298 tests", stdout.getvalue())
            self.assertIn(
                "test_x ... ok",
                log.read_text(encoding="utf-8"),
            )
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "PASS")
            self.assertEqual(payload["tests"], 298)
            self.assertEqual(payload["exit_code"], 0)

    def test_concise_failure_replays_name_and_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            log = root / "quality.log"
            summary = root / "summary.json"
            failed = SimpleNamespace(
                returncode=1,
                stdout="",
                stderr=(
                    "test_polskie_znaki (tests.test_x.Case) ... FAIL\\n"
                    "Traceback (most recent call last):\\n"
                    "AssertionError\\n"
                    "Ran 1 test in 0.1s\\n"
                    "FAILED\\n"
                ),
            )
            stderr = io.StringIO()

            with (
                mock.patch.object(
                    quality,
                    "quality_steps",
                    return_value=[("Run unit tests", ["tests"])],
                ),
                mock.patch.object(
                    quality.subprocess,
                    "run",
                    return_value=failed,
                ),
                redirect_stderr(stderr),
            ):
                result = quality.run_quality_checks(
                    REPOSITORY,
                    concise=True,
                    log_file=log,
                    summary_file=summary,
                )

            self.assertEqual(result, 1)
            self.assertIn("test_polskie_znaki", stderr.getvalue())
            self.assertIn("Traceback", stderr.getvalue())
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "FAIL")
            self.assertEqual(payload["tests"], 1)

    def test_captured_mode_stops_after_first_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            with (
                mock.patch.object(
                    quality,
                    "quality_steps",
                    return_value=[
                        ("First", ["first"]),
                        ("Second", ["second"]),
                    ],
                ),
                mock.patch.object(
                    quality.subprocess,
                    "run",
                    return_value=SimpleNamespace(
                        returncode=5,
                        stdout="",
                        stderr="boom\\n",
                    ),
                ) as run,
            ):
                result = quality.run_quality_checks(
                    REPOSITORY,
                    database=root / "db.sqlite",
                    concise=True,
                    log_file=root / "quality.log",
                )

            self.assertEqual(result, 5)
            self.assertEqual(run.call_count, 1)

    def test_parse_args_accepts_structured_outputs(self) -> None:
        arguments = quality.parse_args(
            [
                "--concise",
                "--log-file",
                "quality.log",
                "--summary-json",
                "quality.json",
                "--database",
                "quality.sqlite",
            ]
        )

        self.assertTrue(arguments.concise)
        self.assertEqual(arguments.log_file, Path("quality.log"))
        self.assertEqual(arguments.summary_json, Path("quality.json"))
        self.assertEqual(arguments.database, Path("quality.sqlite"))


if __name__ == "__main__":
    unittest.main()
