#!/usr/bin/env python3
from __future__ import annotations

import ast
import base64
import gzip
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = Path(__file__).resolve()
SOURCE_COMMIT = "e671d14d4bd26307b8e66d3fdbc4f99ad68b25c1"
completed = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:tools/materialize_bigster_page20_hybridg150_rpm.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
match = re.search(r'^payload = (".*")$', completed.stdout, re.MULTILINE)
if match is None:
    raise SystemExit("original materializer payload is missing")
payload = ast.literal_eval(match.group(1))
source = gzip.decompress(base64.b64decode(payload)).decode("utf-8")
old = '"data_type": "decimal", "unit": "rpm", "status": "active"'
new = '"data_type": "integer", "unit": "rpm", "status": "active"'
if source.count(old) != 3:
    raise SystemExit(f"expected three RPM contract occurrences, found {source.count(old)}")
source = source.replace(old, new)
PATH.write_text(source, encoding="utf-8", newline="\n")
os.execv(sys.executable, [sys.executable, str(PATH)])
