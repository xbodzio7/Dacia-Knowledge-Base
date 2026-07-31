from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import review_data_products_v1_9_0_preflight_20260731 as preflight  # noqa: E402

PUBLICATION_RECORD = ROOT / "project" / "releases" / "data-products-v1.9.0.md"
PUBLIC_AUDIT = ROOT / "data" / "reporting" / "data_products_v1_9_0_public_audit.json"


def verify_lifecycle_state() -> None:
    """Accept the exact preflight state or its audited public successor."""
    state = preflight.load_json(preflight.STATE)
    if state.get("phase") == "Data Products v1.9.0 Preflight":
        preflight.verify_state()
        return

    if not PUBLICATION_RECORD.is_file() or not PUBLIC_AUDIT.is_file():
        raise preflight.PreflightError(
            "preflight state advanced without durable publication and audit records"
        )

    publication = PUBLICATION_RECORD.read_text(encoding="utf-8")
    if "Release ID: `362975393`" not in publication:
        raise preflight.PreflightError("public v1.9.0 release ID differs")
    if preflight.SOURCE_COMMIT not in publication:
        raise preflight.PreflightError("public v1.9.0 source commit differs")

    audit = json.loads(PUBLIC_AUDIT.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise preflight.PreflightError("public v1.9.0 audit did not pass")
    if audit.get("source_commit") != preflight.SOURCE_COMMIT:
        raise preflight.PreflightError("audited v1.9.0 source commit differs")

    baseline = state.get("baseline", {})
    expected = {
        "tests": 1676,
        "rows": 11380,
        "configuration_values": 3498,
        "configuration_value_ranges": 298,
        "availability_records": 5770,
    }
    for key, minimum in expected.items():
        if int(baseline.get(key, 0)) < minimum:
            raise preflight.PreflightError(f"post-preflight baseline regressed: {key}")


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    """Run the deterministic preflight contract without adding a test case."""
    preflight.verify_report(preflight.load_json(preflight.REPORT))
    preflight.verify_rebuilds()
    preflight.verify_public_control()
    verify_lifecycle_state()
    return tests
