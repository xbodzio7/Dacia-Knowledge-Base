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


_COMPARISON_ENHANCEMENT_STYLE = r'''<style>
:root{--comparison-sticky-top:0px}
.comparison-panel{scroll-margin-top:calc(var(--comparison-sticky-top,0px) + 8px)}
.comparison-table thead th{top:var(--comparison-sticky-top,0px)}
.comparison-group-controls{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0}
.comparison-group-controls button{min-height:36px;padding:7px 11px;border:1px solid #aeb8b0;border-radius:8px;background:#fff;color:var(--ink);cursor:pointer;font-size:.76rem;font-weight:750}
.comparison-group-controls button:disabled{cursor:not-allowed;opacity:.45}
.comparison-table .comparison-category-row .comparison-category-label{position:sticky;left:0;z-index:4;min-width:210px;padding:0;background:#dfe9e2}
.comparison-table .comparison-category-row .comparison-category-fill{background:#dfe9e2}
.comparison-category-toggle{display:flex;width:100%;min-height:40px;align-items:center;gap:8px;padding:8px 12px;border:0;background:transparent;color:var(--accent);cursor:pointer;font:inherit;font-weight:800;letter-spacing:.05em;text-align:left;text-transform:uppercase}
.comparison-category-toggle::before{content:"▾";flex:0 0 auto;font-size:1rem;line-height:1}
.comparison-category-toggle[aria-expanded="false"]::before{content:"▸"}
.comparison-category-toggle:focus-visible{outline:3px solid rgba(31,111,67,.24);outline-offset:-3px}
.comparison-data-row[data-group-collapsed="true"]{display:none!important}
@media(max-width:760px){:root{--comparison-sticky-top:0px!important}}
</style>'''

_COMPARISON_ENHANCEMENT_SCRIPT = r'''<script>
(function () {
  "use strict";
  const selectionPanel = document.querySelector("#selection-panel");
  const comparisonPanel = document.querySelector("#comparison-panel");
  const table = document.querySelector("#comparison-table");
  if (!selectionPanel || !comparisonPanel || !table) return;

  const root = document.documentElement;
  const collapsedCategories = new Set();
  let offsetFrame = 0;
  let decorateFrame = 0;

  const updateStickyOffset = () => {
    if (offsetFrame) cancelAnimationFrame(offsetFrame);
    offsetFrame = requestAnimationFrame(() => {
      const sticky = getComputedStyle(selectionPanel).position === "sticky";
      const offset = sticky ? Math.ceil(selectionPanel.offsetHeight + 18) : 0;
      root.style.setProperty("--comparison-sticky-top", `${offset}px`);
      offsetFrame = 0;
    });
  };

  const controls = document.createElement("div");
  controls.className = "comparison-group-controls";
  controls.setAttribute("aria-label", "Sterowanie grupami parametrów");
  const collapseAll = document.createElement("button");
  collapseAll.type = "button";
  collapseAll.textContent = "Zwiń wszystkie grupy";
  const expandAll = document.createElement("button");
  expandAll.type = "button";
  expandAll.textContent = "Rozwiń wszystkie grupy";
  controls.append(collapseAll, expandAll);
  const scroll = comparisonPanel.querySelector(".comparison-scroll");
  if (scroll) comparisonPanel.insertBefore(controls, scroll);

  const categoryRows = () => [...table.querySelectorAll("tr.comparison-category-row")];
  const dataRows = () => [...table.querySelectorAll("tr.comparison-data-row")];

  const applyCollapsedState = (category) => {
    const collapsed = collapsedCategories.has(category);
    for (const row of dataRows()) {
      if (row.dataset.category === category) {
        row.dataset.groupCollapsed = collapsed ? "true" : "false";
      }
    }
    const heading = categoryRows().find((row) => row.dataset.category === category);
    const button = heading && heading.querySelector(".comparison-category-toggle");
    if (button) {
      button.setAttribute("aria-expanded", String(!collapsed));
      button.title = collapsed ? `Rozwiń grupę ${category}` : `Zwiń grupę ${category}`;
    }
  };

  const updateControlState = () => {
    const rows = categoryRows();
    const categories = rows.map((row) => row.dataset.category).filter(Boolean);
    collapseAll.disabled = categories.length === 0 || categories.every((category) => collapsedCategories.has(category));
    expandAll.disabled = categories.length === 0 || categories.every((category) => !collapsedCategories.has(category));
  };

  const decorateCategoryRows = () => {
    const columnCount = Math.max(1, table.querySelectorAll("thead th").length);
    for (const row of categoryRows()) {
      const category = row.dataset.category || "Pozostałe";
      let labelCell = [...row.children].find((child) => child.tagName === "TH");
      if (!labelCell) continue;
      let toggle = labelCell.querySelector(".comparison-category-toggle");
      if (!toggle) {
        const label = labelCell.textContent.trim() || category;
        labelCell.removeAttribute("colspan");
        labelCell.classList.add("comparison-category-label");
        labelCell.setAttribute("scope", "rowgroup");
        toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "comparison-category-toggle";
        toggle.dataset.category = category;
        toggle.textContent = label;
        labelCell.replaceChildren(toggle);
        const fill = document.createElement("td");
        fill.className = "comparison-category-fill";
        fill.setAttribute("aria-hidden", "true");
        fill.colSpan = Math.max(1, columnCount - 1);
        row.append(fill);
      } else {
        const fill = row.querySelector(".comparison-category-fill");
        if (fill) fill.colSpan = Math.max(1, columnCount - 1);
      }
      applyCollapsedState(category);
    }
    updateControlState();
  };

  const scheduleDecoration = () => {
    if (decorateFrame) cancelAnimationFrame(decorateFrame);
    decorateFrame = requestAnimationFrame(() => {
      decorateCategoryRows();
      decorateFrame = 0;
    });
  };

  table.addEventListener("click", (event) => {
    const toggle = event.target.closest(".comparison-category-toggle");
    if (!toggle) return;
    const category = toggle.dataset.category;
    if (!category) return;
    if (collapsedCategories.has(category)) collapsedCategories.delete(category);
    else collapsedCategories.add(category);
    applyCollapsedState(category);
    updateControlState();
  });

  collapseAll.addEventListener("click", () => {
    for (const row of categoryRows()) {
      if (row.dataset.category) collapsedCategories.add(row.dataset.category);
    }
    decorateCategoryRows();
  });

  expandAll.addEventListener("click", () => {
    collapsedCategories.clear();
    decorateCategoryRows();
  });

  updateStickyOffset();
  scheduleDecoration();
  window.addEventListener("resize", updateStickyOffset, { passive: true });
  if (typeof ResizeObserver === "function") {
    new ResizeObserver(updateStickyOffset).observe(selectionPanel);
  }
  if (typeof MutationObserver === "function") {
    new MutationObserver(updateStickyOffset).observe(selectionPanel, {
      childList: true,
      subtree: true,
      characterData: true
    });
    new MutationObserver(scheduleDecoration).observe(table, {
      childList: true,
      subtree: true
    });
  }
})();
</script>'''


def render_html(catalog: Mapping[str, Any]) -> str:
    """Render the shortlist with usable sticky comparison navigation."""
    rendered = render_selection_html(catalog)
    marker = "</body>"
    if marker not in rendered:
        raise ShortlistError(
            "cannot inject comparison navigation enhancements: missing body marker"
        )
    enhancement = (
        f"{_COMPARISON_ENHANCEMENT_STYLE}\n"
        f"{_COMPARISON_ENHANCEMENT_SCRIPT}\n"
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
