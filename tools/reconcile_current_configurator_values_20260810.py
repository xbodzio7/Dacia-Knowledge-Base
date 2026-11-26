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
    codes = {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    if not codes:
        raise SystemExit(f"Baseline code snapshot is empty: {path}")
    return codes


def diagnostic_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = ("id", "code", "value", "observation_date", "source_code", "notes")
    return [
        {field: (row.get(field) or "").strip() for field in fields}
        for row in rows
    ]


def reconcile(baseline_codes: set[str], apply: bool = False) -> int:
    _, rows = read_rows()
    contextual_codes = read_contextual_value_codes()
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[canonical_key(row)].append(row)

    preserved_compatible_groups = 0
    preserved_divergent_groups = 0

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
        # outside this guard's scope. Only a group touched by one of the current
        # configurator-PDF importers needs evaluation here.
        if not imported:
            continue

        prior = [
            row
            for row in relevant
            if (row.get("code") or "").strip() in baseline_codes
        ]

        # configuration_attribute_values.csv is an observation table, not a
        # mutable current-value cache. Dated source observations must therefore
        # remain immutable and coexist even when later official material reports
        # a different value. Chronology is provenance, not an instruction to
        # overwrite an older source.
        semantic_values = {
            (row.get("value") or "").strip()
            for row in relevant
        }
        if len(semantic_values) == 1:
            preserved_compatible_groups += 1
            print(
                "preserved compatible source observations: "
                f"configuration={key[0]} attribute={key[1]} "
                f"fuel={key[2] or '-'} gear={key[3] or '-'} "
                f"value={next(iter(semantic_values))!r} "
                f"prior={len(prior)} imported={len(imported)}"
            )
            continue

        # A genuine disagreement is also preserved verbatim. We deliberately do
        # not guess which source is authoritative and do not collapse the rows to
        # a single "current" value. Downstream consumers can resolve observations
        # by source/date/as-of policy; this importer only guarantees lossless
        # source assimilation and reports the disagreement for auditability.
        preserved_divergent_groups += 1
        print(
            "preserved divergent source observations: "
            f"key={key!r}, prior={diagnostic_rows(prior)!r}, "
            f"imported={diagnostic_rows(imported)!r}"
        )

    if apply:
        # Deliberately no mutation. The command remains CLI-compatible with the
        # apply workflow, while all source observations stay verbatim.
        pass

    print(f"compatible multi-source groups preserved: {preserved_compatible_groups}")
    print(f"divergent multi-source groups preserved: {preserved_divergent_groups}")
    print("canonical current-value reconciliations: 0")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-codes-file", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    reconcile(baseline_codes=load_baseline_codes(args.baseline_codes_file), apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
