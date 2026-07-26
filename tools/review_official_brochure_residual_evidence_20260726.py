#!/usr/bin/env python3
"""Verify the residual official brochure evidence review."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "official_brochure_residual_evidence_review.json"
GAP_REVIEW = REPORTING / "official_brochure_technical_gap_review.json"
GAP_CLOSURE = REPORTING / "official_brochure_technical_gap_resolution_closure_review.json"
CLOSURE_VERIFIER = ROOT / "tools" / "review_official_brochure_technical_gap_resolution_closure_20260726.py"

EXPECTED_STABLE = {
    "bigster_core_powertrain_covered_or_newer",
    "jogger_core_powertrain_covered_or_newer",
    "sandero_manual_core_covered",
    "stepway_core_covered",
    "duster_core_powertrain_covered_or_newer",
    "sandero_tce100_without_exact_configuration",
    "stepway_tce110_without_exact_configuration",
    "duster_hybridg150_without_exact_configuration",
    "jogger_blank_wltp_cells",
    "sandero_wltp_placeholders",
    "jogger_mass_table_label_conflict",
}
EXPECTED_COVERED = {
    "bigster_dimensions_covered_and_cargo_deferred",
    "stepway_dimensions_and_cargo",
}
EXPECTED_CANDIDATES = {
    "sandero_dimensions_and_cargo",
    "jogger_dimensions_and_cargo",
    "duster_wltp_placeholders_and_dimensions",
}
CORE_DIMENSIONS = {
    "overall_length",
    "overall_width",
    "overall_width_with_mirrors",
    "overall_height",
    "roof_height_with_rails",
    "wheelbase",
    "ground_clearance",
    "front_track",
    "rear_track",
    "front_overhang",
    "rear_overhang",
    "approach_angle",
    "departure_angle",
}
MODEL_CODES = {
    "sandero_iii",
    "sandero_stepway_iii",
    "jogger",
    "bigster",
    "duster_iii",
}


class ReviewError(RuntimeError):
    """Raised when the residual review contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def active_configuration_models() -> dict[str, str]:
    versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
    return {
        row["code"]: versions.get(row.get("version_code", ""), {}).get("model_code", "")
        for row in rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported residual review version")
    ensure(payload.get("kind") == "official_brochure_residual_evidence_review", "unexpected residual review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "residual review is not complete")
    ensure(payload.get("source_closure") == "official_brochure_technical_gap_resolution_closure_review.json", "source closure differs")
    ensure(payload.get("scope") == {"sources": 5, "residual_classifications": 16}, "review scope differs")
    ensure(
        payload.get("resolution_summary")
        == {"stable_non_import": 11, "closed_by_existing_exact_coverage": 2, "semantic_mapping_review_candidate": 3},
        "resolution summary differs",
    )

    stable = payload.get("stable_non_import")
    covered = payload.get("closed_by_existing_exact_coverage")
    candidates = payload.get("semantic_mapping_review_candidates")
    ensure(isinstance(stable, list) and {str(item.get("code", "")) for item in stable} == EXPECTED_STABLE, "stable non-import set differs")
    ensure(isinstance(covered, list) and {str(item.get("code", "")) for item in covered} == EXPECTED_COVERED, "covered dimension set differs")
    ensure(isinstance(candidates, list) and {str(item.get("code", "")) for item in candidates} == EXPECTED_CANDIDATES, "dimension candidate set differs")
    ensure(all(item.get("status") == "semantic_mapping_review_candidate" for item in candidates), "dimension candidate status differs")
    ensure({int(item.get("source_page", 0)) for item in candidates} == {20, 22, 24}, "dimension candidate pages differ")

    coverage = payload.get("current_dimension_coverage")
    ensure(
        coverage
        == {
            "sandero_exact_values": 10,
            "sandero_exact_configurations": 2,
            "stepway_exact_values": 25,
            "stepway_exact_configurations": 5,
            "jogger_exact_values": 0,
            "jogger_exact_configurations": 0,
            "bigster_exact_values": 140,
            "bigster_exact_configurations": 14,
            "duster_exact_values": 0,
            "duster_exact_configurations": 0,
            "duster_basis_qualified_turning_values": 10,
        },
        "dimension coverage summary differs",
    )
    rules = payload.get("non_inference_contract")
    ensure(isinstance(rules, list) and len(rules) == 6, "expected six non-inference rules")
    ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Semantic Mapping Review", "next package differs")


def verify_partition() -> None:
    gap = load_json(GAP_REVIEW)
    closure = load_json(GAP_CLOSURE)
    residual = set(closure["residual_evidence"]["classification_codes"])
    ensure(residual == EXPECTED_STABLE | EXPECTED_COVERED | EXPECTED_CANDIDATES, "residual partition differs")
    classifications = {item["code"]: item for item in gap["classifications"]}
    ensure(all(code in classifications for code in residual), "residual classification missing from source review")
    ensure(classifications["jogger_mass_table_label_conflict"]["status"] == "ambiguous_source_evidence", "Jogger ambiguity status differs")
    ensure(
        {code for code in EXPECTED_STABLE if classifications[code]["status"] == "unmodeled_exact_configuration"}
        == {
            "sandero_tce100_without_exact_configuration",
            "stepway_tce110_without_exact_configuration",
            "duster_hybridg150_without_exact_configuration",
        },
        "unmodeled exact configuration set differs",
    )


def verify_active_scopes() -> None:
    models = active_configuration_models()
    counts = Counter(models.values())
    ensure(counts["sandero_iii"] == 4, "active Sandero scope differs")
    ensure(counts["sandero_stepway_iii"] == 5, "active Stepway scope differs")
    ensure(counts["jogger"] == 22, "active Jogger scope differs")
    ensure(counts["bigster"] == 14, "active Bigster scope differs")
    ensure(counts["duster_iii"] == 27, "active Duster scope differs")


def verify_dimension_coverage() -> None:
    models = active_configuration_models()
    values = rows(MASTER / "configuration_attribute_values.csv")

    selected: dict[str, list[dict[str, str]]] = {model: [] for model in MODEL_CODES}
    for row in values:
        model = models.get(row.get("configuration_code", ""), "")
        if model in selected and row.get("attribute_code") in CORE_DIMENSIONS:
            selected[model].append(row)

    ensure(len(selected["sandero_iii"]) == 10, "Sandero exact dimension coverage differs")
    ensure(len({row["configuration_code"] for row in selected["sandero_iii"]}) == 2, "Sandero exact dimension configuration count differs")
    ensure(len(selected["sandero_stepway_iii"]) == 25, "Stepway exact dimension coverage differs")
    ensure(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}) == 5, "Stepway exact dimension configuration count differs")
    ensure(selected["jogger"] == [], "Jogger dimensions unexpectedly already imported")
    ensure(len(selected["bigster"]) == 140, "Bigster exact dimension coverage differs")
    ensure(len({row["configuration_code"] for row in selected["bigster"]}) == 14, "Bigster exact dimension configuration count differs")
    ensure(selected["duster_iii"] == [], "Duster core dimensions unexpectedly already imported")

    turning = [
        row
        for row in values
        if models.get(row.get("configuration_code", "")) == "duster_iii"
        and row.get("attribute_code") == "turning_circle_wheel_track"
        and row.get("source_code") == "src_pl_duster_mini_brochure_20251020"
    ]
    ensure(len(turning) == 10, "Duster basis-qualified turning coverage differs")


