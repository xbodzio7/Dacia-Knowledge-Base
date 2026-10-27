# Jogger Remaining Technical Architecture Review

## Status

`ACTION_REQUIRED`

All Jogger MY26 page-6 observations that fit the repository's existing exact
scalar model without loss of source meaning have been implemented. The
remaining evidence crosses controlled-value, measurement-basis or interval
architecture boundaries and must not be imported under the current schema.

## Completed exact evidence

The completed Jogger packages now cover:

- 312 exact scalar observations;
- 32 injection-type observations;
- 38 gearbox-type and source-stated gear-count observations;
- 22 minimum-qualified kerb-weight observations;
- 44 measurement-specific VDA cargo observations;
- 20 LPG total-vessel and filling-capacity observations;
- 6 source-stated total hybrid-system-power observations.

The resulting page-6 suffix ends at configuration-value ID 1198.

## Remaining source evidence

| Evidence | Source form | Current blocker |
| --- | --- | --- |
| Hybrid battery chemistry | lithium-ion | `hybrid_battery_type` is enum, but no controlled battery dictionary or validated attribute-to-domain mapping exists |
| Hybrid battery capacity | 1.4 kWh | source does not state gross, nominal or usable basis; current attribute means usable capacity |
| Fuel consumption | closed numeric ranges | scalar `value` field cannot preserve both endpoints |
| CO2 emissions | closed numeric ranges | scalar `value` field cannot preserve both endpoints |
| Maximum payload | five-/seven-seat numeric ranges | scalar value would discard variability and endpoint semantics |
| Hybrid acceleration | 8.9-9.0 s | scalar value would select an unsupported representative point |
| Power and torque engine speeds | rpm ranges | current integer attributes accept one point only |

No endpoint, midpoint, average or preferred value is source-authorized.

## Decision 1: controlled battery chemistry

### E1 — Dedicated battery dictionary

Add `data/master/enums/battery_chemistries.csv`, hard-code it into current
reference/status validators, and validate `hybrid_battery_type` observations
against it.

**Consequences**

- smallest implementation;
- matches the repository's current hard-coded enum-file pattern;
- permits six `lithium_ion` observations immediately;
- adds another special case and does not solve other enum attributes lacking
  controlled domains.

### E2 — General attribute-to-enum-domain registry — recommended

Add a canonical registry such as `attribute_enum_domains.csv` that maps each
enum attribute to a controlled domain file. Update import, reference and status
validation to resolve enum values through the registry. Register existing
controlled attributes and add a battery-chemistry domain containing
`lithium_ion`.

**Consequences**

- larger first package than E1;
- removes hard-coded coupling between import logic and individual enum files;
- provides a reusable contract for future enum attributes;
- requires migration tests proving all currently controlled enums retain their
  behavior.

### E3 — Store chemistry as a literal string — not recommended

Change or bypass the enum contract and import source text directly.

**Consequences**

- fastest path;
- weakens canonical consistency and permits spelling variants;
- contradicts the current `hybrid_battery_type` enum definition.

## Decision 2: battery-capacity basis

### B1 — Defer 1.4 kWh until a basis-qualified source is available — recommended

Keep the existing usable-capacity attribute unchanged and do not import the
unqualified value.

**Consequences**

- zero semantic loss;
- no architecture work;
- capacity remains absent until a gross, nominal or usable basis is proven.

### B2 — Add an unspecified-basis capacity attribute — not recommended

Introduce `hybrid_battery_capacity_unspecified_basis` and import 1.4 kWh.

**Consequences**

- preserves the literal source value;
- creates a weak concept that cannot be compared safely with gross or usable
  capacities;
- likely requires later migration or deprecation.

### B3 — Add measurement-basis context

Introduce a reusable capacity-observation model with an explicit basis code
such as `gross`, `nominal`, `usable` or `unspecified`.

**Consequences**

- most expressive long-term model;
- requires schema, importer, reporting and migration decisions beyond the
  current Jogger milestone;
- an `unspecified` observation still has limited comparison value.

## Decision 3: interval-valued observations

### R1 — Separate range-observation table — recommended

Add `configuration_attribute_value_ranges.csv` rather than changing the scalar
table. A proposed initial contract is:

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

Add a versioned import-spec kind for ranges and validators for references,
attribute numeric type, canonical endpoint formatting, endpoint order,
uniqueness and source provenance.

Reporting must preserve range semantics. At minimum it should distinguish:

- identical ranges;
- different but overlapping ranges;
- disjoint ranges;
- missing or not-applicable evidence.

**Consequences**

- leaves all existing scalar rows and import specs unchanged;
- supports every remaining Jogger interval without attribute proliferation;
- requires new SQLite, statistics, source-coverage and comparison/reporting
  behavior;
- creates a reusable model for future catalogue ranges.

### R2 — Extend the scalar table with value-kind and endpoint columns

Change `configuration_attribute_values.csv` to contain scalar and range rows.

**Consequences**

- one unified observation table;
- changes the stable CSV header and every importer, validator, SQLite builder,
  report and test that consumes it;
- substantially higher migration and regression risk.

### R3 — Create minimum and maximum attributes per concept — not recommended

Represent each source range using pairs such as consumption minimum/maximum or
payload minimum/maximum.

**Consequences**

- works with the current scalar table;
- multiplies canonical attributes and embeds observation shape into attribute
  identity;
- scales poorly and makes comparison semantics inconsistent across domains.

## Approval packages

### Option A — Staged reusable architecture — recommended

1. Implement E2: generalized enum-domain registry and six lithium-ion
   observations.
2. Keep battery capacity deferred under B1.
3. Implement R1 as a separate range-observation table, then import all remaining
   page-6 ranges in bounded follow-up packages.

This option has moderate implementation cost and the strongest reusable model
without rewriting existing scalar data.

### Option B — Minimal architecture

1. Implement E1: one dedicated battery-chemistry dictionary and six
   lithium-ion observations.
2. Keep battery capacity and every interval deferred.

This option has the lowest immediate risk but leaves most remaining source
evidence unavailable.

### Option C — Unified broad redesign

1. Implement E2.
2. Implement B3 measurement-basis context.
3. Implement R2 by redesigning the scalar observation table.

This option offers the broadest single model but has the highest migration,
reporting and regression risk. It is not recommended for the current
milestone.

## Required approval

Approve **Option A**, **Option B** or **Option C**, or provide a modified
combination. No architecture implementation should begin before this decision.

## Resume stage

`jogger_remaining_architecture_approval`
