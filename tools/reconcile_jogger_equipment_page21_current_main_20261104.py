#!/usr/bin/env python3
"""Reconcile Jogger brochure page 21 selected evidence against current main."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE_SHA256 = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
AMBIGUITY = ROOT / "data/reporting/jogger_equipment_page21_ambiguity_review.json"
CHUNKS = (
    ROOT / "data/reporting/jogger_equipment_page21_unresolved_review_chunk1.json",
    ROOT / "data/reporting/jogger_equipment_page21_unresolved_review_chunk2.json",
)
MASTER = ROOT / "data/master/configuration_attribute_availability.csv"
REPORT = ROOT / "data/reporting/jogger_equipment_page21_current_main_reconciliation_20261104.json"
REVIEW = ROOT / "project/reviews/jogger-equipment-page21-current-main-reconciliation-2026-11-04.md"

class ReconciliationError(RuntimeError):
    pass

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ReconciliationError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-sha", required=True)
    parser.add_argument("--expected-main-sha", required=True)
    args = parser.parse_args()
    if args.main_sha != args.expected_main_sha:
        raise ReconciliationError(
            "main advanced after this package branch was created; refresh the branch "
            f"(expected {args.expected_main_sha}, found {args.main_sha})"
        )
    if len(args.main_sha) != 40:
        raise ReconciliationError("main SHA must be a full 40-character commit")

    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ReconciliationError(f"Jogger brochure SHA-256 mismatch: {digest}")

    review = read_json(AMBIGUITY)
    receipt = review["source_receipt"]
    if (receipt["source_code"] != "src_pl_jogger_brochure_20251217"
        or receipt["page"] != 21 or receipt["sha256"] != SOURCE_SHA256
        or review["status"] != "complete"):
        raise ReconciliationError("page-21 ambiguity review source receipt differs")

    selected: dict[str, dict] = {}
    for decision in review["decisions"]:
        if decision["authored_decision"] != "deferred_source_conflict":
            raise ReconciliationError("the page-21 Journey conflict must remain deferred")
        for signature in decision["selected_evidence_signatures"]:
            expected_attribute = signature["signature"]["attribute_code"]
            expected_status = signature["signature"]["availability_status"]
            for item in signature["records"]:
                if item["table"] != "configuration_attribute_availability":
                    raise ReconciliationError("unexpected evidence table in page-21 review")
                code = item["record_code"]
                record = {
                    "record_code": code,
                    "configuration_code": item["configuration_code"],
                    "source_code": item["source_code"],
                    "source_page": item["source_page"],
                    "attribute_code": expected_attribute,
                    "availability_status": expected_status,
                }
                if code in selected and selected[code] != record:
                    raise ReconciliationError(f"conflicting review references for {code}")
                selected[code] = record

    if len(selected) != 30:
        raise ReconciliationError(f"expected 30 unique selected record codes, found {len(selected)}")
    if review["summary"]["selected_evidence_record_count"] != 30:
        raise ReconciliationError("ambiguity review selected-record count differs")
    if review["summary"]["selected_evidence_signature_count"] != 2:
        raise ReconciliationError("ambiguity review signature count differs")

    fields, master_rows = read_csv(MASTER)
    required = {"code", "configuration_code", "source_code", "attribute_code", "availability_status"}
    if not required.issubset(fields):
        raise ReconciliationError(f"availability master schema lacks {sorted(required - set(fields))}")
    by_code: dict[str, list[dict[str, str]]] = {}
    for row in master_rows:
        by_code.setdefault(row["code"], []).append(row)

    checked = []
    for code, expected in sorted(selected.items()):
        matches = by_code.get(code, [])
        if len(matches) != 1:
            raise ReconciliationError(f"expected exactly one current-main row for {code}, found {len(matches)}")
        actual = matches[0]
        for field in ("configuration_code", "source_code", "attribute_code", "availability_status"):
            if actual.get(field, "") != expected[field]:
                raise ReconciliationError(
                    f"current-main mismatch for {code}.{field}: "
                    f"{actual.get(field)!r} != {expected[field]!r}"
                )
        if expected["source_page"] is not None and "source_page" in actual:
            if str(actual["source_page"]) != str(expected["source_page"]):
                raise ReconciliationError(f"current-main source-page mismatch for {code}")
        checked.append({**expected, "current_main_presence": "present"})

    unresolved_count = 0
    unresolved_chunks = []
    for path in CHUNKS:
        chunk = read_json(path)
        scope, summary = chunk["scope"], chunk["summary"]
        if chunk["status"] != "complete":
            raise ReconciliationError(f"unresolved review is not closed: {path.name}")
        if summary["selected_evidence_signature_count"] != 0 or summary["selected_evidence_record_count"] != 0:
            raise ReconciliationError(f"unresolved chunk unexpectedly has selected evidence: {path.name}")
        if not chunk["policy"]["zero_attached_evidence_preserved"]:
            raise ReconciliationError(f"unresolved evidence boundary changed: {path.name}")
        unresolved_count += scope["candidate_count"]
        unresolved_chunks.append({
            "file": path.relative_to(ROOT).as_posix(),
            "candidate_count": scope["candidate_count"],
            "selected_evidence_signature_count": summary["selected_evidence_signature_count"],
            "selected_evidence_record_count": summary["selected_evidence_record_count"],
        })
    if unresolved_count != 72:
        raise ReconciliationError(f"expected 72 unresolved candidates, found {unresolved_count}")

    report = {
        "version": 1,
        "kind": "jogger_equipment_page21_current_main_reconciliation",
        "reviewed_on": "2026-11-04",
        "status": "complete_no_new_import",
        "package_id": "jogger_equipment_page21_current_main_reconciliation_20261104_001",
        "current_main": {"branch": "main", "sha": args.main_sha},
        "source": {
            "source_code": receipt["source_code"],
            "file_path": receipt["file_path"],
            "page": receipt["page"],
            "sha256": receipt["sha256"],
        },
        "reviewed_artifacts": [
            "data/reporting/jogger_equipment_page21_ambiguity_review.json",
            "data/reporting/jogger_equipment_page21_unresolved_review_chunk1.json",
            "data/reporting/jogger_equipment_page21_unresolved_review_chunk2.json",
        ],
        "scope": {
            "ambiguity_candidates": 1,
            "selected_evidence_signature_count": 2,
            "selected_evidence_record_references": 30,
            "unique_selected_record_codes": 30,
            "selected_record_codes_already_present_in_current_main": len(checked),
            "missing_selected_record_codes": 0,
            "unresolved_candidates": unresolved_count,
            "unresolved_review_chunks": unresolved_chunks,
        },
        "summary": {
            "review_decisions": {"deferred_source_conflict": 1},
            "all_selected_observations_already_present": True,
            "no_exact_import_ready_gap": True,
            "master_data_changes": 0,
            "import_specs_added": 0,
        },
        "selected_evidence_records": checked,
        "result": (
            "All 30 unique selected record codes are present exactly once in current main "
            "configuration_attribute_availability.csv. The 72 unresolved candidates have no "
            "selected evidence signatures. Preserve the heated-steering-wheel Journey conflict "
            "as deferred; no new import or master-data change is warranted."
        ),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text(
        "# Jogger Brochure Equipment Page 21 — Current Main Reconciliation\n\n"
        "Date: 2026-11-04  \n"
        f"Current main: {args.main_sha}  \n"
        f"Source: {receipt['source_code']}, page 21\n\n"
        "## Result\n\n"
        "**No new import.** All 30 unique selected evidence record codes from the completed "
        "ambiguity review are present exactly once in current-main "
        "data/master/configuration_attribute_availability.csv.\n\n"
        "| Review outcome | Count |\n|---|---:|\n"
        "| Deferred heated-steering-wheel source conflict | 1 |\n"
        "| Selected evidence signatures | 2 |\n"
        "| Selected evidence records | 30 |\n"
        "| Selected codes missing from current main | 0 |\n"
        "| Unresolved candidates without selected evidence | 72 |\n\n"
        "The 72 unresolved candidates remain non-importable: both completed review chunks have "
        "zero selected evidence signatures and zero selected records. The Journey heated-steering-wheel "
        "conflict remains deferred; no configuration availability is inferred.\n\n"
        "## Scope closure\n\n"
        "- New import specifications: 0\n"
        "- Master-data changes: 0\n"
        "- Repeated page review: prohibited unless new direct evidence appears\n\n"
        "Durable machine-readable receipt: "
        "data/reporting/jogger_equipment_page21_current_main_reconciliation_20261104.json.\n",
        encoding="utf-8",
    )
    print("Jogger page-21 current-main reconciliation: PASS (30 present, 72 unresolved, no import)")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, TypeError, ValueError, ReconciliationError) as exc:
        raise SystemExit(f"ERROR: {exc}")
