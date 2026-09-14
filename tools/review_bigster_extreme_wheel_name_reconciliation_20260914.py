"""Audit the four active Bigster Extreme wheel-design slots selected from CAT-GAP-014.

This is intentionally a reconciliation-only audit. It does not write master data.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data" / "master" / "configuration_attribute_values.csv"
OUTPUT = ROOT / "data" / "reporting" / "bigster_extreme_wheel_name_reconciliation_20260914.json"

TARGETS = {
    "bigster_extreme_mildhybrid140_4x2_manual": {"drive": "4x2"},
    "bigster_extreme_mildhybridg140_4x2_manual": {"drive": "4x2"},
    "bigster_extreme_hybrid155_4x2_automatic": {"drive": "4x2"},
    "bigster_extreme_hybridg150_4x4_automatic": {"drive": "4x4"},
}


def main() -> int:
    rows: list[dict[str, str]] = []
    with VALUES.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("attribute_code") != "wheel_design":
                continue
            if row.get("configuration_code") not in TARGETS:
                continue
            rows.append(row)

    by_config: dict[str, list[dict[str, str]]] = {code: [] for code in TARGETS}
    for row in rows:
        by_config[row["configuration_code"]].append(row)

    observations = []
    failures = []
    for code, spec in TARGETS.items():
        matches = by_config[code]
        if len(matches) != 1:
            failures.append({"configuration_code": code, "reason": f"expected exactly one wheel_design row, found {len(matches)}"})
            continue
        value = matches[0].get("value", "")
        ok = "TAGASAN" in value and "pół diamentowane" in value
        if spec["drive"] == "4x4":
            ok = ok and "225" in value
        else:
            ok = ok and "225" not in value
        if not ok:
            failures.append({"configuration_code": code, "reason": "unexpected wheel_design literal", "value": value})
        observations.append({
            "configuration_code": code,
            "attribute_code": "wheel_design",
            "value": value,
            "source_code": matches[0].get("source_code"),
            "source_date": matches[0].get("source_date"),
        })

    report = {
        "version": 1,
        "kind": "bigster_extreme_wheel_name_reconciliation",
        "captured_on": "2026-09-14",
        "gap_id": "CAT-GAP-014",
        "target_count": len(TARGETS),
        "observed_count": len(observations),
        "missing_slots": [code for code, matches in by_config.items() if not matches],
        "duplicate_slots": [code for code, matches in by_config.items() if len(matches) > 1],
        "validation_failures": failures,
        "new_master_rows_required": 0 if not failures else None,
        "status": "closed_zero_data_delta" if not failures else "blocked",
        "observations": observations,
        "source_rule": "Current official Dacia catalogue pages were used to confirm the exact configuration identities and wheel naming; canonical rows are not duplicated when the current repository already occupies the exact configuration/attribute slot.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
