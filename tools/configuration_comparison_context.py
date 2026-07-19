#!/usr/bin/env python3
"""Add exact catalog-context filtering to configuration-difference CSV output."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import configuration_comparison as core


def comparison_filter_context(
    item: Mapping[str, Any],
    domain: str,
) -> str:
    """Return the exact context exposed by the item catalog."""
    if domain == "prices":
        return (
            f"market={item['market']};"
            f"currency_code={item['currency_code']}"
        )
    if domain == "technical":
        return f"fuel_type_code={item['fuel_type_code']}"
    return ""


def difference_contexts(report: Mapping[str, Any]) -> tuple[str, ...]:
    """Return all catalog contexts in the active comparison scope."""
    return tuple(
        sorted(
            {
                comparison_filter_context(item, domain)
                for pair in report["pairs"]
                for domain in core.DIFFERENCE_DOMAINS
                for item in pair[domain]
            }
        )
    )


def csv_row_filter_context(row: Mapping[str, str]) -> str:
    """Normalize an existing difference row to its catalog context."""
    domain = row.get("domain", "")
    context = row.get("context", "")
    if domain != "prices":
        return context

    parts: dict[str, str] = {}
    for component in context.split(";"):
        if "=" not in component:
            continue
        key, value = component.split("=", 1)
        parts[key] = value
    return (
        f"market={parts.get('market', '')};"
        f"currency_code={parts.get('currency_code', '')}"
    )


def difference_csv_rows(
    report: Mapping[str, Any],
    difference_domain: str | None = None,
    difference_item_code: str | None = None,
    known_item_codes: Sequence[str] | None = None,
    difference_context: str | None = None,
    known_contexts: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Return existing difference rows constrained by one exact context."""
    if difference_context is not None:
        available_contexts = set(
            known_contexts
            if known_contexts is not None
            else difference_contexts(report)
        )
        if difference_context not in available_contexts:
            raise core.ComparisonError(
                "unsupported difference context: "
                f"{difference_context!r}"
            )

    rows = core.difference_csv_rows(
        report,
        difference_domain,
        difference_item_code,
        known_item_codes,
    )
    if difference_context is None:
        return rows
    return [
        row
        for row in rows
        if csv_row_filter_context(row) == difference_context
    ]


