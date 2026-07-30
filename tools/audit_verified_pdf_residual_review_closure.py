#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRIORITIZATION = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
REPORTING = ROOT / "data/reporting"
OUT = ROOT / "verified_pdf_residual_review_closure_audit"
PACKAGE_RE = re.compile(r"^residual_gap_\d{3}$")
HEX64_RE = re.compile(r"\b[0-9a-f]{64}\b")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def candidate_ids_from_text(text: str, known: set[str]) -> set[str]:
    return {match.group(0) for match in HEX64_RE.finditer(text) if match.group(0) in known}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prioritization = load(PRIORITIZATION)
    packages = prioritization["packages"]
    assert len(packages) == 52
    expected = {item["package_id"]: item for item in packages}
    assert set(expected) == {f"residual_gap_{index:03d}" for index in range(1, 53)}
    all_expected_ids = [identifier for item in packages for identifier in item["candidate_ids"]]
    assert len(all_expected_ids) == len(set(all_expected_ids))
    known = set(all_expected_ids)

    artifact_candidates: dict[str, list[Path]] = defaultdict(list)
    parse_errors = []
    for path in sorted(REPORTING.glob("*.json")):
        try:
            payload = load(path)
        except Exception as exc:
            parse_errors.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
            continue
        if not isinstance(payload, dict):
            continue
        package_id = payload.get("package_id")
        if isinstance(package_id, str) and PACKAGE_RE.fullmatch(package_id):
            artifact_candidates[package_id].append(path)

    rows = []
    reviewed_ids = []
    missing_packages = []
    duplicate_artifacts = []
    mismatched_packages = []
    for package_id, package in expected.items():
        paths = artifact_candidates.get(package_id, [])
        if not paths:
            missing_packages.append(package_id)
            rows.append({"package_id": package_id, "status": "missing", "expected_count": package["candidate_count"]})
            continue
        if len(paths) > 1:
            duplicate_artifacts.append({"package_id": package_id, "paths": [str(path.relative_to(ROOT)) for path in paths]})
        path = paths[-1]
        payload = load(path)
        found: set[str] = set()
        related_markdown: set[Path] = set()
        same_stem = path.with_suffix(".md")
        if same_stem.is_file():
            related_markdown.add(same_stem)
        for text in strings(payload):
            found.update(candidate_ids_from_text(text, known))
            if text.endswith(".md"):
                candidate_path = ROOT / text
                if candidate_path.is_file():
                    related_markdown.add(candidate_path)
        for md_path in related_markdown:
            found.update(candidate_ids_from_text(md_path.read_text(encoding="utf-8"), known))
        expected_ids = list(package["candidate_ids"])
        found_ordered = [identifier for identifier in expected_ids if identifier in found]
        missing_ids = [identifier for identifier in expected_ids if identifier not in found]
        extra_ids = sorted(found - set(expected_ids))
        status = str(payload.get("status", ""))
        match = status == "complete" and not missing_ids and not extra_ids and len(found) == len(expected_ids)
        if not match:
            mismatched_packages.append(
                {
                    "package_id": package_id,
                    "artifact": str(path.relative_to(ROOT)),
                    "artifact_status": status,
                    "expected_count": len(expected_ids),
                    "found_count": len(found),
                    "missing_ids": missing_ids,
                    "extra_ids": extra_ids,
                    "related_markdown": [str(item.relative_to(ROOT)) for item in sorted(related_markdown)],
                }
            )
        reviewed_ids.extend(found_ordered)
        policy_text = json.dumps(payload.get("policy", {}), ensure_ascii=False).casefold()
        rows.append(
            {
                "package_id": package_id,
                "priority": package["priority"],
                "source_code": package["source_code"],
                "domain": package["domain"],
                "page": package["page"],
                "coverage_status": package["coverage_status"],
                "expected_count": len(expected_ids),
                "artifact": str(path.relative_to(ROOT)),
                "artifact_status": status,
                "candidate_ids_found": len(found),
                "candidate_ids_match": match,
                "related_markdown": [str(item.relative_to(ROOT)) for item in sorted(related_markdown)],
                "policy_mentions_no_master_change": "master_data_changes" in policy_text and "false" in policy_text,
            }
        )

    duplicate_reviewed_ids = [identifier for identifier, count in Counter(reviewed_ids).items() if count > 1]
    source_counts = Counter(item["source_code"] for item in packages)
    domain_counts = Counter(item["domain"] for item in packages)
    status_counts = Counter(item["coverage_status"] for item in packages)
    candidate_source_counts = Counter()
    candidate_domain_counts = Counter()
    candidate_status_counts = Counter()
    for item in packages:
        candidate_source_counts[item["source_code"]] += item["candidate_count"]
        candidate_domain_counts[item["domain"]] += item["candidate_count"]
        candidate_status_counts[item["coverage_status"]] += item["candidate_count"]

    result = {
        "version": 1,
        "kind": "verified_pdf_candidate_residual_review_closure_audit",
        "status": "pass" if not (parse_errors or missing_packages or duplicate_artifacts or mismatched_packages or duplicate_reviewed_ids) else "fail",
        "summary": {
            "package_count": len(packages),
            "expected_candidate_count": len(all_expected_ids),
            "reviewed_candidate_count": len(reviewed_ids),
            "unique_reviewed_candidate_count": len(set(reviewed_ids)),
            "missing_package_count": len(missing_packages),
            "duplicate_artifact_count": len(duplicate_artifacts),
            "mismatched_package_count": len(mismatched_packages),
            "duplicate_reviewed_candidate_count": len(duplicate_reviewed_ids),
        },
        "package_counts_by_source": dict(sorted(source_counts.items())),
        "package_counts_by_domain": dict(sorted(domain_counts.items())),
        "package_counts_by_coverage_status": dict(sorted(status_counts.items())),
        "candidate_counts_by_source": dict(sorted(candidate_source_counts.items())),
        "candidate_counts_by_domain": dict(sorted(candidate_domain_counts.items())),
        "candidate_counts_by_coverage_status": dict(sorted(candidate_status_counts.items())),
        "parse_errors": parse_errors,
        "missing_packages": missing_packages,
        "duplicate_artifacts": duplicate_artifacts,
        "mismatched_packages": mismatched_packages,
        "duplicate_reviewed_candidate_ids": duplicate_reviewed_ids,
        "packages": rows,
    }
    (OUT / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Verified PDF Candidate Residual Review Closure Audit", "",
        f"Status: **{result['status']}**", "",
        f"Packages: {len(packages)}", f"Expected candidates: {len(all_expected_ids)}",
        f"Reviewed candidates: {len(reviewed_ids)}", f"Unique reviewed candidates: {len(set(reviewed_ids))}", "",
        "| Package | Artifact | Expected | Found | Match |", "| --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['package_id']}` | `{row.get('artifact', '')}` | {row['expected_count']} | {row.get('candidate_ids_found', 0)} | {row.get('candidate_ids_match', False)} |")
    (OUT / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    if result["status"] != "pass":
        raise SystemExit("residual review closure audit failed")


if __name__ == "__main__":
    main()
