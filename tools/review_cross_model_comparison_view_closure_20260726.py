#!/usr/bin/env python3
"""Verify closure of the scope-preserving cross-model navigation milestone."""

from __future__ import annotations

import argparse
import json
import posixpath
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Mapping, Sequence

from catalog_completion_history import completion_applied
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "data"
    / "reporting"
    / "cross_model_comparison_view_closure_review.json"
)
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.cross_model_comparison_view import (  # noqa: E402
    collect_view,
    render_html,
    render_json,
)
from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402


class ClosureError(RuntimeError):
    """Raised when the closure contract drifts."""


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value is not None:
                self.hrefs.append(value)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def local_target(source: str, href: str) -> str:
    ensure(not href.startswith("/"), f"absolute local link is forbidden: {href}")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), href))
    ensure(target != "..", f"local link escapes release root: {href}")
    ensure(not target.startswith("../"), f"local link escapes release root: {href}")
    return target


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported closure version")
    ensure(
        payload.get("kind") == "cross_model_comparison_view_closure_review",
        "unexpected closure kind",
    )
    ensure(payload.get("reviewed_on") == "2026-07-26", "closure date differs")
    ensure(payload.get("status") == "complete", "closure is not complete")

    source = payload.get("source_package")
    ensure(isinstance(source, Mapping), "source package is missing")
    ensure(source.get("pull_request") == 281, "source pull request differs")
    ensure(
        source.get("merge_commit")
        == "4f11eaa9be96dd028d4c7f5e0e36c1ba27325558",
        "source merge commit differs",
    )

    contract = payload.get("product_contract")
    ensure(isinstance(contract, Mapping), "product contract is missing")
    expected = {
        "kind": "scope_preserving_cross_model_comparison_view",
        "view_version": 1,
        "snapshot_date": "2026-07-25",
        "model_family_count": 5,
        "reporting_scope_count": 19,
        "single_model_scope_count": 18,
        "mixed_model_scope_count": 1,
        "active_configuration_count": 72,
        "within_scope_pair_count": 114,
        "catalog_price_recorded_count": 72,
    }
    for key, value in expected.items():
        ensure(contract.get(key) == value, f"product contract differs: {key}")

    mixed = contract.get("mixed_scope")
    ensure(isinstance(mixed, Mapping), "mixed-scope contract is missing")
    ensure(mixed.get("slug") == "sandero_ecog120_manual", "mixed scope differs")
    ensure(mixed.get("configuration_count") == 5, "mixed configuration count differs")
    ensure(mixed.get("pair_count") == 10, "mixed pair count differs")
    ensure(mixed.get("technical_slot_count") == 56, "mixed slot count differs")
    ensure(
        mixed.get("model_codes") == ["sandero_iii", "sandero_stepway_iii"],
        "mixed model codes differ",
    )

    output = payload.get("output_contract")
    ensure(isinstance(output, Mapping), "output contract is missing")
    ensure(output.get("release_archive_member_count") == 85, "archive count differs")
    ensure(output.get("comparison_paths_in_json") == 76, "JSON path count differs")
    ensure(output.get("navigation_paths_in_json") == 2, "navigation count differs")
    ensure(output.get("local_file_links_in_html") == 57, "HTML link count differs")
    ensure(output.get("standalone_html") is True, "HTML is not standalone")
    ensure(output.get("javascript_used") is False, "JavaScript boundary differs")
    ensure(output.get("runtime_image_dependency") is False, "image boundary differs")
    ensure(output.get("byte_deterministic") is True, "determinism boundary differs")

    unknown = payload.get("unknown_contract")
    ensure(isinstance(unknown, Mapping), "unknown contract is missing")
    ensure(
        unknown.get("models_without_recorded_seat_values")
        == ["bigster", "duster_iii"],
        "unknown-seat models differ",
    )
    ensure(unknown.get("machine_state") == "not_stated", "unknown state differs")
    ensure(unknown.get("zero_substitution_allowed") is False, "zero substitution allowed")
    ensure(
        unknown.get("assumed_five_seats_allowed") is False,
        "five-seat inference allowed",
    )

    boundaries = payload.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "semantic boundaries are missing")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
        "master_data_changed",
        "schema_changed",
        "comparison_engine_changed",
    ):
        ensure(boundaries.get(key) is False, f"semantic boundary differs: {key}")

    decision = payload.get("closure_decision")
    ensure(isinstance(decision, Mapping), "closure decision is missing")
    ensure(decision.get("result") == "closed", "milestone is not closed")
    next_package = payload.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    ensure(
        next_package.get("name") == "Post-Cross-Model Priority Selection Review",
        "next package differs",
    )


