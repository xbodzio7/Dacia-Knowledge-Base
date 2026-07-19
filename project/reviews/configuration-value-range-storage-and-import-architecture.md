# Configuration Value Range Storage and Import Architecture

## Status

`IMPLEMENTING`

This package implements the storage and import foundation of approved Option A.
It adds a separate numeric range table and leaves the stable scalar observation
table unchanged.

## Master table

`data/master/configuration_attribute_value_ranges.csv` has the exact contract:

- `id`;
- `code`;
- `configuration_code`;
- `attribute_code`;
- `fuel_type_code`;
- `minimum_value`;
- `maximum_value`;
- `lower_inclusive`;
- `upper_inclusive`;
- `observation_date`;
- `source_code`;
- `notes`.

The architecture package intentionally leaves the table header-only. No Jogger
range is imported until storage, validation and reporting are independently
green.

## Declarative importer

The new versioned kind is `configuration_attribute_value_ranges`. It requires:

- one active integer or decimal attribute contract;
- canonical numeric endpoint text;
- a strictly increasing minimum and maximum;
- explicit boolean endpoint inclusivity;
- configuration and optional fuel context;
- ISO observation date;
- registered source and source-to-configuration mapping;
- page, section and source text provenance;
- append-only contiguous IDs within the range table;
- no scalar observation with the same configuration, attribute, fuel and date.

The importer reuses the scalar importer's registered-file SHA-256 and PDF-page
text verification.

## Global validation

The repository validator checks:

- exact table header;
- positive contiguous IDs and unique codes;
- unique semantic keys;
- active numeric attributes;
- known configurations, fuels and sources;
- source registration metadata and configuration coverage;
- canonical endpoints and strict endpoint order;
- `true` or `false` inclusivity flags;
- ISO dates and non-empty notes;
- absence of scalar/range collisions.

## SQLite

The existing generic SQLite builder discovers every master CSV recursively.
Therefore the new header-only CSV becomes a typed-text SQLite table without a
special migration or change to scalar tables.

## Package boundary

This PR does not:

- import Jogger ranges;
- alter `configuration_attribute_values.csv`;
- count ranges as completeness evidence;
- expose ranges through source-coverage reports;
- compare identical, overlapping or disjoint ranges.

Those reporting semantics belong to the next logical package.

## Expected baseline

After implementation:

- 512 tests;
- 37 master CSV files and 3,845 rows;
- 1,204 scalar configuration values;
- 71 scalar configuration-value import specifications;
- 1,811 equipment-availability records;
- 357 canonical attributes in 30 categories;
- 0 range observations.

## Next package

**Configuration Value Range Reporting Integration** will make range observations
visible to completeness and source coverage, then add comparison states for
identical, overlapping and disjoint ranges before any Jogger range import.
