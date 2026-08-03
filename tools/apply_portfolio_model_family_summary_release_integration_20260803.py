#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, text: str) -> None:
    (ROOT / relative).write_text(text, encoding="utf-8")


def replace_once(
    relative: str,
    old: str,
    new: str,
    *,
    label: str,
) -> None:
    text = read(relative)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"{label}: anchor not found in {relative}")
    write(relative, text.replace(old, new, 1))


def insert_before(
    relative: str,
    anchor: str,
    insertion: str,
    *,
    marker: str,
    label: str,
    start_at: int = 0,
) -> None:
    text = read(relative)
    if marker in text:
        return
    index = text.find(anchor, start_at)
    if index < 0:
        raise RuntimeError(f"{label}: insertion point not found in {relative}")
    write(relative, text[:index] + insertion + text[index:])


def patch_release_builder() -> None:
    relative = "tools/reporting/data_product_release.py"
    import_anchor = "from reporting.data_product_release_model import (\n"
    family_import = """from reporting.portfolio_model_family_summary import (
    PortfolioModelFamilySummaryError,
    collect_summary as collect_portfolio_model_family_summary,
    render_html as render_portfolio_model_family_html,
    render_json as render_portfolio_model_family_json,
    render_markdown as render_portfolio_model_family_markdown,
)
"""
    insert_before(
        relative,
        import_anchor,
        family_import,
        marker="collect_portfolio_model_family_summary",
        label="family-summary import",
    )

    function_anchor = "def _configuration_codes(report: Mapping[str, Any]) -> tuple[str, ...]:\n"
    family_writer = """def _write_portfolio_model_family_summary(
    repository: Path,
    payload: Path,
    bundle: Mapping[str, Any],
    cross_model_view: Mapping[str, Any],
) -> dict[str, Any]:
    summary = collect_portfolio_model_family_summary(repository)
    totals = summary.get("summary")
    cross_totals = cross_model_view.get("summary")
    if not isinstance(totals, dict) or not isinstance(cross_totals, dict):
        raise ReleaseError("portfolio model-family summary is malformed")
    groups = bundle.get("groups")
    if not isinstance(groups, list):
        raise ReleaseError("comparison bundle groups are missing")
    expected = {
        "model_family_count": cross_totals.get("model_family_count"),
        "reporting_scope_count": bundle.get("scope_group_count"),
        "active_configuration_count": bundle.get(
            "selected_configuration_count"
        ),
        "within_scope_pair_count": sum(
            int(group.get("pair_count", 0))
            for group in groups
            if isinstance(group, dict)
        ),
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        if totals.get(key) != value:
            raise ReleaseError(
                "portfolio model-family summary differs for "
                f"{key}: {totals.get(key)!r}"
            )
    directory = payload / "model-families"
    write_text(
        directory / "portfolio-model-family-summary.json",
        render_portfolio_model_family_json(summary),
    )
    write_text(
        directory / "portfolio-model-family-summary.md",
        render_portfolio_model_family_markdown(summary),
    )
    write_text(
        directory / "portfolio-model-family-summary.html",
        render_portfolio_model_family_html(summary),
    )
    return summary


"""
    insert_before(
        relative,
        function_anchor,
        family_writer,
        marker="def _write_portfolio_model_family_summary(",
        label="family-summary release writer",
    )

    replace_once(
        relative,
        """        "The archive contains the complete active-configuration shortlist, "
        "one full-portfolio comparison bundle and a scope-preserving "
        "cross-model navigation view. Existing source dates, evidence "
        "states and independent reporting scopes are preserved.",
""",
        """        "The archive contains the complete active-configuration shortlist, "
        "one full-portfolio comparison bundle, a scope-preserving cross-model "
        "navigation view and a source-preserving model-family summary. Existing "
        "source dates, evidence states and independent reporting scopes are "
        "preserved.",
""",
        label="release-notes product inventory",
    )

    replace_once(
        relative,
        """        cross_model_view = _write_cross_model_view(repository, payload, bundle)

        write_text(
""",
        """        cross_model_view = _write_cross_model_view(repository, payload, bundle)
        model_family_summary = _write_portfolio_model_family_summary(
            repository,
            payload,
            bundle,
            cross_model_view,
        )

        write_text(
""",
        label="release build invocation",
    )

    replace_once(
        relative,
        """            "cross_model_view_generated": True,
            "comparable_scope_count": bundle["comparable_scope_count"],
""",
        """            "cross_model_view_generated": True,
            "model_family_summary_generated": True,
            "model_family_summary_source_count": model_family_summary["summary"][
                "provenance_source_count"
            ],
            "model_family_summary_relationship_count": model_family_summary[
                "summary"
            ]["source_configuration_relationship_count"],
            "comparable_scope_count": bundle["comparable_scope_count"],
""",
        label="release manifest family-summary receipt",
    )

    replace_once(
        relative,
        """    except (ShortlistError, BundleError, CrossModelViewError) as exc:
""",
        """    except (
        ShortlistError,
        BundleError,
        CrossModelViewError,
        PortfolioModelFamilySummaryError,
    ) as exc:
""",
        label="release error boundary",
    )


