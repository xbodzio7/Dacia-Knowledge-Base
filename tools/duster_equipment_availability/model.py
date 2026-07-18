"""Source contract for Duster equipment availability."""
from __future__ import annotations

from collections import Counter

from .constants import (
    CURRENT, DATE, LEGACY, MASTER, MATRICES, MATRIX_FIELDS, SOURCE, SOURCE_CODE,
    SOURCE_SHA256, STATUSES, STATUS_COUNTS, ContractError, file_sha256,
    read_rows, require_header,
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
            for field in MATRIX_FIELDS[3:12]:
                if row[field].strip() not in STATUSES:
                    raise ContractError(f"invalid status for {code}/{field}")
            row["attribute_code"] = code
            result.append(row)
    if len(result) != 58:
        raise ContractError(f"expected 58 matrix attributes, found {len(result)}")
    return result


def duster_configurations() -> list[dict[str, str]]:
    result = [
        row for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
        and row.get("version_code", "").startswith("duster_iii_")
    ]
    if len(result) != 24:
        raise ContractError(f"expected 24 Duster configurations, found {len(result)}")
    return result


def matrix_status(matrix: dict[str, str], configuration: dict[str, str]) -> str:
    code = configuration["code"]
    if any(token in code for token in LEGACY):
        group = "legacy"
    elif any(token in code for token in CURRENT):
        group = "current"
    else:
        raise ContractError(f"configuration is outside source matrices: {code}")
    trim = configuration["version_code"].removeprefix("duster_iii_")
    status = matrix.get(f"{group}_{trim}", "").strip()
    if status not in STATUSES:
        raise ContractError(f"missing status for {code}/{matrix['attribute_code']}")
    return status


def generated_rows() -> list[dict[str, str]]:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    matrices = load_matrices()
    active_attributes = {
        row["code"] for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    missing = sorted({row["attribute_code"] for row in matrices} - active_attributes)
    if missing:
        raise ContractError("inactive or missing attributes: " + ", ".join(missing))
    active_statuses = {
        row["code"] for row in read_rows(MASTER / "equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }
    if not STATUSES <= active_statuses:
        raise ContractError("required availability statuses are not active")

    result: list[dict[str, str]] = []
    for configuration in duster_configurations():
        for matrix in matrices:
            attribute = matrix["attribute_code"]
            note = (
                f"Source pages {matrix['source_pages']}: {matrix['source_label']}. "
                "Version-level status expanded to this source-backed configuration."
            )
            if matrix["notes"].strip():
                note += f" {matrix['notes'].strip()}."
            result.append({
                "code": f"{configuration['code']}_{attribute}_20260206",
                "configuration_code": configuration["code"],
                "attribute_code": attribute,
                "availability_status": matrix_status(matrix, configuration),
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": note,
            })

    keys = [(row["configuration_code"], row["attribute_code"]) for row in result]
    if len(result) != 1392 or len(keys) != len(set(keys)):
        raise ContractError("expected 1,392 unique generated rows")
    if dict(Counter(row["availability_status"] for row in result)) != STATUS_COUNTS:
        raise ContractError("unexpected availability status distribution")
    counts = Counter(row["configuration_code"] for row in result)
    if len(counts) != 24 or set(counts.values()) != {58}:
        raise ContractError("each Duster configuration must receive 58 attributes")
    return result
