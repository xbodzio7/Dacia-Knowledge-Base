#!/usr/bin/env python3
"""Verify the visual semantic mapping review for brochure dimension diagrams."""

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
REPORT = REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json"
RESIDUAL_VERIFIER = ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py"

SOURCE_CODES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_jogger_brochure_20251217",
    "src_pl_duster_mini_brochure_20251020",
}
ATTRIBUTE_CODES = {
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
}
SANDERO_MAPPING = {
    "overall_height": 1496,
    "front_track": 1533,
    "overall_width": 1853,
    "overall_width_with_mirrors": 2012,
    "rear_track": 1519,
    "front_overhang": 833,
    "wheelbase": 2604,
    "rear_overhang": 665,
    "overall_length": 4102,
    "ground_clearance": 162,
}
JOGGER_MAPPING = {
    "roof_height_with_rails": 1689,
    "overall_height": 1630,
    "front_track": 1520,
    "overall_width": 1853,
    "overall_width_with_mirrors": 2012,
    "rear_track": 1509,
    "front_overhang": 833,
    "wheelbase": 2898,
    "rear_overhang": 819,
    "overall_length": 4550,
    "ground_clearance": 200,
}
DUSTER_4X2_MAPPING = {
    "roof_height_with_rails": 1656,
    "front_track": 1574,
    "overall_width": 1813,
    "overall_width_with_mirrors": 2069,
    "rear_track": 1547,
    "ground_clearance": 209,
    "front_overhang": 857,
    "wheelbase": 2657,
    "rear_overhang": 828,
    "overall_length": 4343,
}
DUSTER_4X4_MAPPING = {
    "roof_height_with_rails": 1661,
    "front_track": 1573,
    "overall_width": 1813,
    "overall_width_with_mirrors": 2069,
    "rear_track": 1562,
    "ground_clearance": 217,
    "front_overhang": 857,
    "wheelbase": 2657,
    "rear_overhang": 828,
    "overall_length": 4343,
}
EXPECTED_RELATIONSHIPS = {
    "src_pl_sandero_brochure_20260202": 4,
    "src_pl_jogger_brochure_20251217": 22,
    "src_pl_duster_mini_brochure_20251020": 10,
}


class ReviewError(RuntimeError):
    """Raised when the visual mapping contract drifts."""


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


