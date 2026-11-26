#!/usr/bin/env python3
"""Generate a deterministic one-row-per-pair configuration summary CSV."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import configuration_comparison as comparison

PAIR_SUMMARY_FIELDS = (
    "pair_code",
    "pair_type",
    "left_configuration_code",
    "left_version_code",
    "left_transmission_type",
    "right_configuration_code",
    "right_version_code",
    "right_transmission_type",
    "price_comparisons",
    "price_equal",
    "price_different",
    "price_not_comparable",
    "technical_comparisons",
    "technical_equal",
    "technical_different",
    "technical_not_comparable",
    "equipment_comparisons",
    "equipment_equal",
    "equipment_different",
    "equipment_not_comparable",
    "total_comparisons",
    "total_equal",
    "total_different",
    "total_not_comparable",
)


def pair_summary_rows(
    report: Mapping[str, Any],
) -> list[dict[str, str]]:
    """Flatten pair summaries without recalculating comparison semantics."""
    rows: list[dict[str, str]] = []
    for pair in report["pairs"]:
        left = pair["left_configuration"]
        right = pair["right_configuration"]
        summaries = pair["summary"]
        totals = {
            key: sum(
                int(summaries[domain][key])
                for domain in comparison.DIFFERENCE_DOMAINS
            )
            for key in (
                "comparisons",
                "equal",
                "different",
                "not_comparable",
            )
        }
        rows.append(
            {
                "pair_code": str(pair["pair_code"]),
                "pair_type": str(pair["pair_type"]),
                "left_configuration_code": str(
                    left["configuration_code"]
                ),
                "left_version_code": str(left["version_code"]),
                "left_transmission_type": str(
                    left["transmission_type"]
                ),
                "right_configuration_code": str(
                    right["configuration_code"]
                ),
                "right_version_code": str(right["version_code"]),
                "right_transmission_type": str(
                    right["transmission_type"]
                ),
                "price_comparisons": str(
                    summaries["prices"]["comparisons"]
                ),
                "price_equal": str(summaries["prices"]["equal"]),
                "price_different": str(
                    summaries["prices"]["different"]
                ),
                "price_not_comparable": str(
                    summaries["prices"]["not_comparable"]
                ),
                "technical_comparisons": str(
                    summaries["technical"]["comparisons"]
                ),
                "technical_equal": str(
                    summaries["technical"]["equal"]
                ),
                "technical_different": str(
                    summaries["technical"]["different"]
                ),
                "technical_not_comparable": str(
                    summaries["technical"]["not_comparable"]
                ),
                "equipment_comparisons": str(
                    summaries["equipment"]["comparisons"]
                ),
                "equipment_equal": str(
                    summaries["equipment"]["equal"]
                ),
                "equipment_different": str(
                    summaries["equipment"]["different"]
                ),
                "equipment_not_comparable": str(
                    summaries["equipment"]["not_comparable"]
                ),
                "total_comparisons": str(totals["comparisons"]),
                "total_equal": str(totals["equal"]),
                "total_different": str(totals["different"]),
                "total_not_comparable": str(
                    totals["not_comparable"]
                ),
            }
        )
    return rows


def render_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=PAIR_SUMMARY_FIELDS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(pair_summary_rows(report))
    return output.getvalue()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic pair-level configuration comparison "
            "summary CSV."
        )
    )
    parser.add_argument(
        "--completeness-spec",
        type=Path,
        default=comparison.DEFAULT_COMPLETENESS_SPEC,
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=comparison.DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument("--as-of")
    parser.add_argument(
        "--pair-type",
        choices=comparison.PAIR_TYPES,
        help="Limit the summary to one pair classification.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        type=Path,
        dest="csv_path",
        help="Write the pair summary CSV.",
    )
    return parser.parse_args(argv)


def _resolve(repository: Path, path: Path) -> Path:
    return path if path.is_absolute() else repository / path


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = comparison.repository_root()
    try:
        report = comparison.collect_report(
            repository,
            _resolve(repository, arguments.completeness_spec),
            _resolve(repository, arguments.evidence_spec),
            arguments.as_of,
            arguments.pair_type,
        )
        rows = pair_summary_rows(report)
        comparison.write_atomic(arguments.csv_path, render_csv(report))
        print(
            "Configuration comparison pair summary written to "
            f"{arguments.csv_path}: {len(rows)} pairs"
        )
        return 0
    except comparison.ComparisonError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
