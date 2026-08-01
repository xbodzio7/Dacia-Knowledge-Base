from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
TMP = ROOT / "project" / "tmp"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pdftotext",
            "-layout",
            str(ROOT / "PDF/Cenniki/DACIA SANDERO I SANDERO STEPWAY cennik MY26 20260703.pdf"),
            str(TMP / "sandero-stepway-price-20260703.txt"),
        ],
        check=True,
    )

    configurations = {
        row["code"]: row
        for row in rows("configurations.csv")
        if row.get("status") == "active"
    }
    versions = {row["code"]: row for row in rows("versions.csv")}
    models = {row["code"]: row for row in rows("models.csv")}
    availability = [
        row
        for row in rows("configuration_attribute_availability.csv")
        if row.get("configuration_code") in configurations
        and row.get("availability_status") == "optional"
    ]
    item_attributes: dict[str, set[str]] = defaultdict(set)
    for row in rows("commercial_item_attributes.csv"):
        item_attributes[row["commercial_item_code"]].add(row["attribute_code"])
    mappings: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows("commercial_item_configurations.csv"):
        if (
            row.get("configuration_code") in configurations
            and row.get("availability_status") == "optional"
        ):
            mappings[row["configuration_code"]].append(row)

    gaps: list[dict[str, str]] = []
    for row in availability:
        configuration_code = row["configuration_code"]
        attribute_code = row["attribute_code"]
        covering = [
            mapping
            for mapping in mappings.get(configuration_code, [])
            if attribute_code
            in item_attributes.get(mapping["commercial_item_code"], set())
        ]
        if covering:
            continue
        version = versions[configurations[configuration_code]["version_code"]]
        model = models[version["model_code"]]
        gaps.append(
            {
                "configuration_code": configuration_code,
                "model_code": version["model_code"],
                "model_name": model["name"],
                "version_code": version["code"],
                "version_name": version["name"],
                "attribute_code": attribute_code,
                "availability_source_code": row.get("source_code", ""),
                "availability_observation_date": row.get("observation_date", ""),
            }
        )

    by_model: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    for gap in gaps:
        by_model[gap["model_code"]] += 1
        by_source[gap["availability_source_code"]] += 1
    audit = {
        "active_configurations": len(configurations),
        "optional_availability_rows": len(availability),
        "unpriced_optional_links": len(gaps),
        "by_model": dict(sorted(by_model.items())),
        "by_source": dict(sorted(by_source.items())),
        "gaps": gaps,
    }
    (TMP / "interface-feedback-price-coverage.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    url = (
        "https://www.dacia.pl/agg/vn/unique/"
        "ONE_DACIA_PP_XLARGE_DENSITY1/d_brandSite_carPicker_1.png?"
        "uri=https%3A%2F%2Fcdn.group.renault.com%2Fpackshots%2F"
        "dacia-spring-bbg24-ph2"
    )
    probe: dict[str, object] = {"url": url}
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Dacia-Knowledge-Base/1.0",
                "Accept": "image/*",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            probe.update(
                {
                    "ok": True,
                    "status": getattr(response, "status", 200),
                    "content_type": response.headers.get_content_type(),
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
    except Exception as exc:
        probe.update({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
    (TMP / "spring-media-probe.json").write_text(
        json.dumps(probe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
