from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project/tmp/sandero-page17-key-coverage.json"
OUT = ROOT / "project/tmp/sandero-page17-coverage-matrix.json"


def group(code: str) -> str:
    if "tce100_manual" in code:
        return "tce100_manual"
    if "ecog120_manual" in code:
        return "ecog120_manual"
    if "ecog120_automatic" in code:
        return "ecog120_automatic"
    raise AssertionError(code)


def compact(rows: list[dict], range_rows: bool = False) -> dict:
    buckets: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        context = row.get("fuel_type_code", "")
        gear = row.get("gear_number", "")
        buckets[(group(row["configuration_code"]), context, gear)].append(row)
    result = {}
    for (group_code, context, gear), items in sorted(buckets.items()):
        key = "|".join((group_code, context or "none", gear or "none"))
        values = Counter(
            f"{row['minimum_value']}..{row['maximum_value']}" if range_rows else row["value"]
            for row in items
        )
        sources = Counter(row["source_code"] for row in items)
        result[key] = {
            "configuration_count": len({row["configuration_code"] for row in items}),
            "row_count": len(items),
            "values": dict(sorted(values.items())),
            "sources": dict(sorted(sources.items())),
            "configurations": sorted({row["configuration_code"] for row in items}),
        }
    return result


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    matrix = {
        "group_sizes": Counter(group(row["code"]) for row in data["configurations"]),
        "same_source_page17_scalar_count": data["same_source_page17_scalar_count"],
        "same_source_page17_range_count": data["same_source_page17_range_count"],
        "same_source_page17": {
            attribute: compact(rows)
            for attribute, rows in data["same_source_page17_by_attribute"].items()
        },
        "latest_values": {
            attribute: compact(rows)
            for attribute, rows in data["latest_key_values_by_attribute"].items()
        },
        "latest_ranges": {
            attribute: compact(rows, range_rows=True)
            for attribute, rows in data["latest_rpm_ranges_by_attribute"].items()
        },
    }
    OUT.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
