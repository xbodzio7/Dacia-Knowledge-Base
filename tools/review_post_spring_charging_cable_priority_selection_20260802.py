from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/post_spring_charging_cable_priority_selection_review.json"
REPORT_MD = ROOT / "data/reporting/post_spring_charging_cable_priority_selection_review.md"
STATE = ROOT / "project/state.json"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build(root: Path = ROOT) -> dict:
    representation = read_json(root / "data/reporting/spring_standard_equipment_representation_review.json")
    semantic = read_json(root / "data/reporting/spring_exact_current_semantic_migration_review.json")
    cable = read_json(root / "data/reporting/spring_charging_cable_commercial_semantics_migration.json")
    values = read_rows(root / "data/master/configuration_attribute_values.csv")
    mappings = read_rows(root / "data/master/commercial_item_configurations.csv")

    target_configuration = "spring_essential_electric70_automatic"
    target_attribute = "exterior_color"
    target_mapping = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"

    direct_values = [
        row
        for row in values
        if row["configuration_code"] == target_configuration
        and row["attribute_code"] == target_attribute
    ]
    mapping = next(row for row in mappings if row["code"] == target_mapping)
    representation_decision = next(
        row
        for row in representation["decisions"]
        if row["concept"] == "Essential Biel Alpejska default colour"
    )
    semantic_decision = next(
        row
        for row in semantic["semantic_migrations"]
        if row["mapping_code"] == target_mapping
    )

    candidates = [
        {
            "package_id": "spring_biel_alpejska_default_colour_migration_001",
            "classification": "selected",
            "readiness": "approved_evidence_and_existing_schema_pattern",
            "master_data_delta": {
                "configuration_attribute_values": 1,
                "commercial_item_configurations": 0,
                "commercial_mapping_updates": 1,
                "net_master_rows": 1,
            },
            "reason": "The exact-current default colour, direct exterior_color representation and bounded commercial mapping transition were already accepted; the prior implementation was reverted for an importer-contract defect rather than an evidence defect.",
        },
        {
            "package_id": "spring_expression_current_commercial_state_capture_001",
            "classification": "deferred_missing_exact_option_state",
            "reason": "Expression prices, complete palette and residual charging-option states remain unresolved in exact-current evidence.",
        },
        {
            "package_id": "spring_extreme_paint_palette_capture_001",
            "classification": "deferred_missing_complete_palette",
            "reason": "No complete exact-current Extreme paint palette with prices is registered.",
        },
        {
            "package_id": "spring_residual_essential_palette_reconciliation_001",
            "classification": "deferred_non_inference_boundary",
            "reason": "Absence of four legacy colours from the bounded current capture is not evidence of unavailability.",
        },
    ]

    return {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "package_id": "post_spring_charging_cable_priority_selection_review_001",
        "scope": {
            "master_data_mutation_authorized": False,
            "candidate_count": len(candidates),
            "source_reports": [
                "data/reporting/spring_standard_equipment_representation_review.json",
                "data/reporting/spring_exact_current_semantic_migration_review.json",
                "data/reporting/spring_charging_cable_commercial_semantics_migration.json",
            ],
        },
        "completed_dependency": {
            "package_id": cable["package_id"],
            "status": cable["status"],
            "domestic_socket_mapping_count": cable["domestic_socket_item"]["mapping_count"],
        },
        "selected_evidence": {
            "configuration_code": target_configuration,
            "attribute_code": target_attribute,
            "value": "biel alpejska",
            "observation_date": "2026-08-02",
            "source_code": "src_pl_spring_commercial_context_20260802",
            "current_direct_value_count": len(direct_values),
            "commercial_mapping": {
                "code": target_mapping,
                "current_availability_status": mapping["availability_status"],
                "current_amount": mapping["amount"] or None,
                "target_availability_status": "standard",
                "target_amount_pln": 0,
            },
            "representation_classification": representation_decision["classification"],
            "semantic_current_state": semantic_decision["current_model_state"],
            "semantic_target_state": semantic_decision["exact_current_state"],
        },
        "candidates": candidates,
        "selection": {
            "package_id": "spring_biel_alpejska_default_colour_migration_001",
            "kind": "bounded_configuration_value_and_commercial_mapping_migration",
            "goal": "Add the exact-current Spring Essential Biel Alpejska direct exterior_color value through the canonical declarative import contract and convert only its existing commercial mapping to standard at zero surcharge.",
            "required_boundaries": [
                "Use the current configuration-value import-spec schema and importer.",
                "Change no Expression or Extreme paint mapping.",
                "Change no charging-cable record.",
                "Do not infer unavailability for residual colours.",
                "Add exactly one master row and update exactly one existing mapping.",
            ],
        },
        "mutation_summary": {
            "master_rows_changed": 0,
            "configuration_values_added": 0,
            "commercial_mappings_changed": 0,
        },
    }