def verify_non_import_boundaries() -> None:
    values = rows(MASTER / "configuration_attribute_values.csv")
    sources = {
        "src_pl_sandero_brochure_20260202",
        "src_pl_sandero_stepway_brochure_20260202",
        "src_pl_jogger_brochure_20251217",
        "src_pl_bigster_brochure_20251210",
        "src_pl_duster_mini_brochure_20251020",
    }
    ensure(
        not any(row.get("source_code") in sources and row.get("attribute_code") in CORE_DIMENSIONS for row in values),
        "generic brochure dimensions were imported before semantic mapping review",
    )
    ensure(
        not any(
            row.get("source_code") == "src_pl_jogger_brochure_20251217"
            and row.get("attribute_code") in {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
            for row in values
        ),
        "ambiguous Jogger mass evidence was imported",
    )


def verify_source_closure() -> None:
    completed = subprocess.run(
        [sys.executable, str(CLOSURE_VERIFIER), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    ensure(completed.returncode == 0, completed.stderr or completed.stdout)


def check() -> None:
    verify_report(load_json(REPORT))
    verify_partition()
    verify_active_scopes()
    verify_dimension_coverage()
    verify_non_import_boundaries()
    verify_source_closure()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ReviewError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print("PASS: official brochure residual evidence review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
