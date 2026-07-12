#!/usr/bin/env python3
"""
Run the complete local quality gate for Dacia Knowledge Base.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def quality_steps(
    repository: Path,
    database: Path,
) -> list[tuple[str, list[str]]]:
    """Build the commands that mirror the GitHub Actions quality job."""
    tools = repository / "tools"
    dkb = tools / "dkb.py"

    return [
        (
            "Compile Python sources",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "tools",
                "scripts",
                "tests",
            ],
        ),
        (
            "Run unit tests",
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
        ),
        (
            "Check CSV encoding",
            [sys.executable, str(dkb), "normalize"],
        ),
        (
            "Validate repository data",
            [sys.executable, str(dkb), "validate"],
        ),
        (
            "Build SQLite database",
            [
                sys.executable,
                str(dkb),
                "sqlite",
                "--output",
                str(database),
            ],
        ),
        (
            "Verify SQLite database",
            [
                sys.executable,
                str(dkb),
                "sqlite-verify",
                str(database),
            ],
        ),
    ]


def run_step(
    label: str,
    command: list[str],
    repository: Path,
) -> int:
    """Run one quality step and return its exit code."""
    print(f"\n==> {label}", flush=True)

    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            check=False,
        )
    except OSError as exc:
        print(
            f"ERROR: cannot run quality step '{label}': {exc}",
            file=sys.stderr,
        )
        return 1

    return completed.returncode


def run_quality_checks(repository: Path) -> int:
    """Run all checks, stopping at the first failed step."""
    with tempfile.TemporaryDirectory(
        prefix="dkb-quality-",
    ) as temporary_directory:
        database = (
            Path(temporary_directory)
            / "dacia_knowledge_base.sqlite"
        )

        for label, command in quality_steps(
            repository,
            database,
        ):
            return_code = run_step(
                label,
                command,
                repository,
            )

            if return_code != 0:
                print(
                    f"\nQuality checks failed at: {label} "
                    f"(exit code {return_code})",
                    file=sys.stderr,
                )
                return return_code

    print("\nQuality checks passed.")
    return 0


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run compilation, tests, encoding checks, validation "
            "and SQLite parity verification."
        )
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    return run_quality_checks(repository_root())


if __name__ == "__main__":
    raise SystemExit(main())
