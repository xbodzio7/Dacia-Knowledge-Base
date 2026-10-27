# Duster Mini Technical Page 20 Ambiguity Review

Authored review of `residual_gap_003`. Decisions preserve page and candidate boundaries and do not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 5 |
| Covered by selected evidence | 3 |
| Partially covered | 2 |
| Selected evidence signatures | 9 |
| Selected evidence records | 34 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 52 | `ec2ff275fa561863a5da266d3c552ab95d5de4c4a1efe2135e7597da30ad6e77` | `covered_by_selected_evidence` | 1 | Układ kierowniczy                                                    układu kierowniczego            układu kierowniczego |
| 87 | `6da4e74ede4d02c9cce0f2b899db297ed61cb74316ed00120126a034ff584153` | `covered_by_selected_evidence` | 2 | Maks. masa całkowita samochodu gotowego |
| 95 | `3acabcb9d6f1db21630d6a687ae88008952748f44e44a04ca244dcfc3f863932` | `covered_by_selected_evidence` | 2 | Maks./min. ładowność(5)                                                     455/487                          454/528 |
| 103 | `86fc1329b953a27106b7ebae34c739fcb87fed2dad8dd02225966be30bda9e26` | `partially_covered` | 3 | (dm3 VDA) |
| 106 | `814fd871b681107ac44c91516f42db45b174611169bf385c3d928480125dcfbb` | `partially_covered` | 1 | zapasowym(6), (7) (dm3 VDA) |

## Partial findings

### Line 103 — `86fc1329b953a27106b7ebae34c739fcb87fed2dad8dd02225966be30bda9e26`

The unit fragment completes the upright VDA cargo row. Only 453, 517 and 474 are visible in the page-20 row; folded-row and page-21 Hybrid 155 signatures are not substituted.
- `boot_capacity`: `430`, `349`, `1415` — Hybrid 155 values belong to the following source page and are excluded from this page-20 candidate.
- `boot_capacity`: `1545`, `1609`, `1566` — These attached values belong to the following folded-seat VDA row, not the upright row completed by this fragment.

### Line 106 — `814fd871b681107ac44c91516f42db45b174611169bf385c3d928480125dcfbb`

The fragment belongs to the folded-seat VDA row and the attached 1566 dm3 spare-wheel value is selected. Repair-kit values are visible but are not attached to this candidate, while Hybrid 155 values belong to page 21.
- `boot_capacity`: `1545`, `1609` — Visible repair-kit folded-seat values remain source facts because their signatures are attached to the adjacent line-103 candidate.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- page-21 Hybrid 155 values are not substituted into page 20;
- signatures attached to an adjacent candidate are not silently reassigned;
- payload source order is preserved without relabelling the numeric interval endpoints.

## Next package

**Sandero Technical Page 17 Ambiguity Review** — Review the 5 ambiguous technical candidates from the Sandero brochure page 17 against their 10 preserved evidence signatures without creating master-data rows or approved import specifications.
