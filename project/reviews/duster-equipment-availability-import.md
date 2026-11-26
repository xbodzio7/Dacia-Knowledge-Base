# Duster Equipment Availability Import

## Scope

This package imports version-level equipment availability stated explicitly in
pages 4–7 of the official Duster MY26/PY25 price list and expands each stated
trim status to every source-backed configuration of that trim within the
corresponding powertrain matrix.

The durable input is split into two declarative matrices:

- `data/imports/duster_equipment_availability_appearance.csv` for seats,
  safety and visibility rows from pages 4 and 6,
- `data/imports/duster_equipment_availability_control.csv` for driving,
  comfort and multimedia rows from pages 5 and 7.

## Normalization contract

Source symbols are normalized as follows:

- a filled dot becomes `standard`,
- an explicit dash becomes `not_available`,
- a package marker or explicit option price becomes `optional`,
- a missing or ambiguous cell creates no record.

The source describes availability by version rather than by full powertrain
configuration. Each status is therefore expanded to every existing,
source-backed configuration belonging to that version and source matrix. The
expansion is recorded in every row note and does not assert differences that
are absent from the document.

## Evidence boundary

The import is limited to 58 attributes that already exist in the canonical
catalogue and can be mapped without creating a new domain interpretation.

The package deliberately excludes:

- exterior colours, upholstery variants and wheel dimensions, which are
  configuration values rather than equipment-availability flags,
- package names as synthetic attributes,
- adaptive cruise control because the source makes availability conditional
  on transmission and the version-level matrix alone is insufficient,
- seat adjustments and other rows that cannot be mapped to a current
  canonical attribute without a separate modelling decision.

No blank, footnote-only statement or conditional phrase is converted into a
single unconditional configuration-level fact.

## Result

- 58 source-backed attributes,
- 24 active Duster configurations,
- 1,392 new availability records,
- 1,092 `standard`, 112 `optional` and 188 `not_available` records,
- 1,811 total availability records in the repository,
- unchanged 419 non-Duster availability records,
- unchanged Duster catalogue prices and technical observations,
- unchanged seven-configuration Sandero reporting subset.

## Reproducibility

`tools/import_duster_equipment_availability.py` verifies the registered PDF
SHA-256, matrix headers, active attributes, active status vocabulary, exact
row count, status distribution and per-configuration coverage. `--apply`
materializes the master rows idempotently; `--check` verifies semantic parity
between the matrices and stored data.
