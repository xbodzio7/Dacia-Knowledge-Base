#!/usr/bin/env python3
"""Filter active configurations into an evidence-aware shortlist."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

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
from reporting.configuration_shortlist_html import collect_browser_catalog
from reporting.configuration_shortlist_selection_html import (
    render_html as render_selection_html,
)


_STICKY_COMPARISON_STYLE = r'''<style>
:root{--comparison-sticky-top:0px}
.comparison-panel{scroll-margin-top:calc(var(--comparison-sticky-top,0px) + 8px)}
.comparison-table thead th{top:var(--comparison-sticky-top,0px)}
@media(max-width:760px){:root{--comparison-sticky-top:0px!important}}
</style>'''

_STICKY_COMPARISON_SCRIPT = r'''<script>
(function () {
  "use strict";
  const panel = document.querySelector("#selection-panel");
  if (!panel) return;
  const root = document.documentElement;
  let frame = 0;
  const update = () => {
    if (frame) cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const sticky = getComputedStyle(panel).position === "sticky";
      const offset = sticky ? Math.ceil(panel.offsetHeight + 18) : 0;
      root.style.setProperty("--comparison-sticky-top", `${offset}px`);
      frame = 0;
    });
  };
  update();
  window.addEventListener("resize", update, { passive: true });
  if (typeof ResizeObserver === "function") {
    new ResizeObserver(update).observe(panel);
  }
  if (typeof MutationObserver === "function") {
    new MutationObserver(update).observe(panel, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }
})();
</script>'''


def render_html(catalog: Mapping[str, Any]) -> str:
    """Render the shortlist with a dynamic sticky comparison-header offset."""
    rendered = render_selection_html(catalog)
    marker = "</body>"
    if marker not in rendered:
        raise ShortlistError(
            "cannot inject sticky comparison offset: missing body marker"
        )
    enhancement = (
        f"{_STICKY_COMPARISON_STYLE}\n"
        f"{_STICKY_COMPARISON_SCRIPT}\n"
        f"{marker}"
    )
    return rendered.replace(marker, enhancement, 1)


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
    parser.add_argument(
        "--html",
        type=Path,
        help=(
            "Write a self-contained interactive HTML browser containing "
            "the complete snapshot and the CLI criteria as its initial state."
        ),
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
    selected_repository = (
        repository if repository is not None else repository_root()
    )
    criteria = _criteria(arguments)
    try:
        report = collect_report(selected_repository, criteria)
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
        if arguments.html is not None:
            catalog = collect_browser_catalog(
                selected_repository,
                criteria,
            )
            write_atomic(arguments.html, render_html(catalog))
            print(
                "Interactive HTML configuration shortlist written to "
                f"{arguments.html}"
            )
        _print_summary(report)
    except (ShortlistError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