def verify_view(view: Mapping[str, Any]) -> None:
    ensure(view.get("version") == 1, "view version differs")
    ensure(
        view.get("kind") == "scope_preserving_cross_model_comparison_view",
        "view kind differs",
    )
    ensure(view.get("as_of") == "2026-07-25", "view snapshot differs")
    summary = view.get("summary")
    ensure(isinstance(summary, Mapping), "view summary is missing")
    expected = {
        "model_family_count": 5,
        "reporting_scope_count": 19,
        "single_model_scope_count": 18,
        "mixed_model_scope_count": 1,
        "active_configuration_count": 72,
        "within_scope_pair_count": 114,
        "catalog_price_recorded_count": 72,
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        ensure(summary.get(key) == value, f"view summary differs: {key}")

    models = view.get("models")
    scopes = view.get("scopes")
    ensure(isinstance(models, list) and len(models) == 5, "model cards differ")
    ensure(isinstance(scopes, list) and len(scopes) == 19, "scope cards differ")
    ensure(
        sum(int(scope.get("configuration_count", 0)) for scope in scopes) == 72,
        "scope configuration total differs",
    )
    ensure(
        sum(int(scope.get("pair_count", 0)) for scope in scopes) == 114,
        "scope pair total differs",
    )
    mixed = [scope for scope in scopes if scope.get("mixed_model") is True]
    ensure(len(mixed) == 1, "mixed scope count differs")
    ensure(mixed[0].get("slug") == "sandero_ecog120_manual", "mixed scope differs")
    ensure(mixed[0].get("configuration_count") == 5, "mixed configuration count differs")
    ensure(mixed[0].get("pair_count") == 10, "mixed pair count differs")
    ensure(mixed[0].get("technical_slot_count") == 56, "mixed slot count differs")

    model_index = {
        str(model.get("model_code")): model
        for model in models
        if isinstance(model, Mapping)
    }
    for code in ("bigster", "duster_iii"):
        model = model_index.get(code)
        ensure(isinstance(model, Mapping), f"model is missing: {code}")
        ensure(model.get("seat_summary_state") == "not_stated", f"seat state differs: {code}")
        ensure(model.get("recorded_seat_values") == [], f"seat values inferred: {code}")


def verify_cli(view: Mapping[str, Any]) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        json_path = root / "view.json"
        html_path = root / "view.html"
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "dkb.py"),
                "cross-model-comparison-view",
                "--json",
                str(json_path),
                "--html",
                str(html_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        ensure(completed.returncode == 0, completed.stderr or completed.stdout)
        ensure(json_path.read_text(encoding="utf-8") == render_json(view), "CLI JSON differs")
        ensure(html_path.read_text(encoding="utf-8") == render_html(view), "CLI HTML differs")


def verify_release(view: Mapping[str, Any]) -> None:
    version = "9.9.9"
    commit_sha = "2" * 40
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, version, commit_sha)
        archive_path = output / archive_name(version)
        ensure(manifest.get("selected_configuration_count") == 72, "release selection differs")
        ensure(manifest.get("scope_group_count") == 19, "release scope count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "release created cross-scope pairs")
        ensure(manifest.get("ranking_generated") is False, "release created ranking")
        ensure(manifest.get("recommendations_generated") is False, "release created recommendations")
        ensure(manifest.get("inferred_values_generated") is False, "release created inferred values")

        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            name_set = set(names)
            ensure(len(names) == 85, "release archive member count differs")
            ensure(len(name_set) == 85, "release archive contains duplicate paths")
            json_name = "cross-model/cross-model-comparison-view.json"
            html_name = "cross-model/cross-model-comparison-view.html"
            ensure(json_name in name_set, "cross-model JSON is missing from release")
            ensure(html_name in name_set, "cross-model HTML is missing from release")
            archived_view = json.loads(archive.read(json_name).decode("utf-8"))
            archived_html = archive.read(html_name).decode("utf-8")

        ensure(archived_view == view, "archived view differs from generator")
        ensure(archived_html == render_html(view), "archived HTML differs from generator")
        ensure("<script" not in archived_html.lower(), "archived HTML contains JavaScript")
        ensure("<img" not in archived_html.lower(), "archived HTML depends on runtime images")
        ensure("nie podano" in archived_html, "unknown human label is missing")

        comparison_paths: list[str] = []
        scopes = archived_view.get("scopes")
        ensure(isinstance(scopes, list), "archived scopes are missing")
        for scope in scopes:
            ensure(isinstance(scope, Mapping), "archived scope is invalid")
            paths = scope.get("comparison_paths")
            ensure(isinstance(paths, Mapping), "scope paths are missing")
            ensure(
                set(paths) == {"html", "json", "markdown", "differences_csv"},
                "scope path formats differ",
            )
            comparison_paths.extend(str(value) for value in paths.values())
        ensure(len(comparison_paths) == 76, "comparison path count differs")

        navigation = archived_view.get("navigation")
        ensure(isinstance(navigation, Mapping), "navigation paths are missing")
        navigation_paths = [
            str(navigation.get("shortlist_html", "")),
            str(navigation.get("comparison_bundle_manifest", "")),
        ]
        ensure(all(navigation_paths), "navigation path is empty")
        for href in [*comparison_paths, *navigation_paths]:
            ensure(
                local_target(json_name, href) in name_set,
                f"JSON target is missing from release: {href}",
            )

        parser = LinkCollector()
        parser.feed(archived_html)
        local_file_hrefs = [
            href
            for href in parser.hrefs
            if not href.startswith("#")
            and not href.startswith("http://")
            and not href.startswith("https://")
        ]
        ensure(len(local_file_hrefs) == 57, "HTML local-file link count differs")
        for href in local_file_hrefs:
            ensure(
                local_target(html_name, href) in name_set,
                f"HTML target is missing from release: {href}",
            )


def verify_state() -> None:
    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package")
    ensure(isinstance(current, Mapping), "current package is missing")
    ensure(isinstance(current.get("name"), str) and bool(current["name"]), "current package name is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    ensure(isinstance(next_package.get("name"), str) and bool(next_package["name"]), "next package name is missing")
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 998, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 2949, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 244, "configuration ranges regressed")
    ensure(baseline.get("availability_records", 0) >= 4754, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


def verify() -> None:
    report = load_json(REPORT)
    verify_report(report)
    if completion_applied(ROOT):
        verify_state()
        return
    view = collect_view(ROOT)
    verify_view(view)
    ensure(render_json(view) == render_json(collect_view(ROOT)), "JSON generation is not deterministic")
    ensure(render_html(view) == render_html(collect_view(ROOT)), "HTML generation is not deterministic")
    verify_cli(view)
    verify_release(view)
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the closure contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ClosureError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: cross-model comparison view closure review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
