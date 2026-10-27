#!/usr/bin/env python3
"""Build a deterministic visual-review bundle for one residual PDF package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIORITIZATION = (
    ROOT
    / "data"
    / "reporting"
    / "verified_pdf_candidate_residual_gap_prioritization.json"
)
DEFAULT_SOURCE_RECEIPT = (
    ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"
)
DEFAULT_STATE = ROOT / "project" / "state.json"
BUNDLE_FILES = (
    "review-package.json",
    "candidates.json",
    "candidates.md",
    "source-page.txt",
    "source-page.png",
)


class ResidualReviewBundleError(RuntimeError):
    """Raised when package metadata, source evidence or rendering differs."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ResidualReviewBundleError(message)


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ResidualReviewBundleError(f"cannot read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ResidualReviewBundleError(f"invalid {label} JSON: {path}") from exc
    ensure(isinstance(payload, dict), f"{label} root must be an object")
    return payload


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_by_id(prioritization: Mapping[str, Any], package_id: str) -> dict[str, Any]:
    packages = prioritization.get("packages")
    ensure(isinstance(packages, list), "prioritization packages are missing")
    matches = [
        item
        for item in packages
        if isinstance(item, dict) and item.get("package_id") == package_id
    ]
    ensure(len(matches) == 1, f"package must occur exactly once: {package_id}")
    return dict(matches[0])


def source_by_code(receipt: Mapping[str, Any], source_code: str) -> dict[str, Any]:
    sources = receipt.get("sources")
    ensure(isinstance(sources, list), "source receipt sources are missing")
    matches = [
        item
        for item in sources
        if isinstance(item, dict) and item.get("source_code") == source_code
    ]
    ensure(len(matches) == 1, f"source must occur exactly once: {source_code}")
    return dict(matches[0])


def default_package_id(state: Mapping[str, Any]) -> str:
    for key in ("current_package", "next_package"):
        package = state.get(key)
        if not isinstance(package, dict):
            continue
        if package.get("kind") != "residual_review":
            continue
        if key == "current_package" and package.get("status") == "complete":
            continue
        package_id = package.get("package_id")
        if isinstance(package_id, str) and package_id.strip():
            return package_id
    package = state.get("next_package")
    if isinstance(package, dict) and package.get("kind") == "residual_review":
        package_id = package.get("package_id")
        if isinstance(package_id, str) and package_id.strip():
            return package_id
    raise ResidualReviewBundleError(
        "canonical state does not declare an active or next residual review package"
    )


def resolve_source_path(repository: Path, source: Mapping[str, Any]) -> Path:
    relative = source.get("file_path")
    ensure(isinstance(relative, str) and relative.strip(), "source file_path is missing")
    path = repository / relative
    ensure(path.is_file(), f"registered source file is missing: {relative}")
    expected_bytes = source.get("bytes")
    ensure(
        isinstance(expected_bytes, int) and expected_bytes > 0,
        "source byte count is invalid",
    )
    ensure(path.stat().st_size == expected_bytes, f"source byte count differs: {relative}")
    expected_sha = source.get("sha256")
    ensure(isinstance(expected_sha, str), "source SHA-256 is missing")
    actual_sha = file_sha256(path)
    ensure(actual_sha == expected_sha, f"source SHA-256 differs: {relative}")
    return path


def _decode_output(data: bytes) -> str:
    for encoding in ("utf-8", "cp1250", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_page_text(source_path: Path, page: int) -> str:
    executable = shutil.which("pdftotext")
    ensure(executable is not None, "pdftotext executable is unavailable")
    completed = subprocess.run(
        [
            executable,
            "-f",
            str(page),
            "-l",
            str(page),
            "-layout",
            "-enc",
            "UTF-8",
            str(source_path),
            "-",
        ],
        check=False,
        capture_output=True,
    )
    ensure(completed.returncode == 0, "PDF page text extraction failed")
    return _decode_output(completed.stdout).replace("\r\n", "\n").replace("\r", "\n")


def render_page_png(source_path: Path, page: int, target: Path) -> None:
    executable = shutil.which("pdftoppm")
    ensure(executable is not None, "pdftoppm executable is unavailable")
    prefix = target.with_suffix("")
    completed = subprocess.run(
        [
            executable,
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-png",
            "-r",
            "200",
            str(source_path),
            str(prefix),
        ],
        check=False,
        capture_output=True,
    )
    detail = _decode_output(completed.stderr + completed.stdout).strip()
    ensure(completed.returncode == 0, f"PDF page rendering failed: {detail}")
    ensure(target.is_file() and target.stat().st_size > 0, "rendered page PNG is missing")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def render_candidates_markdown(package: Mapping[str, Any], source: Mapping[str, Any]) -> str:
    candidates = package["candidates"]
    lines = [
        f"# Residual review bundle — {package['package_id']}",
        "",
        "This file reproduces the canonical candidate block without approving imports.",
        "",
        "## Scope",
        "",
        f"- source: `{package['source_code']}`;",
        f"- source file: `{source['file_path']}`;",
        f"- source SHA-256: `{source['sha256']}`;",
        f"- model: `{package['model_code']}`;",
        f"- domain: `{package['domain']}`;",
        f"- page: {package['page']};",
        f"- chunk: {package['chunk_index']} of {package['chunk_count']};",
        f"- candidates: {package['candidate_count']} of {package['group_candidate_count']};",
        f"- attached evidence signatures: {package['evidence_signature_count']};",
        f"- attached evidence records: {package['evidence_record_count']}.",
        "",
        "## Candidates",
        "",
        "| # | Lines | Candidate | Kind | Exact text |",
        "| ---: | ---: | --- | --- | --- |",
    ]
    for index, candidate in enumerate(candidates, start=1):
        start = candidate["line_start"]
        end = candidate["line_end"]
        line_range = str(start) if start == end else f"{start}-{end}"
        lines.append(
            "| "
            f"{index} | {line_range} | `{candidate['candidate_id']}` | "
            f"`{candidate['candidate_kind']}` | "
            f"{markdown_cell(candidate['exact_text'])} |"
        )
    return "\n".join(lines) + "\n"


def validate_package(package: Mapping[str, Any], source: Mapping[str, Any]) -> None:
    candidates = package.get("candidates")
    candidate_ids = package.get("candidate_ids")
    ensure(isinstance(candidates, list), "package candidates are missing")
    ensure(isinstance(candidate_ids, list), "package candidate_ids are missing")
    ensure(package.get("candidate_count") == len(candidates), "candidate count differs")
    ensure(candidate_ids == [item.get("candidate_id") for item in candidates], "candidate ID order differs")
    ensure(package.get("source_code") == source.get("source_code"), "package source differs")
    ensure(package.get("model_code") == source.get("model_code"), "package model differs")
    page = package.get("page")
    ensure(isinstance(page, int) and page > 0, "package page is invalid")
    pages = source.get("pages")
    ensure(isinstance(pages, int) and page <= pages, "package page exceeds source pages")
    ensure(package.get("evidence_signature_count") == 0, "bundle is limited to zero-signature residual packages")
    ensure(package.get("evidence_record_count") == 0, "bundle is limited to zero-record residual packages")


def bundle_manifest(directory: Path, package_id: str, source: Mapping[str, Any]) -> dict[str, Any]:
    files = []
    for name in BUNDLE_FILES:
        path = directory / name
        ensure(path.is_file(), f"bundle output is missing: {name}")
        files.append(
            {
                "path": name,
                "size_bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    return {
        "version": 1,
        "kind": "residual_review_bundle_manifest",
        "package_id": package_id,
        "source_code": source["source_code"],
        "source_sha256": source["sha256"],
        "files": files,
    }


def build_bundle(
    repository: Path,
    package_id: str,
    output_directory: Path,
    *,
    prioritization_path: Path = DEFAULT_PRIORITIZATION,
    source_receipt_path: Path = DEFAULT_SOURCE_RECEIPT,
    text_extractor: Callable[[Path, int], str] = extract_page_text,
    page_renderer: Callable[[Path, int, Path], None] = render_page_png,
) -> dict[str, Any]:
    prioritization = read_json(prioritization_path, "prioritization")
    receipt = read_json(source_receipt_path, "source receipt")
    package = package_by_id(prioritization, package_id)
    source_code = package.get("source_code")
    ensure(isinstance(source_code, str), "package source_code is missing")
    source = source_by_code(receipt, source_code)
    validate_package(package, source)
    source_path = resolve_source_path(repository, source)

    output_directory = output_directory.resolve()
    if output_directory.exists():
        ensure(output_directory.is_dir(), "output path is not a directory")
        ensure(not any(output_directory.iterdir()), "output directory must be empty")
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{output_directory.name}.tmp-",
            dir=output_directory.parent,
        )
    )
    try:
        package_payload = {
            key: value for key, value in package.items() if key != "candidates"
        }
        package_payload["source_receipt"] = {
            "file_path": source["file_path"],
            "sha256": source["sha256"],
            "bytes": source["bytes"],
            "pages": source["pages"],
            "document_date": source["document_date"],
        }
        write_json(temporary / "review-package.json", package_payload)
        write_json(
            temporary / "candidates.json",
            {
                "version": 1,
                "kind": "residual_review_candidate_block",
                "package_id": package_id,
                "candidate_count": len(package["candidates"]),
                "candidates": package["candidates"],
            },
        )
        (temporary / "candidates.md").write_text(
            render_candidates_markdown(package, source),
            encoding="utf-8",
            newline="\n",
        )
        page = int(package["page"])
        (temporary / "source-page.txt").write_text(
            text_extractor(source_path, page),
            encoding="utf-8",
            newline="\n",
        )
        page_renderer(source_path, page, temporary / "source-page.png")
        manifest = bundle_manifest(temporary, package_id, source)
        write_json(temporary / "bundle-manifest.json", manifest)

        if output_directory.exists():
            output_directory.rmdir()
        temporary.replace(output_directory)
        return manifest
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a source-verified candidate block, page text and page PNG "
            "for one canonical residual review package."
        )
    )
    parser.add_argument("--package-id")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--prioritization", type=Path, default=DEFAULT_PRIORITIZATION)
    parser.add_argument("--source-receipt", type=Path, default=DEFAULT_SOURCE_RECEIPT)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        package_id = arguments.package_id
        if package_id is None:
            package_id = default_package_id(read_json(arguments.state, "project state"))
        manifest = build_bundle(
            ROOT,
            package_id,
            arguments.output_directory,
            prioritization_path=arguments.prioritization,
            source_receipt_path=arguments.source_receipt,
        )
    except ResidualReviewBundleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Residual review bundle: PASS ({manifest['package_id']})")
    print(f"Output: {arguments.output_directory.resolve()}")
    for item in manifest["files"]:
        print(f"- {item['path']}: {item['size_bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
