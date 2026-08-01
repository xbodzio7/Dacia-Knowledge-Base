#!/usr/bin/env python3
"""Print the exact automatic Stepway Expression source and canonical missing slots."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PDF" / "Cenniki" / "NOWE SANDERO STEPWAY expression stepway Eco-G 120 auto f.pdf"
SOURCE_CODE = "src_pl_sandero_stepway_expression_ecog120_at_20260626"
SOURCE_SHA256 = "385409e33a0932e48cbd901b5805f873831ec005c6451cd6ed1623a06fa15667"
CONFIGURATION = "sandero_stepway_iii_expression_ecog120_automatic"
ANALYSIS = ROOT / "data" / "reporting" / "existing_configuration_missing_data_analysis.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    actual_sha = sha256(SOURCE)
    if actual_sha != SOURCE_SHA256:
        raise SystemExit(f"source SHA mismatch: {actual_sha}")

    payload = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    configurations = [
        item
        for item in payload["configurations"]
        if item["configuration_code"] == CONFIGURATION
        and item["source_code"] == SOURCE_CODE
    ]
    candidates = [
        item
        for item in payload["ranked_candidates"]
        if item["source_code"] == SOURCE_CODE
    ]
    print("SOURCE_SHA256", actual_sha)
    print("CONFIGURATION_GAPS")
    print(json.dumps(configurations, ensure_ascii=False, indent=2))
    print("CANDIDATE")
    print(json.dumps(candidates, ensure_ascii=False, indent=2))

    result = subprocess.run(
        ["pdftotext", "-layout", str(SOURCE), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    for page_number, page in enumerate(result.stdout.split("\f"), start=1):
        if not page.strip():
            continue
        print(f"===== SOURCE PAGE {page_number} =====")
        print(page.rstrip())


if __name__ == "__main__":
    main()
