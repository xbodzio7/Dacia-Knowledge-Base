#!/usr/bin/env python3
"""Filter active configurations into an evidence-aware shortlist."""

from __future__ import annotations

import argparse
import json
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


_SPRING_MEDIA_SOURCE = Path(
    "project/sources/dacia-pl-spring-model-media-20260801.json"
)
_REVIEWED_GAP_REPORT = Path(
    "data/reporting/registered_source_completeness_reconciliation.json"
)
_OFFICIAL_MEDIA_PREFIXES = (
    "https://www.dacia.pl/",
    "https://cdn.group.renault.com/",
)

_COMPARISON_ENHANCEMENT_STYLE = r'''<style>
:root{--comparison-sticky-top:0px}
.comparison-panel{scroll-margin-top:8px}
.comparison-table thead th{top:0}
body:has(#comparison-panel:not([hidden])) .selection-panel,
.selection-panel.comparison-is-open{position:static;top:auto}
.comparison-group-help{margin:12px 0 0;color:var(--config-muted);font-size:.82rem;line-height:1.45}
.comparison-group-controls{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0}
.comparison-group-controls button{min-height:36px;padding:7px 11px;border:1px solid var(--line);border-radius:8px;background:var(--config-panel);color:var(--config-text);cursor:pointer;font-size:.76rem;font-weight:750}
.comparison-group-controls button:disabled{cursor:not-allowed;opacity:.45}
.comparison-table .comparison-category-row .comparison-category-label{position:sticky;left:0;z-index:7;width:var(--parameter-column,280px);min-width:var(--parameter-column,280px);max-width:var(--parameter-column,280px);padding:0;background:var(--soft)}
.comparison-table .comparison-category-row .comparison-category-fill{background:var(--soft)}
.comparison-category-toggle{display:flex;width:100%;min-height:40px;align-items:center;gap:8px;padding:8px 12px;border:0;background:transparent;color:var(--accent);cursor:pointer;font:inherit;font-weight:800;letter-spacing:.05em;text-align:left;text-transform:uppercase}
.comparison-category-toggle::before{content:"▾";flex:0 0 auto;font-size:1rem;line-height:1}
.comparison-category-toggle[aria-expanded="false"]::before{content:"▸"}
.comparison-category-toggle:focus-visible{outline:3px solid rgba(31,111,67,.24);outline-offset:-3px}
.comparison-data-row[data-group-collapsed="true"]{display:none!important}
.comparison-source-note{display:inline-flex;align-items:center;justify-content:center;width:1.15rem;height:1.15rem;margin-left:.35rem;border:1px solid var(--line);border-radius:50%;color:var(--accent);font-size:.68rem;font-weight:800;line-height:1;vertical-align:middle;cursor:help}
.comparison-source-note:focus-visible{outline:3px solid rgba(31,111,67,.24);outline-offset:2px}
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
  const storageKey = "dkb-comparison-collapsed-groups-v1";
  const collapsedCategories = new Set();
  try {
    const stored = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
    if (Array.isArray(stored)) {
      for (const category of stored) {
        if (typeof category === "string" && category) collapsedCategories.add(category);
      }
    }
  } catch (_error) {
    sessionStorage.removeItem(storageKey);
  }
  let offsetFrame = 0;
  let decorateFrame = 0;

  const persistCollapsedState = () => {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify([...collapsedCategories]));
    } catch (_error) {
      // Session storage is an enhancement, not a requirement.
    }
  };

  const updateStickyOffset = () => {
    if (offsetFrame) cancelAnimationFrame(offsetFrame);
    offsetFrame = requestAnimationFrame(() => {
      const comparisonOpen = !comparisonPanel.hidden;
      selectionPanel.classList.toggle("comparison-is-open", comparisonOpen);
      const sticky = getComputedStyle(selectionPanel).position === "sticky";
      const offset = sticky ? Math.ceil(selectionPanel.offsetHeight + 18) : 0;
      root.style.setProperty("--comparison-sticky-top", `${offset}px`);
      offsetFrame = 0;
    });
  };

  const help = document.createElement("p");
  help.className = "comparison-group-help";
  help.textContent = "Kliknij nazwę grupy w tabeli, aby ją zwinąć lub rozwinąć. Ustawienie jest pamiętane do końca bieżącej sesji przeglądarki.";
  const controls = document.createElement("div");
  controls.className = "comparison-group-controls";
  controls.setAttribute("aria-label", "Sterowanie grupami parametrów");
  const collapseAll = document.createElement("button");
  collapseAll.type = "button";
  collapseAll.textContent = "Ukryj wszystkie grupy";
  const expandAll = document.createElement("button");
  expandAll.type = "button";
  expandAll.textContent = "Pokaż wszystkie grupy";
  controls.append(collapseAll, expandAll);
  const scroll = comparisonPanel.querySelector(".comparison-scroll");
  if (scroll) {
    comparisonPanel.insertBefore(help, scroll);
    comparisonPanel.insertBefore(controls, scroll);
  }

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
      const labelCell = [...row.children].find((child) => child.tagName === "TH");
      if (!labelCell) continue;
      let fill = row.querySelector(".comparison-category-fill")
        || [...row.children].find((child) => child.tagName === "TD");
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
      }
      if (!fill) {
        fill = document.createElement("td");
        row.append(fill);
      }
      fill.classList.add("comparison-category-fill");
      fill.setAttribute("aria-hidden", "true");
      fill.colSpan = Math.max(1, columnCount - 1);
      applyCollapsedState(category);
    }
    updateControlState();
  };

  const scheduleDecoration = () => {
    if (decorateFrame) cancelAnimationFrame(decorateFrame);
    decorateFrame = requestAnimationFrame(() => {
      decorateCategoryRows();
      updateStickyOffset();
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
    persistCollapsedState();
    applyCollapsedState(category);
    updateControlState();
  });

  collapseAll.addEventListener("click", () => {
    for (const row of categoryRows()) {
      if (row.dataset.category) collapsedCategories.add(row.dataset.category);
    }
    persistCollapsedState();
    decorateCategoryRows();
  });

  expandAll.addEventListener("click", () => {
    collapsedCategories.clear();
    persistCollapsedState();
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
    new MutationObserver(updateStickyOffset).observe(comparisonPanel, {
      attributes: true,
      attributeFilter: ["hidden"]
    });
    new MutationObserver(scheduleDecoration).observe(table, {
      childList: true,
      subtree: true
    });
  }
})();
</script>'''


