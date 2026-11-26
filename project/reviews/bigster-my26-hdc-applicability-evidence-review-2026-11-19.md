# Bigster MY26 HDC Applicability Evidence Review — 2026-11-19

## Objective

Close the bounded review of the HDC equipment row in the official Polish Bigster MY26 cennik effective 2026-10-01, printed page 4, without guessing configuration applicability.

## Exact evidence boundary

The source displays a grade-level matrix (Essential unavailable; Expression, Extreme and Journey standard) and the qualifier “wyłącznie dla wersji Extreme oraz 4x4”. The qualifier does not specify whether the two conditions are conjunctive or disjunctive. It is not safe to project the grade-level matrix to six exact configurations.

The six current configuration-level observations implement the strict Extreme AND 4x4 interpretation. Preserve them unchanged; the source does not prove that this interpretation is correct.

## Deliverables

- `data/reporting/bigster_my26_20261001_hdc_applicability_evidence_review_20261119_001.json`
- `data/reporting/bigster_my26_20261001_hdc_applicability_evidence_review_20261119_001.md`
- Report registry entry.
- No master-data or import-spec changes.

## Validation

Reuse the existing exact-source and HDC-deferral tests in `tests/test_bigster_price_list_20261001_equipment_availability.py`. The full required CI suite must pass on the exact final PR head.

## Completion rule

The evidence review may close with the fact explicitly deferred as `Do sprawdzenia`. It must not be described as a resolved HDC truth table.
