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
    "autonomy-decision": (
        "autonomy_decision.py",
        "Resolve the next autonomous workflow action from an event.",
        "--event FILE [--state FILE] [--json FILE]",
    ),
    "normalize": (
        "normalize_csv_encoding.py",
        "Check CSV encoding or convert files to UTF-8.",
        "[--apply]",
    ),
    "configuration-shortlist": (
        "configuration_shortlist.py",
        "Filter active configurations into an evidence-aware shortlist.",
        "[--as-of YYYY-MM-DD] [--model CODE] [--version CODE] "
        "[--transmission TYPE] [--powertrain TEXT] "
        "[--min-price PLN] [--max-price PLN] [--seats N] "
        "[--require-equipment CODE] "
        "[--require-standard-equipment CODE] "
        "[--json FILE] [--markdown FILE] [--csv FILE]",
    ),
    "configuration-comparison": (
        "configuration_comparison.py",
        "Compare active configuration prices, values and equipment.",
        "[--completeness-spec FILE] [--evidence-spec FILE] "
        "[--as-of YYYY-MM-DD] [--pair-type TYPE] "
        "[--difference-domain DOMAIN] [--difference-item-code CODE] "
        "[--difference-context CONTEXT] "
        "[--json FILE] [--markdown FILE] [--csv FILE] [--html FILE]",
    ),
    "configuration-comparison-item-catalog": (
        "configuration_comparison_item_catalog.py",
        "Catalog item codes available to configuration comparison.",
        "[--completeness-spec FILE] [--evidence-spec FILE] "
        "[--as-of YYYY-MM-DD] [--csv FILE]",
    ),
    "configuration-comparison-pair-summary": (
        "configuration_comparison_pair_summary.py",
        "Generate a one-row-per-pair comparison summary CSV.",
        "[--completeness-spec FILE] [--evidence-spec FILE] "
        "[--as-of YYYY-MM-DD] [--pair-type TYPE] --csv FILE",
    ),
    "configuration-gap-resolution-plan": (
        "configuration_gap_resolution_plan.py",
        "Plan evidence-backed gap resolution without importing data.",
        "[--evidence-spec FILE] [--plan-spec FILE] "
        "[--write-plan-spec FILE] [--json FILE] [--markdown FILE]",
    ),
    "configuration-gap-source-review": (
        "configuration_gap_source_review.py",
        "Review ambiguous gaps against registered PDF source pages.",
        "[--review-spec FILE] [--evidence-spec FILE] "
        "[--write-evidence-spec FILE] [--verify] "
        "[--json FILE] [--markdown FILE]",
    ),
    "configuration-gap-evidence": (
        "configuration_gap_evidence.py",
        "Classify gap evidence without inferring source content.",
        "[--evidence-spec FILE] [--completeness-spec FILE] "
        "[--as-of YYYY-MM-DD] [--json FILE] [--markdown FILE]",
    ),
    "configuration-gap-triage": (
        "configuration_gap_triage.py",
        "Generate a deterministic source-verification queue for gaps.",
        "[--spec FILE] [--as-of YYYY-MM-DD] "
        "[--json FILE] [--markdown FILE]",
    ),
    "source-coverage": (
        "source_coverage.py",
        "Generate source registration and record coverage reports.",
        "[--spec FILE] [--as-of YYYY-MM-DD] "
        "[--json FILE] [--markdown FILE]",
    ),
    "configuration-completeness": (
        "configuration_completeness.py",
        "Generate configuration-data completeness reports.",
        "[--spec FILE] [--as-of YYYY-MM-DD] "
        "[--json FILE] [--markdown FILE]",
    ),
    "documentation-baseline": (
        "documentation_baseline.py",
        "Generate or verify documentation baseline counters.",
        "[--check | --apply] [--database FILE] [--json FILE] "
        "[--markdown FILE]",
    ),
    "project-state": (
        "project_state.py",
        "Validate canonical project state and generated summary.",
        "[--check | --apply] [--state FILE] [--summary FILE]",
    ),
    "import-configuration-values": (
        "import_configuration_values.py",
        "Apply or verify one declarative configuration-value import.",
        "--spec FILE [--apply | --verify] [--skip-source-text] "
        "[--skip-source-files]",
    ),
    "import-configuration-value-ranges": (
        "import_configuration_value_ranges.py",
        "Apply or verify one declarative configuration-value range import.",
        "--spec FILE [--apply | --verify] [--skip-source-text] "
        "[--skip-source-files]",
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
        {command: details[0] for command, details in REPORT_COMMANDS.items()}
    )
    descriptions.update(
        {command: details[1] for command, details in WORKFLOW_COMMANDS.items()}
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
    print("  python tools/dkb.py autonomy-decision --event ../event.json")
    print(
        "  python tools/dkb.py import-configuration-values "
        "--spec data/imports/configuration_values/example.json --verify"
    )
    print(
        "  python tools/dkb.py configuration-shortlist --transmission automatic "
        "--max-price 100000 --csv ../configuration-shortlist.csv"
    )
    print(
        "  python tools/dkb.py configuration-comparison "
        "--difference-context fuel_type_code=lpg "
        "--csv ../configuration-comparison-differences.csv"
    )
    print(
        "  python tools/dkb.py configuration-comparison "
        "--html ../configuration-comparison.html"
    )
    print(
        "  python tools/dkb.py configuration-comparison-item-catalog "
        "--csv ../configuration-comparison-item-catalog.csv"
    )
    print(
        "  python tools/dkb.py configuration-comparison-pair-summary "
        "--csv ../configuration-comparison-pair-summary.csv"
    )
    print(
        "  python tools/dkb.py configuration-gap-resolution-plan "
        "--json ../configuration-gap-resolution-plan.json"
    )
    print(
        "  python tools/dkb.py configuration-gap-source-review "
        "--verify --json ../configuration-gap-source-review.json"
    )
    print(
        "  python tools/dkb.py configuration-gap-evidence "
        "--json ../configuration-gap-evidence.json"
    )
    print(
        "  python tools/dkb.py configuration-gap-triage "
        "--json ../configuration-gap-triage.json"
    )
    print(
        "  python tools/dkb.py source-coverage "
        "--json ../source-coverage.json"
    )
    print(
        "  python tools/dkb.py configuration-completeness "
        "--json ../configuration-completeness.json"
    )
    print("  python tools/dkb.py project-state --check")
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
    print("  python tools/dkb.py documentation-baseline --check")
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


def _configuration_comparison_script(arguments: Sequence[str]) -> str:
    use_context_wrapper = any(
        argument in {"--difference-context", "--help", "-h"}
        or argument.startswith("--difference-context=")
        for argument in arguments
    )
    return (
        "configuration_comparison_context.py"
        if use_context_wrapper
        else "configuration_comparison.py"
    )


def run_script(command: str, arguments: list[str]) -> int:
    script_name = SCRIPT_COMMANDS[command][0]
    if command == "configuration-comparison":
        script_name = _configuration_comparison_script(arguments)
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