def render_difference_csv(
    report: Mapping[str, Any],
    difference_domain: str | None = None,
    difference_item_code: str | None = None,
    known_item_codes: Sequence[str] | None = None,
    difference_context: str | None = None,
    known_contexts: Sequence[str] | None = None,
) -> str:
    """Render the flat difference CSV while preserving its schema."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=core.DIFFERENCE_CSV_FIELDS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(
        difference_csv_rows(
            report,
            difference_domain,
            difference_item_code,
            known_item_codes,
            difference_context,
            known_contexts,
        )
    )
    return output.getvalue()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic pairwise comparisons for active "
            "configuration prices, technical values and equipment states."
        )
    )
    parser.add_argument(
        "--completeness-spec",
        type=Path,
        default=core.DEFAULT_COMPLETENESS_SPEC,
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=core.DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument("--as-of")
    parser.add_argument(
        "--pair-type",
        choices=core.PAIR_TYPES,
        help=(
            "Limit output to one deterministic version/transmission "
            "pair classification."
        ),
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument(
        "--difference-domain",
        choices=core.DIFFERENCE_DOMAINS,
        help=(
            "Limit the flat CSV to price, technical or equipment "
            "differences without changing JSON or Markdown."
        ),
    )
    parser.add_argument(
        "--difference-item-code",
        help=(
            "Limit the flat CSV to one exact item code known to the "
            "full active comparison report."
        ),
    )
    parser.add_argument(
        "--difference-context",
        help=(
            "Limit the flat CSV to one exact context exposed by the item "
            "catalog. Use --difference-context= for the empty equipment "
            "context."
        ),
    )
    parser.add_argument(
        "--html",
        dest="html_path",
        type=Path,
        help="Write a self-contained interactive HTML report.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Write a flat CSV containing only actual differences.",
    )
    return parser.parse_args(argv)


def _resolve_spec(repository: Path, path: Path) -> Path:
    return path if path.is_absolute() else repository / path


def _display_context(value: str | None) -> str:
    if value is None:
        return "all"
    return value if value else "<empty>"


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = core.repository_root()
    completeness_spec = _resolve_spec(
        repository,
        arguments.completeness_spec,
    )
    evidence_spec = _resolve_spec(repository, arguments.evidence_spec)

    try:
        report = core.collect_report(
            repository,
            completeness_spec,
            evidence_spec,
            arguments.as_of,
            arguments.pair_type,
        )

        validation_report = report
        requires_full_validation = (
            arguments.difference_item_code is not None
            or arguments.difference_context is not None
        )
        if requires_full_validation and arguments.pair_type is not None:
            validation_report = core.collect_report(
                repository,
                completeness_spec,
                evidence_spec,
                arguments.as_of,
                None,
            )

        known_item_codes: tuple[str, ...] | None = None
        if arguments.difference_item_code is not None:
            known_item_codes = core.difference_item_codes(
                validation_report
            )

        known_contexts: tuple[str, ...] | None = None
        if arguments.difference_context is not None:
            known_contexts = difference_contexts(validation_report)

        if arguments.json_path is not None:
            core.write_atomic(
                arguments.json_path,
                core.render_json(report),
            )
            print(
                "JSON configuration comparison report written to "
                f"{arguments.json_path}"
            )
        if arguments.markdown is not None:
            core.write_atomic(
                arguments.markdown,
                core.render_markdown(report),
            )
            print(
                "Markdown configuration comparison report written to "
                f"{arguments.markdown}"
            )

        if arguments.html_path is not None:
            core.write_atomic(
                arguments.html_path,
                core.render_html(report),
            )
            print(
                "HTML configuration comparison report written to "
                f"{arguments.html_path}"
            )

        rows = difference_csv_rows(
            report,
            arguments.difference_domain,
            arguments.difference_item_code,
            known_item_codes,
            arguments.difference_context,
            known_contexts,
        )
        if arguments.csv_path is not None:
            core.write_atomic(
                arguments.csv_path,
                render_difference_csv(
                    report,
                    arguments.difference_domain,
                    arguments.difference_item_code,
                    known_item_codes,
                    arguments.difference_context,
                    known_contexts,
                ),
            )
            print(
                "CSV configuration differences written to "
                f"{arguments.csv_path}"
            )

        print("Configuration comparison")
        print("------------------------")
        print(f"As of                  : {report['as_of']}")
        print(
            "Active configurations  : "
            f"{report['scope']['active_configurations']}"
        )
        print(
            "Pair type filter       : "
            f"{report['scope']['pair_type_filter'] or 'all'}"
        )
        print(
            "Available pairs        : "
            f"{report['scope']['unfiltered_pair_count']}"
        )
        print(f"Selected pairs         : {report['scope']['pair_count']}")
        print(
            "Price differences      : "
            f"{report['summary']['prices']['different']}"
        )
        print(
            "Technical differences  : "
            f"{report['summary']['technical']['different']}"
        )
        print(
            "Equipment differences  : "
            f"{report['summary']['equipment']['different']}"
        )
        print(
            "CSV difference domain  : "
            f"{arguments.difference_domain or 'all'}"
        )
        print(
            "CSV difference item    : "
            f"{arguments.difference_item_code or 'all'}"
        )
        print(
            "CSV difference context : "
            f"{_display_context(arguments.difference_context)}"
        )
        print(f"CSV difference rows    : {len(rows)}")
        print(
            "Not-comparable states  : "
            f"{sum(report['summary'][domain]['not_comparable'] for domain in core.DIFFERENCE_DOMAINS)}"
        )
        return 0
    except core.ComparisonError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
