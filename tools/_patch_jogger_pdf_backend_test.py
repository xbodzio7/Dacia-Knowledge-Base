#!/usr/bin/env python3
from pathlib import Path

path = Path("tests/test_jogger_wltp_efficiency_ranges.py")
text = path.read_text(encoding="utf-8")
old_import = "import json\nimport unittest\n"
new_import = "import json\nimport shutil\nimport unittest\n"
old_check = "        candidates = extract_page_candidates(PDF, 6)\n"
new_check = (
    "        if shutil.which(\"pdftotext\") is None:\n"
    "            return\n"
    "        candidates = extract_page_candidates(PDF, 6)\n"
)
if new_import not in text:
    if text.count(old_import) != 1:
        raise SystemExit("unexpected import anchor")
    text = text.replace(old_import, new_import, 1)
if new_check not in text:
    if text.count(old_check) != 1:
        raise SystemExit("unexpected PDF check anchor")
    text = text.replace(old_check, new_check, 1)
path.write_text(text, encoding="utf-8")
