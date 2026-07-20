from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from urllib.parse import quote

from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    safe_member_name,
)


INDEX_NAME = "index.html"
BUNDLE_MANIFEST_MEMBER = (
    "comparison-bundle/comparison-bundle-manifest.json"
)
SCOPE_PATTERN = re.compile(r"[a-z0-9][a-z0-9_]*\Z")
REPORT_LABELS = {
    "html": "Interactive HTML",
    "markdown": "Markdown",
    "csv": "Differences CSV",
    "json": "Full JSON",
}
REPORT_ORDER = ("html", "markdown", "csv", "json")


class WorkspaceIndexError(ReleaseError):
    """Raised when a verified workspace cannot receive a safe local index."""


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise WorkspaceIndexError(f"{label} must be an object")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorkspaceIndexError(f"{label} must be a non-empty string")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise WorkspaceIndexError(
            f"{label} must be an integer greater than or equal to {minimum}"
        )
    return value


def _read_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise WorkspaceIndexError(f"cannot read {label} {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise WorkspaceIndexError(f"invalid JSON in {label} {path}: {exc}") from exc
    return _object(value, label)


def _release_members(manifest: Mapping[str, Any]) -> set[str]:
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise WorkspaceIndexError("release manifest file inventory is empty")
    members: set[str] = set()
    for index, raw_record in enumerate(raw_files):
        record = _object(raw_record, f"release manifest file record {index}")
        path = safe_member_name(
            _string(record.get("path"), f"release manifest file {index}.path")
        )
        if path in members:
            raise WorkspaceIndexError(f"duplicate release member: {path}")
        members.add(path)
    return members


def _workspace_file(
    workspace_root: Path,
    relative_name: str,
    *,
    label: str,
) -> Path:
    normalized = safe_member_name(relative_name)
    relative = PurePosixPath(normalized)
    path = workspace_root.joinpath(*relative.parts)
    if not path.is_file():
        raise WorkspaceIndexError(f"{label} is missing: {relative_name}")
    return path


def _verified_content_path(
    workspace_root: Path,
    release_members: set[str],
    member_name: str,
    *,
    label: str,
) -> str:
    normalized = safe_member_name(member_name)
    if normalized not in release_members:
        raise WorkspaceIndexError(
            f"{label} is not present in the verified release manifest: {normalized}"
        )
    workspace_name = f"contents/{normalized}"
    _workspace_file(workspace_root, workspace_name, label=label)
    return workspace_name


def _verified_bundle_path(
    workspace_root: Path,
    release_members: set[str],
    relative_name: str,
    *,
    label: str,
) -> str:
    normalized = safe_member_name(relative_name)
    return _verified_content_path(
        workspace_root,
        release_members,
        f"comparison-bundle/{normalized}",
        label=label,
    )


def _asset_path(
    workspace_root: Path,
    relative_name: str,
    *,
    label: str,
) -> str:
    normalized = safe_member_name(relative_name)
    workspace_name = f"assets/{normalized}"
    _workspace_file(workspace_root, workspace_name, label=label)
    return workspace_name


def _href(path: str) -> str:
    normalized = safe_member_name(path)
    encoded = "/".join(
        quote(part, safe="-._~")
        for part in PurePosixPath(normalized).parts
    )
    return escape(encoded, quote=True)


def _external_href(value: Any) -> str:
    url = _string(value, "release URL")
    expected_prefix = (
        "https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/"
    )
    if not url.startswith(expected_prefix):
        raise WorkspaceIndexError("release URL is not the canonical GitHub URL")
    return escape(url, quote=True)


def _file_record_path(
    raw_record: Any,
    label: str,
) -> str:
    record = _object(raw_record, label)
    try:
        return safe_member_name(
            _string(record.get("path"), f"{label}.path")
        )
    except ReleaseError as exc:
        raise WorkspaceIndexError(str(exc)) from exc


def _configuration_codes(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise WorkspaceIndexError(f"{label} must be a non-empty list")
    codes: list[str] = []
    for index, raw_code in enumerate(value):
        code = _string(raw_code, f"{label}[{index}]")
        if code != code.strip():
            raise WorkspaceIndexError(
                f"{label}[{index}] must not contain surrounding whitespace"
            )
        codes.append(code)
    if len(codes) != len(set(codes)):
        raise WorkspaceIndexError(f"{label} must not contain duplicates")
    return tuple(codes)


def _scope_records(
    workspace_root: Path,
    release_members: set[str],
    bundle: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    raw_groups = bundle.get("groups")
    if not isinstance(raw_groups, list) or not raw_groups:
        raise WorkspaceIndexError("comparison bundle groups must be a non-empty list")
    expected_count = _integer(
        bundle.get("scope_group_count"),
        "comparison bundle scope_group_count",
        minimum=1,
    )
    if expected_count != len(raw_groups):
        raise WorkspaceIndexError(
            "comparison bundle scope_group_count does not match groups"
        )

    scopes: list[dict[str, Any]] = []
    seen: set[str] = set()
    comparable_count = 0
    singleton_count = 0
    for index, raw_group in enumerate(raw_groups):
        group = _object(raw_group, f"comparison bundle group {index}")
        scope = _string(group.get("scope"), f"group {index}.scope")
        if SCOPE_PATTERN.fullmatch(scope) is None:
            raise WorkspaceIndexError(f"unsafe comparison scope slug: {scope!r}")
        if scope in seen:
            raise WorkspaceIndexError(f"duplicate comparison scope: {scope}")
        seen.add(scope)
        status = _string(group.get("status"), f"group {scope}.status")
        if status not in {"comparable", "singleton"}:
            raise WorkspaceIndexError(
                f"unsupported comparison scope status: {status!r}"
            )
        codes = _configuration_codes(
            group.get("configuration_codes"),
            f"group {scope}.configuration_codes",
        )
        pair_count = _integer(
            group.get("pair_count"),
            f"group {scope}.pair_count",
        )
        difference_count = _integer(
            group.get("total_differences"),
            f"group {scope}.total_differences",
        )
        raw_files = group.get("files")
        files = _object(raw_files, f"group {scope}.files")
        links: list[dict[str, str]] = []
        if status == "singleton":
            singleton_count += 1
            if len(codes) != 1 or pair_count != 0 or difference_count != 0:
                raise WorkspaceIndexError(
                    f"singleton scope has invalid counts: {scope}"
                )
            if files:
                raise WorkspaceIndexError(
                    f"singleton scope must not contain report files: {scope}"
                )
        else:
            comparable_count += 1
            if len(codes) < 2 or pair_count < 1:
                raise WorkspaceIndexError(
                    f"comparable scope has invalid configuration or pair count: {scope}"
                )
            unknown_keys = sorted(set(files) - set(REPORT_ORDER))
            if unknown_keys:
                raise WorkspaceIndexError(
                    f"comparison scope contains unknown report types: {unknown_keys}"
                )
            if not files:
                raise WorkspaceIndexError(
                    f"comparable scope has no report files: {scope}"
                )
            for report_type in REPORT_ORDER:
                if report_type not in files:
                    continue
                relative_name = _file_record_path(
                    files[report_type],
                    f"group {scope}.files.{report_type}",
                )
                workspace_name = _verified_bundle_path(
                    workspace_root,
                    release_members,
                    relative_name,
                    label=f"{scope} {report_type} report",
                )
                links.append(
                    {
                        "label": REPORT_LABELS[report_type],
                        "path": workspace_name,
                    }
                )
        scopes.append(
            {
                "scope": scope,
                "status": status,
                "configuration_codes": codes,
                "pair_count": pair_count,
                "difference_count": difference_count,
                "artifact_count": len(files),
                "links": tuple(links),
            }
        )

    if comparable_count != _integer(
        bundle.get("comparable_scope_count"),
        "comparison bundle comparable_scope_count",
    ):
        raise WorkspaceIndexError(
            "comparison bundle comparable_scope_count does not match groups"
        )
    if singleton_count != _integer(
        bundle.get("singleton_scope_count"),
        "comparison bundle singleton_scope_count",
    ):
        raise WorkspaceIndexError(
            "comparison bundle singleton_scope_count does not match groups"
        )
    if bundle.get("cross_scope_pairs_generated") is not False:
        raise WorkspaceIndexError(
            "comparison bundle must explicitly disable cross-scope pairs"
        )
    return tuple(scopes)


def _primary_links(
    workspace_root: Path,
    release_members: set[str],
    bundle: Mapping[str, Any],
) -> tuple[dict[str, str], ...]:
    workbook_name = _file_record_path(
        bundle.get("workbook"),
        "comparison bundle workbook",
    )
    links = (
        {
            "title": "Configuration shortlist",
            "description": "Browse and filter all released active configurations.",
            "path": _verified_content_path(
                workspace_root,
                release_members,
                "shortlist/configuration-shortlist.html",
                label="shortlist HTML",
            ),
        },
        {
            "title": "Comparison workbook",
            "description": "Open the six-sheet XLSX overview of all release scopes.",
            "path": _verified_bundle_path(
                workspace_root,
                release_members,
                workbook_name,
                label="comparison workbook",
            ),
        },
        {
            "title": "Comparison bundle manifest",
            "description": "Inspect scope groups, counts, artifact paths and hashes.",
            "path": _verified_content_path(
                workspace_root,
                release_members,
                BUNDLE_MANIFEST_MEMBER,
                label="comparison bundle manifest",
            ),
        },
        {
            "title": "Release notes",
            "description": "Read the immutable product inventory and provenance summary.",
            "path": _verified_content_path(
                workspace_root,
                release_members,
                "RELEASE_NOTES.md",
                label="release notes",
            ),
        },
    )
    return links


def _asset_links(
    workspace_root: Path,
    release_manifest: Mapping[str, Any],
) -> tuple[dict[str, str], ...]:
    archive = _object(release_manifest.get("archive"), "release manifest archive")
    archive_name = _string(archive.get("path"), "release manifest archive.path")
    return (
        {
            "label": "Original release archive",
            "path": _asset_path(
                workspace_root,
                archive_name,
                label="original release archive",
            ),
        },
        {
            "label": "External release manifest",
            "path": _asset_path(
                workspace_root,
                MANIFEST_NAME,
                label="external release manifest",
            ),
        },
        {
            "label": "SHA256SUMS",
            "path": _asset_path(
                workspace_root,
                CHECKSUMS_NAME,
                label="SHA256SUMS",
            ),
        },
    )


def _render_primary_cards(links: Sequence[Mapping[str, str]]) -> str:
    cards = []
    for link in links:
        cards.append(
            "".join(
                [
                    '<a class="product-card" href="',
                    _href(link["path"]),
                    '"><strong>',
                    escape(link["title"]),
                    '</strong><span>',
                    escape(link["description"]),
                    "</span></a>",
                ]
            )
        )
    return "\n".join(cards)


def _render_scope(scope: Mapping[str, Any]) -> str:
    status = str(scope["status"])
    status_label = "Comparable" if status == "comparable" else "Singleton"
    codes = "".join(
        f"<li><code>{escape(code)}</code></li>"
        for code in scope["configuration_codes"]
    )
    raw_links = scope["links"]
    if raw_links:
        links = "".join(
            '<a href="' + _href(link["path"]) + '">' + escape(link["label"]) + "</a>"
            for link in raw_links
        )
    else:
        links = '<span class="muted">No pair report for a singleton scope.</span>'
    return "".join(
        [
            '<article class="scope-card" id="scope-',
            escape(str(scope["scope"]), quote=True),
            '"><div class="scope-heading"><div><h3>',
            escape(str(scope["scope"])),
            '</h3><span class="badge ',
            escape(status),
            '">',
            status_label,
            '</span></div><dl><div><dt>Configurations</dt><dd>',
            str(len(scope["configuration_codes"])),
            "</dd></div><div><dt>Pairs</dt><dd>",
            str(scope["pair_count"]),
            "</dd></div><div><dt>Differences</dt><dd>",
            str(scope["difference_count"]),
            "</dd></div><div><dt>Artifacts</dt><dd>",
            str(scope["artifact_count"]),
            "</dd></div></dl></div><ul class=\"codes\">",
            codes,
            '</ul><nav class="scope-links">',
            links,
            "</nav></article>",
        ]
    )


def render_workspace_index(
    workspace_root: Path,
    release_manifest: Mapping[str, Any],
    release_metadata: Mapping[str, Any],
) -> str:
    release_members = _release_members(release_manifest)
    bundle_path = _workspace_file(
        workspace_root,
        f"contents/{BUNDLE_MANIFEST_MEMBER}",
        label="comparison bundle manifest",
    )
    bundle = _read_object(bundle_path, "comparison bundle manifest")
    if bundle.get("version") != 1:
        raise WorkspaceIndexError("unsupported comparison bundle manifest version")

    release_configuration_count = _integer(
        release_manifest.get("selected_configuration_count"),
        "release selected_configuration_count",
        minimum=1,
    )
    bundle_configuration_count = _integer(
        bundle.get("selected_configuration_count"),
        "comparison bundle selected_configuration_count",
        minimum=1,
    )
    if release_configuration_count != bundle_configuration_count:
        raise WorkspaceIndexError(
            "release and comparison bundle configuration counts do not match"
        )
    release_scope_count = _integer(
        release_manifest.get("scope_group_count"),
        "release scope_group_count",
        minimum=1,
    )
    bundle_scope_count = _integer(
        bundle.get("scope_group_count"),
        "comparison bundle scope_group_count",
        minimum=1,
    )
    if release_scope_count != bundle_scope_count:
        raise WorkspaceIndexError(
            "release and comparison bundle scope counts do not match"
        )

    scopes = _scope_records(
        workspace_root,
        release_members,
        bundle,
    )
    selected_codes = _configuration_codes(
        bundle.get("selected_configuration_codes"),
        "comparison bundle selected_configuration_codes",
    )
    if len(selected_codes) != bundle_configuration_count:
        raise WorkspaceIndexError(
            "comparison bundle selected configuration count does not match codes"
        )
    grouped_codes = tuple(
        code
        for scope in scopes
        for code in scope["configuration_codes"]
    )
    if len(grouped_codes) != len(set(grouped_codes)):
        raise WorkspaceIndexError(
            "comparison bundle configuration codes overlap between scopes"
        )
    if set(grouped_codes) != set(selected_codes):
        raise WorkspaceIndexError(
            "comparison bundle selected configuration codes do not match groups"
        )
    primary_links = _primary_links(
        workspace_root,
        release_members,
        bundle,
    )
    asset_links = _asset_links(workspace_root, release_manifest)

    version = _string(
        release_manifest.get("release_version"),
        "release version",
    )
    tag = _string(release_manifest.get("release_tag"), "release tag")
    commit = _string(
        release_manifest.get("repository_commit"),
        "repository commit",
    )
    snapshot_date = _string(
        release_manifest.get("snapshot_date"),
        "snapshot date",
    )
    if release_metadata.get("release_tag") != tag:
        raise WorkspaceIndexError(
            "downloaded release metadata tag does not match manifest"
        )
    if release_metadata.get("repository_commit") != commit:
        raise WorkspaceIndexError(
            "downloaded release metadata commit does not match manifest"
        )
    release_url = _external_href(release_metadata.get("release_url"))

    scope_html = "\n".join(_render_scope(scope) for scope in scopes)
    asset_html = "\n".join(
        '<li><a href="'
        + _href(link["path"])
        + '">'
        + escape(link["label"])
        + "</a></li>"
        for link in asset_links
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dacia Knowledge Base data products v{escape(version)}</title>
<style>
:root{{--bg:#f4f5f2;--surface:#fff;--ink:#182018;--muted:#5c675d;--line:#d8ddd6;--accent:#156b45;--accent-soft:#e8f3ed;--mono:#eef0ec}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}main{{width:min(1180px,calc(100% - 32px));margin:32px auto 64px}}header{{padding:32px;border:1px solid var(--line);border-radius:20px;background:var(--surface)}}h1,h2,h3,p{{margin-top:0}}h1{{font-size:clamp(2rem,5vw,3.7rem);line-height:1.05;max-width:16ch}}h2{{margin-top:40px;font-size:1.65rem}}a{{color:var(--accent)}}.eyebrow{{color:var(--accent);font-weight:700;letter-spacing:.08em;text-transform:uppercase}}.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:24px}}.summary div,.scope-heading dl div{{padding:12px;border-radius:12px;background:var(--bg)}}dt{{color:var(--muted);font-size:.8rem;text-transform:uppercase}}dd{{margin:2px 0 0;font-weight:700;overflow-wrap:anywhere}}.products{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}.product-card{{display:flex;flex-direction:column;gap:8px;min-height:150px;padding:22px;border:1px solid var(--line);border-radius:16px;background:var(--surface);text-decoration:none}}.product-card:hover{{border-color:var(--accent)}}.product-card strong{{font-size:1.15rem}}.product-card span,.muted{{color:var(--muted)}}.scope-list{{display:grid;gap:16px}}.scope-card{{padding:22px;border:1px solid var(--line);border-radius:16px;background:var(--surface)}}.scope-heading{{display:grid;grid-template-columns:minmax(220px,1fr) minmax(360px,2fr);gap:20px}}.scope-heading dl{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0}}.badge{{display:inline-block;padding:3px 9px;border-radius:999px;font-size:.8rem;font-weight:700}}.badge.comparable{{color:var(--accent);background:var(--accent-soft)}}.badge.singleton{{color:#765c1d;background:#f7efcf}}.codes{{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}}code{{padding:3px 7px;border-radius:6px;background:var(--mono);overflow-wrap:anywhere}}.scope-links{{display:flex;flex-wrap:wrap;gap:12px}}.scope-links a{{padding:8px 11px;border:1px solid var(--line);border-radius:9px;text-decoration:none}}.provenance{{padding:22px;border:1px solid var(--line);border-radius:16px;background:var(--surface)}}.provenance ul{{margin-bottom:0}}@media(max-width:760px){{.scope-heading{{grid-template-columns:1fr}}.scope-heading dl{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
<main>
<header>
<p class="eyebrow">Verified offline workspace</p>
<h1>Dacia Knowledge Base data products v{escape(version)}</h1>
<p>This landing page links only files validated from the immutable public release.</p>
<div class="summary">
<div><dt>Tag</dt><dd>{escape(tag)}</dd></div>
<div><dt>Commit</dt><dd><code>{escape(commit)}</code></dd></div>
<div><dt>Snapshot</dt><dd>{escape(snapshot_date)}</dd></div>
<div><dt>Configurations</dt><dd>{release_configuration_count}</dd></div>
<div><dt>Scopes</dt><dd>{release_scope_count}</dd></div>
<div><dt>Public release</dt><dd><a href="{release_url}">GitHub Release</a></dd></div>
</div>
</header>
<section>
<h2>Start here</h2>
<div class="products">
{_render_primary_cards(primary_links)}
</div>
</section>
<section>
<h2>Comparison scopes</h2>
<div class="scope-list">
{scope_html}
</div>
</section>
<section class="provenance">
<h2>Release provenance</h2>
<p>The original downloaded assets remain available for independent verification.</p>
<ul>
{asset_html}
</ul>
</section>
</main>
</body>
</html>
"""
    return html


def write_workspace_index(
    workspace_root: Path,
    release_manifest: Mapping[str, Any],
    release_metadata: Mapping[str, Any],
) -> Path:
    content = render_workspace_index(
        workspace_root,
        release_manifest,
        release_metadata,
    )
    output = workspace_root / INDEX_NAME
    output.write_text(content, encoding="utf-8", newline="")
    return output
