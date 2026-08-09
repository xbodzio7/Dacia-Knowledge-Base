from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
CARGO_CONTEXTS = ROOT / "data/master/configuration_cargo_volume_contexts.csv"


def read_rows() -> tuple[list[str], list[dict[str, str]]]:
    with VALUES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_contextual_value_codes() -> set[str]:
    if not CARGO_CONTEXTS.is_file():
        return set()
    with CARGO_CONTEXTS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            (row.get("configuration_attribute_value_code") or "").strip()
            for row in reader
            if (row.get("configuration_attribute_value_code") or "").strip()
        }


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


def load_baseline_codes(path: Path) -> set[str]:
    if not path.is_file():
        raise SystemExit(f"Baseline code snapshot does not exist: {path}")
    codes = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    if not codes:
        raise SystemExit(f"Baseline code snapshot is empty: {path}")
    return codes


def reconcile(baseline_codes: set[str], apply: bool = False) -> int:
    fields, rows = read_rows()
    contextual_codes = read_contextual_value_codes()
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[canonical_key(row)].append(row)

    remove_ids: set[str] = set()
    reconciled = 0

    for key, same in groups.items():
        if len(same) <= 1:
            continue

        # Cargo-volume values with explicit measurement/seat/spare-wheel context
        # are intentionally multi-valued. They are not canonical collisions and
        # must be evaluated through configuration_cargo_volume_contexts.csv.
        relevant = [
            row
            for row in same
            if (row.get("code") or "").strip() not in contextual_codes
        ]
        if len(relevant) <= 1:
            continue

        imported = [
            row
            for row in relevant
            if (row.get("code") or "").strip() not in baseline_codes
        ]

        # Pre-existing multi-source groups are valid repository history and are
        # outside this repair's scope. Only a collision introduced by one of the
        # two current-PDF importers may be reconciled here.
        if not imported:
            continue

        prior = [
            row
            for row in relevant
            if (row.get("code") or "").strip() in baseline_codes
        ]

        # Stay deliberately narrow. A more complicated shape can represent a
        # real source conflict or an importer bug and must remain visible rather
        # than being guessed away automatically.
        if len(imported) != 1 or len(prior) != 1 or len(relevant) != 2:
            raise SystemExit(
                "Unsafe canonical collision introduced by current PDF import; "
                "refusing automatic reconciliation: "
                f"key={key!r}, prior_codes={[row.get('code') for row in prior]!r}, "
                f"imported_codes={[row.get('code') for row in imported]!r}"
            )

        current = imported[0]
        existing = prior[0]

        # Preserve the stable canonical identity/code, but supersede its current
        # value and provenance with the newer explicit saved-configurator fact.
        for field in fields:
            if field in {
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "gear_number",
            }:
                continue
            existing[field] = current.get(field, "")

        remove_ids.add(current.get("id", ""))
        reconciled += 1
        print(
            "reconciled canonical current value: "
            f"configuration={key[0]} attribute={key[1]} "
            f"fuel={key[2] or '-'} gear={key[3] or '-'} "
            f"kept_code={existing.get('code')} removed_import_code={current.get('code')}"
        )

    if apply and reconciled:
        rows = [row for row in rows if row.get("id", "") not in remove_ids]
        write_rows(fields, rows)

    print(f"canonical current-value reconciliations: {reconciled}")
    return reconciled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-codes-file", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    baseline_codes = load_baseline_codes(args.baseline_codes_file)
    reconcile(baseline_codes=baseline_codes, apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
