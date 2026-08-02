#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reporting.portfolio_model_family_summary import (
    collect_summary,
    render_html,
    render_json,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_BASE = ROOT / "data/reporting/portfolio_model_family_summary"
PACKAGE_DOC = ROOT / "project/packages/portfolio-model-family-summary-20260803.md"
STATE_PATH = ROOT / "project/state.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
PACKAGE_ID = "portfolio_model_family_summary_001"
NEXT_PACKAGE_ID = "portfolio_model_family_summary_release_integration_001"
CHANGELOG_ENTRY = (
    "* Added deterministic JSON, Markdown and standalone HTML portfolio model-family "
    "summaries for all 81 active configurations across six canonical families, "
    "preserving 22 independent reporting scopes, 251 explicit source relationships "
    "and exact source hashes without cross-scope pairs, rankings, recommendations "
    "or inferred values."
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_state() -> dict[str, Any]:
    state = read_json(STATE_PATH)
    state["phase"] = "Portfolio Model Family Summary"
    state["reference_delivery"] = {
        "name": "Post-v1.11.0 Release Priority Selection Review",
        "pull_request": 475,
        "head_sha": "96f30c70dbfb7d1da967e6275526735fef5c9602",
        "quality_run": 30772159207,
    }
    state["baseline"]["tests"] = 1852
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "reporting_product",
        "name": "Portfolio Model Family Summary",
        "status": "complete",
        "goal": (
            "Create deterministic JSON, Markdown and HTML summaries for each "
            "model family from current source-backed active configurations, "
            "preserving independent reporting scopes and exact provenance without "
            "cross-scope pairs, ranking, recommendations or inferred values."
        ),
        "manifest_paths": [
            "tools/reporting/portfolio_model_family_summary.py",
            "tools/portfolio_model_family_summary.py",
            "tools/generate_portfolio_model_family_summary_package_20260803.py",
            "tools/dkb.py",
            "data/reporting/portfolio_model_family_summary.json",
            "data/reporting/portfolio_model_family_summary.md",
            "data/reporting/portfolio_model_family_summary.html",
            "tests/test_portfolio_model_family_summary.py",
            "project/packages/portfolio-model-family-summary-20260803.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
        ],
    }
    state["next_package"] = {
        "package_id": NEXT_PACKAGE_ID,
        "kind": "reporting_release_integration",
        "name": "Portfolio Model Family Summary Release Integration",
        "status": "planned",
        "goal": (
            "Add the verified model-family JSON, Markdown and HTML summary to the "
            "versioned data-product archive, download verification and offline "
            "workspace navigation without changing source data or comparison semantics."
        ),
        "manifest_paths": [],
    }
    return state


def render_package(summary: dict[str, Any]) -> str:
    totals = summary["summary"]
    return f"""# Portfolio Model Family Summary

Date: 2026-08-03

Package ID: `{PACKAGE_ID}`

Status: **complete**

## Result

The package adds deterministic JSON, Markdown and standalone HTML summaries for the current source-backed portfolio:

- {totals['model_family_count']} canonical model families;
- {totals['active_configuration_count']} active configurations;
- {totals['reporting_scope_count']} existing reporting scopes;
- {totals['within_scope_pair_count']} existing within-scope pairs;
- {totals['provenance_source_count']} distinct provenance sources;
- {totals['source_configuration_relationship_count']} explicit source-to-configuration relationships;
- zero configurations without provenance.

Each family preserves exact configuration codes, price coverage, recorded seat states, powertrain and transmission labels, exclusive/shared reporting scopes, source codes, source types, document dates, covered configurations and source SHA-256 values.

## Formats

- `data/reporting/portfolio_model_family_summary.json`;
- `data/reporting/portfolio_model_family_summary.md`;
- `data/reporting/portfolio_model_family_summary.html`.

The HTML output is standalone and contains no script, remote image or runtime network dependency.

## Safety boundary

The package does not create cross-scope pairs, rank models, recommend configurations, infer missing values or modify master data. Existing unknown states remain explicit.

## Next package

`{NEXT_PACKAGE_ID}` will integrate the verified outputs into the versioned release archive, public-download verification and offline workspace navigation.

## Verification

```bash
python tools/generate_portfolio_model_family_summary_package_20260803.py --verify
python -m unittest tests.test_portfolio_model_family_summary
python tools/dkb.py project-state --check
python tools/dkb.py quality --concise
```
"""


def update_changelog() -> None:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY in text:
        return
    marker = "### Added\n"
    if marker not in text:
        raise RuntimeError("CHANGELOG Added section not found")
    CHANGELOG_PATH.write_text(
        text.replace(marker, marker + "\n" + CHANGELOG_ENTRY + "\n", 1),
        encoding="utf-8",
    )


def apply() -> None:
    summary = collect_summary(ROOT)
    REPORT_BASE.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_DOC.parent.mkdir(parents=True, exist_ok=True)
    REPORT_BASE.with_suffix(".json").write_text(
        render_json(summary), encoding="utf-8", newline=""
    )
    REPORT_BASE.with_suffix(".md").write_text(
        render_markdown(summary), encoding="utf-8", newline=""
    )
    REPORT_BASE.with_suffix(".html").write_text(
        render_html(summary), encoding="utf-8", newline=""
    )
    PACKAGE_DOC.write_text(render_package(summary), encoding="utf-8", newline="")
    STATE_PATH.write_text(
        json.dumps(expected_state(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    update_changelog()


def verify() -> None:
    summary = collect_summary(ROOT)
    expected_outputs = {
        REPORT_BASE.with_suffix(".json"): render_json(summary),
        REPORT_BASE.with_suffix(".md"): render_markdown(summary),
        REPORT_BASE.with_suffix(".html"): render_html(summary),
        PACKAGE_DOC: render_package(summary),
    }
    for path, expected in expected_outputs.items():
        if not path.exists():
            raise RuntimeError(f"missing generated output: {path.relative_to(ROOT)}")
        if path.read_text(encoding="utf-8") != expected:
            raise RuntimeError(f"generated output differs: {path.relative_to(ROOT)}")

    state = read_json(STATE_PATH)
    expected = expected_state()
    if state["phase"] != expected["phase"]:
        raise RuntimeError("canonical project phase differs")
    if state["reference_delivery"] != expected["reference_delivery"]:
        raise RuntimeError("reference delivery differs")
    if state["baseline"]["tests"] != 1852:
        raise RuntimeError("canonical test baseline differs")
    for section in ("current_package", "next_package"):
        for key in ("package_id", "kind", "name", "status", "goal"):
            if state[section][key] != expected[section][key]:
                raise RuntimeError(
                    f"canonical project state differs for {section}.{key}"
                )
    required_manifest = set(expected["current_package"]["manifest_paths"])
    actual_manifest = set(state["current_package"]["manifest_paths"])
    if not required_manifest.issubset(actual_manifest):
        raise RuntimeError("canonical package manifest is incomplete")
    if CHANGELOG_ENTRY not in CHANGELOG_PATH.read_text(encoding="utf-8"):
        raise RuntimeError("CHANGELOG receipt is missing")
    dkb_source = (ROOT / "tools/dkb.py").read_text(encoding="utf-8")
    if '"portfolio-model-family-summary"' not in dkb_source:
        raise RuntimeError("unified CLI command is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    verify()
    print("Portfolio model-family summary package: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
