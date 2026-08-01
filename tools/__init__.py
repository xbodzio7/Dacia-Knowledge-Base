"""One-shot initializer for the temporary Extreme automatic materializer."""
from pathlib import Path

package_dir = Path(__file__).resolve().parent
target = package_dir / "import_sandero_stepway_extreme_auto_source_gap_20260626.py"
if target.exists():
    text = target.read_text(encoding="utf-8")
    old = "sandero_stepway_expression_auto_source_gap_review"
    new = "sandero_stepway_extreme_auto_source_gap_review"
    if old in text:
        target.write_text(text.replace(old, new), encoding="utf-8")
    elif new not in text:
        raise RuntimeError("Extreme automatic review-path anchor not found")
    Path(__file__).unlink()
