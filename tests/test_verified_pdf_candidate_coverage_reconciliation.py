from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import verified_pdf_candidate_coverage_reconciliation as reconciliation  # noqa: E402

LEDGER = ROOT / reconciliation.DEFAULT_LEDGER
REVIEW = ROOT / reconciliation.DEFAULT_REVIEW
ARTIFACT_JSON = ROOT / reconciliation.DEFAULT_JSON
ARTIFACT_MARKDOWN = ROOT / reconciliation.DEFAULT_MARKDOWN


def json_differences(
    left: Any,
    right: Any,
    path: tuple[str, ...] = (),
) -> list[tuple[tuple[str, ...], Any, Any]]:
    if type(left) is not type(right):
        return [(path, left, right)]
    if isinstance(left, dict):
        differences: list[tuple[tuple[str, ...], Any, Any]] = []
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                differences.append((path + (str(key),), left.get(key), right.get(key)))
                continue
            differences.extend(json_differences(left[key], right[key], path + (str(key),)))
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return [(path + ("length",), len(left), len(right))]
        differences: list[tuple[tuple[str, ...], Any, Any]] = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(json_differences(left_item, right_item, path + (str(index),)))
        return differences
    return [] if left == right else [(path, left, right)]


class CoverageReconciliationUnitTests(unittest.TestCase):
    def candidate(self, **overrides: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "candidate_id": "a" * 64,
            "source_code": "source_a",
            "model_code": "model_a",
            "page": 7,
            "line_start": 3,
            "line_end": 3,
            "candidate_kind": "table_row",
            "rule_code": "table_row_surface",
            "exact_text": "Światła do jazdy dziennej LED      •     •",
            "normalized_text": "Światła do jazdy dziennej LED • •",
        }
        payload.update(overrides)
        return payload

    def group(self, **overrides: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "group_id": "group_a",
            "source_code": "source_a",
            "model_code": "model_a",
            "domain": "technical_tables",
            "page_start": 7,
            "page_end": 7,
            "candidate_ids": ["a" * 64],
            "decision_code": reconciliation.TARGET_DECISION,
        }
        payload.update(overrides)
        return payload

    def evidence(self, **overrides: object) -> dict[str, object]:
        signature = {"attribute_code": "daytime_lights", "value": "LED"}
        payload: dict[str, object] = {
            "table": "configuration_attribute_values",
            "record_code": "record_a",
            "configuration_code": "configuration_a",
            "model_code": "model_a",
            "source_code": "source_a",
            "source_page": 7,
            "notes": "Official brochure page 7: Światła do jazdy dziennej LED",
            "note_tokens": reconciliation.meaningful_tokens(
                "Official brochure page 7: Światła do jazdy dziennej LED"
            ),
            "signature": signature,
            "signature_key": reconciliation.signature_key(signature),
        }
        payload.update(overrides)
        return payload

    def test_match_key_is_unicode_and_punctuation_stable(self) -> None:
        self.assertEqual(
            reconciliation.match_key("Światła — ŁÓDŹ, 205/60 R16"),
            "swiatla lodz 205 60 r16",
        )

    def test_candidate_tokens_prefer_left_table_label(self) -> None:
        self.assertEqual(
            reconciliation.candidate_match_tokens(self.candidate()),
            ["swiatla", "jazdy", "dziennej", "led"],
        )

    def test_ordered_match_requires_two_tokens(self) -> None:
        self.assertFalse(reconciliation.is_ordered_subsequence(["swiatla"], ["swiatla"]))
        self.assertTrue(
            reconciliation.is_ordered_subsequence(
                ["swiatla", "dziennej", "led"],
                ["swiatla", "do", "jazdy", "dziennej", "led"],
            )
        )

    def test_heading_is_explicit_non_import(self) -> None:
        result = reconciliation.reconcile_candidate(
            self.candidate(candidate_kind="heading", exact_text="OSIĄGI"), self.group(), []
        )
        self.assertEqual(result["coverage_status"], "explicit_non_import")

    def test_numbered_footnote_is_explicit_non_import(self) -> None:
        result = reconciliation.reconcile_candidate(
            self.candidate(exact_text="(1) Oficjalne wartości homologacyjne"), self.group(), []
        )
        self.assertEqual(result["coverage_status"], "explicit_non_import")

    def test_technical_match_requires_same_source_and_page(self) -> None:
        matches = reconciliation.evidence_matches(
            self.candidate(),
            self.group(),
            [
                self.evidence(),
                self.evidence(record_code="wrong_source", source_code="source_b"),
                self.evidence(record_code="wrong_page", source_page=8),
            ],
        )
        self.assertEqual([match["record_code"] for match in matches], ["record_a"])

    def test_equipment_match_requires_same_model_and_availability_table(self) -> None:
        signature = {
            "attribute_code": "led_daytime_running_lights",
            "availability_status": "standard",
        }
        good = self.evidence(
            table="configuration_attribute_availability",
            source_code="catalogue_source",
            signature=signature,
            signature_key=reconciliation.signature_key(signature),
        )
        matches = reconciliation.evidence_matches(
            self.candidate(),
            self.group(domain="equipment_matrix"),
            [
                good,
                dict(good, record_code="wrong_model", model_code="model_b"),
                self.evidence(record_code="wrong_table"),
            ],
        )
        self.assertEqual([match["record_code"] for match in matches], ["record_a"])

    def test_single_signature_is_already_covered(self) -> None:
        duplicate = dict(self.evidence(), record_code="record_b", configuration_code="configuration_b")
        result = reconciliation.reconcile_candidate(
            self.candidate(), self.group(), [self.evidence(), duplicate]
        )
        self.assertEqual(result["coverage_status"], "already_covered")
        self.assertEqual(len(result["evidence_signatures"]), 1)
        self.assertEqual(result["evidence_signatures"][0]["record_count"], 2)

    def test_multiple_signatures_are_ambiguous(self) -> None:
        signature = {"attribute_code": "daytime_lights", "value": "halogen"}
        second = self.evidence(
            record_code="record_b",
            signature=signature,
            signature_key=reconciliation.signature_key(signature),
        )
        result = reconciliation.reconcile_candidate(
            self.candidate(), self.group(), [self.evidence(), second]
        )
        self.assertEqual(result["coverage_status"], "ambiguous")
        self.assertEqual(len(result["evidence_signatures"]), 2)

    def test_no_match_is_unresolved_not_negative_evidence(self) -> None:
        result = reconciliation.reconcile_candidate(self.candidate(), self.group(), [])
        self.assertEqual(result["coverage_status"], "unresolved")
        self.assertNotIn("not_stated", json.dumps(result))

    def test_target_groups_require_exact_review_boundary(self) -> None:
        groups = [
            self.group(
                group_id=f"group_{index}",
                domain="technical_tables" if index < 5 else "equipment_matrix",
            )
            for index in range(10)
        ]
        self.assertEqual(len(reconciliation.target_groups({"groups": groups})), 10)
        with self.assertRaisesRegex(reconciliation.CoverageReconciliationError, "exactly 10"):
            reconciliation.target_groups({"groups": groups[:-1]})

    def test_build_assigns_every_selected_candidate_once(self) -> None:
        candidates = []
        groups = []
        for index in range(10):
            candidate_id = f"{index:064x}"
            candidates.append(
                self.candidate(
                    candidate_id=candidate_id,
                    source_code=f"source_{index}",
                    model_code=f"model_{index}",
                    page=index + 1,
                    exact_text="OSIĄGI",
                    normalized_text="OSIĄGI",
                    candidate_kind="heading",
                )
            )
            groups.append(
                self.group(
                    group_id=f"group_{index}",
                    source_code=f"source_{index}",
                    model_code=f"model_{index}",
                    domain="technical_tables" if index < 5 else "equipment_matrix",
                    page_start=index + 1,
                    page_end=index + 1,
                    candidate_ids=[candidate_id],
                )
            )
        payload = reconciliation.build_reconciliation(
            {"version": 1, "kind": "verified_pdf_candidate_ledger", "candidates": candidates},
            {
                "version": 1,
                "kind": "verified_pdf_candidate_ledger_review",
                "status": "complete",
                "policy": {
                    "every_candidate_assigned_exactly_once": True,
                    "master_data_changes": False,
                    "approved_import_spec_generation": False,
                },
                "groups": groups,
            },
            [],
        )
        self.assertEqual(payload["summary"]["candidate_count"], 10)
        self.assertEqual(payload["summary"]["coverage_status_counts"]["explicit_non_import"], 10)

    def test_duplicate_selected_candidate_is_rejected(self) -> None:
        candidates = []
        groups = []
        shared_id = "b" * 64
        for index in range(10):
            candidate_id = shared_id if index < 2 else f"{index:064x}"
            if candidate_id not in {candidate["candidate_id"] for candidate in candidates}:
                candidates.append(
                    self.candidate(
                        candidate_id=candidate_id,
                        source_code=f"source_{index}",
                        model_code=f"model_{index}",
                        page=index + 1,
                        exact_text="OSIĄGI",
                        normalized_text="OSIĄGI",
                        candidate_kind="heading",
                    )
                )
            source_index = index if index != 1 else 0
            groups.append(
                self.group(
                    group_id=f"group_{index}",
                    source_code=f"source_{source_index}",
                    model_code=f"model_{source_index}",
                    domain="technical_tables" if index < 5 else "equipment_matrix",
                    page_start=index + 1,
                    page_end=index + 1,
                    candidate_ids=[candidate_id],
                )
            )
        with self.assertRaisesRegex(reconciliation.CoverageReconciliationError, "assigned twice"):
            reconciliation.build_reconciliation(
                {"version": 1, "kind": "verified_pdf_candidate_ledger", "candidates": candidates},
                {
                    "version": 1,
                    "kind": "verified_pdf_candidate_ledger_review",
                    "status": "complete",
                    "policy": {
                        "every_candidate_assigned_exactly_once": True,
                        "master_data_changes": False,
                        "approved_import_spec_generation": False,
                    },
                    "groups": groups,
                },
                [],
            )

    def test_render_and_json_are_deterministic(self) -> None:
        payload = {
            "summary": {
                "target_groups": 1,
                "candidate_count": 1,
                "coverage_status_counts": {
                    "already_covered": 0,
                    "ambiguous": 0,
                    "explicit_non_import": 1,
                    "unresolved": 0,
                },
            },
            "domain_status_counts": {
                "technical_tables": {
                    "already_covered": 0,
                    "ambiguous": 0,
                    "explicit_non_import": 1,
                    "unresolved": 0,
                }
            },
            "groups": [
                {
                    "group_id": "group_a",
                    "source_code": "source_a",
                    "domain": "technical_tables",
                    "page_start": 7,
                    "page_end": 7,
                    "candidate_count": 1,
                    "coverage_status_counts": {
                        "already_covered": 0,
                        "ambiguous": 0,
                        "explicit_non_import": 1,
                        "unresolved": 0,
                    },
                }
            ],
            "next_package": {"name": reconciliation.NEXT_PACKAGE},
        }
        self.assertEqual(
            reconciliation.canonical_json(payload),
            reconciliation.canonical_json(copy.deepcopy(payload)),
        )
        self.assertEqual(
            reconciliation.render_markdown(payload),
            reconciliation.render_markdown(copy.deepcopy(payload)),
        )

    def test_restricted_output_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(reconciliation.CoverageReconciliationError, "restricted"):
                reconciliation.ensure_safe_output(root, Path("data/master/output.json"))
            with self.assertRaisesRegex(reconciliation.CoverageReconciliationError, "restricted"):
                reconciliation.ensure_safe_output(root, Path("data/imports/output.json"))


class CoverageReconciliationRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload, cls.markdown = reconciliation.build_from_paths(
            ROOT, reconciliation.DEFAULT_LEDGER, reconciliation.DEFAULT_REVIEW
        )

    def test_real_reconciliation_has_expected_candidate_partition(self) -> None:
        self.assertEqual(self.payload["summary"]["target_groups"], 10)
        self.assertEqual(self.payload["summary"]["candidate_count"], 1583)
        self.assertEqual(
            self.payload["summary"]["coverage_status_counts"],
            {
                "already_covered": 129,
                "ambiguous": 116,
                "explicit_non_import": 195,
                "unresolved": 1143,
            },
        )
        candidate_ids = [item["candidate_id"] for item in self.payload["candidates"]]
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))

    def test_committed_artifacts_preserve_the_dated_review_boundary(self) -> None:
        committed_payload = json.loads(ARTIFACT_JSON.read_text(encoding="utf-8"))
        committed_markdown = ARTIFACT_MARKDOWN.read_text(encoding="utf-8")
        self.assertEqual(committed_markdown, reconciliation.render_markdown(committed_payload))

        differences = json_differences(committed_payload, self.payload)
        self.assertEqual(len(differences), 2)
        recognized = {
            "configuration_attribute_availability": (5906, 5911),
            "configuration_attribute_values": (3490, 3491),
        }
        current_with_historical_counts = copy.deepcopy(self.payload)
        seen: set[str] = set()
        for path, committed_value, current_value in differences:
            joined = ".".join(path)
            matched = next((name for name in recognized if name in joined), None)
            self.assertIsNotNone(matched, joined)
            assert matched is not None
            self.assertEqual((committed_value, current_value), recognized[matched])
            seen.add(matched)
            target: Any = current_with_historical_counts
            for key in path[:-1]:
                target = target[int(key)] if isinstance(target, list) else target[key]
            final_key = path[-1]
            if isinstance(target, list):
                target[int(final_key)] = committed_value
            else:
                target[final_key] = committed_value
        self.assertEqual(seen, set(recognized))
        self.assertEqual(current_with_historical_counts, committed_payload)
        self.assertEqual(self.markdown, reconciliation.render_markdown(self.payload))

        encoded = reconciliation.canonical_json(self.payload)
        self.assertNotIn('"approved_import_spec"', encoded)
        self.assertTrue(self.payload["policy"]["master_data_changes"] is False)
        self.assertTrue(self.payload["policy"]["automatic_promotion"] is False)
        self.assertEqual(
            self.payload["next_package"]["name"],
            "Verified PDF Candidate Residual Gap Prioritization",
        )


if __name__ == "__main__":
    unittest.main()
