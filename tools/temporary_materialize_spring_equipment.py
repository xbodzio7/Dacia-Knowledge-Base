#!/usr/bin/env python3
"""Materialize the reviewed Spring equipment package payload.

This helper is intentionally temporary. The materializer workflow removes it,
the encoded payload parts and the workflow itself before committing the final
package.
"""

from __future__ import annotations

import base64
import hashlib
import io
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PART_SPECS = [
    (".temporary_spring_payload_00", 9000, "7394abf62697bbea1e5ca76ec7272fcd1b0cb80bf41b68b2ee673fae886a3908"),
    (".temporary_spring_payload_01_0", 3000, "b9d12efd8b0d9cb3b80fa2c30cef6e20f4df73c2bbec62ca4145010ece66ea96"),
    (".temporary_spring_payload_01_1", 3000, "891ada3393bea56f821d1b3cc8e7a4555e9890aa2e981cdb264d30c6aafcf0fd"),
    (".temporary_spring_payload_01_2", 3000, "fdc4a5d5040ef65c5254dae1602ed6bd9a2df14bc3b35b7813fdd870623a04c9"),
    (".temporary_spring_payload_02", 9000, "84f6a4869dab84cd1d752abdda98bec3bb554885622f9a5b3b052ea9c21a664d"),
    (".temporary_spring_payload_03", 9000, "af1085e188df9e9a73ce74bd202a657c07eae2b32170e71a253d1e1f1e51adb2"),
    (".temporary_spring_payload_04", 9000, "6aeed8738038dd0dd9534e35dd450829fcd9f6c11e39180e168e002d29cadcd5"),
    (".temporary_spring_payload_05", 9000, "2d49617fbd35ffd5c18ec2582852772a784aca27db4f9e5ff16ee39f25373d0c"),
    (".temporary_spring_payload_06", 9000, "75cdc852ae720fcfb53a18aadbce69d321cc38bb928059def47917b178d78c04"),
    (".temporary_spring_payload_07", 8588, "f356aef5d6f18973c58fa62bfb48759cab13e76aced215f7243c6801ece6530f"),
]
EXPECTED_ENCODED_SHA256 = "fd29dcbb758cb66e1b81acfd781a4633130a8a65b9e61e1ab7c6112e3816048e"
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
    chunks: list[bytes] = []
    failures: list[str] = []
    for name, expected_length, expected_sha in PART_SPECS:
        path = ROOT / "tools" / name
        if not path.is_file():
            failures.append(f"missing part: tools/{name}")
            continue
        chunk = path.read_bytes()
        actual_length = len(chunk)
        actual_sha = hashlib.sha256(chunk).hexdigest()
        if (actual_length, actual_sha) != (expected_length, expected_sha):
            failures.append(
                f"{name}: expected length/hash {(expected_length, expected_sha)}, "
                f"got {(actual_length, actual_sha)}; "
                f"padding={chunk.count(b'=')}, tail={chunk[-16:]!r}"
            )
        chunks.append(chunk)
    if failures:
        raise SystemExit("Payload part integrity failure:\n" + "\n".join(failures))

    encoded_bytes = b"".join(chunks)
    encoded_sha = hashlib.sha256(encoded_bytes).hexdigest()
    if encoded_sha != EXPECTED_ENCODED_SHA256:
        raise SystemExit(
            "Combined payload SHA-256 mismatch: "
            f"expected {EXPECTED_ENCODED_SHA256}, got {encoded_sha}"
        )
    raw = base64.b64decode(encoded_bytes, validate=True)

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
