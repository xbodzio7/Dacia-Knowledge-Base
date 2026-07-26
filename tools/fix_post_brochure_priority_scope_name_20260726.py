#!/usr/bin/env python3
"""Normalize the Stepway automatic evidence filename in the priority verifier."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "review_post_brochure_priority_selection_20260726.py"
OLD = '"sandero_stepway_ecog120_automatic_completeness.json": "sandero_stepway_ecog120_automatic_gap_evidence.spec",'
NEW = '"sandero_stepway_ecog120_automatic_completeness.json": "sandero_stepway_ecog120_automatic_gap_evidence.json",'


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if OLD in text:
        TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    elif NEW not in text:
        raise RuntimeError("unexpected Stepway automatic evidence filename")
    print("PASS: Stepway automatic evidence filename normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