def patch_release_download() -> None:
    relative = "tools/reporting/data_product_release_download.py"
    replace_once(
        relative,
        """OPTIONAL_ENTRY_POINTS = {
    "cross_model_html": "cross-model/cross-model-comparison-view.html",
}
""",
        """OPTIONAL_ENTRY_POINTS = {
    "cross_model_html": "cross-model/cross-model-comparison-view.html",
    "model_family_summary_html": (
        "model-families/portfolio-model-family-summary.html"
    ),
}
""",
        label="verified-download optional family entry point",
    )


def patch_workspace_index() -> None:
    relative = "tools/reporting/data_product_workspace_index.py"
    replace_once(
        relative,
        """CROSS_MODEL_HTML_MEMBER = "cross-model/cross-model-comparison-view.html"
SCOPE_PATTERN = re.compile""",
        """CROSS_MODEL_HTML_MEMBER = "cross-model/cross-model-comparison-view.html"
MODEL_FAMILY_HTML_MEMBER = (
    "model-families/portfolio-model-family-summary.html"
)
SCOPE_PATTERN = re.compile""",
        label="workspace model-family member constant",
    )

    text = read(relative)
    if '"title": "Model family summary"' not in text:
        function_start = text.find("def _primary_links(\n")
        if function_start < 0:
            raise RuntimeError("workspace primary-links function not found")
        return_index = text.find("    return tuple(links)\n", function_start)
        if return_index < 0:
            raise RuntimeError("workspace primary-links return not found")
        block = """    if MODEL_FAMILY_HTML_MEMBER in release_members:
        links.append(
            {
                "title": "Model family summary",
                "description": (
                    "Review each family with exact scopes, configurations and "
                    "source provenance."
                ),
                "path": _verified_content_path(
                    workspace_root,
                    release_members,
                    MODEL_FAMILY_HTML_MEMBER,
                    label="portfolio model-family summary HTML",
                ),
            }
        )
"""
        write(relative, text[:return_index] + block + text[return_index:])


def patch_download_cli() -> None:
    relative = "tools/data_product_release_download.py"
    replace_once(
        relative,
        """        "cross_model_html": "Cross-model navigation",
        "release_notes": "Release notes",
""",
        """        "cross_model_html": "Cross-model navigation",
        "model_family_summary_html": "Model family summary",
        "release_notes": "Release notes",
""",
        label="download CLI family label",
    )
    replace_once(
        relative,
        """    if "cross_model_html" in raw_entry_points:
        keys.append("cross_model_html")
    keys.append("release_notes")
""",
        """    if "cross_model_html" in raw_entry_points:
        keys.append("cross_model_html")
    if "model_family_summary_html" in raw_entry_points:
        keys.append("model_family_summary_html")
    keys.append("release_notes")
""",
        label="download CLI family ordering",
    )


def patch_tests_and_manifest() -> None:
    replace_once(
        "tests/test_data_product_release.py",
        "            self.assertEqual(len(names), 93)\n",
        "            self.assertEqual(len(names), 96)\n",
        label="release archive member count",
    )

    relative = (
        "tools/generate_portfolio_model_family_summary_release_integration_20260803.py"
    )
    text = read(relative)
    script_path = (
        '            "tools/apply_portfolio_model_family_summary_release_'
        'integration_20260803.py",\n'
    )
    if script_path not in text:
        anchor = (
            '            "tools/generate_portfolio_model_family_summary_release_'
            'integration_20260803.py",\n'
        )
        if anchor not in text:
            raise RuntimeError("package manifest generator anchor not found")
        write(relative, text.replace(anchor, script_path + anchor, 1))


def verify_markers() -> None:
    required: dict[str, tuple[str, ...]] = {
        "tools/reporting/data_product_release.py": (
            "collect_portfolio_model_family_summary",
            "def _write_portfolio_model_family_summary(",
            '"model_family_summary_generated": True',
            '"model_family_summary_source_count"',
            '"model_family_summary_relationship_count"',
        ),
        "tools/reporting/data_product_release_download.py": (
            '"model_family_summary_html"',
            "model-families/portfolio-model-family-summary.html",
        ),
        "tools/reporting/data_product_workspace_index.py": (
            "MODEL_FAMILY_HTML_MEMBER",
            '"title": "Model family summary"',
        ),
        "tools/data_product_release_download.py": (
            '"model_family_summary_html": "Model family summary"',
            'keys.append("model_family_summary_html")',
        ),
        "tests/test_data_product_release.py": (
            "self.assertEqual(len(names), 96)",
        ),
    }
    for relative, markers in required.items():
        text = read(relative)
        for marker in markers:
            if marker not in text:
                raise RuntimeError(f"integration marker missing in {relative}: {marker}")


def main() -> int:
    patch_release_builder()
    patch_release_download()
    patch_workspace_index()
    patch_download_cli()
    patch_tests_and_manifest()
    verify_markers()
    print("Portfolio model-family release integration patch: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