def render_markdown(payload: dict) -> str:
    selected = payload["selection"]
    evidence = payload["selected_evidence"]
    lines = [
        "# Post-Spring Charging Cable Priority Selection Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Selected next package",
        "",
        f"`{selected['package_id']}`",
        "",
        selected["goal"],
        "",
        "## Evidence",
        "",
        f"- configuration: `{evidence['configuration_code']}`;",
        f"- direct attribute: `{evidence['attribute_code']}` = `biel alpejska`;",
        f"- source: `{evidence['source_code']}` dated `{evidence['observation_date']}`;",
        f"- current direct value rows: `{evidence['current_direct_value_count']}`;",
        f"- current commercial mapping: `{evidence['commercial_mapping']['current_availability_status']}` with unknown amount;",
        "- target commercial state: `standard`, `0 PLN`.",
        "",
        "## Boundaries",
        "",
    ]
    lines.extend(f"- {item}" for item in selected["required_boundaries"])
    lines.extend(["", "## Deferred candidates", ""])
    lines.extend(
        f"- `{item['package_id']}` — {item['classification']}: {item['reason']}"
        for item in payload["candidates"]
        if item["classification"] != "selected"
    )
    return "\n".join(lines) + "\n"


def verify(root: Path = ROOT) -> None:
    payload = build(root)
    if payload["selected_evidence"]["current_direct_value_count"] != 0:
        raise RuntimeError("Spring Essential exterior_color is already materialized")
    mapping = payload["selected_evidence"]["commercial_mapping"]
    if mapping["current_availability_status"] != "optional" or mapping["current_amount"] is not None:
        raise RuntimeError("Biel Alpejska commercial mapping no longer matches the approved pre-migration state")
    if payload["completed_dependency"]["status"] != "complete":
        raise RuntimeError("charging-cable commercial migration is not complete")
    if REPORT_JSON.exists() and read_json(REPORT_JSON) != payload:
        raise RuntimeError("committed priority review JSON is not deterministic")
    if REPORT_MD.exists() and REPORT_MD.read_text(encoding="utf-8") != render_markdown(payload):
        raise RuntimeError("committed priority review Markdown is not deterministic")


def apply(root: Path = ROOT) -> None:
    payload = build(root)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(payload), encoding="utf-8")
    state_path = root / "project/state.json"
    state = read_json(state_path)
    state["phase"] = "Post-Spring Charging Cable Priority Selection Review"
    state["current_package"] = {
        "package_id": "post_spring_charging_cable_priority_selection_review_001",
        "kind": "bounded_priority_selection_review",
        "name": "Post-Spring Charging Cable Priority Selection Review",
        "status": "complete",
        "goal": "Select the next bounded repository package from current evidence and unresolved queues without changing master data.",
        "manifest_paths": [
            "data/reporting/post_spring_charging_cable_priority_selection_review.json",
            "data/reporting/post_spring_charging_cable_priority_selection_review.md",
            "project/packages/post-spring-charging-cable-priority-selection-review-20260802.md",
            "project/STATE_SUMMARY.md",
            "project/state.json",
            "tests/test_post_spring_charging_cable_priority_selection_review_20260802.py",
            "tools/review_post_spring_charging_cable_priority_selection_20260802.py",
        ],
    }
    state["next_package"] = {
        "package_id": "spring_biel_alpejska_default_colour_migration_001",
        "kind": "bounded_configuration_value_and_commercial_mapping_migration",
        "name": "Spring Essential Biel Alpejska Default Colour Migration",
        "status": "planned",
        "goal": payload["selection"]["goal"],
        "manifest_paths": [
            "data/imports/configuration_attribute_value_imports.csv",
            "data/master/configuration_attribute_values.csv",
            "data/master/commercial_item_configurations.csv",
            "data/reporting/",
            "project/state.json",
            "project/STATE_SUMMARY.md",
            "tests/",
            "tools/",
        ],
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    package = root / "project/packages/post-spring-charging-cable-priority-selection-review-20260802.md"
    package.write_text(
        "# Post-Spring Charging Cable Priority Selection Review\n\n"
        "Package: `post_spring_charging_cable_priority_selection_review_001`\n\n"
        "Status: complete\n\n"
        "The review selects `spring_biel_alpejska_default_colour_migration_001` as the next bounded package. It changes no master data.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    verify()
