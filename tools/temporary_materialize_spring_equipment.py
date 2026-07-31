#!/usr/bin/env python3
"""Materialize the reviewed Spring equipment package payload.

This helper is intentionally temporary. The materializer workflow removes it,
the encoded payload parts and the workflow itself before committing the final
package.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PARTS = [ROOT / "tools" / f".temporary_spring_payload_{index:02d}" for index in range(8)]
EXPECTED_PATHS = [
    "CHANGELOG.md",
    "README.md",
    "data/imports/spring_equipment_availability_20260219.csv",
    "data/reporting/spring_electric100_automatic_completeness.json",
    "data/reporting/spring_electric70_automatic_completeness.json",
    "project/ROADMAP.md",
    "project/state.json",
    "project/packages/spring-version-equipment-matrix-availability-20260731.md",
    "tests/test_spring_equipment_availability.py",
    "tools/import_spring_equipment_availability.py",
]


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in PARTS if not path.is_file()]
    if missing:
        raise SystemExit(f"Missing payload parts: {', '.join(missing)}")

    encoded = "".join(path.read_text(encoding="ascii") for path in PARTS)
    raw = base64.b64decode(encoded, validate=True)

    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        names = archive.getnames()
        if names != EXPECTED_PATHS:
            raise SystemExit(
                "Unexpected payload manifest:\n"
                f"expected={EXPECTED_PATHS!r}\n"
                f"actual={names!r}"
            )

        root = ROOT.resolve()
        for member in archive.getmembers():
            if not member.isfile():
                raise SystemExit(f"Non-file payload member: {member.name}")
            target = (ROOT / member.name).resolve()
            if root not in target.parents:
                raise SystemExit(f"Payload path escapes repository: {member.name}")
            source = archive.extractfile(member)
            if source is None:
                raise SystemExit(f"Cannot read payload member: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read())

    print(f"Materialized {len(EXPECTED_PATHS)} reviewed Spring package files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
