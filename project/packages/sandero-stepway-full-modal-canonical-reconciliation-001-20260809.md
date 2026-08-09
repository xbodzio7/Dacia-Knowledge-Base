# Sandero Stepway Full Modal Canonical Reconciliation 001

Date: 2026-08-09
Status: complete

## Goal

Reconcile all 1,708 literal rows captured from the complete technical and standard-equipment modals of the 15 exact current Sandero and Sandero Stepway configurator states, importing only observations that can be mapped to the canonical model without inference.

## Result

- 1,708 captured rows were reviewed: 1,029 standard-equipment rows and 679 technical rows.
- 655 standard-equipment rows were mapped through exact literals that had one unique canonical attribute/status mapping in already verified historical evidence.
- 180 technical rows were mapped through an explicit allow-list of unambiguous scalar labels.
- 374 equipment rows and 499 technical rows remain preserved as literal unmatched or ambiguous evidence.
- The full-modal snapshot is registered as `src_pl_sandero_stepway_full_modal_20260809` and linked to all 15 exact configurations.
- 655 dated availability observations and 180 dated technical value observations were added for 2026-08-09.

## Import boundaries

- No grade, engine, gearbox or model inheritance is inferred.
- Absence from the standard-equipment modal does not imply `not_available`.
- Composite literals that historically decompose into more than one canonical attribute remain unresolved in this package.
- Model-qualified, mixed petrol/LPG, composite dimension and otherwise non-scalar technical strings remain source evidence only.
- Unmatched rows are retained in `data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json` for future source-backed reconciliation.

## Changed data surfaces

- `data/master/sources.csv`
- `data/master/source_configurations.csv`
- `data/master/configuration_attribute_availability.csv`
- `data/master/configuration_attribute_values.csv`
- `data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json`
- `data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.md`

## Verification

`tests/test_sandero_stepway_full_modal_canonical_reconciliation_20260809.py` protects the 1,708-row accounting, 15 exact source/configuration relationships, canonical observation counts, source/date boundaries and explicit residual evidence.

## Follow-up

The remaining 873 rows are not errors. They form a bounded residual set for later exact reconciliation when the canonical schema or source evidence supports a non-ambiguous mapping.
