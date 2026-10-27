# Jogger Injection-Type Import

## Status

`IMPLEMENTED`

The accepted Jogger MY26 page-6 injection evidence is represented as 32 exact,
dated configuration observations without changing the canonical attribute or
enum dictionaries.

## Imported denominator

| Group | Configurations | Contexts | Observations |
| --- | ---: | --- | ---: |
| Eco-G 120 manual | 6 | petrol + LPG | 12 |
| Eco-G 120 automatic | 4 | petrol + LPG | 8 |
| TCe 110 manual | 6 | none | 6 |
| Hybrid 155 automatic | 6 | none | 6 |
| **Total** | **22** | — | **32** |

The rows use IDs 1037–1068 and observation date `2026-04-01`. They are governed
by one strict declarative import specification and reference the exact
repository-local Jogger source, page 6, section `SILNIKI`.

## Controlled mapping

- source `benzyna bezpośredni` maps to `direct_injection` with `petrol` context;
- source `LPG pośredni` maps to `port_injection` with `lpg` context;
- source `bezpośredni` maps to `direct_injection` without a fuel qualifier;
- source `wielopunktowy` maps to `multi_point_injection` without a fuel qualifier.

All targets were active before this package. No enum code, engine entity,
gearbox entity, model association or configuration identity was created or
modified.

## Semantic guarantees

Every Eco-G configuration has two observations. The import does not collapse the
petrol and LPG systems into one generic injection value. TCe 110 and Hybrid 155
retain their single source-stated values.

The shared importer verifies the active `injection_type` attribute contract,
source-to-configuration relations, contiguous IDs, registered source hash and
exact page text. Dedicated regression tests additionally require all imported
values to belong to the active injection enum.

## Unchanged evidence boundary

This package does not reinterpret any remaining deferred evidence. WLTP and
payload ranges, minimum-qualified kerb weights, the Hybrid acceleration range,
condition-specific cargo measurements, LPG total/filling capacity, hybrid
system/battery semantics, gearbox associations and engine-speed ranges remain
outside scalar data.

## Verified baseline

After materialization the expected repository baseline is:

- 464 tests;
- 34 master CSV files and 3,690 rows;
- 1,068 dated configuration values;
- 62 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 351 canonical attributes in 30 categories.

## Next package

**Jogger Remaining Deferred Technical Evidence Review** will reassess the
remaining ranges, qualifiers, measurement boundaries and master-association
questions and select the next bounded package without weakening source meaning.
