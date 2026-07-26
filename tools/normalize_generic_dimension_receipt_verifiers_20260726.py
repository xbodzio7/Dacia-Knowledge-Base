#!/usr/bin/env python3
"""Normalize receipt-aware review verifiers after the generic dimension import."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_segment(text: str, start: str, end: str, replacement: str, label: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"{label}: start marker missing")
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise RuntimeError(f"{label}: end marker missing")
    return text[:start_index] + replacement.rstrip() + text[end_index:]


def replace_function(text: str, signature: str, next_name: str, replacement: str) -> str:
    return replace_segment(text, f"def {signature}", f"\n\ndef {next_name}", replacement, signature)


def normalize_mapping_verifier() -> None:
    path = ROOT / "tools" / "review_brochure_generic_dimensions_semantic_mapping_20260726.py"
    text = path.read_text(encoding="utf-8")
    text = replace_segment(
        text,
        '    rules = payload.get("non_inference_contract")\n',
        "\n\ndef verify_attribute_contracts",
        '''    rules = payload.get("non_inference_contract")
    ensure(isinstance(rules, list) and len(rules) == 7, "expected seven non-inference rules")
    receipt = payload.get("import_receipt")
    if receipt is None:
        ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Observation Import", "next package differs")
    else:
        ensure(isinstance(receipt, dict), "import receipt must be an object")
        ensure(receipt.get("status") == "imported", "import receipt status differs")
        ensure((receipt.get("scalar_id_start"), receipt.get("scalar_id_end")) == (2568, 2949), "import receipt ID range differs")
        ensure(receipt.get("scalar_values") == 382, "import receipt scalar total differs")
        ensure(receipt.get("configurations") == 36, "import receipt configuration total differs")
        ensure(
            receipt.get("source_values")
            == {
                "src_pl_sandero_brochure_20260202": 40,
                "src_pl_jogger_brochure_20251217": 242,
                "src_pl_duster_mini_brochure_20251020": 100,
            },
            "import receipt source totals differ",
        )
        ensure(receipt.get("duster_4x4_status") == "deferred_without_exact_source_relationship", "Duster 4x4 receipt boundary differs")
        ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Import Closure Review", "next package differs")
''',
        "mapping report tail",
    )
    text = replace_function(
        text,
        "verify_current_dimension_boundaries(payload: Mapping[str, Any]) -> None:",
        "planned_rows",
        '''def verify_current_dimension_boundaries(payload: Mapping[str, Any]) -> None:
    _, models = active_configuration_models()
    values = rows(MASTER / "configuration_attribute_values.csv")
    brochure_generic = [
        row
        for row in values
        if row.get("source_code") in SOURCE_CODES and row.get("attribute_code") in ATTRIBUTE_CODES
    ]
    receipt = payload.get("import_receipt")
    if receipt is None:
        ensure(brochure_generic == [], "generic brochure dimensions were imported before the approved import package")
        current_by_model = {
            model: [
                row
                for row in values
                if models.get(row.get("configuration_code", "")) == model
                and row.get("attribute_code") in ATTRIBUTE_CODES
            ]
            for model in ("sandero_iii", "jogger", "duster_iii")
        }
        ensure(len(current_by_model["sandero_iii"]) == 10, "current exact Sandero dimension coverage differs")
        ensure(len({row["configuration_code"] for row in current_by_model["sandero_iii"]}) == 2, "current Sandero dimension configuration count differs")
        ensure(current_by_model["jogger"] == [], "Jogger generic dimensions unexpectedly already imported")
        ensure(current_by_model["duster_iii"] == [], "Duster generic dimensions unexpectedly already imported")
        ensure(max(int(row["id"]) for row in values) == 2567, "configuration value ID boundary differs")
        return

    ensure(len(brochure_generic) == 382, "approved generic brochure dimension total differs")
    ensure([int(row["id"]) for row in brochure_generic] == list(range(2568, 2950)), "approved dimension IDs are not contiguous")
    ensure(
        Counter(row.get("source_code", "") for row in brochure_generic)
        == Counter(
            {
                "src_pl_sandero_brochure_20260202": 40,
                "src_pl_jogger_brochure_20251217": 242,
                "src_pl_duster_mini_brochure_20251020": 100,
            }
        ),
        "approved dimension source distribution differs",
    )
    current_by_model = {
        model: [
            row
            for row in values
            if models.get(row.get("configuration_code", "")) == model
            and row.get("attribute_code") in ATTRIBUTE_CODES
        ]
        for model in ("sandero_iii", "jogger", "duster_iii")
    }
    ensure(len(current_by_model["sandero_iii"]) == 50, "post-import Sandero dimension coverage differs")
    ensure(len({row["configuration_code"] for row in current_by_model["sandero_iii"]}) == 4, "post-import Sandero configuration count differs")
    ensure(len(current_by_model["jogger"]) == 242, "post-import Jogger dimension coverage differs")
    ensure(len({row["configuration_code"] for row in current_by_model["jogger"]}) == 22, "post-import Jogger configuration count differs")
    ensure(len(current_by_model["duster_iii"]) == 100, "post-import Duster dimension coverage differs")
    ensure(len({row["configuration_code"] for row in current_by_model["duster_iii"]}) == 10, "post-import Duster configuration count differs")
    ensure(max(int(row["id"]) for row in values) == 2949, "configuration value ID boundary differs")
''',
    )
    text = replace_segment(
        text,
        "def check() -> None:\n",
        "\n\ndef main",
        '''def check() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_attribute_contracts()
    verify_projection_scopes()
    verify_current_dimension_boundaries(payload)
    verify_import_plan(payload)
    verify_residual_receipt()
''',
        "mapping check",
    )
    path.write_text(text, encoding="utf-8")


def normalize_residual_verifier() -> None:
    path = ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py"
    text = path.read_text(encoding="utf-8")
    text = replace_segment(
        text,
        '    rules = payload.get("non_inference_contract")\n',
        "\n\ndef verify_partition",
        '''    rules = payload.get("non_inference_contract")
    ensure(isinstance(rules, list) and len(rules) == 6, "expected six non-inference rules")
    receipt = payload.get("follow_up_import_receipt")
    if receipt is None:
        ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Semantic Mapping Review", "next package differs")
    else:
        ensure(isinstance(receipt, dict), "follow-up import receipt must be an object")
        ensure(receipt.get("status") == "imported_with_documented_deferral", "follow-up import status differs")
        ensure(receipt.get("scalar_values") == 382, "follow-up scalar total differs")
        ensure(set(receipt.get("resolved_classifications", [])) == {"sandero_dimensions_and_cargo", "jogger_dimensions_and_cargo"}, "resolved follow-up classifications differ")
        ensure(receipt.get("partially_resolved_classifications") == ["duster_wltp_placeholders_and_dimensions"], "partial follow-up classification differs")
        ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Import Closure Review", "next package differs")
''',
        "residual report tail",
    )
    text = replace_function(
        text,
        "verify_dimension_coverage(payload: Mapping[str, Any]) -> None:",
        "verify_non_import_boundaries",
        '''def verify_dimension_coverage(payload: Mapping[str, Any]) -> None:
    models = active_configuration_models()
    values = rows(MASTER / "configuration_attribute_values.csv")
    selected: dict[str, list[dict[str, str]]] = {model: [] for model in MODEL_CODES}
    for row in values:
        model = models.get(row.get("configuration_code", ""), "")
        if model in selected and row.get("attribute_code") in CORE_DIMENSIONS:
            selected[model].append(row)

    receipt = payload.get("follow_up_import_receipt")
    if receipt is None:
        ensure(len(selected["sandero_iii"]) == 10, "Sandero exact dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["sandero_iii"]}) == 2, "Sandero exact dimension configuration count differs")
        ensure(len(selected["sandero_stepway_iii"]) == 25, "Stepway exact dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}) == 5, "Stepway exact dimension configuration count differs")
        ensure(selected["jogger"] == [], "Jogger dimensions unexpectedly already imported")
        ensure(len(selected["bigster"]) == 140, "Bigster exact dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["bigster"]}) == 14, "Bigster exact dimension configuration count differs")
        ensure(selected["duster_iii"] == [], "Duster core dimensions unexpectedly already imported")
    else:
        ensure(len(selected["sandero_iii"]) == 50, "post-import Sandero dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["sandero_iii"]}) == 4, "post-import Sandero configuration count differs")
        ensure(len(selected["sandero_stepway_iii"]) == 25, "Stepway exact dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}) == 5, "Stepway exact dimension configuration count differs")
        ensure(len(selected["jogger"]) == 242, "post-import Jogger dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["jogger"]}) == 22, "post-import Jogger configuration count differs")
        ensure(len(selected["bigster"]) == 140, "Bigster exact dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["bigster"]}) == 14, "Bigster exact dimension configuration count differs")
        ensure(len(selected["duster_iii"]) == 100, "post-import Duster dimension coverage differs")
        ensure(len({row["configuration_code"] for row in selected["duster_iii"]}) == 10, "post-import Duster configuration count differs")

    turning = [
        row
        for row in values
        if models.get(row.get("configuration_code", "")) == "duster_iii"
        and row.get("attribute_code") == "turning_circle_wheel_track"
        and row.get("source_code") == "src_pl_duster_mini_brochure_20251020"
    ]
    ensure(len(turning) == 10, "Duster basis-qualified turning coverage differs")
''',
    )
    text = replace_function(
        text,
        "verify_non_import_boundaries(payload: Mapping[str, Any]) -> None:",
        "verify_source_closure",
        '''def verify_non_import_boundaries(payload: Mapping[str, Any]) -> None:
    values = rows(MASTER / "configuration_attribute_values.csv")
    sources = {
        "src_pl_sandero_brochure_20260202",
        "src_pl_sandero_stepway_brochure_20260202",
        "src_pl_jogger_brochure_20251217",
        "src_pl_bigster_brochure_20251210",
        "src_pl_duster_mini_brochure_20251020",
    }
    receipt = payload.get("follow_up_import_receipt")
    generic = [
        row
        for row in values
        if row.get("source_code") in sources and row.get("attribute_code") in CORE_DIMENSIONS
    ]
    if receipt is None:
        ensure(generic == [], "generic brochure dimensions were imported before semantic mapping review")
    else:
        approved = [row for row in generic if 2568 <= int(row["id"]) <= 2949]
        ensure(len(approved) == 382 and len(generic) == 382, "approved generic dimension package differs")
        ensure([int(row["id"]) for row in approved] == list(range(2568, 2950)), "approved dimension IDs differ")
        ensure(
            Counter(row.get("source_code", "") for row in approved)
            == Counter(
                {
                    "src_pl_sandero_brochure_20260202": 40,
                    "src_pl_jogger_brochure_20251217": 242,
                    "src_pl_duster_mini_brochure_20251020": 100,
                }
            ),
            "approved dimension source totals differ",
        )
        configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
        duster = [row for row in approved if row.get("source_code") == "src_pl_duster_mini_brochure_20251020"]
        ensure(all("4x2" in configurations[row["configuration_code"]].get("powertrain_label", "") for row in duster), "Duster 4x4 dimension was imported")
        ensure(not any(row.get("attribute_code") in {"approach_angle", "departure_angle"} for row in approved), "seatback angle was imported as an off-road angle")

    ensure(
        not any(
            row.get("source_code") == "src_pl_jogger_brochure_20251217"
            and row.get("attribute_code") in {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
            for row in values
        ),
        "ambiguous Jogger mass evidence was imported",
    )
''',
    )
    text = replace_segment(
        text,
        "def check() -> None:\n",
        "\n\ndef main",
        '''def check() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_partition()
    verify_active_scopes()
    verify_dimension_coverage(payload)
    verify_non_import_boundaries(payload)
    verify_source_closure()
''',
        "residual check",
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    normalize_mapping_verifier()
    normalize_residual_verifier()
    print("PASS: generic dimension receipt verifiers normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
