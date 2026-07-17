#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from configuration_comparison import (
    DEFAULT_COMPLETENESS_SPEC,
    DEFAULT_EVIDENCE_SPEC,
    DIFFERENCE_DOMAINS,
    ComparisonError,
    collect_report,
    comparison_item_code,
    repository_root,
    write_atomic,
)

CATALOG_CSV_FIELDS = (
    "domain",
    "item_code",
    "item_name",
    "category",
    "context_count",
    "comparison_count",
    "equal_count",
    "different_count",
    "not_comparable_count",
)
COMPARISON_STATES = ("equal", "different", "not_comparable")


def item_metadata(
    item: Mapping[str, Any],
    domain: str,
) -> tuple[str, str, str]:
    if domain == "prices":
        context = (
            f"market={item['market']};"
            f"currency_code={item['currency_code']}"
        )
        return "", "", context
    if domain == "technical":
        fuel = str(item.get("fuel_type_code", ""))
        return (
            str(item.get("attribute_name", "")),
            str(item.get("category", "")),
            f"fuel_type_code={fuel}",
        )
    return (
        str(item.get("attribute_name", "")),
        str(item.get("category", "")),
        "",
    )


def catalog_rows(report: Mapping[str, Any]) -> list[dict[str, str]]:
    entries: dict[tuple[str, str], dict[str, Any]] = {}
    domains_by_code: dict[str, set[str]] = defaultdict(set)

    for pair in report["pairs"]:
        for domain in DIFFERENCE_DOMAINS:
            for item in pair[domain]:
                item_code = comparison_item_code(item, domain)
                item_name, category, context = item_metadata(item, domain)
                comparison = str(item.get("comparison", ""))
                if comparison not in COMPARISON_STATES:
                    raise ComparisonError(
                        "unsupported comparison state in item catalog: "
                        f"{comparison!r}"
                    )

                domains_by_code[item_code].add(domain)
                key = (domain, item_code)
                entry = entries.setdefault(
                    key,
                    {
                        "item_name": item_name,
                        "category": category,
                        "contexts": set(),
                        "counts": Counter(),
                    },
                )
                if (
                    entry["item_name"] != item_name
                    or entry["category"] != category
                ):
                    raise ComparisonError(
                        "inconsistent item metadata in catalog for "
                        f"{domain}/{item_code}"
                    )
                entry["contexts"].add(context)
                entry["counts"][comparison] += 1

    collisions = sorted(
        item_code
        for item_code, domains in domains_by_code.items()
        if len(domains) > 1
    )
    if collisions:
        raise ComparisonError(
            "difference item code collision across domains: "
            + ", ".join(collisions)
        )

    domain_order = {
        domain: index for index, domain in enumerate(DIFFERENCE_DOMAINS)
    }
    rows: list[dict[str, str]] = []
    for (domain, item_code), entry in sorted(
        entries.items(),
        key=lambda value: (domain_order[value[0][0]], value[0][1]),
    ):
        counts = entry["counts"]
        comparison_count = sum(counts[state] for state in COMPARISON_STATES)
        rows.append(
            {
                "domain": domain,
                "item_code": item_code,
                "item_name": str(entry["item_name"]),
                "category": str(entry["category"]),
                "context_count": str(len(entry["contexts"])),
                "comparison_count": str(comparison_count),
                "equal_count": str(counts["equal"]),
                "different_count": str(counts["different"]),
                "not_comparable_count": str(counts["not_comparable"]),
            }
        )
    return rows


def render_catalog_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=CATALOG_CSV_FIELDS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(catalog_rows(report))
    return output.getvalue()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic catalog of configuration-comparison "
            "item codes from the full active report."
        )
    )
    parser.add_argument(
        "--completeness-spec",
        type=Path,
        default=DEFAULT_COMPLETENESS_SPEC,
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument("--as-of")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Write the deterministic difference-item catalog CSV.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    completeness_spec = arguments.completeness_spec
    evidence_spec = arguments.evidence_spec
    if not completeness_spec.is_absolute():
        completeness_spec = repository / completeness_spec
    if not evidence_spec.is_absolute():
        evidence_spec = repository / evidence_spec

    try:
        report = collect_report(
            repository,
            completeness_spec,
            evidence_spec,
            arguments.as_of,
            None,
        )
        rows = catalog_rows(report)
        if arguments.csv_path is not None:
            write_atomic(arguments.csv_path, render_catalog_csv(report))
            print(
                "CSV configuration comparison item catalog written to "
                f"{arguments.csv_path}"
            )

        domain_counts = Counter(row["domain"] for row in rows)
        print("Configuration comparison item catalog")
        print("-------------------------------------")
        print(f"As of                  : {report['as_of']}")
        print(f"Catalog items          : {len(rows)}")
        for domain in DIFFERENCE_DOMAINS:
            print(
                f"{domain.capitalize():<23}: "
                f"{domain_counts[domain]}"
            )
        return 0
    except ComparisonError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
