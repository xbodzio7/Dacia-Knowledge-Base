# Sandero Technical Page 17 Ambiguity Review

Date: 2026-07-28
Package: `residual_gap_004`
Source: `src_pl_sandero_brochure_20260202`
Page: 17

## Scope

The package reviews all five ambiguous technical-table candidates while preserving candidate IDs, exact extracted text, source lines, attached signatures and records. It creates no master-data row and no approved import specification.

## Authored decisions

- Power label, line 15: select the attached 90 kW LPG and 84 kW petrol signatures for the two Eco-G 120 automatic configurations. The source-visible TCe 74 kW cell and equivalent manual Eco-G cells remain facts without attached evidence.
- Torque label, line 19: select the attached 197 Nm LPG and 190 Nm petrol automatic signatures. TCe 200 Nm and the manual Eco-G cells are not inferred.
- Maximum kerb mass, line 82: select 1209 kg for manual Eco-G and 1232 kg for automatic Eco-G. The visible 1132 kg TCe value has no attached signature.
- First repeated gross-mass label, line 84: select only `gross_vehicle_weight=1665`; reject the attached gross-train signature for this row.
- Second repeated gross-mass label, line 87: select only `gross_train_weight=2765`; reject the attached gross-vehicle signature for this row.

## Result

All five candidates are `partially_covered`. The review selects 8 evidence signatures containing 16 exact records. Unattached values remain source facts, not inferred configuration observations.

## Safety boundary

- `data/master` is unchanged.
- `data/imports` is unchanged.
- Evidence is copied without reinterpretation.
- Automatic-only records are not projected onto manual or TCe configurations.
- Gross-vehicle and gross-train evidence is not exchanged between repeated label fragments.
- The review is not import approval.

## Next package

**Sandero Stepway Technical Page 17 Ambiguity Review** — review 4 ambiguous technical candidates and 12 preserved evidence signatures under the same no-import boundary.
