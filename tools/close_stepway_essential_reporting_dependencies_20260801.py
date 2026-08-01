#!/usr/bin/env python3
"""Close reporting dependencies resolved by the Stepway Essential source-gap import."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import verified_pdf_candidate_coverage_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/reporting/sandero_ecog120_manual_gap_evidence.json"
TARGET_CONFIGURATION = "sandero_stepway_iii_essential_ecog120_manual"
TARGETS = {
    ("ground_clearance", ""),
    ("max_torque_rpm", "lpg"),
    ("max_torque_rpm", "petrol"),
    ("overall_height", ""),
    ("overall_width_with_mirrors", ""),
    ("wheel_finish", ""),
}


class DependencyError(RuntimeError):
    pass


def canonical(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def evidence_payload() -> dict[str, object]:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("decisions"), list):
        raise DependencyError("unexpected Sandero evidence payload")
    return payload


def targeted(decision: object) -> bool:
    if not isinstance(decision, dict):
        return False
    return (
        decision.get("domain") == "technical"
        and decision.get("configuration_code") == TARGET_CONFIGURATION
        and (str(decision.get("attribute_code", "")), str(decision.get("fuel_type_code", ""))) in TARGETS
    )


def filtered_evidence(payload: dict[str, object]) -> tuple[dict[str, object], int]:
    decisions = payload["decisions"]
    assert isinstance(decisions, list)
    removed = sum(targeted(item) for item in decisions)
    output = dict(payload)
    output["decisions"] = [item for item in decisions if not targeted(item)]
    return output, removed


def reconciliation_outputs() -> tuple[str, str]:
    payload, markdown = reconciliation.build_from_paths(
        ROOT, reconciliation.DEFAULT_LEDGER, reconciliation.DEFAULT_REVIEW
    )
    return reconciliation.canonical_json(payload), markdown


def apply() -> None:
    payload = evidence_payload()
    output, removed = filtered_evidence(payload)
    if removed not in {0, 6}:
        raise DependencyError(f"expected zero or six resolved evidence decisions, found {removed}")
    EVIDENCE.write_text(canonical(output), encoding="utf-8")
    json_text, markdown = reconciliation_outputs()
    (ROOT / reconciliation.DEFAULT_JSON).write_text(json_text, encoding="utf-8")
    (ROOT / reconciliation.DEFAULT_MARKDOWN).write_text(markdown, encoding="utf-8")


def check() -> None:
    payload = evidence_payload()
    _, removed = filtered_evidence(payload)
    if removed:
        raise DependencyError(f"{removed} resolved evidence decisions remain")
    json_text, markdown = reconciliation_outputs()
    if (ROOT / reconciliation.DEFAULT_JSON).read_text(encoding="utf-8") != json_text:
        raise DependencyError("coverage reconciliation JSON is stale")
    if (ROOT / reconciliation.DEFAULT_MARKDOWN).read_text(encoding="utf-8") != markdown:
        raise DependencyError("coverage reconciliation Markdown is stale")
    print("Stepway Essential reporting dependencies: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            check()
        else:
            apply()
            check()
    except (DependencyError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
