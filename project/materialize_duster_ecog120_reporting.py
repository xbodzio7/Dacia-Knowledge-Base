from __future__ import annotations

import json
from pathlib import Path


def insert_once(text: str, anchor: str, addition: str, *, after: bool) -> str:
    if addition.strip() in text:
        return text
    if text.count(anchor) != 1:
        raise RuntimeError(f"expected one anchor: {anchor!r}")
    replacement = anchor + addition if after else addition + anchor
    return text.replace(anchor, replacement, 1)


def update_quality_workflow() -> None:
    path = Path(".github/workflows/quality.yml")
    text = path.read_text(encoding="utf-8")
    step = '''
      - name: Generate Duster Eco-G 120 reporting artifacts
        if: matrix.python-version == '3.13'
        run: |
          python tools/dkb.py configuration-completeness \
            --spec data/reporting/duster_ecog120_completeness.json \
            --as-of 2026-02-06 \
            --json "${RUNNER_TEMP}/duster-ecog120-completeness.json" \
            --markdown "${RUNNER_TEMP}/duster-ecog120-completeness.md"
          python tools/dkb.py source-coverage \
            --spec data/reporting/duster_ecog120_completeness.json \
            --as-of 2026-02-06 \
            --json "${RUNNER_TEMP}/duster-ecog120-source-coverage.json" \
            --markdown "${RUNNER_TEMP}/duster-ecog120-source-coverage.md"
          python tools/dkb.py configuration-comparison \
            --completeness-spec data/reporting/duster_ecog120_completeness.json \
            --evidence-spec data/reporting/duster_ecog120_gap_evidence.spec \
            --as-of 2026-02-06 \
            --json "${RUNNER_TEMP}/duster-ecog120-comparison.json" \
            --markdown "${RUNNER_TEMP}/duster-ecog120-comparison.md" \
            --csv "${RUNNER_TEMP}/duster-ecog120-comparison-differences.csv"

'''
    text = insert_once(
        text,
        "      - name: Generate Quality artifact manifest\n",
        step,
        after=False,
    )
    manifest = '''            --file "${RUNNER_TEMP}/duster-ecog120-completeness.json" \
            --file "${RUNNER_TEMP}/duster-ecog120-completeness.md" \
            --file "${RUNNER_TEMP}/duster-ecog120-source-coverage.json" \
            --file "${RUNNER_TEMP}/duster-ecog120-source-coverage.md" \
            --file "${RUNNER_TEMP}/duster-ecog120-comparison.json" \
            --file "${RUNNER_TEMP}/duster-ecog120-comparison.md" \
            --file "${RUNNER_TEMP}/duster-ecog120-comparison-differences.csv" \
'''
    text = insert_once(
        text,
        '            --file "${RUNNER_TEMP}/configuration-comparison-pair-summary.csv" \\\n',
        manifest,
        after=True,
    )
    upload = '''            ${{ runner.temp }}/duster-ecog120-completeness.json
            ${{ runner.temp }}/duster-ecog120-completeness.md
            ${{ runner.temp }}/duster-ecog120-source-coverage.json
            ${{ runner.temp }}/duster-ecog120-source-coverage.md
            ${{ runner.temp }}/duster-ecog120-comparison.json
            ${{ runner.temp }}/duster-ecog120-comparison.md
            ${{ runner.temp }}/duster-ecog120-comparison-differences.csv
'''
    text = insert_once(
        text,
        "            ${{ runner.temp }}/configuration-comparison-pair-summary.csv\n",
        upload,
        after=True,
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def update_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-18"
    state["reference_delivery"] = {
        "name": "Duster III Equipment Availability Import",
        "pull_request": 84,
        "head_sha": "13eb8741b50324e4cfdd7f6761123428a8ec0e0a",
        "quality_run": 315,
    }
    state["baseline"]["tests"] = 446
    state["current_package"] = {
        "name": "Remaining Duster Powertrain Reporting Portfolio Review",
        "status": "active",
        "goal": "Review the six remaining homogeneous Duster powertrain groups and select the next source-complete reporting subset without changing the Sandero or Eco-G 120 denominators.",
    }
    state["next_package"] = {
        "name": "Selected Remaining Duster Reporting Promotion Implementation",
        "status": "planned",
        "goal": "Publish the next selected homogeneous Duster reporting subset through the existing Quality artifact workflow with deterministic comparison outputs.",
    }
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_narrative() -> None:
    readme = Path("README.md")
    text = readme.read_text(encoding="utf-8")
    anchor = """Macierze wyposażenia stron 4-7 dostarczają 1 392 datowane rekordy
dostępności dla 58 kanonicznych atrybutów i 24 konfiguracji Duster.
Import zachowuje jawne statusy `standard`, `optional` i `not_available`,
a pozycje warunkowe lub bez bezpiecznego mapowania pozostawia poza zakresem.
"""
    addition = """
Pierwszy jawnie promowany podzbiór raportowy Duster obejmuje cztery aktualne
konfiguracje Eco-G 120. Ma pełne pokrycie 17 slotów technicznych, 58 atrybutów
wyposażenia i cen, a jego sześć porównań jest publikowanych jako oddzielne
artefakty bez zmiany domyślnego zakresu Sandero.
"""
    if addition.strip() not in text:
        if anchor not in text:
            raise RuntimeError("README Duster equipment anchor not found")
        text = text.replace(anchor, anchor + addition, 1)
    readme.write_text(text, encoding="utf-8", newline="\n")

    changelog = Path("CHANGELOG.md")
    text = changelog.read_text(encoding="utf-8")
    bullet = "* Explicit Duster Eco-G 120 reporting subset with complete technical, equipment, price and source coverage plus six deterministic trim comparisons.\n"
    if bullet not in text:
        text = text.replace("### Added\n\n", "### Added\n\n" + bullet, 1)
    changelog.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    update_quality_workflow()
    update_state()
    update_narrative()
