from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
text = path.read_text(encoding="utf-8")
header = "### Added\n"
entry = (
    header
    + "\n* Deterministic six-sheet XLSX workbooks for comparison bundles.\n"
    + "* Typed values, evidence states and byte-identical Linux/Windows output."
)
if entry not in text:
    if header not in text:
        raise RuntimeError("changelog Added marker not found")
    text = text.replace(header, entry, 1)
path.write_text(text, encoding="utf-8")
