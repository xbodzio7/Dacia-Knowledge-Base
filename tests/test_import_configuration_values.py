from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import import_configuration_values as importer  # noqa: E402


VALUE_FIELDS = list(importer.VALUE_FIELDS)


class ImportConfigurationValuesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name)
        self.master = self.repository / "data" / "master"
        self.master.mkdir(parents=True)
        (self.repository / "PDF").mkdir()

        self._write_csv(
            "attributes.csv",
            [
                "id",
                "code",
                "category",
                "name",
                "data_type",
                "unit",
                "description",
                "status",
            ],
            [{
                "id": "1",
                "code": "maximum_payload",
                "category": "Weights",
                "name": "Maximum payload",
                "data_type": "integer",
                "unit": "kg",
                "description": "Source-stated payload",
                "status": "active",
            }],
        )
        self._write_csv(
            "configurations.csv",
            ["id", "code"],
            [
                {"id": "1", "code": "configuration_a"},
                {"id": "2", "code": "configuration_b"},
            ],
        )

        self.source_file = self.repository / "PDF" / "source.pdf"
        self.source_file.write_bytes(b"registered source bytes")
        source_sha = hashlib.sha256(self.source_file.read_bytes()).hexdigest()
        self._write_csv(
            "sources.csv",
            [
                "id",
                "code",
                "source_type",
                "title",
                "publisher",
                "market",
                "document_date",
                "external_reference",
                "file_path",
                "sha256",
                "status",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "source_a",
                    "source_type": "configuration_pdf",
                    "title": "Source A",
                    "publisher": "Dacia",
                    "market": "PL",
                    "document_date": "2026-06-26",
                    "external_reference": "A",
                    "file_path": "PDF/source.pdf",
                    "sha256": source_sha,
                    "status": "active",
                    "notes": "",
                },
                {
                    "id": "2",
                    "code": "source_b",
                    "source_type": "configuration_pdf",
                    "title": "Source B",
                    "publisher": "Dacia",
                    "market": "PL",
                    "document_date": "2026-06-26",
                    "external_reference": "B",
                    "file_path": "PDF/source.pdf",
                    "sha256": source_sha,
                    "status": "active",
                    "notes": "",
                },
            ],
        )
        self._write_csv(
            "source_configurations.csv",
            [
                "id",
                "source_code",
                "configuration_code",
                "relationship",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "source_code": "source_a",
                    "configuration_code": "configuration_a",
                    "relationship": "documents",
                    "notes": "",
                },
                {
                    "id": "2",
                    "source_code": "source_b",
                    "configuration_code": "configuration_b",
                    "relationship": "documents",
                    "notes": "",
                },
            ],
        )
        self._write_csv(
            "configuration_attribute_values.csv",
            VALUE_FIELDS,
            [],
        )
        self.spec_path = self.repository / "spec.json"
        self._write_spec()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_csv(
        self,
        name: str,
        fields: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        with (self.master / name).open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fields,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)

    def _read_values(self) -> list[dict[str, str]]:
        with (
            self.master / "configuration_attribute_values.csv"
        ).open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            return list(csv.DictReader(handle))

    def _payload(self) -> dict[str, object]:
        return {
            "version": 1,
            "kind": "configuration_attribute_values",
            "id_start": 1,
            "attribute_code": "maximum_payload",
            "attribute_contract": {
                "data_type": "integer",
                "unit": "kg",
                "status": "active",
            },
            "observation_date": "2026-06-26",
            "fuel_type_code": "",
            "source_page": 5,
            "source_section": "Dopuszczalna masa całkowita",
            "notes_template": (
                "Source page {page}, section {section}: {source_text}"
            ),
            "rows": [
                {
                    "configuration_code": "configuration_a",
                    "source_code": "source_a",
                    "value": "373",
                    "source_text": "Maksymalna Ładowność (Kg) 373",
                },
                {
                    "configuration_code": "configuration_b",
                    "source_code": "source_b",
                    "value": "371",
                    "source_text": "Maksymalna Ładowność (Kg) 371",
                },
            ],
        }

    def _write_spec(
        self,
        payload: dict[str, object] | None = None,
    ) -> None:
        self.spec_path.write_text(
            json.dumps(
                self._payload() if payload is None else payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_loads_valid_versioned_spec(self) -> None:
        spec = importer.load_spec(self.spec_path)

        self.assertEqual(spec.id_start, 1)
        self.assertEqual(spec.attribute_code, "maximum_payload")
        self.assertEqual(spec.data_type, "integer")
        self.assertEqual(len(spec.rows), 2)

    def test_rejects_unknown_top_level_key(self) -> None:
        payload = self._payload()
        payload["unexpected"] = True
        self._write_spec(payload)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "unknown keys",
        ):
            importer.load_spec(self.spec_path)

    def test_rejects_invalid_observation_date(self) -> None:
        payload = self._payload()
        payload["observation_date"] = "26-06-2026"
        self._write_spec(payload)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "ISO date",
        ):
            importer.load_spec(self.spec_path)

    def test_rejects_duplicate_configuration_and_fuel_context(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[1]["configuration_code"] = "configuration_a"
        self._write_spec(payload)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "duplicates configuration",
        ):
            importer.load_spec(self.spec_path)

    def test_rejects_unknown_row_key(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["unexpected"] = "value"
        self._write_spec(payload)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "unknown keys",
        ):
            importer.load_spec(self.spec_path)

    def test_builds_exact_deterministic_rows(self) -> None:
        spec = importer.load_spec(self.spec_path)

        rows = importer.build_expected_rows(self.repository, spec)

        self.assertEqual(
            rows,
            (
                {
                    "id": "1",
                    "code": (
                        "configuration_a_maximum_payload_20260626"
                    ),
                    "configuration_code": "configuration_a",
                    "attribute_code": "maximum_payload",
                    "fuel_type_code": "",
                    "value": "373",
                    "observation_date": "2026-06-26",
                    "source_code": "source_a",
                    "notes": (
                        "Source page 5, section Dopuszczalna masa "
                        "całkowita: Maksymalna Ładowność (Kg) 373"
                    ),
                },
                {
                    "id": "2",
                    "code": (
                        "configuration_b_maximum_payload_20260626"
                    ),
                    "configuration_code": "configuration_b",
                    "attribute_code": "maximum_payload",
                    "fuel_type_code": "",
                    "value": "371",
                    "observation_date": "2026-06-26",
                    "source_code": "source_b",
                    "notes": (
                        "Source page 5, section Dopuszczalna masa "
                        "całkowita: Maksymalna Ładowność (Kg) 371"
                    ),
                },
            ),
        )

    def test_rejects_unknown_attribute(self) -> None:
        payload = self._payload()
        payload["attribute_code"] = "unknown_attribute"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "exactly one attribute",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_rejects_attribute_contract_mismatch(self) -> None:
        payload = self._payload()
        contract = payload["attribute_contract"]
        assert isinstance(contract, dict)
        contract["data_type"] = "decimal"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "attribute contract differs",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_rejects_unknown_configuration(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["configuration_code"] = "unknown_configuration"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "unknown configuration",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_rejects_unknown_source(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["source_code"] = "unknown_source"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "unknown source",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_rejects_source_configuration_mismatch(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["source_code"] = "source_b"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "does not document configuration",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_rejects_noncanonical_integer_value(self) -> None:
        payload = self._payload()
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["value"] = "0373"
        self._write_spec(payload)
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "canonical integer",
        ):
            importer.build_expected_rows(self.repository, spec)

    def test_plan_reports_exact_existing_rows(self) -> None:
        spec = importer.load_spec(self.spec_path)
        expected = importer.build_expected_rows(self.repository, spec)
        self._write_csv(
            "configuration_attribute_values.csv",
            VALUE_FIELDS,
            list(expected),
        )

        plan = importer.plan_import(self.repository, spec)

        self.assertEqual(plan.existing_rows, expected)
        self.assertEqual(plan.missing_rows, ())

    def test_apply_appends_atomically_and_is_idempotent(self) -> None:
        spec = importer.load_spec(self.spec_path)

        first = importer.apply_import(self.repository, spec)
        second = importer.apply_import(self.repository, spec)

        self.assertEqual(len(first.existing_rows), 2)
        self.assertEqual(first.missing_rows, ())
        self.assertEqual(second, first)
        self.assertEqual(
            self._read_values(),
            list(first.expected_rows),
        )

    def test_rejects_existing_id_conflict(self) -> None:
        conflicting = {
            field: ""
            for field in VALUE_FIELDS
        }
        conflicting.update({
            "id": "1",
            "code": "different_code",
            "configuration_code": "configuration_a",
            "attribute_code": "maximum_payload",
            "value": "999",
            "observation_date": "2026-06-26",
            "source_code": "source_a",
        })
        self._write_csv(
            "configuration_attribute_values.csv",
            VALUE_FIELDS,
            [conflicting],
        )
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "conflicts with spec",
        ):
            importer.plan_import(self.repository, spec)

    def test_verify_rejects_missing_rows(self) -> None:
        spec = importer.load_spec(self.spec_path)

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "missing rows",
        ):
            importer.verify_import(self.repository, spec)

    def test_registered_source_hash_mismatch_is_rejected(self) -> None:
        spec = importer.load_spec(self.spec_path)
        self.source_file.write_bytes(b"changed")

        with self.assertRaisesRegex(
            importer.ImportSpecError,
            "SHA-256 differs",
        ):
            importer.verify_registered_sources(
                self.repository,
                spec,
                verify_text=False,
            )

    def test_registered_source_text_mismatch_is_rejected(self) -> None:
        spec = importer.load_spec(self.spec_path)

        with (
            mock.patch.object(
                importer,
                "extract_page_candidates",
                return_value=[
                    (
                        "mock",
                        "Dopuszczalna masa całkowita "
                        "Maksymalna Ładowność (Kg) 999",
                    )
                ],
            ),
            self.assertRaisesRegex(
                importer.ImportSpecError,
                "does not contain",
            ),
        ):
            importer.verify_registered_sources(
                self.repository,
                spec,
                verify_text=True,
            )


if __name__ == "__main__":
    unittest.main()
