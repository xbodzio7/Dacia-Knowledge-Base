"""Zero-count gate for comparison headers below the sticky selection panel."""

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
    assert "--comparison-sticky-top" in source
    assert ".comparison-table thead th{top:var(--comparison-sticky-top,0px)}" in source
    assert "panel.offsetHeight + 18" in source
    assert "ResizeObserver" in source
    assert "MutationObserver" in source
    assert "getComputedStyle(panel).position === \"sticky\"" in source

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
    assert "new ResizeObserver(update).observe(panel)" in rendered
    assert "new MutationObserver(update).observe(panel" in rendered
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
