from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


EXPECTED_FAMILY_COUNTS = {
    "sandero": 7,
    "sandero_stepway": 8,
    "jogger_5": 11,
    "jogger_7": 11,
    "duster": 16,
    "bigster": 14,
    "spring": 3,
}
EXPECTED_DOCUMENT_COUNT = 70
SOURCE_PREFIX = "src_pl_cfgpdf_"
SOURCE_SUFFIX = "_20260809"


class DaciaConfiguratorNativePdfArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.manifest_path = (
            cls.root
            / "project/sources/dacia-pl-configurator-native-pdf-archive-20260809.json"
        )
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))

        with (cls.root / "data/master/configurations.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.active_configurations = {
                row["code"]
                for row in csv.DictReader(handle)
                if row.get("status") == "active"
            }
        with (cls.root / "data/master/sources.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.sources = list(csv.DictReader(handle))
        with (cls.root / "data/master/source_configurations.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.relationships = list(csv.DictReader(handle))

    def test_manifest_preserves_exact_current_configurator_scope(self) -> None:
        self.assertEqual(
            self.manifest["source_kind"],
            "dacia_pl_current_configurator_native_pdf_archive",
        )
        self.assertEqual(self.manifest["observed_date"], "2026-08-09")
        self.assertTrue(self.manifest["native_exports_only"])
        self.assertEqual(
            self.manifest["expected_configuration_count"], EXPECTED_DOCUMENT_COUNT
        )
        self.assertEqual(self.manifest["configuration_count"], EXPECTED_DOCUMENT_COUNT)
        self.assertEqual(self.manifest["family_counts"], EXPECTED_FAMILY_COUNTS)

        documents = self.manifest["documents"]
        self.assertEqual(len(documents), EXPECTED_DOCUMENT_COUNT)
        configuration_codes = [row["configuration_code"] for row in documents]
        dacia_codes = [row["dacia_configuration_code"] for row in documents]
        hashes = [row["sha256"] for row in documents]
        self.assertEqual(len(set(configuration_codes)), EXPECTED_DOCUMENT_COUNT)
        self.assertEqual(len(set(dacia_codes)), EXPECTED_DOCUMENT_COUNT)
        self.assertEqual(len(set(hashes)), EXPECTED_DOCUMENT_COUNT)
        self.assertTrue(set(configuration_codes) <= self.active_configurations)
        self.assertEqual(
            {family: sum(row["family"] == family for row in documents)
             for family in EXPECTED_FAMILY_COUNTS},
            EXPECTED_FAMILY_COUNTS,
        )

    def test_native_pdf_binaries_match_manifest_hashes(self) -> None:
        for row in self.manifest["documents"]:
            path = self.root / row["file_path"]
            self.assertTrue(path.is_file(), row["file_path"])
            payload = path.read_bytes()
            self.assertTrue(payload.startswith(b"%PDF-"), row["file_path"])
            self.assertEqual(len(payload), row["bytes"], row["file_path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                row["sha256"],
                row["file_path"],
            )
            self.assertGreaterEqual(row["pages"], 1)
            self.assertEqual(row["capture_method"], "signed_url")

    def test_each_pdf_is_registered_as_one_exact_configuration_source(self) -> None:
        source_rows = {
            row["code"]: row
            for row in self.sources
            if row["code"].startswith(SOURCE_PREFIX)
            and row["code"].endswith(SOURCE_SUFFIX)
        }
        self.assertEqual(len(source_rows), EXPECTED_DOCUMENT_COUNT)

        archive_configuration_codes = {
            row["configuration_code"] for row in self.manifest["documents"]
        }
        archive_relationships = [
            row
            for row in self.relationships
            if row["source_code"] in source_rows
        ]
        self.assertEqual(len(archive_relationships), EXPECTED_DOCUMENT_COUNT)
        self.assertEqual(
            {row["configuration_code"] for row in archive_relationships},
            archive_configuration_codes,
        )

        relationships_by_source = {
            row["source_code"]: row for row in archive_relationships
        }
        self.assertEqual(len(relationships_by_source), EXPECTED_DOCUMENT_COUNT)

        manifest_by_configuration = {
            row["configuration_code"]: row for row in self.manifest["documents"]
        }
        for source_code, source in source_rows.items():
            relation = relationships_by_source[source_code]
            document = manifest_by_configuration[relation["configuration_code"]]
            self.assertEqual(relation["relationship"], "documents")
            self.assertEqual(source["source_type"], "configuration_pdf")
            self.assertEqual(source["publisher"], "Dacia")
            self.assertEqual(source["market"], "PL")
            self.assertEqual(source["document_date"], "2026-08-09")
            self.assertEqual(source["status"], "active")
            self.assertEqual(source["file_path"], document["file_path"])
            self.assertEqual(source["sha256"], document["sha256"])
            self.assertEqual(
                source["external_reference"], document["dacia_configuration_code"]
            )


if __name__ == "__main__":
    unittest.main()
