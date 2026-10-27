# Sandero Stepway Technical Page 17 Ambiguity Review

Date: 2026-07-28
Source: `src_pl_sandero_stepway_brochure_20260202`
Page: 17
Package: `residual_gap_005`

## Scope

The package reviews all four ambiguous technical candidates and all twelve attached evidence signatures without changing master data or approved import specifications.

## Authored decisions

- line 42, `Układ kierowniczy –`: partially covered by the exact 10.64 m turning-circle signature; suspension, tyre and kerb-mass signatures belong to other rows;
- line 80, `gotowego do jazdy`: unresolved signature mismatch because the fragment completes the minimum kerb-mass row 1095/1194/1222 kg while both attached signatures are maximum masses;
- line 81, `Maksymalna masa pojazdu`: partially covered by 1225 and 1249 kg for manual and automatic Eco-G; the visible 1149 kg TCe 110 value remains unattached;
- line 83, `gotowego do jazdy`: the same maximum-row boundary is preserved and the two Eco-G signatures remain valid.

## Evidence result

Five signatures and fifteen exact evidence records are selected. Three candidates are partially covered and one remains an explicit cross-row signature mismatch.

## Safety boundary

- no file under `data/master` changes;
- no file under `data/imports` changes;
- no automatic promotion is authorized;
- evidence is not exchanged between steering, suspension, tyre, minimum-mass and maximum-mass rows;
- selected Eco-G values are not projected onto TCe 110.

## Next package

`Duster Mini Technical Page 21 Ambiguity Review` — one ambiguous technical candidate with seven preserved evidence signatures.
