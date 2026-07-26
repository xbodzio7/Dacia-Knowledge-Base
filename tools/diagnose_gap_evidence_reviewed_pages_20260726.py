#!/usr/bin/env python3
"""Persist compact diagnostics for evidence decisions missing reviewed pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
SOURCE = REPORTING / "configuration_gap_evidence.json"
OUTPUT = ROOT / ".github" / "gap-evidence-reviewed-pages-diagnostics.json"
FIELDS = (
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


def compact(decision: dict[str, Any]) -> dict[str, Any]:
    return {key: decision.get(key) for key in FIELDS}


def load_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def main() -> int:
    payload = load_object(SOURCE)
    if payload is None:
        raise RuntimeError(f"cannot load {SOURCE}")
    invalid = [
        compact(decision)
        for decision in payload.get("decisions", [])
        if isinstance(decision, dict)
        and decision.get("classification") == "not_stated"
        and not decision.get("reviewed_pages")
    ]
    attributes = {item["attribute_code"] for item in invalid}
    related: list[dict[str, Any]] = []
    for path in sorted(REPORTING.glob("*gap_evidence*")):
        candidate = load_object(path)
        if candidate is None:
            continue
        for decision in candidate.get("decisions", []):
            if (
                isinstance(decision, dict)
                and decision.get("attribute_code") in attributes
                and decision.get("reviewed_pages")
            ):
                related.append({"evidence_file": path.name, **compact(decision)})
    review = load_object(REPORTING / "configuration_gap_source_review.json") or {}
    rules = [
        {
            "attribute_code": rule.get("attribute_code"),
            "review_pages": rule.get("review_pages"),
            "source_section": rule.get("source_section"),
        }
        for rule in review.get("rules", [])
        if isinstance(rule, dict) and rule.get("attribute_code") in attributes
    ]
    OUTPUT.write_text(
        json.dumps(
            {
                "count": len(invalid),
                "decisions": invalid,
                "related_reviewed_decisions": related,
                "source_review_rules": rules,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: persisted "
        f"{len(invalid)} invalid decisions and {len(related)} related decisions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
