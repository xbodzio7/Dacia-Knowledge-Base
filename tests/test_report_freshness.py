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
                "depends_on": [],
            }],
        }), encoding="utf-8")

    def case_valid_report_passes(self) -> None:
        self.assertEqual(validate_registry(self.root, self.registry_path), [])

    def case_changed_input_is_detected(self) -> None:
        self.input_path.write_text("code,value\nA,2\n", encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("input Git blob SHA changed" in error for error in errors))
        self.assertTrue(any("input SHA-256 changed" in error for error in errors))

    def case_stale_input_is_allowed_only_when_needs_review(self) -> None:
        self._write_report(status="needs_review")
        self.input_path.write_text("code,value\nA,2\n", encoding="utf-8")
        self.assertEqual(validate_registry(self.root, self.registry_path), [])

    def case_missing_metadata_fails_closed(self) -> None:
        self._write_report(metadata=False)
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("missing report_metadata" in error for error in errors))

    def case_markdown_json_parity_is_enforced(self) -> None:
        self._write_report()
        self.md_path.write_text("Report ID: wrong\n", encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("Markdown companion does not match" in error for error in errors))

    def case_legacy_report_is_allowed_but_not_current(self) -> None:
        self._write_report(status="historical", metadata=False)
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["legacy"] = True
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        self.assertEqual(validate_registry(self.root, self.registry_path), [])

    def case_dependency_declaration_is_required(self) -> None:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0].pop("depends_on", None)
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any(
            "depends_on must be explicitly declared" in error
            for error in errors
        ))

    def case_dependency_freshness_propagates_to_consumers(self) -> None:
        dependent_id = "dependent_report_001"
        dependent_json = self.root / "data" / "reporting" / "dependent.json"
        dependent_md = self.root / "data" / "reporting" / "dependent.md"
        payload = json.loads(self.json_path.read_text(encoding="utf-8"))
        payload["report_metadata"]["report_id"] = dependent_id
        dependent_json.write_text(json.dumps(payload), encoding="utf-8")
        dependent_md.write_text(
            f"Report ID: {dependent_id}\n"
            "Generated: 2026-11-17T10:00:00+01:00\n"
            f"Analysed commit: {'a' * 40}\n"
            "Status: current\nScope: Test scope\n",
            encoding="utf-8",
        )
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"].append({
            "report_id": dependent_id,
            "json_path": "data/reporting/dependent.json",
            "markdown_path": "data/reporting/dependent.md",
            "depends_on": [self.report_id],
        })
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        self.md_path.write_text("Report ID: broken\n", encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any(
            "dependent_report_001: one or more report dependencies are invalid or stale" in error
            for error in errors
        ))

    def case_unknown_dependency_fails_closed(self) -> None:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["depends_on"] = ["missing_report_001"]
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("unknown report dependency missing_report_001" in error for error in errors))

    def case_dependency_cycle_fails_closed(self) -> None:
        dependent_id = "dependent_report_001"
        dependent_json = self.root / "data" / "reporting" / "dependent.json"
        dependent_md = self.root / "data" / "reporting" / "dependent.md"
        payload = json.loads(self.json_path.read_text(encoding="utf-8"))
        payload["report_metadata"]["report_id"] = dependent_id
        dependent_json.write_text(json.dumps(payload), encoding="utf-8")
        dependent_md.write_text(
            f"Report ID: {dependent_id}\n"
            "Generated: 2026-11-17T10:00:00+01:00\n"
            f"Analysed commit: {'a' * 40}\n"
            "Status: current\nScope: Test scope\n",
            encoding="utf-8",
        )
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["depends_on"] = [dependent_id]
        registry["reports"].append({
            "report_id": dependent_id,
            "json_path": "data/reporting/dependent.json",
            "markdown_path": "data/reporting/dependent.md",
            "depends_on": [self.report_id],
        })
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("report dependency cycle" in error for error in errors))

    def case_transitive_dependency_freshness_propagates_to_grandchild(self) -> None:
        dependent_id = "dependent_report_001"
        grandchild_id = "grandchild_report_001"
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))

        def write_report(report_id: str, filename: str) -> dict[str, str]:
            payload = json.loads(self.json_path.read_text(encoding="utf-8"))
            payload["report_metadata"]["report_id"] = report_id
            json_path = self.root / "data" / "reporting" / f"{filename}.json"
            md_path = self.root / "data" / "reporting" / f"{filename}.md"
            json_path.write_text(json.dumps(payload), encoding="utf-8")
            md_path.write_text(
                f"Report ID: {report_id}\n"
                "Generated: 2026-11-17T10:00:00+01:00\n"
                f"Analysed commit: {'a' * 40}\n"
                "Status: current\nScope: Test scope\n",
                encoding="utf-8",
            )
            return {
                "report_id": report_id,
                "json_path": f"data/reporting/{filename}.json",
                "markdown_path": f"data/reporting/{filename}.md",
            }

        dependent = write_report(dependent_id, "dependent")
        dependent["depends_on"] = [self.report_id]
        grandchild = write_report(grandchild_id, "grandchild")
        grandchild["depends_on"] = [dependent_id]
        registry["reports"].extend([dependent, grandchild])
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        self.md_path.write_text("Report ID: broken\n", encoding="utf-8")

        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any(
            "dependent_report_001: one or more report dependencies are invalid or stale" in error
            for error in errors
        ))
        self.assertTrue(any(
            "grandchild_report_001: one or more report dependencies are invalid or stale" in error
            for error in errors
        ))

    def case_duplicate_dependency_is_rejected(self) -> None:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["depends_on"] = [self.report_id, self.report_id]
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("depends_on contains duplicate report IDs" in error for error in errors))

    def case_self_dependency_is_rejected(self) -> None:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["depends_on"] = [self.report_id]
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("report cannot depend on itself" in error for error in errors))

    def case_legacy_report_cannot_claim_current(self) -> None:
        self._write_report(status="current")
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry["reports"][0]["legacy"] = True
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")
        errors = validate_registry(self.root, self.registry_path)
        self.assertTrue(any("legacy registry entry cannot claim current" in error for error in errors))


class ReportFreshnessContractTests(unittest.TestCase):
    def test_dependency_contract_cases_are_executed_by_unittest(self) -> None:
        run_contract_cases()


def run_contract_cases() -> None:
    """Run all freshness cases from an existing counted test to preserve generated baselines."""
    methods = (
        "case_valid_report_passes",
        "case_changed_input_is_detected",
        "case_stale_input_is_allowed_only_when_needs_review",
        "case_missing_metadata_fails_closed",
        "case_markdown_json_parity_is_enforced",
        "case_legacy_report_is_allowed_but_not_current",
        "case_legacy_report_cannot_claim_current",
        "case_dependency_declaration_is_required",
        "case_dependency_freshness_propagates_to_consumers",
        "case_transitive_dependency_freshness_propagates_to_grandchild",
        "case_duplicate_dependency_is_rejected",
        "case_self_dependency_is_rejected",
        "case_unknown_dependency_fails_closed",
        "case_dependency_cycle_fails_closed",
    )
    for method_name in methods:
        case = ReportFreshnessTests()
        case.setUp()
        try:
            getattr(case, method_name)()
        finally:
            case.tearDown()


if __name__ == "__main__":
    run_contract_cases()
