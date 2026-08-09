from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
IMPORT_DATE = "2026-08-09"
IMPORT_CODE_MARKER = "20260809"


def read_rows() -> tuple[list[str], list[dict[str, str]]]:
    with VALUES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(fields: list[str], rows: list[dict[str, str]]) -> None:
    with VALUES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        (row.get("configuration_code") or "").strip(),
        (row.get("attribute_code") or "").strip(),
        (row.get("fuel_type_code") or "").strip(),
        (row.get("gear_number") or "").strip(),
    )


def is_current_import(row: dict[str, str]) -> bool:
    return (
        (row.get("observation_date") or "").strip() == IMPORT_DATE
        and IMPORT_CODE_MARKER in (row.get("code") or "")
    )


def reconcile(apply: bool = False) -> int:
    fields, rows = read_rows()
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[canonical_key(row)].append(row)

    remove_ids: set[str] = set()
    reconciled = 0

    for key, same in groups.items():
        if len(same) <= 1:
            continue

        imported = [row for row in same if is_current_import(row)]
        prior = [row for row in same if not is_current_import(row)]

        # This tool is intentionally narrow: it only resolves a collision between
        # one pre-existing canonical current value and one value imported from the
        # saved 2026-08-09 configurator PDFs. Any other shape remains an error.
        if len(imported) != 1 or len(prior) != 1 or len(same) != 2:
            raise SystemExit(
                "Unsafe canonical collision; refusing automatic reconciliation: "
                f"key={key!r}, rows={[row.get('id') for row in same]!r}"
            )

        current = imported[0]
        existing = prior[0]

        # Preserve the stable row identity/code in case anything refers to it,
        # while replacing the current value and its provenance with the newer,
        # explicit saved-configurator observation.
        for field in fields:
            if field in {"id", "code", "configuration_code", "attribute_code", "fuel_type_code", "gear_number"}:
                continue
            existing[field] = current.get(field, "")

        remove_ids.add(current.get("id", ""))
        reconciled += 1
        print(
            "reconciled canonical current value: "
            f"configuration={key[0]} attribute={key[1]} "
            f"fuel={key[2] or '-'} gear={key[3] or '-'} "
            f"kept_id={existing.get('id')} removed_import_id={current.get('id')}"
        )

    if apply and reconciled:
        rows = [row for row in rows if row.get("id", "") not in remove_ids]
        write_rows(fields, rows)

    print(f"canonical current-value reconciliations: {reconciled}")
    return reconciled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    reconcile(apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
