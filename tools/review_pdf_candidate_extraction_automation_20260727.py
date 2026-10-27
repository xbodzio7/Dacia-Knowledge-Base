#!/usr/bin/env python3
"""Verify the selected PDF candidate extraction automation architecture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "pdf_candidate_extraction_automation_review.json"
RECEIPT = ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"
GAP_REVIEW = ROOT / "data" / "reporting" / "official_dacia_brochure_gap_review.json"
VALUE_IMPORTER = ROOT / "tools" / "import_configuration_values.py"
PAGE_REVIEWER = ROOT / "tools" / "configuration_gap_source_review.py"
DKB = ROOT / "tools" / "dkb.py"
STATE = ROOT / "project" / "state.json"


class ReviewError(RuntimeError):
    """Raised when the PDF candidate extraction review contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def weighted_score(scores: Mapping[str, Any], weights: Mapping[str, Any]) -> int:
    total = 0.0
    for key, weight in weights.items():
        value = scores.get(key)
        ensure(isinstance(value, int) and 1 <= value <= 5, f"invalid score: {key}")
        ensure(isinstance(weight, int), f"invalid weight: {key}")
        total += value * weight / 5
    return round(total)


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "review version differs")
    ensure(
        payload.get("kind") == "pdf_candidate_extraction_automation_review",
        "review kind differs",
    )
    ensure(payload.get("reviewed_on") == "2026-07-27", "review date differs")
    ensure(payload.get("status") == "complete", "review is not complete")
    ensure(
        payload.get("source_milestone")
        == "post_cross_model_workspace_priority_selection_review.json",
        "source milestone differs",
    )

    inventory = payload.get("input_inventory")
    ensure(isinstance(inventory, Mapping), "input inventory is missing")
    ensure(inventory.get("registered_sources") == 5, "source count differs")
    ensure(inventory.get("declared_pages") == 114, "page count differs")
    ensure(inventory.get("declared_bytes") == 40608101, "byte count differs")
    ensure(inventory.get("all_sources_have_sha256") is True, "SHA coverage differs")
    ensure(
        inventory.get("model_codes")
        == [
            "bigster",
            "duster_iii",
            "jogger",
            "sandero_iii",
            "sandero_stepway_iii",
        ],
        "model inventory differs",
    )

    policy = payload.get("selection_policy")
    ensure(isinstance(policy, Mapping), "selection policy is missing")
    weights = policy.get("weights_percent")
    ensure(isinstance(weights, Mapping), "selection weights are missing")
    expected_weights = {
        "evidence_safety": 30,
        "determinism": 25,
        "candidate_utility": 20,
        "existing_tooling_reuse": 15,
        "low_implementation_risk": 10,
    }
    ensure(dict(weights) == expected_weights, "selection weights differ")
    ensure(sum(int(value) for value in weights.values()) == 100, "weights do not sum to 100")

    candidates = payload.get("architecture_candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "candidate count differs")
    ensure(
        [candidate.get("rank") for candidate in candidates] == [1, 2, 3, 4, 5],
        "candidate ranks differ",
    )
    expected_codes = [
        "verified_page_candidate_ledger",
        "gap_scoped_candidate_probe",
        "raw_page_text_archive",
        "direct_import_spec_synthesis",
        "ocr_first_multimodal_pipeline",
    ]
    expected_scores = [98, 94, 85, 65, 49]
    expected_statuses = [
        "selected",
        "alternative",
        "alternative",
        "rejected_boundary",
        "deferred_out_of_scope",
    ]
    ensure(
        [candidate.get("code") for candidate in candidates] == expected_codes,
        "candidate codes differ",
    )
    ensure(
        [candidate.get("status") for candidate in candidates] == expected_statuses,
        "candidate statuses differ",
    )
    for candidate, expected in zip(candidates, expected_scores, strict=True):
        ensure(isinstance(candidate, Mapping), "candidate is invalid")
        scores = candidate.get("scores")
        ensure(isinstance(scores, Mapping), "candidate scores are missing")
        ensure(weighted_score(scores, weights) == expected, f"calculated score differs: {candidate.get('code')}")
        ensure(candidate.get("weighted_score") == expected, f"stored score differs: {candidate.get('code')}")

    selection = payload.get("selection")
    ensure(isinstance(selection, Mapping), "selection is missing")
    ensure(selection.get("code") == "verified_page_candidate_ledger", "selected code differs")
    ensure(selection.get("weighted_score") == 98, "selected score differs")

    architecture = payload.get("selected_architecture")
    ensure(isinstance(architecture, Mapping), "selected architecture is missing")
    input_contract = architecture.get("input_contract")
    ensure(isinstance(input_contract, Mapping), "input contract is missing")
    ensure(input_contract.get("receipt_driven") is True, "receipt boundary differs")
    ensure(input_contract.get("fail_closed_on_integrity_difference") is True, "integrity boundary differs")
    ensure(
        input_contract.get("verify_before_extraction")
        == ["file_path", "bytes", "sha256", "declared_pages"],
        "integrity checks differ",
    )

    extraction = architecture.get("extraction_contract")
    ensure(isinstance(extraction, Mapping), "extraction contract is missing")
    ensure(
        extraction.get("canonical_backend_order")
        == ["pdftotext-layout", "pdftotext-default", "pdftotext-raw"],
        "canonical backend order differs",
    )
    ensure(
        extraction.get("optional_backends_are_diagnostics_only") == ["pypdf", "PyPDF2"],
        "optional backend boundary differs",
    )
    ensure(
        extraction.get("canonical_candidate_ids_do_not_depend_on_optional_backend_presence") is True,
        "optional backend independence differs",
    )
    ensure(extraction.get("empty_or_unreadable_text_does_not_mean_not_stated") is True, "negative-evidence boundary differs")

    identity = architecture.get("candidate_identity")
    ensure(isinstance(identity, Mapping), "candidate identity is missing")
    ensure(identity.get("algorithm") == "sha256", "candidate ID algorithm differs")
    for component in (
        "source_sha256",
        "page",
        "rule_code",
        "line_start",
        "line_end",
        "normalized_text",
    ):
        ensure(component in identity.get("components", []), f"candidate ID component missing: {component}")

    required_fields = architecture.get("required_candidate_fields")
    ensure(isinstance(required_fields, list), "candidate fields are missing")
    for field in (
        "candidate_id",
        "source_code",
        "source_sha256",
        "page",
        "backend",
        "backend_version",
        "line_start",
        "line_end",
        "exact_text",
        "normalized_text",
        "candidate_kind",
        "review_status",
    ):
        ensure(field in required_fields, f"candidate field missing: {field}")

    statuses = architecture.get("review_statuses")
    ensure(isinstance(statuses, list), "review statuses are missing")
    for status in (
        "unreviewed_candidate",
        "requires_visual_review",
        "ambiguous_source_evidence",
        "explicit_non_import",
    ):
        ensure(status in statuses, f"review status missing: {status}")

    boundaries = architecture.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "semantic boundaries are missing")
    for key in (
        "configuration_code_is_not_inferred",
        "attribute_code_is_not_approved_by_extraction",
        "units_are_not_canonicalized_without_review",
        "missing_text_is_not_negative_evidence",
        "diagram_or_image_content_requires_visual_review",
        "candidate_output_is_not_an_import_spec",
    ):
        ensure(boundaries.get(key) is True, f"semantic boundary differs: {key}")
    ensure(boundaries.get("master_data_changes") is False, "master-data boundary differs")
    ensure(boundaries.get("approved_import_spec_generation") is False, "import-spec boundary differs")
    ensure(boundaries.get("automatic_promotion") is False, "promotion boundary differs")

    implementation = payload.get("implementation_contract")
    ensure(isinstance(implementation, Mapping), "implementation contract is missing")
    ensure(implementation.get("command") == "pdf-candidate-ledger", "command differs")
    scope = implementation.get("first_delivery_scope")
    ensure(isinstance(scope, Mapping), "first delivery scope is missing")
    ensure(scope.get("sources") == 5 and scope.get("pages") == 114, "delivery scope differs")
    ensure(scope.get("master_data_changes") == 0, "delivery changes master data")
    ensure(scope.get("approved_import_specs_created") == 0, "delivery creates approved imports")
    ensure(scope.get("ocr") is False, "delivery enables OCR")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    ensure(next_package.get("name") == "Verified PDF Candidate Ledger Foundation", "next package differs")


