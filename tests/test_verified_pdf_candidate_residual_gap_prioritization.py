from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "verified_pdf_candidate_residual_gap_prioritization.py"
SPEC = importlib.util.spec_from_file_location("residual_prioritization", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
prioritization = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prioritization)


class ResidualGapPrioritizationUnitTests(unittest.TestCase):
    def candidate(self, **changes: object) -> dict[str, object]:
        value: dict[str, object] = {
            "candidate_id": "a" * 64,
            "group_id": "source_technical",
            "domain": "technical_tables",
            "source_code": "source_a",
            "model_code": "model_a",
            "page": 20,
            "line_start": 10,
            "line_end": 10,
            "candidate_kind": "table_row",
            "rule_code": "layout_table_row",
            "exact_text": "Exact technical row",
            "match_tokens": ["exact", "technical", "row"],
            "coverage_status": "ambiguous",
            "classification_basis": "multiple_existing_evidence_signatures",
            "evidence_signatures": [
                {
                    "signature": {"attribute_code": "attribute_a", "value": "1"},
                    "record_count": 1,
                    "records": [
                        {
                            "table": "configuration_attribute_values",
                            "record_code": "record_a",
                            "configuration_code": "configuration_a",
                            "source_code": "source_a",
                            "source_page": 20,
                            "match_basis": "same_source_page_ordered_text",
                        }
                    ],
                }
            ],
        }
        value.update(changes)
        return value

    def reconciliation(self, candidates: list[dict[str, object]]) -> dict[str, object]:
        return {
            "version": 1,
            "kind": "verified_pdf_candidate_coverage_reconciliation",
            "status": "complete",
            "policy": {
                "master_data_changes": False,
                "approved_import_spec_generation": False,
            },
            "semantic_boundaries": {
                "candidate_text_and_candidate_id_are_preserved": True,
            },
            "candidates": candidates,
        }

    def test_canonical_json_is_deterministic(self) -> None:
        payload = {"b": [2, 1], "a": "ą"}
        self.assertEqual(
            prioritization.canonical_json(payload),
            prioritization.canonical_json(copy.deepcopy(payload)),
        )

    def test_boundary_key_contains_source_domain_page_status(self) -> None:
        self.assertEqual(
            prioritization.boundary_key(self.candidate()),
            ("source_a", "technical_tables", 20, "ambiguous"),
        )

    def test_candidate_sort_key_uses_lines_then_id(self) -> None:
        first = self.candidate(candidate_id="b" * 64, line_start=9, line_end=12)
        second = self.candidate(candidate_id="a" * 64, line_start=10, line_end=10)
        self.assertEqual(
            sorted([second, first], key=prioritization.candidate_sort_key),
            [first, second],
        )

    def test_chunks_respect_maximum_size(self) -> None:
        values = [self.candidate(candidate_id=f"{index:064x}") for index in range(81)]
        self.assertEqual(
            [len(chunk) for chunk in prioritization.chunks(values, 40)],
            [40, 40, 1],
        )

    def test_chunks_reject_non_positive_size(self) -> None:
        with self.assertRaisesRegex(
            prioritization.ResidualGapPrioritizationError, "positive"
        ):
            list(prioritization.chunks([self.candidate()], 0))

    def test_evidence_counts_preserve_all_references(self) -> None:
        candidate = self.candidate()
        duplicate = copy.deepcopy(candidate["evidence_signatures"][0])
        duplicate["signature"] = {"attribute_code": "attribute_b", "value": "2"}
        duplicate["records"][0]["record_code"] = "record_b"
        candidate["evidence_signatures"].append(duplicate)
        self.assertEqual(prioritization.evidence_counts([candidate]), (2, 2))

    def test_evidence_count_mismatch_is_rejected(self) -> None:
        candidate = self.candidate()
        candidate["evidence_signatures"][0]["record_count"] = 2
        with self.assertRaisesRegex(
            prioritization.ResidualGapPrioritizationError, "count differs"
        ):
            prioritization.evidence_counts([candidate])

    def test_package_group_order_prefers_ambiguous(self) -> None:
        unresolved = (
            ("source_a", "technical_tables", 20, "unresolved"),
            [self.candidate(coverage_status="unresolved")],
        )
        ambiguous = (
            ("source_b", "equipment_matrix", 20, "ambiguous"),
            [self.candidate(source_code="source_b", domain="equipment_matrix")],
        )
        self.assertEqual(
            sorted([unresolved, ambiguous], key=prioritization.package_group_sort_key)[0],
            ambiguous,
        )

    def test_package_group_order_prefers_technical(self) -> None:
        equipment = (
            ("source_a", "equipment_matrix", 20, "ambiguous"),
            [self.candidate(domain="equipment_matrix")],
        )
        technical = (
            ("source_b", "technical_tables", 20, "ambiguous"),
            [self.candidate(source_code="source_b")],
        )
        self.assertEqual(
            sorted([equipment, technical], key=prioritization.package_group_sort_key)[0],
            technical,
        )

    def test_package_group_order_prefers_larger_group(self) -> None:
        small = (("source_a", "technical_tables", 20, "ambiguous"), [self.candidate()])
        large_candidates = [
            self.candidate(candidate_id=f"{index:064x}", source_code="source_b")
            for index in range(2)
        ]
        large = (("source_b", "technical_tables", 20, "ambiguous"), large_candidates)
        self.assertEqual(
            sorted([small, large], key=prioritization.package_group_sort_key)[0],
            large,
        )

    def test_make_package_preserves_candidate_identity_and_text(self) -> None:
        candidate = self.candidate()
        package = prioritization.make_package(
            1,
            prioritization.boundary_key(candidate),
            1,
            1,
            1,
            [candidate],
        )
        self.assertEqual(package["candidate_ids"], [candidate["candidate_id"]])
        self.assertEqual(package["candidates"][0]["exact_text"], candidate["exact_text"])

    def test_make_package_rejects_cross_boundary_candidate(self) -> None:
        candidate = self.candidate()
        wrong = self.candidate(candidate_id="b" * 64, page=21)
        with self.assertRaisesRegex(
            prioritization.ResidualGapPrioritizationError, "crosses"
        ):
            prioritization.make_package(
                1,
                prioritization.boundary_key(candidate),
                2,
                1,
                1,
                [candidate, wrong],
            )

    def test_build_selects_only_residual_statuses(self) -> None:
        values = [
            self.candidate(),
            self.candidate(candidate_id="b" * 64, coverage_status="unresolved", evidence_signatures=[]),
            self.candidate(candidate_id="c" * 64, coverage_status="already_covered"),
        ]
        payload = prioritization.build_prioritization(self.reconciliation(values))
        self.assertEqual(payload["summary"]["candidate_count"], 2)
        self.assertEqual(
            {candidate for package in payload["packages"] for candidate in package["candidate_ids"]},
            {"a" * 64, "b" * 64},
        )

    def test_build_assigns_each_residual_candidate_once(self) -> None:
        values = [
            self.candidate(candidate_id=f"{index:064x}", line_start=index + 1, line_end=index + 1)
            for index in range(41)
        ]
        payload = prioritization.build_prioritization(self.reconciliation(values))
        assigned = [identifier for package in payload["packages"] for identifier in package["candidate_ids"]]
        self.assertEqual(len(assigned), 41)
        self.assertEqual(len(set(assigned)), 41)
        self.assertEqual([package["candidate_count"] for package in payload["packages"]], [40, 1])

    def test_build_preserves_status_boundary(self) -> None:
        values = [
            self.candidate(),
            self.candidate(candidate_id="b" * 64, coverage_status="unresolved", evidence_signatures=[]),
        ]
        payload = prioritization.build_prioritization(self.reconciliation(values))
        self.assertEqual(len(payload["packages"]), 2)
        self.assertEqual(
            [package["coverage_status"] for package in payload["packages"]],
            ["ambiguous", "unresolved"],
        )

    def test_duplicate_reconciliation_candidate_is_rejected(self) -> None:
        candidate = self.candidate()
        with self.assertRaisesRegex(
            prioritization.ResidualGapPrioritizationError, "not unique"
        ):
            prioritization.build_prioritization(self.reconciliation([candidate, copy.deepcopy(candidate)]))

    def test_no_residual_candidates_is_rejected(self) -> None:
        value = self.candidate(coverage_status="already_covered")
        with self.assertRaisesRegex(
            prioritization.ResidualGapPrioritizationError, "no residual"
        ):
            prioritization.build_prioritization(self.reconciliation([value]))

    def test_render_markdown_is_deterministic(self) -> None:
        payload = prioritization.build_prioritization(self.reconciliation([self.candidate()]))
        self.assertEqual(
            prioritization.render_markdown(payload),
            prioritization.render_markdown(copy.deepcopy(payload)),
        )
        self.assertIn("Highest priority", prioritization.render_markdown(payload))

    def test_restricted_output_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(
                prioritization.ResidualGapPrioritizationError, "restricted"
            ):
                prioritization.ensure_safe_output(root, Path("data/master/output.json"))
            with self.assertRaisesRegex(
                prioritization.ResidualGapPrioritizationError, "restricted"
            ):
                prioritization.ensure_safe_output(root, Path("data/imports/output.json"))

    def test_verify_output_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.json"
            path.write_text("different\n", encoding="utf-8")
            with self.assertRaisesRegex(
                prioritization.ResidualGapPrioritizationError, "differs"
            ):
                prioritization.verify_output(path, "expected\n", "output")


class ResidualGapPrioritizationRepositoryTests(unittest.TestCase):
    def test_real_repository_partition_and_highest_priority(self) -> None:
        payload, markdown = prioritization.build_from_path(
            ROOT, prioritization.DEFAULT_RECONCILIATION
        )
        self.assertEqual(payload["summary"]["candidate_count"], 1264)
        self.assertEqual(
            payload["summary"]["coverage_status_counts"],
            {'ambiguous': 111, 'unresolved': 1153},
        )
        self.assertEqual(payload["summary"]["package_count"], 52)
        self.assertEqual(payload["summary"]["maximum_package_size"], 40)
        self.assertEqual(
            payload["highest_priority_package"],
            {'package_id': 'residual_gap_001',
             'priority': 1,
             'source_code': 'src_pl_bigster_brochure_20251210',
             'model_code': 'bigster',
             'domain': 'technical_tables',
             'page': 20,
             'coverage_status': 'ambiguous',
             'candidate_count': 25,
             'evidence_signature_count': 198,
             'evidence_record_count': 733},
        )
        assigned = [identifier for package in payload["packages"] for identifier in package["candidate_ids"]]
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertIn(prioritization.NEXT_PACKAGE, markdown)


if __name__ == "__main__":
    unittest.main()
