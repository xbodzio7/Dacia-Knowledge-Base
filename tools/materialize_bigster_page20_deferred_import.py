#!/usr/bin/env python3
from __future__ import annotations

import ast
import base64
import gzip
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = Path(__file__).resolve()
SOURCE_COMMIT = "d45c07cafc4cc8042e765af7241ec9df515f15b4"

completed = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:tools/materialize_bigster_page20_deferred_import.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
match = re.search(r'^payload = (".*")$', completed.stdout, re.MULTILINE)
if match is None:
    raise SystemExit("original compressed payload is missing")
payload = ast.literal_eval(match.group(1))
source = gzip.decompress(base64.b64decode(payload)).decode("utf-8")
source = source.replace(
    'SECTION = "DANE TECHNICZNE"',
    'SECTION = "ZUŻYCIE PALIWA I EMISJA CO2"',
)
source = source.replace(
    'self.assertEqual(spec["source_section"], "DANE TECHNICZNE")',
    'self.assertEqual(spec["source_section"], "ZUŻYCIE PALIWA I EMISJA CO2")',
)
PATH.write_text(source, encoding="utf-8", newline="\n")
exec(compile(source, str(PATH), "exec"))
