# Brochure Cargo Context Reporting Foundation

Date: 2026-07-25

## Purpose

Make every reporting and export surface preserve the measurement context accepted in
D-023 before any official brochure cargo value is imported.

## Observation identity

Scalar technical observations continue to use configuration, attribute and fuel context.
For `boot_capacity`, the semantic cargo-context signature is an additional identity
component. It contains measurement basis, second- and third-row state, compartment and
independent spare-wheel, repair-kit and double-floor states. Empty optional dimensions
remain explicit not-stated values and are not converted to `absent`.

## Reporting surfaces

- pairwise comparison JSON, Markdown, difference CSV and offline HTML;
- exact difference-context filtering and item catalog;
- deterministic comparison workbook and bundles;
- shortlist JSON, Markdown and flat CSV;
- interactive shortlist technical comparison and selection JSON export.

A missing matching context on either side is reported as missing/not comparable. It is
never matched to another cargo observation solely because the attribute and fuel are the
same.

## Compatibility

The production cargo-context relation remains header-only. Therefore existing legacy and
contextless comparison results, context-filter counts and current data products remain
unchanged. The new behavior is exercised with synthetic context-distinct observations.

## Data impact

No configuration value, range, availability, price, source mapping or brochure cargo
context row is added or changed by this package.

## Follow-up

The reporting path is ready for a source-backed official brochure cargo-value import.
