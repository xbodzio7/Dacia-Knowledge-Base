from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "README.md"
text = path.read_text(encoding="utf-8")
marker = "`cross_scope_pairs_generated` zawsze ma wartość `false`."
addition = (
    marker
    + "\n\nPakiet tworzy także deterministyczny skoroszyt XLSX z sześcioma arkuszami, "
    + "pełnymi stanami porównań i proweniencją. Szczegółowy kontrakt opisuje "
    + "`project/packages/configuration-comparison-workbook-export.md`."
)
if addition not in text:
    if marker not in text:
        raise RuntimeError("README workbook marker not found")
    text = text.replace(marker, addition, 1)
path.write_text(text, encoding="utf-8")
