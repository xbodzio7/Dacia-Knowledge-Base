from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import configuration_gap_source_review as review  # noqa: E402


class ConfigurationGapSourceReviewTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        fieldnames: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)

    def fixture(
        self,
    ) -> tuple[
        tempfile.TemporaryDirectory[str],
        Path,
        dict,
        dict,
        dict[tuple[str, int], str],
    ]:
        temporary = tempfile.TemporaryDirectory()
        repository = Path(temporary.name)
        source_path = repository / "PDF" / "source-a.pdf"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(b"fixture-pdf-a")
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()

        self.write_csv(
            repository / "data" / "master" / "sources.csv",
            [
                "id",
                "code",
                "title",
                "document_date",
                "file_path",
                "sha256",
                "status",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "src_a",
                    "title": "Source A",
                    "document_date": "2026-06-01",
                    "file_path": "PDF/source-a.pdf",
                    "sha256": digest,
                    "status": "active",
                    "notes": "",
                }
            ],
        )
        self.write_csv(
            repository
            / "data"
            / "master"
            / "configuration_attribute_availability.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "availability_status",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "anchor-camera",
                    "configuration_code": "cfg_a",
                    "attribute_code": "anchor_camera",
                    "availability_status": "standard",
                    "observation_date": "2026-06-01",
                    "source_code": "src_a",
                    "notes": "Source page 3: kotwica strony trzeciej",
                }
            ],
        )
        self.write_csv(
            repository
            / "data"
            / "master"
            / "configuration_attribute_values.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "value",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "anchor-wheel",
                    "configuration_code": "cfg_a",
                    "attribute_code": "anchor_wheel",
                    "fuel_type_code": "",
                    "value": "ATARA",
                    "observation_date": "2026-06-01",
                    "source_code": "src_a",
                    "notes": (
                        'Source page 2, section Felgi: '
                        '16" felgi stalowe ATARA'
                    ),
                }
            ],
        )
        self.write_csv(
            repository
            / "data"
            / "master"
            / "configuration_prices.csv",
            [
                "id",
                "code",
                "configuration_code",
                "currency_code",
                "gross_price",
                "observation_date",
                "source_code",
                "notes",
            ],
            [],
        )

        def decision(
            key: str,
            attribute_code: str,
        ) -> dict:
            return {
                "triage_key": key,
                "domain": "equipment",
                "source_code": "src_a",
                "configuration_code": "cfg_a",
                "category": "Test",
                "attribute_code": attribute_code,
                "fuel_type_code": "",
                "document_date": "2026-06-01",
                "file_path": "PDF/source-a.pdf",
                "sha256": digest,
                "classification": "ambiguous",
                "candidate_value": "",
                "auto_import": False,
                "manual_source_review_required": True,
                "reason_code": (
                    "direct_source_statement_not_yet_retained"
                ),
                "review_note": "Review required.",
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "reviewed_pages": [],
                "basis": None,
            }

        evidence = {
            "version": 1,
            "as_of": "2026-06-01",
            "review_scope": "structured_evidence_only",
            "review_policy": {
                "allowed_classifications": sorted(
                    review.CLASSIFICATIONS
                ),
                "auto_import": False,
            },
            "decisions": [
                decision("camera", "rear_view_camera"),
                decision("bluetooth", "bluetooth_connectivity"),
                decision("wheel", "wheel_design"),
            ],
        }
        rules = {
            "version": 1,
            "kind": "configuration_gap_source_page_review",
            "as_of": "2026-06-01",
            "review_scope": "relevant_source_pages",
            "auto_import": False,
            "review_triage_keys": [
                "camera",
                "bluetooth",
                "wheel",
            ],
            "rules": [
                {
                    "attribute_code": "rear_view_camera",
                    "source_section": "Equipment",
                    "review_pages": [3],
                    "matches": [
                        {
                            "needle": "kamera cofania",
                            "candidate_value": "standard",
                            "exclude_needles": [],
                        }
                    ],
                },
                {
                    "attribute_code": "bluetooth_connectivity",
                    "source_section": "Equipment",
                    "review_pages": [3],
                    "matches": [
                        {
                            "needle": "Bluetooth",
                            "candidate_value": "standard",
                            "exclude_needles": [],
                        }
                    ],
                },
                {
                    "attribute_code": "wheel_design",
                    "source_section": "Felgi",
                    "review_pages": [2],
                    "matches": [
                        {
                            "needle": "ATARA",
                            "candidate_value": "ATARA",
                            "exclude_needles": [],
                        },
                        {
                            "needle": "TAMIA",
                            "candidate_value": "TAMIA",
                            "exclude_needles": [],
                        },
                    ],
                },
            ],
        }
        page_text = {
            (
                "source-a.pdf",
                2,
            ): (
                '16" felgi stalowe ATARA oraz felgi TAMIA\n'
                + "opis wyposażenia kół " * 20
            ),
            (
                "source-a.pdf",
                3,
            ): (
                "kotwica strony trzeciej\nkamera cofania\n"
                + "opis wyposażenia strony " * 20
            ),
        }
        return temporary, repository, evidence, rules, page_text

    def extractor(
        self,
        page_text: dict[tuple[str, int], str],
    ):
        def extract(path: Path, page: int) -> list[tuple[str, str]]:
            text = page_text.get((path.name, page), "")
            if not text:
                return []
            return [
                ("layout", text),
                ("raw", text.replace("\n", " ")),
            ]

        return extract

    def test_classifies_found_direct_statement(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)

        updated, report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )

        camera = updated["decisions"][0]
        self.assertEqual(camera["classification"], "found")
        self.assertEqual(camera["candidate_value"], "standard")
        self.assertEqual(camera["source_page"], 3)
        self.assertEqual(camera["source_text"], "kamera cofania")
        self.assertEqual(report["summary"]["found"], 1)

    def test_classifies_not_stated_after_complete_page(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)

        updated, report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )

        bluetooth = updated["decisions"][1]
        self.assertEqual(bluetooth["classification"], "not_stated")
        self.assertEqual(bluetooth["reviewed_pages"], [3])
        self.assertFalse(
            bluetooth["manual_source_review_required"]
        )
        self.assertEqual(report["summary"]["not_stated"], 1)

    def test_conflicting_candidates_remain_ambiguous(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)

        updated, report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )

        wheel = updated["decisions"][2]
        self.assertEqual(wheel["classification"], "ambiguous")
        row = report["decisions"][2]
        self.assertEqual(
            row["reason_code"],
            "conflicting_source_statements",
        )
        self.assertEqual(len(row["observations"]), 2)

    def test_incomplete_extraction_remains_ambiguous(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)
        pages.pop(("source-a.pdf", 3))

        updated, report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )

        self.assertEqual(
            updated["decisions"][0]["classification"],
            "ambiguous",
        )
        self.assertEqual(
            report["decisions"][0]["reason_code"],
            "source_page_extraction_incomplete",
        )
        self.assertGreater(
            report["summary"]["incomplete_source_pages"],
            0,
        )

    def test_rules_must_match_ambiguous_attributes(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)
        rules["rules"].pop()

        with self.assertRaisesRegex(
            review.SourcePageReviewError,
            "rules do not match target attributes",
        ):
            review.build_review(
                repository,
                rules,
                evidence,
                extractor=self.extractor(pages),
            )

    def test_source_hash_mismatch_is_rejected(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)
        source_path = repository / "PDF" / "source-a.pdf"
        source_path.write_bytes(b"changed")

        with self.assertRaisesRegex(
            review.SourcePageReviewError,
            "SHA-256 differs",
        ):
            review.build_review(
                repository,
                rules,
                evidence,
                extractor=self.extractor(pages),
            )

    def test_source_text_window_prefers_shortest_window(self) -> None:
        text = (
            "prefix line\n"
            "kamera cofania\n"
            "long suffix line\n"
        )
        self.assertEqual(
            review.source_text_window(text, "kamera cofania"),
            "kamera cofania",
        )

    def test_page_extraction_uses_anchor_calibration(self) -> None:
        def extractor(
            path: Path,
            page: int,
        ) -> list[tuple[str, str]]:
            return [
                ("short", "unrelated content" * 20),
                (
                    "anchored",
                    "kotwica strony trzeciej "
                    + "additional content " * 20,
                ),
            ]

        result = review.page_extraction(
            Path("source.pdf"),
            3,
            ["kotwica strony trzeciej"],
            extractor=extractor,
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["backend"], "anchored")
        self.assertEqual(result["recovered_anchors"], 1)

    def test_updated_spec_and_report_are_deterministic(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)
        first_spec, first_report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )
        second_spec, second_report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )
        self.assertEqual(
            review.render_json(first_spec),
            review.render_json(second_spec),
        )
        self.assertEqual(
            review.render_json(first_report),
            review.render_json(second_report),
        )
        self.assertEqual(
            first_spec["review_scope"],
            "source_page_evidence",
        )

    def test_markdown_is_deterministic_and_conservative(self) -> None:
        temporary, repository, evidence, rules, pages = self.fixture()
        self.addCleanup(temporary.cleanup)
        _, report = review.build_review(
            repository,
            rules,
            evidence,
            extractor=self.extractor(pages),
        )
        markdown = review.render_markdown(report)
        self.assertIn(
            "# Configuration Gap Source Page Review",
            markdown,
        )
        self.assertIn("| Found | 1 |", markdown)
        self.assertIn("| Not stated | 1 |", markdown)
        self.assertIn("| Still ambiguous | 1 |", markdown)
        self.assertIn("automatic import is disabled", markdown)

    def test_parse_args_accepts_review_outputs_and_verify(self) -> None:
        arguments = review.parse_args(
            [
                "--review-spec",
                "review.json",
                "--evidence-spec",
                "evidence.json",
                "--write-evidence-spec",
                "updated.json",
                "--verify",
                "--json",
                "report.json",
                "--markdown",
                "report.md",
            ]
        )
        self.assertEqual(
            arguments.review_spec,
            Path("review.json"),
        )
        self.assertEqual(
            arguments.evidence_spec,
            Path("evidence.json"),
        )
        self.assertEqual(
            arguments.write_evidence_spec,
            Path("updated.json"),
        )
        self.assertTrue(arguments.verify)
        self.assertEqual(arguments.json_path, Path("report.json"))
        self.assertEqual(arguments.markdown, Path("report.md"))


if __name__ == "__main__":
    unittest.main()
