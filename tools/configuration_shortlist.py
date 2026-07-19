#!/usr/bin/env python3
"""Filter active configurations into an evidence-aware shortlist."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from reporting.configuration_shortlist import (
    ShortlistCriteria,
    ShortlistError,
    collect_report,
    render_csv,
    render_json,
    render_markdown,
    repository_root,
    write_atomic,
)


def _price(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(
            f"invalid price: {value!r}"
        ) from exc
    if not result.is_finite():
        raise argparse.ArgumentTypeError(
            f"price must be finite: {value!r}"
        )
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filter active configurations by metadata, current catalogue "
            "price, seat count and equipment availability."
        )
    )
    parser.add_argument(
        "--as-of",
        help="Use records effective on or before YYYY-MM-DD.",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Require an exact model code. Repeat values are ORed.",
    )
    parser.add_argument(
        "--version",
        action="append",
        default=[],
        help="Require an exact version code. Repeat values are ORed.",
    )
    parser.add_argument(
        "--transmission",
        action="append",
        choices=("manual", "automatic"),
        default=[],
        help="Require a transmission type. Repeat values are ORed.",
    )
    parser.add_argument(
        "--powertrain",
        action="append",
        default=[],
        help=(
            "Case-insensitive substring of the powertrain label. "
            "Repeat values are ORed."
        ),
    )
    parser.add_argument(
        "--min-price",
        type=_price,
        help="Minimum current catalogue gross price in PLN.",
    )
    parser.add_argument(
        "--max-price",
        type=_price,
        help="Maximum current catalogue gross price in PLN.",
    )
    parser.add_argument(
        "--seats",
        type=int,
        help="Require an exact recorded number of seats.",
    )
    parser.add_argument(
        "--require-equipment",
        action="append",
        default=[],
        help=(
            "Require an equipment attribute as standard or optional. "
            "Repeat values are ANDed."
        ),
    )
    parser.add_argument(
        "--require-standard-equipment",
        action="append",
        default=[],
        help=(
            "Require an equipment attribute as standard. "
            "Repeat values are ANDed."
        ),
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="Write the complete shortlist report as JSON.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Write the shortlist and audit summary as Markdown.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Write matched configurations as a flat CSV.",
    )
    return parser.parse_args(argv)


def _criteria(arguments: argparse.Namespace) -> ShortlistCriteria:
    return ShortlistCriteria(
        as_of=arguments.as_of,
        models=tuple(arguments.model),
        versions=tuple(arguments.version),
        transmissions=tuple(arguments.transmission),
        powertrains=tuple(arguments.powertrain),
        minimum_price=arguments.min_price,
        maximum_price=arguments.max_price,
        seats=arguments.seats,
        required_equipment=tuple(arguments.require_equipment),
        required_standard_equipment=tuple(
            arguments.require_standard_equipment
        ),
    )


def _print_summary(report: dict[str, object]) -> None:
    summary = report["summary"]
    assert isinstance(summary, dict)
    print(f"Configuration shortlist as of {report['as_of']}")
    print(
        "Matched "
        f"{summary['matched_configurations']} of "
        f"{summary['active_configurations']} active configurations."
    )
    results = report["results"]
    assert isinstance(results, list)
    if not results:
        print("No configurations match all criteria.")
        return
    for item in results:
        assert isinstance(item, dict)
        price = item["catalog_price"]
        seats = item["number_of_seats"]
        assert isinstance(price, dict)
        assert isinstance(seats, dict)
        price_text = (
            f"{price['amount']} {price['currency_code']}"
            if price.get("state") == "recorded"
            else "price missing"
        )
        seats_text = (
            f"{seats['value']} seats"
            if seats.get("state") == "recorded"
            else "seats unknown"
        )
        print(
            f"- {price_text} | {item['model_name']} "
            f"{item['version_name']} | {item['powertrain_label']} | "
            f"{item['transmission_type']} | {seats_text} | "
            f"{item['configuration_code']}"
        )


def main(
    argv: Sequence[str] | None = None,
    repository: Path | None = None,
) -> int:
    arguments = parse_args(argv)
    try:
        report = collect_report(
            repository if repository is not None else repository_root(),
            _criteria(arguments),
        )
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(f"JSON configuration shortlist written to {arguments.json_path}")
        if arguments.markdown is not None:
            write_atomic(arguments.markdown, render_markdown(report))
            print(
                "Markdown configuration shortlist written to "
                f"{arguments.markdown}"
            )
        if arguments.csv is not None:
            write_atomic(arguments.csv, render_csv(report))
            print(f"CSV configuration shortlist written to {arguments.csv}")
        _print_summary(report)
    except (ShortlistError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
