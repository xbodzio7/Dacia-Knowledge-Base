from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from reporting.configuration_comparison_bundle import BundleError, create_bundle
from reporting.configuration_shortlist import (
    ShortlistCriteria,
    ShortlistError,
    collect_report,
    render_csv,
    render_json,
    render_markdown,
)
from reporting.configuration_shortlist_html import collect_browser_catalog
from reporting.configuration_shortlist_selection_html import render_html
from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    RELEASE_SCHEMA_VERSION,
    ReleaseError,
    archive_name,
    checksum_text,
    file_record,
    json_text,
    normalize_commit_sha,
    normalize_version,
    release_tag,
    sha256_file,
    verify_release_assets,
    write_deterministic_zip,
    write_text,
)


PRODUCT_FORMATS = (
    "JSON",
    "Markdown",
    "CSV",
    "HTML",
    "XLSX",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _prepare_output_directory(output_directory: Path) -> Path:
    parent = output_directory.parent
    parent.mkdir(parents=True, exist_ok=True)
    if output_directory.exists():
        if not output_directory.is_dir():
            raise ReleaseError(
                f"release output path is not a directory: {output_directory}"
            )
        if any(output_directory.iterdir()):
            raise ReleaseError(
                "release output directory must not exist or must be empty: "
                f"{output_directory}"
            )
    return Path(
        tempfile.mkdtemp(
            prefix=f".{output_directory.name}.build-",
            dir=parent,
        )
    )


def _write_shortlist(repository: Path, payload: Path) -> dict[str, Any]:
    criteria = ShortlistCriteria()
    report = collect_report(repository, criteria)
    summary = report.get("summary")
    results = report.get("results")
    if not isinstance(summary, dict) or not isinstance(results, list):
        raise ReleaseError("configuration shortlist report is malformed")
    active = summary.get("active_configurations")
    matched = summary.get("matched_configurations")
    if active != matched or matched != len(results):
        raise ReleaseError(
            "complete release shortlist must include every active configuration"
        )

    shortlist = payload / "shortlist"
    write_text(shortlist / "configuration-shortlist.json", render_json(report))
    write_text(
        shortlist / "configuration-shortlist.md",
        render_markdown(report),
    )
    write_text(shortlist / "configuration-shortlist.csv", render_csv(report))
    catalog = collect_browser_catalog(repository, criteria)
    write_text(
        shortlist / "configuration-shortlist.html",
        render_html(catalog),
    )
    return report


def _configuration_codes(report: Mapping[str, Any]) -> tuple[str, ...]:
    raw_results = report.get("results")
    if not isinstance(raw_results, list):
        raise ReleaseError("configuration shortlist results must be a list")
    codes: list[str] = []
    for item in raw_results:
        if not isinstance(item, dict):
            raise ReleaseError("configuration shortlist result must be an object")
        code = item.get("configuration_code")
        if not isinstance(code, str) or not code:
            raise ReleaseError("configuration shortlist result has no code")
        codes.append(code)
    if len(codes) != len(set(codes)):
        raise ReleaseError(
            "complete release shortlist codes must be unique"
        )
    return tuple(sorted(codes))


def _release_notes(
    version: str,
    commit_sha: str,
    shortlist: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> str:
    summary = shortlist["summary"]
    assert isinstance(summary, dict)
    return "\n".join(
        [
            f"# Dacia Knowledge Base Data Products v{version}",
            "",
            f"- Release tag: `{release_tag(version)}`",
            f"- Repository commit: `{commit_sha}`",
            f"- Snapshot date: `{shortlist['as_of']}`",
            "- Selected configurations: "
            f"{bundle['selected_configuration_count']}",
            f"- Independent scopes: {bundle['scope_group_count']}",
            f"- Comparable scopes: {bundle['comparable_scope_count']}",
            f"- Singleton scopes: {bundle['singleton_scope_count']}",
            "- Cross-scope pairs: none",
            "- Formats: " + ", ".join(PRODUCT_FORMATS),
            "",
            "The archive contains the complete active-configuration shortlist "
            "and one full-portfolio comparison bundle. Existing source dates, "
            "evidence states and independent reporting scopes are preserved.",
            "",
            "No ranking, recommendations or inferred values are generated.",
            "",
        ]
    )


def _archive_record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        "path": record["path"],
        "media_type": record["media_type"],
        "size_bytes": record["size_bytes"],
        "sha256": record["sha256"],
    }


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    normalized_version = normalize_version(version)
    normalized_commit = normalize_commit_sha(commit_sha)
    build_root = _prepare_output_directory(output_directory)
    payload = build_root / ".payload"
    payload.mkdir()
    try:
        shortlist = _write_shortlist(repository, payload)
        codes = _configuration_codes(shortlist)
        bundle_directory = payload / "comparison-bundle"
        bundle = create_bundle(
            repository,
            bundle_directory,
            direct_codes=codes,
        )
        if bundle.get("selected_configuration_count") != len(codes):
            raise ReleaseError("comparison bundle selection is incomplete")
        if bundle.get("scope_group_count") != 18:
            raise ReleaseError(
                "complete release bundle must contain 18 independent scopes"
            )
        if bundle.get("cross_scope_pairs_generated") is not False:
            raise ReleaseError("release bundle generated cross-scope pairs")

        write_text(
            payload / "RELEASE_NOTES.md",
            _release_notes(
                normalized_version,
                normalized_commit,
                shortlist,
                bundle,
            ),
        )

        archive_path = build_root / archive_name(normalized_version)
        files = write_deterministic_zip(payload, archive_path)
        manifest = {
            "schema_version": RELEASE_SCHEMA_VERSION,
            "release_version": normalized_version,
            "release_tag": release_tag(normalized_version),
            "repository_commit": normalized_commit,
            "snapshot_date": shortlist["as_of"],
            "selected_configuration_count": bundle[
                "selected_configuration_count"
            ],
            "scope_group_count": bundle["scope_group_count"],
            "comparable_scope_count": bundle["comparable_scope_count"],
            "singleton_scope_count": bundle["singleton_scope_count"],
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
            "archive": _archive_record(archive_path, build_root),
            "files": files,
        }
        manifest_path = build_root / MANIFEST_NAME
        write_text(manifest_path, json_text(manifest))
        write_text(
            build_root / CHECKSUMS_NAME,
            checksum_text(
                {
                    archive_path.name: sha256_file(archive_path),
                    manifest_path.name: sha256_file(manifest_path),
                }
            ),
        )
        shutil.rmtree(payload)
        verified = verify_release_assets(build_root)
        if verified != manifest:
            raise ReleaseError("verified release manifest changed after writing")
        if output_directory.exists():
            output_directory.rmdir()
        build_root.replace(output_directory)
        return manifest
    except (ShortlistError, BundleError) as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        raise ReleaseError(f"cannot build data product release: {exc}") from exc
    except Exception:
        shutil.rmtree(build_root, ignore_errors=True)
        raise