def _apply_supplemental_model_media(
    catalog: dict[str, Any],
    repository: Path,
) -> None:
    path = repository / _SPRING_MEDIA_SOURCE
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortlistError(f"cannot read supplemental model media: {exc}") from exc
    models = payload.get("models", {})
    if not isinstance(models, dict):
        raise ShortlistError("invalid supplemental model media: expected models object")
    captured_on = str(payload.get("captured_on", ""))
    facets = catalog.get("facets", {})
    model_facets = facets.get("models", []) if isinstance(facets, dict) else []
    configurations = catalog.get("configurations", [])
    for model_code, source in models.items():
        if not isinstance(model_code, str) or not isinstance(source, dict):
            continue
        image_url = str(source.get("image_url", ""))
        page_url = str(source.get("source_page_url", ""))
        if not image_url.startswith(_OFFICIAL_MEDIA_PREFIXES):
            raise ShortlistError(
                f"non-official supplemental image URL for {model_code}"
            )
        if not page_url.startswith("https://www.dacia.pl/"):
            raise ShortlistError(
                f"non-official supplemental source page for {model_code}"
            )
        media = {
            "image_url": image_url,
            "source_page_url": page_url,
            "source_name": str(source.get("source_name", "Dacia Polska")),
            "captured_on": captured_on,
        }
        if isinstance(configurations, list):
            for configuration in configurations:
                if (
                    isinstance(configuration, dict)
                    and configuration.get("model_code") == model_code
                ):
                    configuration["model_media"] = dict(media)
        if isinstance(model_facets, list):
            for facet in model_facets:
                if isinstance(facet, dict) and facet.get("code") == model_code:
                    facet["media"] = dict(media)


