"""Source contract for Jogger equipment availability."""
from __future__ import annotations
from collections import Counter
from .constants import (
    DATE, MASTER, MATRICES, MATRIX_FIELDS, SOURCE, SOURCE_CODE, SOURCE_SHA256,
    STATUSES, STATUS_COUNTS, ContractError, file_sha256, read_rows, require_header,
)


def load_matrices() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in MATRICES:
        require_header(path, MATRIX_FIELDS)
        for row in read_rows(path):
            code = row["attribute_code"].strip()
            if not code or code in seen:
                raise ContractError(f"blank or duplicate matrix attribute: {code!r}")
            seen.add(code)
            if not row["source_pages"].strip() or not row["source_label"].strip():
                raise ContractError(f"missing provenance for {code}")
            for field in MATRIX_FIELDS[3:8]:
                if row[field].strip() not in STATUSES:
                    raise ContractError(f"invalid status for {code}/{field}")
            row["attribute_code"] = code
            result.append(row)
    if len(result) != 53:
        raise ContractError(f"expected 53 matrix attributes, found {len(result)}")
    return result


def jogger_configurations() -> list[dict[str, str]]:
    result = [
        row for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active" and row.get("code", "").startswith("jogger_")
    ]
    if len(result) != 22:
        raise ContractError(f"expected 22 Jogger configurations, found {len(result)}")
    return result


def configuration_group(configuration: dict[str, str]) -> str:
    trim = configuration["version_code"].removeprefix("jogger_")
    if trim == "expression":
        return "expression_hybrid" if "_hybrid155_" in configuration["code"] else "expression_non_hybrid"
    if trim in {"essential", "extreme", "journey"}:
        return trim
    raise ContractError(f"configuration is outside source matrix: {configuration['code']}")


def matrix_status(matrix: dict[str, str], configuration: dict[str, str]) -> str:
    status = matrix.get(configuration_group(configuration), "").strip()
    if status not in STATUSES:
        raise ContractError(f"missing status for {configuration['code']}/{matrix['attribute_code']}")
    return status


def generated_rows() -> list[dict[str, str]]:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    matrices = load_matrices()
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    invalid = sorted(
        row["attribute_code"] for row in matrices
        if row["attribute_code"] not in attributes
        or attributes[row["attribute_code"]].get("status") != "active"
        or attributes[row["attribute_code"]].get("data_type") != "boolean"
    )
    if invalid:
        raise ContractError("inactive, missing or non-boolean attributes: " + ", ".join(invalid))
    active_statuses = {
        row["code"] for row in read_rows(MASTER / "enums/equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }
    if not STATUSES <= active_statuses:
        raise ContractError("required availability statuses are not active")
    configurations = jogger_configurations()
    source_pairs = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    if any((SOURCE_CODE, row["code"]) not in source_pairs for row in configurations):
        raise ContractError("Jogger source does not document every selected configuration")

    result: list[dict[str, str]] = []
    for configuration in configurations:
        for matrix in matrices:
            attribute = matrix["attribute_code"]
            note = (
                f"Source page {matrix['source_pages']}: {matrix['source_label']}. "
                "Trim-level status expanded only to this source-backed configuration."
            )
            if matrix["notes"].strip():
                note += f" {matrix['notes'].strip()}."
            result.append({
                "code": f"{configuration['code']}_{attribute}_20260401",
                "configuration_code": configuration["code"],
                "attribute_code": attribute,
                "availability_status": matrix_status(matrix, configuration),
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": note,
            })
    keys = [(row["configuration_code"], row["attribute_code"]) for row in result]
    if len(result) != 1166 or len(keys) != len(set(keys)):
        raise ContractError("expected 1,166 unique generated rows")
    if dict(Counter(row["availability_status"] for row in result)) != STATUS_COUNTS:
        raise ContractError("unexpected availability status distribution")
    counts = Counter(row["configuration_code"] for row in result)
    if len(counts) != 22 or set(counts.values()) != {53}:
        raise ContractError("each Jogger configuration must receive 53 attributes")
    return result
