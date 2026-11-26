# Jogger Gearbox Association and Observation Reconciliation

## Status

`COMPLETE`

The accepted Jogger MY26 page-6 gearbox evidence is represented by exact
configuration observations and reconciled against the repository's existing
transmission master entities.

## Configuration denominator

| Group | Configurations | `gearbox_type` | `gear_count` | Observations |
| --- | ---: | --- | --- | ---: |
| Eco-G 120 manual | 6 | `manual` | 6 | 12 |
| Eco-G 120 automatic | 4 | `dct` | 6 | 8 |
| TCe 110 manual | 6 | `manual` | 6 | 12 |
| Hybrid 155 automatic | 6 | `hybrid` | not source-stated | 6 |
| **Total** | **22** | **22 rows** | **16 rows** | **38** |

Two strict declarative specifications materialize IDs 1069–1106 with
observation date `2026-04-01`, source page 6 and section `SILNIKI`.

Hybrid 155 has no numeric `gear_count`. The source's `automatyczna Multi-mode`
text supports the canonical hybrid transmission type but does not state a
forward-gear count.

## Master-data reconciliation

The implementation preserves and updates existing entities rather than creating
source-invented codes:

- `mt6` remains current and associated with Jogger from 2021;
- the Jogger `e_dht140` association closes at 2025;
- `edc6` returns to current status and is associated with Jogger from 2026;
- `e_dht155` is associated with Jogger from 2026.

The source does not state the internal codes `mt6`, `edc6` or `e_dht155`.
Configuration observations therefore contain only source-stated `gearbox_type`
and `gear_count` values. Entity-code mappings are documented model-association
reconciliations.

## Exact source mapping

- `manualna` maps to `manual`;
- `automatyczna dwusprzęgłowa` maps to `dct`;
- `automatyczna Multi-mode` maps to `hybrid`;
- `6-biegowa` maps to integer `6` only for the 16 configurations where that
  text is present.

## Regression guarantees

Six dedicated tests require:

- two specifications and the contiguous 38-row ID suffix;
- type counts `manual=12`, `dct=4`, `hybrid=6`;
- exactly 16 six-gear observations and no Hybrid numeric count;
- unchanged exact contracts for `mt6`, `edc6` and `e_dht155`;
- the closed `e_dht140` and open MY26 `edc6`/`e_dht155` Jogger associations;
- registered source hash plus declared page and text contracts.

## Verified baseline

The verified repository baseline is:

- 470 tests;
- 34 master CSV files and 3,730 rows;
- 1,106 dated configuration values;
- 64 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 351 canonical attributes in 30 categories.

## Remaining evidence boundary

WLTP and payload ranges, minimum-qualified kerb weights, the unassigned Hybrid
acceleration range, condition-specific cargo measurements, LPG total/filling
capacity, hybrid system and battery semantics, and Eco-G/TCe engine-speed ranges
remain outside the exact scalar model.

## Next package

**Jogger Range and Qualifier Modeling Review** will determine which remaining
evidence requires range endpoints, explicit qualifiers or new measurement
semantics before any further import.
