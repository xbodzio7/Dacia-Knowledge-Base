from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import import_sandero_stepway_price_list_20261102 as sandero_importer  # noqa: E402


class SourceRegistryImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.master = Path(self.temporary.name)
        self.path = self.master / "sources.csv"
        self.fields = [
            "id", "code", "source_type", "title", "publisher", "market",
            "document_date", "external_reference", "file_path", "sha256",
            "status", "notes",
        ]
        self.registered = {
            "id": "1",
            "code": "source_a",
            "source_type": "configuration_pdf",
            "title": "Source A",
            "publisher": "Dacia",
            "market": "PL",
            "document_date": "2026-11-02",
            "external_reference": "https://example.invalid/source.pdf",
            "file_path": "owner_supplied/source.pdf",
            "sha256": "a" * 64,
            "status": "active",
            "notes": "Canonical registry wording.",
        }
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields, lineterminator="\n")
            writer.writeheader()
            writer.writerow(self.registered)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_source_notes_wording_does_not_block_import(self) -> None:
        expected = {**self.registered, "notes": "Equivalent but differently worded note."}
        with mock.patch.object(sandero_importer, "MASTER", self.master):
            missing = sandero_importer.reconcile_table("source", [expected], apply=False)
        self.assertEqual(missing, 0)

    def test_source_sha_mismatch_still_blocks_import(self) -> None:
        expected = {**self.registered, "sha256": "b" * 64}
        with mock.patch.object(sandero_importer, "MASTER", self.master):
            with self.assertRaisesRegex(
                sandero_importer.ContractError,
                "structured source identity",
            ):
                sandero_importer.reconcile_table("source", [expected], apply=False)


if __name__ == "__main__":
    unittest.main()
