# Brochure Cargo Measurement Context Model

Date: 2026-07-25

## Purpose

Define the smallest reusable representation that can preserve the cargo-volume contexts
found in the registered Sandero, Sandero Stepway, Jogger, Bigster and Duster brochures
without creating a new attribute for every combination of measurement method, seat
state and equipment state.

## Existing limitation

`configuration_attribute_values.csv` stores one numeric value with configuration,
attribute, fuel, date, source and notes. It cannot distinguish multiple valid
`boot_capacity` values for the same configuration and source when those values differ
by VDA versus ordinary litres, raised versus folded seats, underfloor versus main space,
or spare-wheel, repair-kit and double-floor conditions.

The catalogue already contains historical cargo attributes that encode selected
qualifiers in their names. Extending that pattern to all brochure combinations would
multiply attributes, make comparisons brittle and still fail to preserve grouped seat
states such as a folded-or-removed third row.

## Accepted representation

The numeric observation stays in `configuration_attribute_values.csv` under the neutral
`boot_capacity` attribute. A new optional one-to-one
`configuration_cargo_volume_contexts.csv` relation will carry only the context needed
to interpret that value.

Planned fields:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `configuration_attribute_value_code` | required, unique | Referenced cargo value |
| `measurement_basis_code` | required | VDA/ISO 3832 or ordinary source-stated litres |
| `second_row_state_code` | optional | Upright, folded, removed or explicit grouped state |
| `third_row_state_code` | optional | Upright, folded, removed or explicit grouped state |
| `compartment_code` | required | Main, underfloor or source-stated total space |
| `spare_wheel_state_code` | optional | Explicit present or absent qualifier |
| `tyre_repair_kit_state_code` | optional | Explicit present or absent qualifier |
| `double_floor_state_code` | optional | Explicit present or absent qualifier |
| `notes` | optional | Remaining source wording and audit detail |

## Dimensions inherited from configuration

Five- versus seven-seat layout and 4x2 versus 4x4 grouping are preserved through the
exact target configuration. They are not duplicated in the context row. Importers must
prove that every selected configuration matches the brochure group before materializing
the value.

## Conservative rules

- Empty optional fields mean not stated, not absent.
- A repair kit is not inferred merely because a spare wheel is absent.
- A spare wheel is not inferred merely because a repair kit is absent.
- Main and underfloor volumes remain separate unless the source states a total.
- Maximum capacity is represented through explicit seat state, not a new maximum-only
  attribute.
- Context-distinct observations must remain separate in reports and SQLite.
- Existing specialized cargo observations are retained without migration.

## Rejected alternatives

### More cargo-specific attributes

Rejected because every new combination of VDA, seat row, compartment, wheel and floor
state would require another attribute and would encode observation context in the
vocabulary rather than the observation.

### Many optional columns in every value row

Rejected because almost all current configuration values do not need cargo-specific
columns. A sparse one-to-one relation keeps the stable value schema focused.

### Generic key-value measurement context

Rejected for this package because type-dependent keys and values would weaken reference
validation and introduce a broad architecture before another domain proves the need.
Gear-specific elasticity remains deferred.

## Follow-up

The next package shall implement the header-only relation and controlled dictionaries,
reference and semantic validation, SQLite discovery, data-dictionary coverage and
regression tests. No brochure cargo values shall be imported until those surfaces and
context-aware reporting behavior are available.
