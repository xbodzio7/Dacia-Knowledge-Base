#!/usr/bin/env python3
"""Unified command-line interface for Dacia Knowledge Base tools."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

from reporting.data_dictionary import generate_data_dictionary
from reporting.entity_catalog import generate_entity_catalog


SCRIPT_COMMANDS = {
    "normalize": (
        "normalize_csv_encoding.py",
        "Check CSV encoding or convert files to UTF-8.",
        "[--apply]",
    ),
    "package-publish": (
        "package_publish.py",
        "Publish one exact manifest-driven package.",
        "--manifest FILE [--base-ref REF] [--output-dir DIR] "
        "[--receipt FILE] [--push]",
    ),
    "quality": (
        "quality.py",
        "Run the complete local quality gate.",
        "[--concise] [--log-file FILE] [--summary-json FILE] "
        "[--database FILE]",
    ),
    "search": (
        "search.py",
        "Search records in repository CSV files.",
        "<phrase> [--field FIELD] [--export PATH]",
    ),
    "sqlite": (
        "build_sqlite.py",
        "Build a local SQLite database from master CSV files.",
        "[--output PATH]",
    ),
    "sqlite-verify": (
        "verify_sqlite.py",
        "Verify SQLite schema and data against master CSV files.",
        "<database>",
    ),
    "stats": (
        "stats.py",
        "Display repository dataset statistics.",
        "",
    ),
    "validate": (
        "validate_dkb.py",
        "Validate repository structure and datasets.",
        "",
    ),
}

REPORT_COMMANDS = {
    "catalog": (
        "Generate the repository entity catalog.",
        "entity_catalog.md",
    ),
    "dictionary": (
        "Generate the CSV data dictionary.",
        "data_dictionary.md",
    ),
}

WORKFLOW_COMMANDS = {
    "package-start": (
        "start",
        "Synchronize main and create a safe package branch.",
        "<branch>",
    ),
    "package-review": (
        "review",
        "Review package scope, diffs and optional quality checks.",
        "[--allow PATH | --manifest FILE] [--base-ref REF] "
        "[--quality] [--show-diff] [--receipt FILE] "
        "[--quality-log FILE]",
    ),
    "package-finish": (
        "finish",
        "Verify a committed package before push.",
        "[--base-ref REF] [--manifest FILE]",
    ),
}


def usage() -> None:
    """Print CLI usage and available commands."""
    print("Dacia Knowledge Base")
    print()
    print("Usage:")
    print("  python tools/dkb.py <command> [arguments]")
    print()
    print("Commands:")

    descriptions = {
        command: details[1]
        for command, details in SCRIPT_COMMANDS.items()
    }
    descriptions.update(
        {
            command: details[0]
            for command, details in REPORT_COMMANDS.items()
        }
    )
    descriptions.update(
        {
            command: details[1]
            for command, details in WORKFLOW_COMMANDS.items()
        }
    )

    width = max(len(command) for command in descriptions)
    for command in sorted(descriptions):
        print(f"  {command:<{width}}  {descriptions[command]}")
    print(f"  {'help':<{width}}  Show this help message.")
    print()
    print("Examples:")
    print("  python tools/dkb.py validate")
    print("  python tools/dkb.py normalize")
    print("  python tools/dkb.py normalize --apply")
    print("  python tools/dkb.py quality")
    print(
        "  python tools/dkb.py quality --concise "
        "--log-file ../quality.log --summary-json ../quality.json"
    )
    print("  python tools/dkb.py sqlite")
    print("  python tools/dkb.py sqlite --output reports/dkb.sqlite")
    print("  python tools/dkb.py sqlite-verify reports/dkb.sqlite")
    print("  python tools/dkb.py search Duster")
    print("  python tools/dkb.py search Duster --field name")
    print("  python tools/dkb.py catalog")
    print("  python tools/dkb.py dictionary")
    print("  python tools/dkb.py package-start tooling/example")
    print(
        "  python tools/dkb.py package-review "
        "--manifest ../package.json --quality --show-diff"
    )
    print(
        "  python tools/dkb.py package-publish "
        "--manifest ../package.json"
    )
    print(
        "  python tools/dkb.py package-finish "
        "--manifest ../package.json"
    )
    print()
    print("Command-specific help:")
    print("  python tools/dkb.py <command> --help")


def run_script(command: str, arguments: list[str]) -> int:
    """Run a script-backed command and propagate its exit code."""
    script_name = SCRIPT_COMMANDS[command][0]
    script = Path(__file__).resolve().parent / script_name
    if not script.is_file():
        print(
            f"ERROR: command script does not exist: {script}",
            file=sys.stderr,
        )
        return 1
    completed = subprocess.run(
        [sys.executable, str(script), *arguments],
        check=False,
    )
    return completed.returncode


def run_workflow(command: str, arguments: list[str]) -> int:
    """Run a package workflow action and propagate its exit code."""
    action = WORKFLOW_COMMANDS[command][0]
    script = Path(__file__).resolve().parent / "package_workflow.py"
    if not script.is_file():
        print(
            f"ERROR: workflow script does not exist: {script}",
            file=sys.stderr,
        )
        return 1
    completed = subprocess.run(
        [sys.executable, str(script), action, *arguments],
        check=False,
    )
    return completed.returncode


def generate_report(command: str, repository: Path) -> int:
    """Generate one of the built-in Markdown reports."""
    reports_dir = repository / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_name = REPORT_COMMANDS[command][1]
    output = reports_dir / output_name
    if command == "catalog":
        generate_entity_catalog(repository, output)
        print(f"Entity catalog written to {output}")
        return 0
    if command == "dictionary":
        generate_data_dictionary(repository, output)
        print(f"Data dictionary written to {output}")
        return 0
    print(f"ERROR: unsupported report command: {command}", file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected DKB command."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in {"help", "--help", "-h"}:
        usage()
        return 0

    command = arguments[0]
    command_arguments = arguments[1:]
    if command in SCRIPT_COMMANDS:
        return run_script(command, command_arguments)
    if command in WORKFLOW_COMMANDS:
        return run_workflow(command, command_arguments)
    if command in REPORT_COMMANDS:
        if command_arguments:
            print(
                f"ERROR: command '{command}' does not accept arguments.",
                file=sys.stderr,
            )
            return 2
        repository = Path(__file__).resolve().parents[1]
        return generate_report(command, repository)

    print(f"ERROR: unknown command: {command}", file=sys.stderr)
    print(file=sys.stderr)
    usage()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
