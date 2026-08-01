"""One-shot repair for the temporary package generator; deletes itself after use."""
from pathlib import Path

root = Path(__file__).resolve().parent
builder = root / "tools" / "build_sandero_stepway_expression_auto_source_gap_20260801.py"
if builder.exists():
    text = builder.read_text(encoding="utf-8")
    old = r"r'expected_counts = \{.*?\n        \}'"
    new = r"r'expected_counts = \{.*?\}'"
    if old in text:
        builder.write_text(text.replace(old, new, 1), encoding="utf-8")
    elif new not in text:
        raise RuntimeError("context snapshot matcher anchor not found")
Path(__file__).unlink()
