from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / ".github/workflows/quality.yml"
STATE = ROOT / "project/state.json"
REVIEW = ROOT / "project/reviews/jogger-ecog120-automatic-reporting-scope-promotion.md"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    original = subprocess.check_output(
        ["git", "show", "origin/main:.github/workflows/quality.yml"], cwd=ROOT, text=True
    )

    generation_anchor = "      - name: Generate Quality artifact manifest\n"
    generation = '''      - name: Generate Jogger Eco-G 120 automatic reporting artifacts
        if: matrix.python-version == '3.13'
        run: |
          python tools/dkb.py configuration-completeness \\
            --spec data/reporting/jogger_ecog120_automatic_completeness.json \\
            --as-of 2026-04-01 \\
            --json "${RUNNER_TEMP}/jogger-ecog120-automatic-completeness.json" \\
            --markdown "${RUNNER_TEMP}/jogger-ecog120-automatic-completeness.md"
          python tools/dkb.py source-coverage \\
            --spec data/reporting/jogger_ecog120_automatic_completeness.json \\
            --as-of 2026-04-01 \\
            --json "${RUNNER_TEMP}/jogger-ecog120-automatic-source-coverage.json" \\
            --markdown "${RUNNER_TEMP}/jogger-ecog120-automatic-source-coverage.md"
          python tools/dkb.py configuration-comparison \\
            --completeness-spec data/reporting/jogger_ecog120_automatic_completeness.json \\
            --evidence-spec data/reporting/jogger_ecog120_automatic_gap_evidence.spec \\
            --as-of 2026-04-01 \\
            --json "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison.json" \\
            --markdown "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison.md" \\
            --csv "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison-differences.csv"

'''
    if generation_anchor not in original:
        raise RuntimeError("quality generation anchor not found")
    text = original.replace(generation_anchor, generation + generation_anchor, 1)

    manifest_anchor = '            --file "${RUNNER_TEMP}/duster-ecog120-comparison-differences.csv" \\\n            --file "reports/validation_report.md"'
    manifest_files = '''            --file "${RUNNER_TEMP}/duster-ecog120-comparison-differences.csv" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-completeness.json" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-completeness.md" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-source-coverage.json" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-source-coverage.md" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison.json" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison.md" \\
            --file "${RUNNER_TEMP}/jogger-ecog120-automatic-comparison-differences.csv" \\
            --file "reports/validation_report.md"'''
    if manifest_anchor not in text:
        raise RuntimeError("quality manifest anchor not found")
    text = text.replace(manifest_anchor, manifest_files, 1)

    upload_anchor = "            ${{ runner.temp }}/duster-ecog120-comparison-differences.csv\n            ${{ runner.temp }}/artifact-manifest.json"
    upload_files = '''            ${{ runner.temp }}/duster-ecog120-comparison-differences.csv
            ${{ runner.temp }}/jogger-ecog120-automatic-completeness.json
            ${{ runner.temp }}/jogger-ecog120-automatic-completeness.md
            ${{ runner.temp }}/jogger-ecog120-automatic-source-coverage.json
            ${{ runner.temp }}/jogger-ecog120-automatic-source-coverage.md
            ${{ runner.temp }}/jogger-ecog120-automatic-comparison.json
            ${{ runner.temp }}/jogger-ecog120-automatic-comparison.md
            ${{ runner.temp }}/jogger-ecog120-automatic-comparison-differences.csv
            ${{ runner.temp }}/artifact-manifest.json'''
    if upload_anchor not in text:
        raise RuntimeError("quality upload anchor not found")
    text = text.replace(upload_anchor, upload_files, 1)
    QUALITY.write_text(text, encoding="utf-8")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["baseline"]["tests"] = 551
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    review = REVIEW.read_text(encoding="utf-8")
    review = review.replace("`IMPLEMENTING`", "`IMPLEMENTED`", 1)
    REVIEW.write_text(review, encoding="utf-8")

    run("python", "tools/dkb.py", "project-state", "--apply")
    run("python", "tools/dkb.py", "documentation-baseline", "--apply")
    run("python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q")
    run("python", "tools/dkb.py", "quality", "--concise", "--database", "/tmp/dkb.sqlite", "--log-file", "/tmp/dkb-quality.log", "--summary-json", "/tmp/dkb-quality.json")


if __name__ == "__main__":
    main()
