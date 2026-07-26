#!/usr/bin/env python3
"""Bind the residual review payload before receipt-aware verification."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py"
OLD = '''def check() -> None:
    verify_report(load_json(REPORT))
    verify_partition()
    verify_active_scopes()
    verify_dimension_coverage(payload)
    verify_non_import_boundaries(payload)
    verify_source_closure()
'''
NEW = '''def check() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_partition()
    verify_active_scopes()
    verify_dimension_coverage(payload)
    verify_non_import_boundaries(payload)
    verify_source_closure()
'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if NEW in text:
        print("PASS: residual verifier payload already assigned")
        return 0
    if text.count(OLD) != 1:
        raise RuntimeError("residual verifier check contract not found exactly once")
    PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("PASS: residual verifier payload assigned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
