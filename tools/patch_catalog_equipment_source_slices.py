#!/usr/bin/env python3
"""Patch the recovered catalogue importer to accept legacy equipment cells."""

from __future__ import annotations

from pathlib import Path

PATH = Path(__file__).resolve().parent / "import_sandero_stepway_catalog_completion.py"

OLD = '''def _apply_equipment(path: Path, *, apply: bool) -> int:
    fields, rows = _read_csv(path)
    if fields != list(FIELDS[path.name]):
        raise CompletionError(f"unexpected header for {path}")
    by_semantic = {
        (row["source_code"], row["configuration_code"], row["attribute_code"]): row
        for row in rows
    }
    by_code = {row["code"]: row for row in rows}
    next_id = _next_id(rows)
    added = 0
    for expected in _equipment_rows():
        semantic = (
            expected["source_code"],
            expected["configuration_code"],
            expected["attribute_code"],
        )
        current = by_semantic.get(semantic)
        if current is not None:
            if current["availability_status"] != expected["availability_status"]:
                raise CompletionError(
                    "existing equipment status differs for "
                    f"{expected['configuration_code']}:{expected['attribute_code']}: "
                    f"{current['availability_status']} != {expected['availability_status']}"
                )
            continue
        if expected["code"] in by_code:
            raise CompletionError(f"equipment code collision: {expected['code']}")
        if not apply:
            raise CompletionError(
                f"missing equipment row {expected['configuration_code']}:{expected['attribute_code']}"
            )
        row = {"id": str(next_id), **expected}
        next_id += 1
        rows.append(row)
        by_semantic[semantic] = row
        by_code[row["code"]] = row
        added += 1
    if apply and added:
        _write_csv(path, fields, rows)
    return added
'''

NEW = '''def _apply_equipment(path: Path, *, apply: bool) -> int:
    fields, rows = _read_csv(path)
    if fields != list(FIELDS[path.name]):
        raise CompletionError(f"unexpected header for {path}")
    by_semantic = {
        (row["source_code"], row["configuration_code"], row["attribute_code"]): row
        for row in rows
    }
    by_code = {row["code"]: row for row in rows}
    next_id = _next_id(rows)
    added = 0
    for expected in _equipment_rows():
        semantic = (
            expected["source_code"],
            expected["configuration_code"],
            expected["attribute_code"],
        )
        current = by_semantic.get(semantic)
        if current is None:
            legacy = by_semantic.get(
                (
                    RAW_PRICE_SOURCE,
                    expected["configuration_code"],
                    expected["attribute_code"],
                )
            )
            if legacy is not None and legacy["observation_date"] == OBSERVATION_DATE:
                current = legacy
        if current is not None:
            if current["availability_status"] != expected["availability_status"]:
                raise CompletionError(
                    "existing equipment status differs for "
                    f"{expected['configuration_code']}:{expected['attribute_code']}: "
                    f"{current['availability_status']} != {expected['availability_status']}"
                )
            continue
        if expected["code"] in by_code:
            raise CompletionError(f"equipment code collision: {expected['code']}")
        if not apply:
            raise CompletionError(
                f"missing equipment row {expected['configuration_code']}:{expected['attribute_code']}"
            )
        row = {"id": str(next_id), **expected}
        next_id += 1
        rows.append(row)
        by_semantic[semantic] = row
        by_code[row["code"]] = row
        added += 1
    if apply and added:
        _write_csv(path, fields, rows)
    return added
'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if NEW in text:
        return 0
    if text.count(OLD) != 1:
        raise SystemExit("equipment importer block not found exactly once")
    updated = text.replace(OLD, NEW, 1)
    compile(updated, str(PATH), "exec")
    PATH.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
