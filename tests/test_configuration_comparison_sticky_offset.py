"""Zero-count gate for comparison headers and collapsible parameter groups."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_shortlist  # noqa: E402


def _verify() -> None:
    source = (TOOLS / "configuration_shortlist.py").read_text(encoding="utf-8")
    for marker in (
        "--comparison-sticky-top",
        ".comparison-table thead th{top:0}",
        'body:has(#comparison-panel:not([hidden])) .selection-panel',
        ".selection-panel.comparison-is-open{position:static;top:auto}",
        'selectionPanel.classList.toggle("comparison-is-open", comparisonOpen)',
        "selectionPanel.offsetHeight + 18",
        'row.querySelector(".comparison-category-fill")',
        "ResizeObserver",
        "MutationObserver",
        'getComputedStyle(selectionPanel).position === "sticky"',
        "comparison-category-label",
        "comparison-category-toggle",
        "Ukryj wszystkie grupy",
        "Pokaż wszystkie grupy",
        "data-group-collapsed",
        "collapsedCategories",
        "sessionStorage",
        "dkb-comparison-collapsed-groups-v1",
        "Kliknij nazwę grupy w tabeli",
        "comparison-source-note",
    ):
        assert marker in source, marker

    rendered = configuration_shortlist.render_html(
        {
            "version": 1,
            "as_of": "2026-07-27",
            "price_dimension": {
                "market": "PL",
                "price_type": "catalog_gross",
                "currency_code": "PLN",
            },
            "initial_filters": {
                "models": [],
                "versions": [],
                "transmissions": [],
                "powertrains": [],
                "minimum_price_pln": None,
                "maximum_price_pln": None,
                "seats": None,
                "required_equipment": [],
                "required_standard_equipment": [],
            },
            "facets": {
                "models": [],
                "versions": [],
                "transmissions": [],
                "powertrains": [],
                "seat_counts": [],
                "comparison_values": [],
                "equipment": [],
            },
            "configurations": [],
        }
    )
    assert rendered.count("--comparison-sticky-top") >= 3
    assert "new ResizeObserver(updateStickyOffset).observe(selectionPanel)" in rendered
    assert "new MutationObserver(scheduleDecoration).observe(table" in rendered
    assert 'attributeFilter: ["hidden"]' in rendered
    assert 'row.querySelector(".comparison-category-fill")' in rendered
    assert "Sterowanie grupami parametrów" in rendered
    assert "comparison-category-fill" in rendered
    assert "Ukryj wszystkie grupy" in rendered
    assert "Pokaż wszystkie grupy" in rendered
    assert rendered.index("--comparison-sticky-top") < rendered.rindex("</body>")


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del loader, pattern
    _verify()
    return tests


if __name__ == "__main__":
    _verify()
