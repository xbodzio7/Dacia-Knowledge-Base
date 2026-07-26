#!/usr/bin/env python3
"""Update historical review verifiers after the approved generic dimension import."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0 and new in text:
        return text
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, next_name: str, replacement: str) -> str:
    start_token = f"def {name}"
    end_token = f"\n\ndef {next_name}"
    start = text.find(start_token)
    if start < 0:
        if replacement.strip() in text:
            return text
        raise RuntimeError(f"function missing: {name}")
    end = text.find(end_token, start)
    if end < 0:
        raise RuntimeError(f"next function missing after {name}: {next_name}")
    return text[:start] + replacement.rstrip() + text[end:]


def patch_mapping_verifier() -> None:
    path = ROOT / "tools" / "review_brochure_generic_dimensions_semantic_mapping_20260726.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Observation Import", "next package differs")\n',
        '''    receipt = payload.get("import_receipt")
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
        "mapping next package",
    )
    text = replace_function(
        text,
        "verify_current_dimension_boundaries() -> None:",
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
    text = replace_once(
        text,
        "    verify_current_dimension_boundaries()\n",
        "    verify_current_dimension_boundaries(payload)\n",
        "mapping boundary call",
    )
    path.write_text(text, encoding="utf-8")


def patch_residual_verifier() -> None:
    path = ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    ensure(payload.get("next_package", {}).get("name") == "Brochure Generic Dimensions Semantic Mapping Review", "next package differs")\n',
        '''    receipt = payload.get("follow_up_import_receipt")
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
        "residual next package",
    )
    text = replace_function(
        text,
        "verify_dimension_coverage() -> None:",
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
        "verify_non_import_boundaries() -> None:",
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
    text = replace_once(text, "    verify_dimension_coverage()\n", "    verify_dimension_coverage(payload)\n", "residual coverage call")
    text = replace_once(text, "    verify_non_import_boundaries()\n", "    verify_non_import_boundaries(payload)\n", "residual boundary call")
    path.write_text(text, encoding="utf-8")


def patch_gap_closure_verifier() -> None:
    path = ROOT / "tools" / "review_official_brochure_technical_gap_resolution_closure_20260726.py"
    text = path.read_text(encoding="utf-8")
    text = replace_function(
        text,
        "verify_current_coverage() -> None:",
        "verify_non_import_boundaries",
        '''def verify_current_coverage() -> None:
    scalar = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") in SOURCES
    ]
    ranges = [
        row
        for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
        if row.get("source_code") in SOURCES
    ]
    follow_up = (REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json")
    imported = False
    if follow_up.is_file():
        imported = load_json(follow_up).get("import_receipt", {}).get("status") == "imported"
    expected_scalar = Counter(EXPECTED_SCALAR_BY_SOURCE)
    expected_total = 736
    if imported:
        expected_scalar.update(
            {
                "src_pl_sandero_brochure_20260202": 40,
                "src_pl_jogger_brochure_20251217": 242,
                "src_pl_duster_mini_brochure_20251020": 100,
            }
        )
        expected_total = 1118
    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")
    ensure(len(ranges) == 68, "expected exactly 68 brochure ranges")
    ensure(Counter(row.get("source_code", "") for row in scalar) == expected_scalar, "master source scalar totals differ")
    ensure(Counter(row.get("source_code", "") for row in ranges) == EXPECTED_RANGE_BY_SOURCE, "master source range totals differ")

    priority_scalar = [row for row in scalar if 2189 <= int(row["id"]) <= 2567]
    priority_ranges = [row for row in ranges if 177 <= int(row["id"]) <= 244]
    ensure(len(priority_scalar) == 379, "priority scalar receipt differs")
    ensure([int(row["id"]) for row in priority_scalar] == list(range(2189, 2568)), "priority scalar IDs are not contiguous")
    ensure(len(priority_ranges) == 68, "priority range receipt differs")
    ensure([int(row["id"]) for row in priority_ranges] == list(range(177, 245)), "priority range IDs are not contiguous")
    if imported:
        dimensions = [row for row in scalar if 2568 <= int(row["id"]) <= 2949]
        ensure(len(dimensions) == 382, "generic dimension follow-up receipt differs")
        ensure([int(row["id"]) for row in dimensions] == list(range(2568, 2950)), "generic dimension IDs differ")
''',
    )
    text = replace_function(
        text,
        "verify_non_import_boundaries() -> None:",
        "verify_receipts",
        '''def verify_non_import_boundaries() -> None:
    scalar = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") in SOURCES
    ]
    jogger_mass = {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
    ensure(
        not any(
            row.get("source_code") == "src_pl_jogger_brochure_20251217"
            and row.get("attribute_code") in jogger_mass
            for row in scalar
        ),
        "ambiguous Jogger mass evidence was imported",
    )
    placeholder_attributes = {"co2_emissions", "fuel_consumption_combined"}
    ensure(
        not any(
            row.get("source_code") in {"src_pl_jogger_brochure_20251217", "src_pl_sandero_brochure_20260202"}
            and row.get("attribute_code") in placeholder_attributes
            for row in scalar
        ),
        "blank or placeholder WLTP evidence was imported",
    )
    approved_attributes = {
        "overall_length", "overall_width", "overall_width_with_mirrors", "overall_height",
        "roof_height_with_rails", "wheelbase", "ground_clearance", "front_track",
        "rear_track", "front_overhang", "rear_overhang",
    }
    dimensions = [row for row in scalar if row.get("attribute_code") in approved_attributes]
    if dimensions:
        approved = [row for row in dimensions if 2568 <= int(row["id"]) <= 2949]
        ensure(len(dimensions) == 382 and len(approved) == 382, "unreviewed generic brochure dimension was imported")
        ensure(
            Counter(row.get("source_code", "") for row in approved)
            == Counter(
                {
                    "src_pl_sandero_brochure_20260202": 40,
                    "src_pl_jogger_brochure_20251217": 242,
                    "src_pl_duster_mini_brochure_20251020": 100,
                }
            ),
            "approved generic dimension source totals differ",
        )
        ensure(not any(row.get("attribute_code") in {"approach_angle", "departure_angle"} for row in approved), "seatback angle was imported as an off-road angle")
''',
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_mapping_verifier()
    patch_residual_verifier()
    patch_gap_closure_verifier()
    print("PASS: generic dimension import receipt verifiers updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
