#!/usr/bin/env python3
"""Close reporting dependencies resolved by the Stepway Expression automatic source-gap import."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import verified_pdf_candidate_coverage_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATHS = (
    ROOT / "data/reporting/configuration_gap_evidence.json",
    ROOT / "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json",
)
SOURCE_REVIEW = ROOT / "data/reporting/configuration_gap_source_review.json"
TARGET_CONFIGURATION = "sandero_stepway_iii_expression_ecog120_automatic"
TARGET_SOURCE = "src_pl_sandero_stepway_expression_ecog120_at_20260626"
TARGETS = {
    ("technical", "ground_clearance", ""),
    ("technical", "max_torque_rpm", "lpg"),
    ("technical", "max_torque_rpm", "petrol"),
    ("technical", "overall_height", ""),
    ("technical", "overall_width_with_mirrors", ""),
    ("technical", "wheel_finish", ""),
    ("equipment", "parking_assist_system", ""),
}


class DependencyError(RuntimeError):
    pass


def canonical(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def load_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DependencyError(f"expected JSON object: {path}")
    return payload


def targeted_decision(decision: object) -> bool:
    if not isinstance(decision, dict):
        return False
    return (
        decision.get("source_code") == TARGET_SOURCE
        and decision.get("configuration_code") == TARGET_CONFIGURATION
        and (str(decision.get("domain", "")), str(decision.get("attribute_code", "")), str(decision.get("fuel_type_code", ""))) in TARGETS
    )


def targeted_key(key: object) -> bool:
    if not isinstance(key, str):
        return False
    parts = key.split("|")
    if len(parts) != 6:
        return False
    domain, source, configuration, _category, attribute, fuel = parts
    return source == TARGET_SOURCE and configuration == TARGET_CONFIGURATION and (domain, attribute, "" if fuel == "none" else fuel) in TARGETS


def filtered_evidence(payload: dict[str, object]) -> tuple[dict[str, object], int]:
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise DependencyError("unexpected evidence payload")
    output = dict(payload)
    output["decisions"] = [item for item in decisions if not targeted_decision(item)]
    return output, len(decisions) - len(output["decisions"])


def filtered_source_review(payload: dict[str, object]) -> tuple[dict[str, object], int]:
    keys = payload.get("review_triage_keys")
    if not isinstance(keys, list):
        raise DependencyError("unexpected configuration source-review payload")
    output = dict(payload)
    output["review_triage_keys"] = [item for item in keys if not targeted_key(item)]
    return output, len(keys) - len(output["review_triage_keys"])


def reconciliation_outputs() -> tuple[str, str]:
    payload, markdown = reconciliation.build_from_paths(ROOT, reconciliation.DEFAULT_LEDGER, reconciliation.DEFAULT_REVIEW)
    return reconciliation.canonical_json(payload), markdown


def apply() -> None:
    for path in EVIDENCE_PATHS:
        evidence, _removed = filtered_evidence(load_object(path))
        path.write_text(canonical(evidence), encoding="utf-8")
    source_review, review_removed = filtered_source_review(load_object(SOURCE_REVIEW))
    if review_removed not in {0, 1, 2}:
        raise DependencyError(f"expected zero, one or two resolved source-review keys, found {review_removed}")
    SOURCE_REVIEW.write_text(canonical(source_review), encoding="utf-8")
    json_text, markdown = reconciliation_outputs()
    (ROOT / reconciliation.DEFAULT_JSON).write_text(json_text, encoding="utf-8")
    (ROOT / reconciliation.DEFAULT_MARKDOWN).write_text(markdown, encoding="utf-8")


def check() -> None:
    for path in EVIDENCE_PATHS:
        _, remaining = filtered_evidence(load_object(path))
        if remaining:
            raise DependencyError(f"{remaining} resolved evidence decisions remain in {path}")
    _, review_remaining = filtered_source_review(load_object(SOURCE_REVIEW))
    if review_remaining:
        raise DependencyError(f"{review_remaining} resolved source-review keys remain")
    json_text, markdown = reconciliation_outputs()
    if (ROOT / reconciliation.DEFAULT_JSON).read_text(encoding="utf-8") != json_text:
        raise DependencyError("coverage reconciliation JSON is stale")
    if (ROOT / reconciliation.DEFAULT_MARKDOWN).read_text(encoding="utf-8") != markdown:
        raise DependencyError("coverage reconciliation Markdown is stale")
    print("Stepway Expression automatic reporting dependencies: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        check() if args.check else (apply(), check())
    except (DependencyError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
