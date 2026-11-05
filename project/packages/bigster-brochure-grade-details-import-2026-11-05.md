# Bigster brochure grade-specific cabin details import — 2026-11-05

## Scope
Import the historical grade-specific cabin details stated on printed pages 14–17 of the registered 2025-12-10 Bigster brochure. This is a bounded sub-package of `official_bigster_brochure_full_assimilation_20261014_001`.

## Manifest
- `data/master/configuration_attribute_values.csv`
- 16 files under `data/imports/configuration_values/bigster-page14-17-*-20251210.json`
- `data/reporting/bigster_brochure_grade_details_import_20261105.json`
- `data/reporting/bigster_brochure_grade_details_import_20261105.md`
- `tests/test_bigster_brochure_grade_details_20251210.py`
- `project/state.json` and synchronized baseline documentation

## Acceptance
1. Add 56 source-specific scalar observations for four existing attributes.
2. Target only the 14 active configurations already linked to the brochure.
3. Preserve the explicit grade inheritance chain and the optional six-speaker Media Nav Live boundary for Expression.
4. Preserve later 2026 configurator observations; do not overwrite any existing row.
5. Verify the registered brochure SHA-256 and exact PDF/printed page mapping.
6. Pass the focused regression test and full repository Quality on the final PR head.

## Evidence boundary
The source is the registered official Polish Bigster brochure dated 2025-12-10. Imported attributes are parking brake type, steering-wheel material, rear-seat folding layout and speaker count. No new attribute or source relationship is introduced.
