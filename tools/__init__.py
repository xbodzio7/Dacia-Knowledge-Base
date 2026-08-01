"""One-shot initializer for the temporary package generator."""
from pathlib import Path

package_dir = Path(__file__).resolve().parent
builder = package_dir / "build_sandero_stepway_expression_auto_source_gap_20260801.py"
text = builder.read_text(encoding="utf-8")
old = "r'expected_counts = \\{.*?\\n        \\}'"
new = "r'expected_counts = \\{.*?\\}'"
if old in text:
    builder.write_text(text.replace(old, new, 1), encoding="utf-8")
elif new not in text:
    raise RuntimeError("context snapshot matcher anchor not found")
Path(__file__).unlink()
