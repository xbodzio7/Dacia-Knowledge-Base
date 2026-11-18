from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from tools.source_registry_contract import (
    SOURCE_REGISTRY_IDENTITY_FIELDS,
    source_registry_identity_differences,
    source_registry_identity_matches,
)


ROOT = Path(__file__).resolve().parents[1]


class SourceRegistryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = {
            "id": "127",
            "code": "src_example",
            "source_type": "configuration_pdf",
            "title": "Dacia price list",
            "publisher": "Dacia",
            "market": "PL",
            "document_date": "2026-11-02",
            "external_reference": "https://example.invalid/source.pdf",
            "file_path": "owner_supplied/source.pdf",
            "sha256": "a" * 64,
            "status": "active",
            "notes": "Original explanatory wording.",
        }

    def test_editorial_notes_do_not_break_source_identity(self) -> None:
        registry = {**self.source, "notes": "Updated editorial wording."}

        self.assertTrue(source_registry_identity_matches(self.source, registry))
        self.assertEqual(source_registry_identity_differences(self.source, registry), {})

    def test_structured_identity_mismatch_is_rejected(self) -> None:
        registry = {**self.source, "sha256": "b" * 64}

        self.assertFalse(source_registry_identity_matches(self.source, registry))
        self.assertEqual(
            source_registry_identity_differences(self.source, registry),
            {"sha256": ("a" * 64, "b" * 64)},
        )

    def test_all_structured_identity_fields_are_checked(self) -> None:
        for field in SOURCE_REGISTRY_IDENTITY_FIELDS:
            with self.subTest(field=field):
                registry = {**self.source, field: "different"}
                self.assertIn(field, source_registry_identity_differences(self.source, registry))

    def test_notes_are_not_a_structured_identity_field(self) -> None:
        self.assertNotIn("notes", SOURCE_REGISTRY_IDENTITY_FIELDS)

    def test_embedded_source_specs_match_canonical_registry_and_archived_hash(
        self,
    ) -> None:
        registry_path = ROOT / "data" / "master" / "sources.csv"
        with registry_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry = {row["code"]: row for row in csv.DictReader(handle)}

        spec_paths = sorted((ROOT / "project" / "sources").glob("*_import_spec.json"))
        self.assertTrue(spec_paths)
        checked = 0
        for spec_path in spec_paths:
            payload = json.loads(spec_path.read_text(encoding="utf-8"))
            source = payload.get("source")
            if not isinstance(source, dict):
                continue
            source_code = str(source.get("code", ""))
            with self.subTest(spec=spec_path.name, source=source_code):
                self.assertIn(source_code, registry)
                registered = registry[source_code]
                self.assertTrue(source_registry_identity_matches(source, registered))
                archive = ROOT / registered["file_path"]
                self.assertTrue(archive.is_file(), f"Missing archived source: {archive}")
                digest = hashlib.sha256(archive.read_bytes()).hexdigest()
                self.assertEqual(digest, registered["sha256"])
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
