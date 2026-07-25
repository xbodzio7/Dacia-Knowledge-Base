from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
RECEIPT = REPOSITORY / "project" / "sources" / "official-dacia-brochures-20260725.json"
GAP_REVIEW = REPOSITORY / "data" / "reporting" / "official_dacia_brochure_gap_review.json"

sys.path.insert(0, str(REPOSITORY / "tools"))
import register_official_dacia_brochures_20260725 as registration  # noqa: E402


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class OfficialDaciaBrochureSources20260725Tests(unittest.TestCase):
    def test_receipt_contains_exact_immutable_source_identities(self) -> None:
        payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["kind"], "official_dacia_brochure_source_receipt")
        self.assertEqual(payload["retrieved_on"], "2026-07-25")
        self.assertEqual(payload["publisher"], "Dacia")
        self.assertEqual(payload["market"], "PL")
        actual = {row["source_code"]: row for row in payload["sources"]}
        self.assertEqual(set(actual), registration.OWNED_CODES)
        for expected in registration.EXPECTED:
            record = actual[expected["source_code"]]
            for field in (
                "title",
                "document_date",
                "url",
                "file_path",
                "pages",
                "publication_marker",
                "model_code",
                "bytes",
                "sha256",
            ):
                self.assertEqual(record[field], expected[field])

    def test_archived_originals_match_pinned_size_and_sha256(self) -> None:
        for expected in registration.EXPECTED:
            with self.subTest(source=expected["source_code"]):
                path = REPOSITORY / expected["file_path"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, expected["bytes"])
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    expected["sha256"],
                )
                self.assertEqual(path.read_bytes()[:5], b"%PDF-")

    def test_five_active_brochure_source_rows_match_contract(self) -> None:
        selected = [row for row in rows("sources.csv") if row["code"] in registration.OWNED_CODES]
        self.assertEqual(len(selected), 5)
        self.assertEqual({row["id"] for row in selected}, {"23", "24", "25", "26", "27"})
        expected = {row["source_code"]: row for row in registration.EXPECTED}
        for row in selected:
            contract = expected[row["code"]]
            self.assertEqual(row["source_type"], "brochure_pdf")
            self.assertEqual(row["title"], contract["title"])
            self.assertEqual(row["publisher"], "Dacia")
            self.assertEqual(row["market"], "PL")
            self.assertEqual(row["document_date"], contract["document_date"])
            self.assertEqual(row["external_reference"], contract["url"])
            self.assertEqual(row["file_path"], contract["file_path"])
            self.assertEqual(row["sha256"], contract["sha256"])
            self.assertEqual(row["status"], "active")

    def test_five_model_only_brochure_relationships_match_contract(self) -> None:
        selected = [
            row
            for row in rows("source_models.csv")
            if row["source_code"] in registration.OWNED_CODES
        ]
        self.assertEqual(len(selected), 5)
        self.assertEqual({row["id"] for row in selected}, {"30", "31", "32", "33", "34"})
        expected_models = {
            row["source_code"]: row["model_code"] for row in registration.EXPECTED
        }
        self.assertEqual(
            {row["source_code"]: row["model_code"] for row in selected},
            expected_models,
        )
        self.assertEqual({row["relationship"] for row in selected}, {"brochure_for"})

    def test_registration_does_not_project_versions_configurations_or_observations(self) -> None:
        self.assertEqual(
            [row for row in rows("source_versions.csv") if row["source_code"] in registration.OWNED_CODES],
            [],
        )
        self.assertEqual(
            [row for row in rows("source_configurations.csv") if row["source_code"] in registration.OWNED_CODES],
            [],
        )
        for path in sorted(MASTER.rglob("*.csv")):
            if path.name in {"sources.csv", "source_models.csv"}:
                continue
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None or "source_code" not in reader.fieldnames:
                    continue
                selected = [
                    row for row in reader if row.get("source_code") in registration.OWNED_CODES
                ]
            self.assertEqual(selected, [], str(path))

    def test_gap_review_preserves_context_and_explicit_non_imports(self) -> None:
        payload = json.loads(GAP_REVIEW.read_text(encoding="utf-8"))
        self.assertEqual(payload["kind"], "official_dacia_brochure_gap_review")
        self.assertEqual(set(payload["source_codes"]), registration.OWNED_CODES)
        summary = payload["summary"]
        self.assertEqual(summary["registered_sources"], 5)
        self.assertEqual(summary["duplicate_existing_groups"], 5)
        self.assertEqual(summary["deferred_context_groups"], 5)
        self.assertEqual(summary["explicit_non_imports"], 2)
        self.assertEqual(summary["master_observations_imported"], 0)
        deferred = payload["classifications"]["deferred_context_model"]
        context = {item for group in deferred for item in group["required_context"]}
        self.assertTrue(
            {
                "measurement_standard",
                "seat_state",
                "passenger_layout",
                "gear_number",
                "fuel_type",
                "drive_type",
                "spare_wheel_or_repair_kit",
                "double_floor",
                "cargo_compartment",
            }
            <= context
        )
        non_import_ids = {
            item["id"] for item in payload["classifications"]["explicit_non_import"]
        }
        self.assertEqual(
            non_import_ids,
            {"sandero_country_placeholder_efficiency", "duster_manual_to_automatic_projection"},
        )

    def test_importer_and_canonical_state_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/register_official_dacia_brochures_20260725.py",
                "--check",
            ],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: official Dacia brochure source registration contract",
            completed.stdout,
        )
        state = json.loads(
            (REPOSITORY / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertTrue(state["phase"])
        self.assertGreaterEqual(state["baseline"]["tests"], 765)
        self.assertGreaterEqual(state["baseline"]["rows"], 8145)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 1831)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 114)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["next_package"]["name"])


if __name__ == "__main__":
    unittest.main()
