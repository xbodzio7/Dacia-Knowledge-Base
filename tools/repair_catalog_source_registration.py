#!/usr/bin/env python3
"""Synchronize the catalogue source-slice hash before rerunning the importer."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CODE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"
SOURCE_FILE = ROOT / "project" / "sources" / "sandero_stepway_catalog_tce_slice_20260703.json"
SOURCES_CSV = ROOT / "data" / "master" / "sources.csv"


def main() -> int:
    digest = hashlib.sha256(SOURCE_FILE.read_bytes()).hexdigest()
    with SOURCES_CSV.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    matches = [row for row in rows if row.get("code") == SOURCE_CODE]
    if len(matches) != 1:
        raise SystemExit(f"expected one source row for {SOURCE_CODE}, found {len(matches)}")
    matches[0]["sha256"] = digest
    with SOURCES_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