def _read_reviewed_gap_report(repository: Path) -> dict[str, Any] | None:
    path = repository / _REVIEWED_GAP_REPORT
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortlistError(f"cannot read reviewed gap report: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("status") != "complete":
        raise ShortlistError("reviewed gap report is not complete")
    groups = payload.get("review_groups")
    if not isinstance(groups, list):
        raise ShortlistError("reviewed gap report has no review_groups list")
    return payload


def _commercial_review_decisions(
    payload: Mapping[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        group: Mapping[str, Any],
        item_code: str,
        configuration_code: str,
        candidate_amount: Any = None,
    ) -> None:
        key = (configuration_code, item_code)
        if key in result:
            raise ShortlistError(f"duplicate commercial review decision: {key}")
        amount = candidate_amount
        if amount is None:
            amount = group.get("candidate_amount_pln")
        result[key] = {
            "review_state": str(group.get("classification", "")),
            "review_reason_code": str(group.get("reason_code", "")),
            "reviewed_on": str(payload.get("generated_on", "")),
            "candidate_amount_pln": amount,
            "candidate_source_code": str(group.get("candidate_source_code", "")),
        }

    for raw_group in payload.get("review_groups", []):
        if not isinstance(raw_group, Mapping) or raw_group.get("area") != "optional-price":
            continue
        configuration_code = str(raw_group.get("configuration_code", ""))
        rows = raw_group.get("rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, list):
                    raise ShortlistError("invalid commercial review row")
                if configuration_code and len(row) == 2:
                    add(raw_group, str(row[0]), configuration_code, row[1])
                elif not configuration_code and len(row) == 3:
                    add(raw_group, str(row[0]), str(row[1]), row[2])
                else:
                    raise ShortlistError("unsupported commercial review row shape")
            continue
        item_codes = raw_group.get("commercial_item_codes")
        if configuration_code and isinstance(item_codes, list):
            for item_code in item_codes:
                add(raw_group, str(item_code), configuration_code)
            continue
        item_code = str(raw_group.get("commercial_item_code", ""))
        configurations = raw_group.get("configurations")
        if item_code and isinstance(configurations, list):
            for code in configurations:
                add(raw_group, item_code, str(code))
            continue
        raise ShortlistError("unsupported commercial review group")

    if len(result) != 29:
        raise ShortlistError(
            f"expected 29 commercial review decisions, found {len(result)}"
        )
    return result


def _technical_review_states(
    payload: Mapping[str, Any],
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for raw_group in payload.get("review_groups", []):
        if not isinstance(raw_group, Mapping) or raw_group.get("area") != "active-comparison":
            continue
        classification = str(raw_group.get("classification", ""))
        reason = str(raw_group.get("reason_code", ""))
        source = str(raw_group.get("source_code", ""))
        configuration_code = str(raw_group.get("configuration_code", ""))
        items = raw_group.get("items")
        if configuration_code and isinstance(items, list):
            pairs = [(configuration_code, str(item)) for item in items]
        else:
            item = str(raw_group.get("item", ""))
            configurations = raw_group.get("configurations")
            if not item or not isinstance(configurations, list):
                raise ShortlistError("unsupported technical review group")
            pairs = [(str(code), item) for code in configurations]
        for code, item in pairs:
            attribute_code, separator, fuel_type = item.partition(":")
            comparison_key = f"{attribute_code}::{fuel_type if separator else 'all'}"
            display = (
                "nie dotyczy — skrzynia automatyczna"
                if reason == "automatic_transmission_scope"
                else "niepodane w dokładnym źródle"
            )
            result.append(
                {
                    "configuration_code": code,
                    "comparison_key": comparison_key,
                    "classification": classification,
                    "reason_code": reason,
                    "source_code": source,
                    "display_value": display,
                }
            )
    if len(result) != 22:
        raise ShortlistError(
            f"expected 22 technical review states, found {len(result)}"
        )
    return result


def _apply_reviewed_gap_states(
    catalog: dict[str, Any],
    repository: Path,
) -> None:
    payload = _read_reviewed_gap_report(repository)
    if payload is None:
        return
    configurations = catalog.get("configurations")
    facets = catalog.get("facets")
    if not isinstance(configurations, list) or not isinstance(facets, dict):
        raise ShortlistError("invalid browser catalog for gap materialization")
    by_code = {
        str(item.get("configuration_code", "")): item
        for item in configurations
        if isinstance(item, dict)
    }
    comparison_facets = facets.get("comparison_values", [])
    facet_by_key = {
        str(item.get("key", "")): item
        for item in comparison_facets
        if isinstance(item, dict)
    }
    reviewed_on = str(payload.get("generated_on", ""))
    technical_count = 0
    for review in _technical_review_states(payload):
        configuration = by_code.get(review["configuration_code"])
        facet = facet_by_key.get(review["comparison_key"])
        if configuration is None:
            raise ShortlistError(
                "reviewed technical gap references an unknown configuration: "
                f"{review['configuration_code']}"
            )
        if facet is None:
            if review["comparison_key"] != "gear_shift_indicator::all":
                raise ShortlistError(
                    "reviewed technical gap does not match the browser catalog: "
                    f"{review['configuration_code']} / {review['comparison_key']}"
                )
            facet = {
                "key": "gear_shift_indicator::all",
                "attribute_code": "gear_shift_indicator",
                "label": "Wskaźnik zmiany biegów",
                "category": "Transmission",
                "data_type": "boolean",
                "unit": "",
                "fuel_type_code": "",
                "fuel_type_label": "",
                "gear_number": "",
                "cargo_context": None,
                "cargo_context_signature": "",
                "cargo_context_label": "",
                "context": "",
            }
            comparison_facets.append(facet)
            facet_by_key[review["comparison_key"]] = facet
        values = configuration.setdefault("comparison_values", {})
        if review["comparison_key"] in values:
            raise ShortlistError(
                "reviewed technical gap already has a recorded value: "
                f"{review['configuration_code']} / {review['comparison_key']}"
            )
        values[review["comparison_key"]] = {
            **facet,
            "kind": "reviewed_gap",
            "value": "",
            "display_value": review["display_value"],
            "observation_date": reviewed_on,
            "source_code": review["source_code"],
            "review_state": review["classification"],
            "review_reason_code": review["reason_code"],
        }
        technical_count += 1

    decisions = _commercial_review_decisions(payload)
    commercial_count = 0
    for configuration_code, configuration in by_code.items():
        components = configuration.get("price_components", [])
        if not isinstance(components, list):
            continue
        for component in components:
            if not isinstance(component, dict):
                continue
            key = (configuration_code, str(component.get("code", "")))
            decision = decisions.get(key)
            if decision is None:
                continue
            component.update(decision)
            commercial_count += 1

    catalog["reviewed_gap_materialization"] = {
        "reviewed_on": reviewed_on,
        "technical_states": technical_count,
        "commercial_states": commercial_count,
        "commercial_decisions": len(decisions),
    }


def collect_enhanced_browser_catalog(
    repository: Path,
    criteria: ShortlistCriteria,
) -> dict[str, Any]:
    """Build the canonical interactive catalog used by CLI and releases."""
    catalog = collect_browser_catalog(repository, criteria)
    _apply_supplemental_model_media(catalog, repository)
    _apply_reviewed_gap_states(catalog, repository)
    return catalog


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
            catalog = collect_enhanced_browser_catalog(
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