def mapping(items: Any) -> dict[str, int]:
    ensure(isinstance(items, list), "mapping must be a list")
    result: dict[str, int] = {}
    for item in items:
        ensure(isinstance(item, dict), "mapping item must be an object")
        code = str(item.get("attribute_code", ""))
        ensure(code and code not in result, f"duplicate or empty mapping attribute: {code}")
        ensure(item.get("unit") == "mm", f"mapping unit differs: {code}")
        value = item.get("value")
        ensure(isinstance(value, int), f"mapping value must be integer: {code}")
        ensure(str(item.get("visual_semantic", "")).strip(), f"mapping semantic is empty: {code}")
        result[code] = value
    return result


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported mapping review version")
    ensure(payload.get("kind") == "brochure_generic_dimensions_semantic_mapping_review", "unexpected mapping review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "mapping review is not complete")
    ensure(payload.get("method") == "visual_pdf_diagram_review", "mapping review method differs")
    ensure(payload.get("source_review") == "official_brochure_residual_evidence_review.json", "source review differs")
    ensure(
        payload.get("scope")
        == {
            "sources": 3,
            "source_pages": 3,
            "active_configurations": 53,
            "source_related_configurations": 36,
            "import_eligible_configurations": 36,
        },
        "mapping scope differs",
    )

    sources = payload.get("sources")
    ensure(isinstance(sources, list) and len(sources) == 3, "expected three source mappings")
    by_source = {str(item.get("source_code", "")): item for item in sources if isinstance(item, dict)}
    ensure(set(by_source) == SOURCE_CODES, "source mapping set differs")

    sandero = by_source["src_pl_sandero_brochure_20260202"]
    ensure(sandero.get("page") == 20, "Sandero source page differs")
    ensure(sandero.get("model_code") == "sandero_iii", "Sandero model differs")
    ensure((sandero.get("active_configurations"), sandero.get("source_related_configurations"), sandero.get("import_eligible_configurations")) == (4, 4, 4), "Sandero projection scope differs")
    ensure(mapping(sandero.get("mappings")) == SANDERO_MAPPING, "Sandero visual mapping differs")
    ensure(sandero.get("planned_scalar_values") == 40, "Sandero planned scalar total differs")

    jogger = by_source["src_pl_jogger_brochure_20251217"]
    ensure(jogger.get("page") == 22, "Jogger source page differs")
    ensure(jogger.get("model_code") == "jogger", "Jogger model differs")
    ensure((jogger.get("active_configurations"), jogger.get("source_related_configurations"), jogger.get("import_eligible_configurations")) == (22, 22, 22), "Jogger projection scope differs")
    ensure(mapping(jogger.get("mappings")) == JOGGER_MAPPING, "Jogger visual mapping differs")
    ensure(jogger.get("planned_scalar_values") == 242, "Jogger planned scalar total differs")

    duster = by_source["src_pl_duster_mini_brochure_20251020"]
    ensure(duster.get("page") == 24, "Duster source page differs")
    ensure(duster.get("model_code") == "duster_iii", "Duster model differs")
    ensure((duster.get("active_configurations"), duster.get("source_related_configurations"), duster.get("import_eligible_configurations")) == (27, 10, 10), "Duster projection scope differs")
    ensure(mapping(duster.get("eligible_4x2_mappings")) == DUSTER_4X2_MAPPING, "Duster 4x2 visual mapping differs")
    ensure(mapping(duster.get("deferred_4x4_mappings")) == DUSTER_4X4_MAPPING, "Duster 4x4 visual mapping differs")
    ensure(duster.get("planned_scalar_values") == 100, "Duster planned scalar total differs")
    ensure(duster.get("deferred_scalar_values") == 0, "Duster deferred scalar total differs")
    ensure(duster.get("deferred_mapping_template_values") == 10, "Duster deferred template total differs")

    contract = payload.get("attribute_contract")
    ensure(isinstance(contract, dict), "attribute contract is missing")
    ensure(set(contract.get("codes", [])) == ATTRIBUTE_CODES, "attribute contract code set differs")
    ensure((contract.get("data_type"), contract.get("unit"), contract.get("new_attributes")) == ("integer", "mm", 0), "attribute contract differs")

    plan = payload.get("import_plan")
    ensure(
        plan
        == {
            "sources": 3,
            "configurations": 36,
            "scalar_values": 382,
            "sandero_scalar_values": 40,
            "jogger_scalar_values": 242,
            "duster_4x2_scalar_values": 100,
            "duster_4x4_scalar_values": 0,
            "mode": "append_only_historical_observations",
        },
        "import plan differs",
    )
    excluded = payload.get("excluded_visual_values")
    ensure(isinstance(excluded, list) and len(excluded) == 3, "expected three exclusion records")
    ensure({str(item.get("source_code", "")) for item in excluded if isinstance(item, dict)} == SOURCE_CODES, "exclusion source set differs")
    duster_exclusion = next(item for item in excluded if item.get("source_code") == "src_pl_duster_mini_brochure_20251020")
    ensure(14 in duster_exclusion.get("values", []), "Duster seatback angle exclusion is missing")
    ensure("approach_angle" in str(duster_exclusion.get("reason", "")), "Duster off-road non-mapping explanation is missing")

    rules = payload.get("non_inference_contract")
    ensure(isinstance(rules, list) and len(rules) == 7, "expected seven non-inference rules")
    receipt = payload.get("import_receipt")
    if receipt is None:
        receipt = payload.get("import_receipt")
    if receipt is None:
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


def verify_attribute_contracts() -> None:
    attributes = {row["code"]: row for row in rows(MASTER / "attributes.csv")}
    for code in ATTRIBUTE_CODES:
        row = attributes.get(code)
        ensure(row is not None, f"dimension attribute missing: {code}")
        ensure(row.get("status") == "active", f"dimension attribute inactive: {code}")
        ensure((row.get("data_type"), row.get("unit")) == ("integer", "mm"), f"dimension attribute contract differs: {code}")


def active_configuration_models() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    configurations = {
        row["code"]: row
        for row in rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
    models = {
        code: versions.get(row.get("version_code", ""), {}).get("model_code", "")
        for code, row in configurations.items()
    }
    return configurations, models


def source_relationship_targets() -> dict[str, set[str]]:
    return {
        source: {
            row.get("configuration_code", "")
            for row in rows(MASTER / "source_configurations.csv")
            if row.get("source_code") == source and row.get("relationship") == "brochure_technical_data_for"
        }
        for source in SOURCE_CODES
    }


def verify_projection_scopes() -> None:
    configurations, models = active_configuration_models()
    model_counts = Counter(models.values())
    ensure(model_counts["sandero_iii"] == 4, "active Sandero count differs")
    ensure(model_counts["jogger"] == 22, "active Jogger count differs")
    ensure(model_counts["duster_iii"] == 27, "active Duster count differs")

    targets = source_relationship_targets()
    ensure({source: len(codes) for source, codes in targets.items()} == EXPECTED_RELATIONSHIPS, "source relationship counts differ")
    ensure(all(models.get(code) == "sandero_iii" for code in targets["src_pl_sandero_brochure_20260202"]), "Sandero relationship targets differ")
    ensure(all(models.get(code) == "jogger" for code in targets["src_pl_jogger_brochure_20251217"]), "Jogger relationship targets differ")
    duster_targets = targets["src_pl_duster_mini_brochure_20251020"]
    ensure(all(models.get(code) == "duster_iii" for code in duster_targets), "Duster relationship targets differ")
    ensure(all("4x2" in configurations[code].get("powertrain_label", "") for code in duster_targets), "Duster import target is not 4x2")
    active_duster_4x4 = {
        code
        for code, row in configurations.items()
        if models.get(code) == "duster_iii" and "4x4" in row.get("powertrain_label", "")
    }
    ensure(len(active_duster_4x4) == 3, "active Duster 4x4 count differs")
    ensure(active_duster_4x4.isdisjoint(duster_targets), "Duster 4x4 target was broadened into source relationships")


def verify_current_dimension_boundaries(payload: Mapping[str, Any]) -> None:
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

def planned_rows(payload: Mapping[str, Any]) -> list[tuple[str, str, int]]:
    targets = source_relationship_targets()
    sources = {str(item["source_code"]): item for item in payload["sources"]}
    result: list[tuple[str, str, int]] = []
    for configuration in sorted(targets["src_pl_sandero_brochure_20260202"]):
        for code, value in sorted(mapping(sources["src_pl_sandero_brochure_20260202"]["mappings"]).items()):
            result.append((configuration, code, value))
    for configuration in sorted(targets["src_pl_jogger_brochure_20251217"]):
        for code, value in sorted(mapping(sources["src_pl_jogger_brochure_20251217"]["mappings"]).items()):
            result.append((configuration, code, value))
    for configuration in sorted(targets["src_pl_duster_mini_brochure_20251020"]):
        for code, value in sorted(mapping(sources["src_pl_duster_mini_brochure_20251020"]["eligible_4x2_mappings"]).items()):
            result.append((configuration, code, value))
    return result


def verify_import_plan(payload: Mapping[str, Any]) -> None:
    planned = planned_rows(payload)
    ensure(len(planned) == 382, "planned scalar row total differs")
    ensure(len(set(planned)) == 382, "planned scalar rows are not unique")
    ensure(Counter(code for _, code, _ in planned)["overall_length"] == 36, "planned overall length distribution differs")
    ensure(Counter(code for _, code, _ in planned)["roof_height_with_rails"] == 32, "planned roof-height distribution differs")
    ensure(Counter(code for _, code, _ in planned)["overall_height"] == 26, "planned overall-height distribution differs")
    ensure(list(range(2568, 2950))[-1] == 2949, "planned scalar ID boundary differs")


def verify_residual_receipt() -> None:
    completed = subprocess.run(
        [sys.executable, str(RESIDUAL_VERIFIER), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    ensure(completed.returncode == 0, completed.stderr or completed.stdout)


def check() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_attribute_contracts()
    verify_projection_scopes()
    verify_current_dimension_boundaries(payload)
    verify_import_plan(payload)
    verify_residual_receipt()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ReviewError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print("PASS: brochure generic dimensions semantic mapping review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
