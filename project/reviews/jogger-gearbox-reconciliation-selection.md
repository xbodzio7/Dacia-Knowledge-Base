# Jogger Gearbox Reconciliation Selection

## Decision status

`SELECTED`

The remaining Jogger page-6 gearbox evidence is exact and can be represented by
existing master entities, model associations and configuration attributes. No
new gearbox type, relation or range model is required.

## Source evidence

| Source group | Source text | Configurations | Canonical gearbox type | Gear count |
| --- | --- | ---: | --- | ---: |
| Eco-G 120 manual | `manualna`, `6-biegowa` | 6 | `manual` | 6 |
| Eco-G 120 automatic | `automatyczna dwusprzęgłowa`, `6-biegowa` | 4 | `dct` | 6 |
| TCe 110 manual | `manualna`, `6-biegowa` | 6 | `manual` | 6 |
| Hybrid 155 automatic | `automatyczna Multi-mode` | 6 | `hybrid` | not stated |

The selected scalar denominator is therefore:

- 22 exact `gearbox_type` observations;
- 16 exact `gear_count` observations;
- **38 observations total**, planned as IDs 1069–1106 in two declarative
  specifications.

Hybrid 155 receives no `gear_count` value. `Multi-mode` is a transmission type,
not evidence for a numeric forward-gear count.

## Master-data reconciliation

The current repository already contains:

- `mt6`, current, manual, six forward gears;
- `edc6`, dual-clutch with six forward gears, but marked archived;
- `e_dht155`, current hybrid transmission;
- an open Jogger `mt6` association from 2021;
- an open Jogger `e_dht140` association from 2023.

The implementation will:

1. retain the existing open Jogger `mt6` association;
2. close the Jogger `e_dht140` association at 2025;
3. reactivate `edc6` because the accepted MY26 source explicitly reintroduces a
   six-speed dual-clutch Jogger configuration;
4. add Jogger associations for `edc6` and `e_dht155` from 2026.

The source does not state the internal codes `mt6`, `edc6` or `e_dht155`.
Those mappings are repository master-data reconciliations based on the exact
existing entity contracts. They will be documented in association notes and
will not be copied into a source-stated `gearbox_code` observation.

## Selected implementation boundary

**Jogger Gearbox Association and Observation Reconciliation** will modify only:

- `gearboxes.csv` status/notes for the returning `edc6` entity;
- `model_gearboxes.csv` Jogger lifecycle associations;
- two declarative configuration-value specifications;
- 38 appended configuration observations;
- focused regression tests and synchronized documentation/state.

It will not modify configuration identities, powertrain labels, prices,
injection observations, the 312-value scalar denominator or any Duster/Sandero
reporting scope.

## Remaining deferred evidence

The following still require separate modelling decisions:

- WLTP fuel-consumption and CO2 ranges;
- payload ranges and minimum-qualified kerb weights;
- the unassigned Hybrid acceleration range;
- two cargo measurements with distinct height boundaries;
- LPG total versus permitted filling capacity;
- Hybrid system power and battery capacity semantics;
- Eco-G and TCe engine-speed ranges.

## Selection rationale

This package resolves a concrete stale master association and adds broad exact
coverage for all 22 configurations. Every selected value is source-stated, the
three canonical transmission types already exist, and the Hybrid numeric gear
count remains absent rather than inferred.

## Next package

After implementation, **Jogger Range and Qualifier Modeling Review** will assess
the remaining evidence that cannot be stored in the current exact scalar model.
