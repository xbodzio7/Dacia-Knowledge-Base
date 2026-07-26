#!/usr/bin/env python3
"""Persist compact diagnostics for evidence decisions missing reviewed pages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/reporting/configuration_gap_evidence.json"
OUTPUT = ROOT / ".github/gap-evidence-reviewed-pages-diagnostics.json"


def main() -> int:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    invalid = [
        {
            key: decision.get(key)
            for key in (
                "triage_key",
                "domain",
                "source_code",
                "configuration_code",
                "category",
                "attribute_code",
                "file_path",
                "classification",
                "reviewed_pages",
                "reason_code",
            )
        }
        for decision in payload.get("decisions", [])
        if decision.get("classification") == "not_stated"
        and not decision.get("reviewed_pages")
    ]
    OUTPUT.write_text(
        json.dumps({"count": len(invalid), "decisions": invalid}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"PASS: persisted {len(invalid)} invalid evidence decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
