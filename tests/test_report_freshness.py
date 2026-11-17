"""Contract tests for analytical report provenance and freshness."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.report_freshness import validate_registry


class ReportFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data" / "reporting").mkdir(parents=True)
        (self.root / "data" / "master").mkdir(parents=True)
        self.input_path = self.root / "data" / "master" / "input.csv"
        self.input_path.write_text("code,value\nA,1\n", encoding="utf-8")
        data = self.input_path.read_bytes()
        self.blob_sha = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.report_id = "sample_report_001"
        self.json_path = self.root / "data" / "reporting" / "sample.json"
        self.md_path = self.root / "data" / "reporting" / "sample.md"
        self.registry_path = self.root / "data" / "reporting" / "report_registry.json"
        self._write_report()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_report(self, *, status: str = "current", metadata: bool = True) -> None:
        document = {"findings": [{
            "finding_id": "gap-001",
            "status": "open",
            "evidence_refs": ["data/master/input.csv"],
            "last_verified_at": "2026-11-17T10:00:00+01:00",
        }]}
        meta = {
            "schema_version": 1,
            "report_id": self.report_id,
            "generated_at": "2026-11-17T10:00:00+01:00",
            "repository": "xbodzio7/Dacia-Knowledge-Base",
            "base_commit_sha": "a" * 40,
            "input_files": [{
                "path": "data/master/input.csv",
                "git_blob_sha": self.blob_sha,
                "sha256": self.sha256,
            }],
            "scope": "Test scope",
            "status": status,
        }
        if metadata:
            document["report_metadata"] = meta
        self.json_path.write_text(json.dumps(document), encoding="utf-8")
        self.md_path.write_text(
            f"Report ID: {self.report_id}\n"
            f"Generated: {meta['generated_at']}\n"
            f"Analysed commit: {meta['base_commit_sha']}\n"
            f"Status: {status}\n"
            f"Scope: Test scope\n",
            encoding="utf-8",
        )
        self.registry_path.write_text(json.dumps({
            "schema_version": 1,
            "reports": [{
                "report_id": self.report_id,
                "json_path": "data/reporting/sample.json",
                "markdown_path": "data/reporting/sample.md",
            }],
        }), encoding="utf-8")

    def test_valid_report_passes(self) -> None:
        self.assertEqual(validate_registry(self.root, self.registry_path), [])

    def test_changed_input_is_detected(self) -> None:
        self.input_path.write_text("code,value\nA,2\n", encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("input Git blob SHA changed" in error for error in errors))
        self.assertTrue(any("input SHA-256 changed" in error for error in errors))

    def test_missing_metadata_fails_closed(self) -> None:
        self._write_report(metadata=False)
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("missing report_metadata" in error for error in errors))

    def test_markdown_json_parity_is_enforced(self) -> None:
        self._write_report()
        self.md_path.write_text("Report ID: wrong\n", encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("Markdown companion does not match" in error for error in errors))

    def test_legacy_report_is_allowed_but_not_current(self) -> None:
        self._write_report(status="historical", metadata=False)
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["legacy"] = True
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        self.assertEqual(validate_registry(self.root, self.registry_path), [])

    def test_legacy_report_cannot_claim_current(self) -> None:
        self._write_report(status="current")
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["legacy"] = True
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("legacy registry entry cannot claim current" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
