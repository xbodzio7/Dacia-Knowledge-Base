from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import pdf_candidate_ledger as ledger  # noqa: E402


class PdfCandidateLedgerTests(unittest.TestCase):
    def fixture(
        self,
        root: Path,
        *,
        pages: tuple[str, ...] = ("DANE TECHNICZNE\nMoc: 74 kW\n",),
        reverse_sources: bool = False,
    ) -> tuple[Path, dict[str, list[str]]]:
        source_specs = []
        extracted: dict[str, list[str]] = {}
        for index, code in enumerate(("src_b", "src_a"), start=1):
            path = root / "PDF" / f"source-{index}.pdf"
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"fixture-{code}".encode("utf-8")
            path.write_bytes(payload)
            source_specs.append(
                {
                    "source_code": code,
                    "title": code,
                    "document_date": "2026-01-01",
                    "url": "https://example.invalid/source.pdf",
                    "file_path": path.relative_to(root).as_posix(),
                    "pages": len(pages),
                    "publication_marker": "01.01.2026",
                    "model_code": f"model_{index}",
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
            extracted[path.name] = list(pages)
        if reverse_sources:
            source_specs.reverse()
        receipt = root / "project" / "sources" / "receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps(
                {
                    "version": 1,
                    "kind": "official_dacia_brochure_source_receipt",
                    "sources": source_specs,
                }
            ),
            encoding="utf-8",
        )
        return receipt, extracted

    @staticmethod
    def extractor(page_map: dict[str, list[str]], *, optional: bool = False):
        def extract(path: Path, declared_pages: int):
            pages = page_map[path.name]
            assert len(pages) == declared_pages
            result = {
                "pdftotext-layout": pages,
                "pdftotext-default": list(pages),
                "pdftotext-raw": list(pages),
            }
            if optional:
                result["pypdf"] = ["optional ignored"] * declared_pages
            return result

        return extract

    def build(self, root: Path, receipt: Path, page_map: dict[str, list[str]], **kwargs):
        return ledger.build_ledger(
            root,
            receipt,
            page_counter=lambda path: len(page_map[path.name]),
            document_extractor=self.extractor(page_map, **kwargs),
            version_reader=lambda: "pdftotext version fixture",
        )

    def test_receipt_sources_are_sorted_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root, reverse_sources=True)
            result = self.build(root, receipt, page_map)
        self.assertEqual(
            [item["source_code"] for item in result["sources"]],
            ["src_a", "src_b"],
        )
        self.assertEqual(result["source_count"], 2)
        self.assertEqual(result["page_count"], 2)

    def test_byte_size_drift_fails_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["sources"][0]["bytes"] += 1
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ledger.CandidateLedgerError, "byte size differs"):
                self.build(root, receipt, page_map)

    def test_sha256_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["sources"][0]["sha256"] = "0" * 64
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ledger.CandidateLedgerError, "SHA-256 differs"):
                self.build(root, receipt, page_map)

    def test_page_count_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            with self.assertRaisesRegex(ledger.CandidateLedgerError, "page count differs"):
                ledger.build_ledger(
                    root,
                    receipt,
                    page_counter=lambda path: len(page_map[path.name]) + 1,
                    document_extractor=self.extractor(page_map),
                    version_reader=lambda: "pdftotext version fixture",
                )

    def test_candidate_identifiers_are_stable(self) -> None:
        first = ledger.candidate_id("a" * 64, 3, "nonempty_line", 4, 4, "Tekst")
        second = ledger.candidate_id("a" * 64, 3, "nonempty_line", 4, 4, "Tekst")
        changed = ledger.candidate_id("a" * 64, 3, "nonempty_line", 5, 5, "Tekst")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertEqual(len(first), 64)

    def test_optional_backend_presence_does_not_change_canonical_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            without_optional = self.build(root, receipt, page_map)
            with_optional = self.build(root, receipt, page_map, optional=True)
        self.assertEqual(ledger.json_bytes(without_optional), ledger.json_bytes(with_optional))

    def test_empty_page_requires_visual_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root, pages=("",))
            result = self.build(root, receipt, page_map)
        self.assertEqual(result["candidate_count"], 2)
        for item in result["candidates"]:
            self.assertEqual(item["review_status"], "requires_visual_review")
            self.assertEqual(item["rule_code"], "empty_page_text")
            self.assertNotIn("not_stated", json.dumps(item))

    def test_repeated_json_output_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            first = ledger.json_bytes(self.build(root, receipt, page_map))
            second = ledger.json_bytes(self.build(root, receipt, page_map))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_repeated_markdown_output_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            first = ledger.markdown_bytes(self.build(root, receipt, page_map))
            second = ledger.markdown_bytes(self.build(root, receipt, page_map))
        self.assertEqual(first, second)
        self.assertIn(b"Promotion boundary", first)

    def test_surface_rules_cover_initial_candidate_kinds(self) -> None:
        cases = {
            "DANE TECHNICZNE": "heading",
            "Silnik    999 cm3": "table_row",
            "dostępne w opcji": "availability_text",
            "100–120 km/h": "range_text",
            "Moc: 74 kW": "scalar_text",
            "Dacia Sandero": "unclassified_text",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                _, actual = ledger.classify_candidate(text)
                self.assertEqual(actual, expected)

    def test_candidate_records_have_all_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            result = self.build(root, receipt, page_map)
        for item in result["candidates"]:
            self.assertEqual(tuple(item), ledger.REQUIRED_CANDIDATE_FIELDS)

    def test_build_does_not_modify_master_or_import_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, page_map = self.fixture(root)
            master = root / "data" / "master" / "sentinel.csv"
            imports = root / "data" / "imports" / "sentinel.json"
            master.parent.mkdir(parents=True, exist_ok=True)
            imports.parent.mkdir(parents=True, exist_ok=True)
            master.write_text("unchanged\n", encoding="utf-8")
            imports.write_text("{}\n", encoding="utf-8")
            before = (master.read_bytes(), imports.read_bytes())
            self.build(root, receipt, page_map)
            after = (master.read_bytes(), imports.read_bytes())
        self.assertEqual(before, after)

    def test_restricted_output_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ledger.CandidateLedgerError, "cannot be written"):
                ledger.ensure_safe_output(root / "data" / "master" / "ledger.json", root)
            with self.assertRaisesRegex(ledger.CandidateLedgerError, "cannot be written"):
                ledger.ensure_safe_output(root / "data" / "imports" / "ledger.json", root)

    def test_split_document_pages_preserves_declared_pages(self) -> None:
        self.assertEqual(
            ledger.split_document_pages("page one\x0cpage two\x0c", 2),
            ["page one", "page two"],
        )
        with self.assertRaisesRegex(ledger.CandidateLedgerError, "extracted page count differs"):
            ledger.split_document_pages("only one", 2)

    @unittest.skipUnless(
        shutil.which("pdftotext") and shutil.which("pdfinfo"),
        "Poppler tools are required for the repository artifact check",
    )
    def test_committed_repository_artifacts_match_registered_pdfs(self) -> None:
        result = ledger.build_ledger(REPOSITORY, ledger.DEFAULT_RECEIPT)
        self.assertEqual(result["source_count"], 5)
        self.assertEqual(result["page_count"], 114)
        self.assertGreater(result["candidate_count"], 0)
        self.assertNotIn("not_stated", json.dumps(result))
        self.assertEqual(ledger.DEFAULT_JSON.read_bytes(), ledger.json_bytes(result))
        self.assertEqual(
            ledger.DEFAULT_MARKDOWN.read_bytes(),
            ledger.markdown_bytes(result),
        )


if __name__ == "__main__":
    unittest.main()
