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
            steps[-2][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "sqlite",
                "--output",
                str(database),
            ],
        )
        self.assertEqual(
            steps[-1][1],
            [
                sys.executable,
                str(TOOLS_DIRECTORY / "dkb.py"),
                "sqlite-verify",
                str(database),
            ],
        )

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


if __name__ == "__main__":
    unittest.main()