def verify_repository() -> None:
    receipt = load_json(RECEIPT)
    sources = receipt.get("sources")
    ensure(isinstance(sources, list) and len(sources) == 5, "registered receipt differs")
    ensure(sum(int(source["pages"]) for source in sources) == 114, "registered page total differs")
    ensure(sum(int(source["bytes"]) for source in sources) == 40608101, "registered byte total differs")
    for source in sources:
        ensure(isinstance(source, Mapping), "registered source is invalid")
        sha256 = source.get("sha256")
        ensure(isinstance(sha256, str) and len(sha256) == 64, "registered source SHA differs")
        path = ROOT / str(source.get("file_path"))
        ensure(path.is_file(), f"registered PDF is missing: {path}")

    gap_review = load_json(GAP_REVIEW)
    ensure(gap_review.get("policy", {}).get("registration_does_not_import_observations") is True, "registration/import boundary differs")
    ensure(gap_review.get("policy", {}).get("missing_source_statements_are_not_negative_values") is True, "missing-statement boundary differs")
    ensure(gap_review.get("summary", {}).get("master_observations_imported") == 0, "gap review imported data")

    importer = VALUE_IMPORTER.read_text(encoding="utf-8")
    for marker in (
        "def extract_page_candidates",
        '"pdftotext-raw"',
        '"pdftotext-layout"',
        '"pdftotext-default"',
        'for module_name in ("pypdf", "PyPDF2")',
        "registered source SHA-256 differs",
        "does not contain the declared",
    ):
        ensure(marker in importer, f"existing importer capability missing: {marker}")

    reviewer = PAGE_REVIEWER.read_text(encoding="utf-8")
    for marker in (
        "def page_extraction",
        "recovered_anchors",
        'if "layout" in backend_name or "table" in backend_name',
        "extract_page_candidates",
    ):
        ensure(marker in reviewer, f"existing page-review capability missing: {marker}")

    cli = DKB.read_text(encoding="utf-8")
    for command in (
        '"configuration-gap-source-review"',
        '"import-configuration-values"',
        '"import-configuration-value-ranges"',
    ):
        ensure(command in cli, f"adjacent CLI command missing: {command}")

    state = load_json(STATE)
    current = state.get("current_package", {})
    current_name = current.get("name")
    phase = state.get("phase")
    ensure(isinstance(current_name, str) and bool(current_name), "current package is missing")
    ensure(isinstance(phase, str) and bool(phase), "project phase is missing")
    ensure(current.get("status") == "complete", "current package is not complete")

    completion = (
        ROOT
        / "data"
        / "imports"
        / "catalog_completion"
        / "sandero-stepway-tce-20260703.json"
    )
    foundation = ROOT / "data" / "reporting" / "official_dacia_pdf_candidate_ledger.json"
    if completion.is_file():
        baseline_floor = {
            "tests": 1071,
            "rows": 11092,
            "configuration_values": 3267,
            "configuration_import_specs": 117,
            "configuration_value_ranges": 244,
            "configuration_range_import_specs": 20,
            "availability_records": 5770,
        }
    else:
        baseline_floor = {
            "tests": 1070,
            "rows": 9688,
            "configuration_values": 2949,
            "configuration_import_specs": 117,
            "configuration_value_ranges": 244,
            "configuration_range_import_specs": 20,
            "availability_records": 4754,
        }

    baseline = state.get("baseline", {})
    for field, minimum in baseline_floor.items():
        actual = baseline.get(field)
        ensure(
            isinstance(actual, int) and actual >= minimum,
            f"{field} baseline regressed",
        )

    if foundation.is_file():
        ensure('"pdf-candidate-ledger"' in cli, "candidate-ledger CLI command missing")
    else:
        expected_current = (
            "Source-Bounded Sandero and Stepway Catalogue Completion"
            if completion.is_file()
            else "PDF Candidate Extraction Automation Review"
        )
        ensure(current_name == expected_current, "historical current package differs")
        ensure(phase == current_name, "historical project phase/current package differ")
        ensure(
            state.get("next_package", {}).get("name")
            == "Verified PDF Candidate Ledger Foundation",
            "state next package differs",
        )


def verify() -> None:
    verify_report(load_json(REPORT))
    verify_repository()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the PDF candidate extraction review contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: PDF candidate extraction automation review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
