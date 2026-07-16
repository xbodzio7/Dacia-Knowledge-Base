#!/usr/bin/env python3
"""Run the complete local quality gate for Dacia Knowledge Base."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


TEST_COUNT_PATTERN = re.compile(r"Ran\s+(\d+)\s+tests?\b")


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def quality_steps(
    repository: Path,
    database: Path,
) -> list[tuple[str, list[str]]]:
    """Build the commands that mirror the GitHub Actions quality job."""
    tools = repository / "tools"
    dkb = tools / "dkb.py"
    baseline_json = database.with_name(
        "documentation-baseline.json"
    )
    baseline_markdown = database.with_name(
        "documentation-baseline.md"
    )
    completeness_json = database.with_name(
        "configuration-completeness.json"
    )
    completeness_markdown = database.with_name(
        "configuration-completeness.md"
    )
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
        (
            "Check documentation baseline",
            [
                sys.executable,
                str(dkb),
                "documentation-baseline",
                "--check",
                "--database",
                str(database),
                "--json",
                str(baseline_json),
                "--markdown",
                str(baseline_markdown),
            ],
        ),
        (
            "Generate configuration completeness report",
            [
                sys.executable,
                str(dkb),
                "configuration-completeness",
                "--json",
                str(completeness_json),
                "--markdown",
                str(completeness_markdown),
            ],
        ),
    ]


def quality_environment() -> dict[str, str]:
    """Return an environment forcing UTF-8 for child tools."""
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["LANG"] = "C.UTF-8"
    environment["LC_ALL"] = "C.UTF-8"
    return environment


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
            env=quality_environment(),
            check=False,
        )
    except OSError as exc:
        print(
            f"ERROR: cannot run quality step '{label}': {exc}",
            file=sys.stderr,
        )
        return 1
    return completed.returncode


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _extract_test_count(output: str) -> int | None:
    matches = TEST_COUNT_PATTERN.findall(output)
    if not matches:
        return None
    return int(matches[-1])


def _captured_step(
    label: str,
    command: list[str],
    repository: Path,
    log_stream: Any,
) -> tuple[int, int | None]:
    """Run one step, preserving its complete output in the full log."""
    log_stream.write(f"\n===== {label} =====\n")
    log_stream.write("Command: " + " ".join(command) + "\n")
    log_stream.flush()
    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            env=quality_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        message = f"ERROR: cannot run quality step '{label}': {exc}\n"
        log_stream.write(message)
        log_stream.flush()
        print(message, end="", file=sys.stderr)
        return 1, None

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if stdout:
        log_stream.write("\n--- stdout ---\n")
        log_stream.write(stdout)
        if not stdout.endswith("\n"):
            log_stream.write("\n")
    if stderr:
        log_stream.write("\n--- stderr ---\n")
        log_stream.write(stderr)
        if not stderr.endswith("\n"):
            log_stream.write("\n")
    log_stream.write(f"Exit code: {completed.returncode}\n")
    log_stream.flush()

    combined = stdout + "\n" + stderr
    tests = _extract_test_count(combined) if label == "Run unit tests" else None
    if completed.returncode == 0:
        suffix = f" ({tests} tests)" if tests is not None else ""
        print(f"==> {label}: PASS{suffix}", flush=True)
    else:
        print(f"==> {label}: FAIL", file=sys.stderr, flush=True)
        if stdout:
            print(stdout, end="" if stdout.endswith("\n") else "\n")
        if stderr:
            print(
                stderr,
                end="" if stderr.endswith("\n") else "\n",
                file=sys.stderr,
            )
    return completed.returncode, tests


def _run_classic_quality(repository: Path, database: Path) -> int:
    for label, command in quality_steps(repository, database):
        return_code = run_step(label, command, repository)
        if return_code != 0:
            print(
                f"\nQuality checks failed at: {label} "
                f"(exit code {return_code})",
                file=sys.stderr,
            )
            return return_code
    print("\nQuality checks passed.")
    return 0


def _run_captured_quality(
    repository: Path,
    database: Path,
    *,
    log_file: Path,
    summary_file: Path | None,
) -> int:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    steps_summary: list[dict[str, Any]] = []
    tests: int | None = None
    exit_code = 0
    failed_label: str | None = None

    with log_file.open("w", encoding="utf-8", newline="\n") as log_stream:
        log_stream.write("Dacia Knowledge Base quality log\n")
        log_stream.write(
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        )
        log_stream.write(f"Python: {sys.version}\n")
        for label, command in quality_steps(repository, database):
            return_code, step_tests = _captured_step(
                label,
                command,
                repository,
                log_stream,
            )
            if step_tests is not None:
                tests = step_tests
            steps_summary.append(
                {
                    "label": label,
                    "status": "PASS" if return_code == 0 else "FAIL",
                    "exit_code": return_code,
                }
            )
            if return_code != 0:
                exit_code = return_code
                failed_label = label
                break

    status = "PASS" if exit_code == 0 else "FAIL"
    summary = {
        "version": 1,
        "status": status,
        "tests": tests,
        "steps": steps_summary,
        "exit_code": exit_code,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if summary_file is not None:
        _write_json_atomic(summary_file, summary)

    if exit_code != 0:
        print(
            f"Quality checks failed at: {failed_label} "
            f"(exit code {exit_code}). Full log: {log_file}",
            file=sys.stderr,
        )
        return exit_code
    if tests is None:
        print(
            "Quality checks passed, but the unit-test count was not found. "
            f"Full log: {log_file}",
            file=sys.stderr,
        )
        return 1
    print(f"Quality checks passed: {tests} tests. Full log: {log_file}")
    return 0


def run_quality_checks(
    repository: Path,
    *,
    database: Path | None = None,
    concise: bool = False,
    log_file: Path | None = None,
    summary_file: Path | None = None,
) -> int:
    """Run all checks, stopping at the first failed step."""
    captured = concise or log_file is not None or summary_file is not None

    if database is not None:
        database.parent.mkdir(parents=True, exist_ok=True)
        if captured:
            resolved_log = log_file or (
                repository.parent / "dacia-knowledge-base-quality.log"
            )
            return _run_captured_quality(
                repository,
                database,
                log_file=resolved_log,
                summary_file=summary_file,
            )
        return _run_classic_quality(repository, database)

    with tempfile.TemporaryDirectory(prefix="dkb-quality-") as temp_dir:
        temporary_database = Path(temp_dir) / "dacia_knowledge_base.sqlite"
        if captured:
            resolved_log = log_file or (
                repository.parent / "dacia-knowledge-base-quality.log"
            )
            return _run_captured_quality(
                repository,
                temporary_database,
                log_file=resolved_log,
                summary_file=summary_file,
            )
        return _run_classic_quality(repository, temporary_database)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run compilation, tests, encoding checks, validation "
            "and SQLite parity verification."
        )
    )
    parser.add_argument(
        "--concise",
        action="store_true",
        help=(
            "Print short PASS summaries; replay complete failed-step output."
        ),
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Write the complete verbose quality output to this file.",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        help="Write a small structured quality summary.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        help="Keep the generated SQLite database at this path.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    return run_quality_checks(
        repository_root(),
        database=arguments.database,
        concise=arguments.concise,
        log_file=arguments.log_file,
        summary_file=arguments.summary_json,
    )


if __name__ == "__main__":
    raise SystemExit(main())
