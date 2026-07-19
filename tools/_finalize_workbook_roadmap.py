from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "project" / "ROADMAP.md"
text = path.read_text(encoding="utf-8")
marker = (
    "- trwały wybór konfiguracji w przeglądarce z deterministycznym eksportem "
    "JSON i TXT zgodnym z pakietem porównań,"
)
addition = marker + (
    "\n- deterministyczny XLSX z sześcioma arkuszami i identycznymi bajtami "
    "na Linuxie oraz Windows,"
)
if addition not in text:
    if marker not in text:
        raise RuntimeError("roadmap workbook marker not found")
    text = text.replace(marker, addition, 1)
text = text.replace("- eksport do Excela,\n", "", 1)
path.write_text(text, encoding="utf-8")
