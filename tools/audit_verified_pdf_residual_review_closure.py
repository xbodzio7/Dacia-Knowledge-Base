#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = Path(__file__).resolve()
SOURCE_COMMIT = "37b46d1014f39cab73c2b40edee882c4be42b31a"
SOURCE_PATH = "tools/audit_verified_pdf_residual_review_closure.py"

source = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
).stdout
old_match = '        match = status == "complete" and not missing_ids and not extra_ids and len(found) == len(expected_ids)\n'
new_match = '        assigned = found & set(expected_ids)\n        match = status == "complete" and not missing_ids and len(assigned) == len(expected_ids)\n'
if source.count(old_match) != 1:
    raise SystemExit("match contract replacement target differs")
source = source.replace(old_match, new_match)
old_row = '                "candidate_ids_match": match,\n                "related_markdown":'
new_row = '                "candidate_ids_match": match,\n                "cross_package_reference_ids": extra_ids,\n                "related_markdown":'
if source.count(old_row) != 1:
    raise SystemExit("row contract replacement target differs")
source = source.replace(old_row, new_row)
old_summary = '            "duplicate_reviewed_candidate_count": len(duplicate_reviewed_ids),\n'
new_summary = '            "duplicate_reviewed_candidate_count": len(duplicate_reviewed_ids),\n            "cross_package_reference_count": sum(len(row.get("cross_package_reference_ids", [])) for row in rows),\n'
if source.count(old_summary) != 1:
    raise SystemExit("summary contract replacement target differs")
source = source.replace(old_summary, new_summary)
PATH.write_text(source, encoding="utf-8", newline="\n")
os.execv(sys.executable, [sys.executable, str(PATH)])
