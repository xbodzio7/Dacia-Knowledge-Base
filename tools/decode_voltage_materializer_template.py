#!/usr/bin/env python3
from __future__ import annotations

import ast
import base64
import gzip
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "c4385419ad4710fa110434ee6525b083b9ef0c30"
SOURCE_PATH = "tools/materialize_bigster_page20_hybrid155_voltage.py"
OUTPUT = ROOT / "tools" / "_decoded_voltage_materializer_template.py"

completed = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
match = re.search(r"^payload = (.+)$", completed.stdout, re.MULTILINE)
if match is None:
    raise SystemExit("materializer payload is missing")
payload = ast.literal_eval(match.group(1))
source = gzip.decompress(base64.b64decode(payload)).decode("utf-8")
OUTPUT.write_text(source, encoding="utf-8", newline="\n")
print(f"Decoded {len(source)} characters to {OUTPUT.relative_to(ROOT)}")
