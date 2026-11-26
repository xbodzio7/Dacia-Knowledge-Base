# Attribute Enum Domain Registry and Jogger Battery Chemistry

## Status

`IMPLEMENTED`

This package implements the controlled-value stage of approved Option A. Enum
configuration observations are resolved through one reusable attribute-to-domain
registry rather than attribute-specific validation code.

## Registry contract

`data/master/attribute_enum_domains.csv` contains one active row per controlled
enum attribute:

- `attribute_code` — active canonical attribute with `data_type=enum`;
- `domain_file` — basename of a CSV below `data/master/enums/`;
- `status` — currently `active`.

The initial registry covers ten unambiguous mappings:

- aspiration type;
- cylinder configuration;
- drive type;
- emission standard;
- engine type;
- fuel type;
- gearbox type;
- hybrid battery type;
- injection type;
- recommended fuel.

## Validation behavior

The package requires:

- exact registry and domain schemas;
- one mapping per attribute;
- active enum attributes and active controlled values;
- safe domain-file basenames below `data/master/enums/`;
- global membership validation for every enum-valued configuration observation;
- importer rejection of enum values outside the registered domain;
- status validation that discovers attribute-domain files from the registry;
- preservation of all existing drive, emission, gearbox and injection values.

## Battery chemistry import

A new domain contains the controlled code `lithium_ion`. One strict declarative
specification materializes IDs 1199–1204 for all six active Jogger Hybrid 155
configurations:

| Seats | Configurations | Value | Observations |
| --- | ---: | --- | ---: |
| 5 | 3 | `lithium_ion` | 3 |
| 7 | 3 | `lithium_ion` | 3 |
| **Total** | **6** | **`lithium_ion`** | **6** |

The observation date is `2026-04-01`, the source is the registered Polish Jogger
MY26 price list, and provenance points to page 6 section `SILNIKI`.

## Evidence boundary

The source-stated 1.4 kWh value remains absent. The source does not identify it
as gross, nominal or usable capacity, while the existing
`hybrid_battery_capacity` attribute means usable capacity. No unspecified-basis
attribute or measurement-basis architecture is introduced.

## Expected baseline

After materialization:

- 502 tests;
- 36 master CSV files and 3,845 rows;
- 1,204 dated configuration values;
- 71 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 357 canonical attributes in 30 categories.

## Next package

**Jogger Range Observation Architecture** will add a separate range-observation
table, importer, validators, SQLite support and reporting semantics without
changing the stable scalar observation table.

## Local validation

The repaired package passed 502 tests, canonical-state verification and the
complete local Quality gate before removing its temporary workflow. The final
branch contains no temporary workflow, audit or diagnostic-log artifact.
