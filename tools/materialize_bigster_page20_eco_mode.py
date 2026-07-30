#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = Path(__file__).resolve()
SOURCE_COMMIT = "9437ce094378f153980f67ac5f0678d10fc6269b"

completed = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:tools/materialize_bigster_page20_eco_mode.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
source = completed.stdout
old = '''    replace_once(closure_test, '"src_pl_bigster_brochure_20251210": 180,', '"src_pl_bigster_brochure_20251210": 194,')
'''
new = '''    closure_text = closure_test.read_text(encoding="utf-8")
    marker = "EXPECTED_CURRENT_SCALAR = Counter("
    if closure_text.count(marker) != 1:
        raise RuntimeError("current scalar contract marker differs")
    prefix, current_section = closure_text.split(marker, 1)
    old_current = '"src_pl_bigster_brochure_20251210": 180,'
    if current_section.count(old_current) != 1:
        raise RuntimeError("expected one current Bigster scalar total")
    closure_test.write_text(
        prefix + marker + current_section.replace(old_current, '"src_pl_bigster_brochure_20251210": 194,', 1),
        encoding="utf-8",
        newline="\\n",
    )
'''
if source.count(old) != 1:
    raise SystemExit("original materializer patch target differs")
quality = subprocess.run(
    ["git", "show", "origin/main:.github/workflows/quality.yml"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
(ROOT / ".github/workflows/quality.yml").write_text(
    quality.stdout,
    encoding="utf-8",
    newline="\n",
)
PATH.write_text(source.replace(old, new), encoding="utf-8", newline="\n")
os.execv(sys.executable, [sys.executable, str(PATH)])
