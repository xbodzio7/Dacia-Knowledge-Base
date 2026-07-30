#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review_bundle_residual_gap_051"
PRIORITIZATION = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
RECONCILIATION = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
PDF = ROOT / "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
PACKAGE_ID = "residual_gap_051"
EXPECTED_SOURCE = "src_pl_sandero_brochure_20260202"
EXPECTED_PAGE = 19
EXPECTED_COUNT = 40
EXPECTED_SHA = ""


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return payload


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    prioritization = load_json(PRIORITIZATION)
    packages = prioritization.get("packages", [])
    package = next((item for item in packages if item.get("package_id") == PACKAGE_ID), None)
    if package is None:
        raise SystemExit(f"package not found: {PACKAGE_ID}")
    if package.get("source_code") != EXPECTED_SOURCE:
        raise SystemExit(f"unexpected source: {package.get('source_code')}")
    if int(package.get("page", -1)) != EXPECTED_PAGE:
        raise SystemExit(f"unexpected page: {package.get('page')}")
    candidate_ids = list(package.get("candidate_ids", []))
    if len(candidate_ids) != EXPECTED_COUNT:
        raise SystemExit(f"expected {EXPECTED_COUNT} candidate IDs, found {len(candidate_ids)}")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise SystemExit("duplicate candidate IDs in package")

    reconciliation = load_json(RECONCILIATION)
    candidates = reconciliation.get("candidates", [])
    by_id = {item.get("candidate_id"): item for item in candidates}
    missing = [identifier for identifier in candidate_ids if identifier not in by_id]
    if missing:
        raise SystemExit(f"candidate IDs missing from reconciliation: {missing[:3]}")
    selected = [by_id[identifier] for identifier in candidate_ids]
    if any(item.get("source_code") != EXPECTED_SOURCE for item in selected):
        raise SystemExit("selected candidate source differs")
    if any(int(item.get("page", -1)) != EXPECTED_PAGE for item in selected):
        raise SystemExit("selected candidate page differs")
    if any(item.get("coverage_status") != "unresolved" for item in selected):
        raise SystemExit("selected candidate coverage status differs")

    sha256 = hashlib.sha256(PDF.read_bytes()).hexdigest()
    metadata = {
        "version": 1,
        "package": package,
        "source": {
            "file_path": str(PDF.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256,
            "page": EXPECTED_PAGE,
        },
        "candidate_count": len(selected),
        "candidate_ids": candidate_ids,
    }
    (OUT / "package.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "candidates.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# {PACKAGE_ID}",
        "",
        f"Source: `{EXPECTED_SOURCE}`",
        f"Page: {EXPECTED_PAGE}",
        f"Candidates: {len(selected)}",
        f"PDF SHA-256: `{sha256}`",
        "",
        "| # | Candidate ID | Kind | Lines | Exact text |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(selected, 1):
        text = str(item.get("exact_text", "")).replace("|", "\\|").replace("\n", " ")
        line_span = f"{item.get('line_start', '')}-{item.get('line_end', '')}"
        lines.append(
            f"| {index} | `{item.get('candidate_id')}` | `{item.get('candidate_kind')}` | {line_span} | {text} |"
        )
    (OUT / "candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    subprocess.run(
        [
            "pdftotext",
            "-f",
            str(EXPECTED_PAGE),
            "-l",
            str(EXPECTED_PAGE),
            "-layout",
            str(PDF),
            str(OUT / "sandero_page19.txt"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            str(EXPECTED_PAGE),
            "-l",
            str(EXPECTED_PAGE),
            "-singlefile",
            "-png",
            "-r",
            "200",
            str(PDF),
            str(OUT / "sandero_page19"),
        ],
        check=True,
    )
    shutil.copy2(PDF, OUT / PDF.name)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
