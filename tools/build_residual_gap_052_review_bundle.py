#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review_bundle_residual_gap_052"
PRIORITIZATION = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
RECONCILIATION = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
PDF = ROOT / "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
PACKAGE_ID = "residual_gap_052"
SOURCE_CODE = "src_pl_sandero_brochure_20260202"
PAGE = 19
COUNT = 25


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected object: {path}")
    return value


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    prioritization = load(PRIORITIZATION)
    package = next(item for item in prioritization["packages"] if item["package_id"] == PACKAGE_ID)
    assert package["source_code"] == SOURCE_CODE
    assert package["page"] == PAGE
    assert package["candidate_count"] == COUNT
    assert package["group_candidate_count"] == 65
    assert package["chunk_index"] == 2 and package["chunk_count"] == 2
    ids = package["candidate_ids"]
    assert len(ids) == len(set(ids)) == COUNT
    reconciliation = load(RECONCILIATION)
    by_id = {item["candidate_id"]: item for item in reconciliation["candidates"]}
    selected = [by_id[item] for item in ids]
    assert all(item["source_code"] == SOURCE_CODE for item in selected)
    assert all(item["page"] == PAGE for item in selected)
    assert all(item["coverage_status"] == "unresolved" for item in selected)
    sha = hashlib.sha256(PDF.read_bytes()).hexdigest()
    metadata = {
        "version": 1,
        "package": package,
        "source": {"file_path": str(PDF.relative_to(ROOT)).replace("\\", "/"), "sha256": sha, "page": PAGE},
        "candidate_count": COUNT,
        "candidate_ids": ids,
    }
    (OUT / "package.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "candidates.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# {PACKAGE_ID}", "", f"Source: `{SOURCE_CODE}`", f"Page: {PAGE}", f"Candidates: {COUNT}",
        f"PDF SHA-256: `{sha}`", "", "| # | Candidate ID | Kind | Lines | Exact text |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(selected, 1):
        text = str(item.get("exact_text", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {index} | `{item['candidate_id']}` | `{item['candidate_kind']}` | {item['line_start']}-{item['line_end']} | {text} |")
    (OUT / "candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    subprocess.run(["pdftotext", "-f", str(PAGE), "-l", str(PAGE), "-layout", str(PDF), str(OUT / "sandero_page19.txt")], check=True)
    subprocess.run(["pdftoppm", "-f", str(PAGE), "-l", str(PAGE), "-singlefile", "-png", "-r", "200", str(PDF), str(OUT / "sandero_page19")], check=True)
    shutil.copy2(PDF, OUT / PDF.name)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
