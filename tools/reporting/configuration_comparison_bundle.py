from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import configuration_comparison as comparison
from reporting.configuration_comparison_workbook import write_bundle_workbook
from reporting.deterministic_xlsx_model import WorkbookError

BUNDLE_VERSION = 1
CURRENT_SCOPE_PREFIXES = ("sandero_", "duster_", "jogger_")


class BundleError(ValueError):
    """Raised when a comparison bundle cannot be created safely."""


@dataclass(frozen=True)
class ScopeDefinition:
    name: str
    slug: str
    completeness_path: Path
    evidence_path: Path
    configuration_codes: tuple[str, ...]
    completeness_spec: Mapping[str, Any]
    evidence_spec: Mapping[str, Any]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BundleError(f"cannot read {label} {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BundleError(f"invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BundleError(f"{label} must contain a JSON object: {path}")
    return value


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def _json_text(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _scope_paths(reporting: Path) -> list[Path]:
    return sorted(
        path
        for path in reporting.glob("*_completeness.json")
        if path.name.startswith(CURRENT_SCOPE_PREFIXES)
    )


def _evidence_path(spec_path: Path) -> Path:
    base = spec_path.name.replace("_completeness.json", "_gap_evidence")
    candidates = (
        spec_path.with_name(f"{base}.json"),
        spec_path.with_name(f"{base}.spec"),
    )
    matches = [path for path in candidates if path.is_file()]
    if len(matches) != 1:
        names = ", ".join(str(path) for path in candidates)
        raise BundleError(
            "expected exactly one evidence specification for "
            f"{spec_path.name}; checked {names}"
        )
    return matches[0]


def discover_scopes(repository: Path) -> tuple[ScopeDefinition, ...]:
    reporting = repository / "data" / "reporting"
    definitions: list[ScopeDefinition] = []
    mapping: dict[str, list[str]] = {}
    for completeness_path in _scope_paths(reporting):
        completeness = _read_json(
            completeness_path,
            "completeness specification",
        )
        raw_configurations = completeness.get("configurations")
        if not isinstance(raw_configurations, list) or not raw_configurations:
            raise BundleError(
                "completeness specification has no configurations: "
                f"{completeness_path}"
            )
        codes: list[str] = []
        for item in raw_configurations:
            if not isinstance(item, dict):
                raise BundleError(
                    "configuration entries must be JSON objects: "
                    f"{completeness_path}"
                )
            code = item.get("configuration_code")
            if not isinstance(code, str) or not code:
                raise BundleError(
                    "configuration entry has no code: "
                    f"{completeness_path}"
                )
            codes.append(code)
            mapping.setdefault(code, []).append(completeness_path.name)
        if len(codes) != len(set(codes)):
            raise BundleError(
                "duplicate configuration code in completeness specification: "
                f"{completeness_path}"
            )
        evidence_path = _evidence_path(completeness_path)
        evidence = _read_json(evidence_path, "evidence specification")
        decisions = evidence.get("decisions", [])
        if not isinstance(decisions, list):
            raise BundleError(
                f"evidence decisions must be a list: {evidence_path}"
            )
        definitions.append(
            ScopeDefinition(
                name=completeness_path.name,
                slug=completeness_path.name.removesuffix(
                    "_completeness.json"
                ),
                completeness_path=completeness_path,
                evidence_path=evidence_path,
                configuration_codes=tuple(codes),
                completeness_spec=completeness,
                evidence_spec=evidence,
            )
        )

    active_rows = comparison.read_csv(
        repository / "data" / "master" / "configurations.csv"
    )
    active_codes = {
        row["code"]
        for row in active_rows
        if row.get("status") == "active"
    }
    if not active_codes:
        raise BundleError("no active configurations found")
    incorrectly_mapped = {
        code: scopes
        for code, scopes in sorted(mapping.items())
        if len(scopes) != 1
    }
    missing = sorted(active_codes - set(mapping))
    extra = sorted(set(mapping) - active_codes)
    if incorrectly_mapped or missing or extra:
        raise BundleError(
            "current comparison scope mapping is not one-to-one; "
            f"overlaps={incorrectly_mapped}, missing={missing}, extra={extra}"
        )
    return tuple(definitions)


def _shortlist_codes(path: Path) -> tuple[list[str], dict[str, Any]]:
    value = _read_json(path, "shortlist report")
    results = value.get("results")
    if not isinstance(results, list):
        raise BundleError(
            f"shortlist report results must be a list: {path}"
        )
    codes: list[str] = []
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            raise BundleError(
                f"shortlist result {index} must be an object: {path}"
            )
        code = item.get("configuration_code")
        if not isinstance(code, str) or not code:
            raise BundleError(
                "shortlist result has no configuration_code at index "
                f"{index}: {path}"
            )
        codes.append(code)
    source = {
        "path": str(path),
        "as_of": value.get("as_of"),
        "configuration_count": len(codes),
    }
    return codes, source


def collect_selection(
    direct_codes: Sequence[str],
    shortlist_paths: Sequence[Path],
) -> tuple[tuple[str, ...], dict[str, Any]]:
    requested: list[str] = []
    direct = [code.strip() for code in direct_codes if code.strip()]
    requested.extend(direct)
    shortlist_sources: list[dict[str, Any]] = []
    for path in shortlist_paths:
        codes, source = _shortlist_codes(path)
        requested.extend(codes)
        shortlist_sources.append(source)
    selected = tuple(sorted(set(requested)))
    if not selected:
        raise BundleError(
            "select at least one configuration with --configuration-code "
            "or --shortlist-json"
        )
    return selected, {
        "direct_configuration_codes": direct,
        "shortlist_reports": shortlist_sources,
        "requested_configuration_count": len(requested),
        "deduplicated_configuration_count": len(selected),
    }


def _subset_completeness(
    scope: ScopeDefinition,
    selected: set[str],
) -> dict[str, Any]:
    subset = json.loads(json.dumps(scope.completeness_spec))
    subset["configurations"] = [
        item
        for item in subset["configurations"]
        if item["configuration_code"] in selected
    ]
    return subset


def _subset_evidence(
    scope: ScopeDefinition,
    selected: set[str],
) -> dict[str, Any]:
    subset = json.loads(json.dumps(scope.evidence_spec))
    subset["decisions"] = [
        item
        for item in subset.get("decisions", [])
        if item.get("configuration_code") in selected
    ]
    return subset


def _group_selection(
    scopes: Sequence[ScopeDefinition],
    selected: Sequence[str],
) -> tuple[list[tuple[ScopeDefinition, tuple[str, ...]]], list[str]]:
    code_to_scope: dict[str, ScopeDefinition] = {}
    for scope in scopes:
        for code in scope.configuration_codes:
            code_to_scope[code] = scope
    unknown = sorted(set(selected) - set(code_to_scope))
    if unknown:
        raise BundleError(
            "unknown or unmapped configuration code(s): "
            + ", ".join(unknown)
        )
    selected_set = set(selected)
    groups = [
        (
            scope,
            tuple(
                code
                for code in scope.configuration_codes
                if code in selected_set
            ),
        )
        for scope in scopes
    ]
    return [item for item in groups if item[1]], unknown


def _render_group(
    repository: Path,
    build_root: Path,
    scope: ScopeDefinition,
    codes: tuple[str, ...],
) -> dict[str, Any]:
    selected = set(codes)
    specs = build_root / ".specs"
    specs.mkdir(parents=True, exist_ok=True)
    completeness_path = specs / scope.completeness_path.name
    evidence_path = specs / scope.evidence_path.name
    _write_text(
        completeness_path,
        _json_text(_subset_completeness(scope, selected)),
    )
    _write_text(
        evidence_path,
        _json_text(_subset_evidence(scope, selected)),
    )
    try:
        report = comparison.collect_report(
            repository,
            completeness_path,
            evidence_path,
        )
    except comparison.ComparisonError as exc:
        raise BundleError(
            f"comparison failed for scope {scope.slug}: {exc}"
        ) from exc

    base = build_root / scope.slug
    paths = {
        "json": base.with_suffix(".comparison.json"),
        "markdown": base.with_suffix(".comparison.md"),
        "csv": base.with_suffix(".differences.csv"),
        "html": base.with_suffix(".comparison.html"),
    }
    _write_text(paths["json"], comparison.render_json(report))
    _write_text(paths["markdown"], comparison.render_markdown(report))
    _write_text(paths["csv"], comparison.render_difference_csv(report))
    _write_text(paths["html"], comparison.render_html(report))
    return {
        "scope": scope.slug,
        "status": "comparable",
        "source_completeness_spec": scope.completeness_path.name,
        "source_evidence_spec": scope.evidence_path.name,
        "configuration_codes": list(codes),
        "pair_count": report["scope"]["pair_count"],
        "total_differences": report["summary"]["total_differences"],
        "evidence_summary": report["evidence_summary"],
        "report_as_of": report["as_of"],
        "files": {
            key: _file_record(path, build_root)
            for key, path in paths.items()
        },
    }


def _prepare_output_directory(output_directory: Path) -> Path:
    parent = output_directory.parent
    parent.mkdir(parents=True, exist_ok=True)
    if output_directory.exists():
        if not output_directory.is_dir():
            raise BundleError(
                f"output path is not a directory: {output_directory}"
            )
        if any(output_directory.iterdir()):
            raise BundleError(
                "output directory must not exist or must be empty: "
                f"{output_directory}"
            )
    return Path(
        tempfile.mkdtemp(
            prefix=f".{output_directory.name}.build-",
            dir=parent,
        )
    )


def create_bundle(
    repository: Path,
    output_directory: Path,
    direct_codes: Sequence[str] = (),
    shortlist_paths: Sequence[Path] = (),
) -> dict[str, Any]:
    scopes = discover_scopes(repository)
    selected, selection_sources = collect_selection(
        direct_codes,
        shortlist_paths,
    )
    groups, _ = _group_selection(scopes, selected)
    build_root = _prepare_output_directory(output_directory)
    try:
        group_records: list[dict[str, Any]] = []
        for scope, codes in groups:
            if len(codes) < 2:
                group_records.append(
                    {
                        "scope": scope.slug,
                        "status": "singleton",
                        "source_completeness_spec": (
                            scope.completeness_path.name
                        ),
                        "source_evidence_spec": scope.evidence_path.name,
                        "configuration_codes": list(codes),
                        "pair_count": 0,
                        "total_differences": 0,
                        "files": {},
                    }
                )
                continue
            group_records.append(
                _render_group(
                    repository,
                    build_root,
                    scope,
                    codes,
                )
            )

        manifest = {
            "version": BUNDLE_VERSION,
            "selection_sources": selection_sources,
            "selected_configuration_codes": list(selected),
            "selected_configuration_count": len(selected),
            "scope_group_count": len(group_records),
            "comparable_scope_count": sum(
                item["status"] == "comparable"
                for item in group_records
            ),
            "singleton_scope_count": sum(
                item["status"] == "singleton"
                for item in group_records
            ),
            "cross_scope_pairs_generated": False,
            "groups": group_records,
        }
        try:
            workbook_path = write_bundle_workbook(
                repository,
                build_root,
                manifest,
            )
        except WorkbookError as exc:
            raise BundleError(f"workbook generation failed: {exc}") from exc
        manifest["workbook"] = _file_record(workbook_path, build_root)
        _write_text(
            build_root / "comparison-bundle-manifest.json",
            _json_text(manifest),
        )
        shutil.rmtree(build_root / ".specs", ignore_errors=True)
        if output_directory.exists():
            output_directory.rmdir()
        build_root.replace(output_directory)
        return manifest
    except Exception:
        shutil.rmtree(build_root, ignore_errors=True)
        raise


def manifest_path(output_directory: Path) -> Path:
    return output_directory / "comparison-bundle-manifest.json"
