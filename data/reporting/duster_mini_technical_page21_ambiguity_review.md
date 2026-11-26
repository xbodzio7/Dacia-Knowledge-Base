# Duster Mini Technical Page 21 Ambiguity Review

Authored review of `residual_gap_006`. The decision preserves row and powertrain boundaries and does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 1 |
| Partially covered | 1 |
| Selected evidence signatures | 1 |
| Selected evidence records | 3 |

## Candidate decision

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 56 | `6fd0360bfac47f6996e0fb04b3de4470e2edb507a12c70d96008d442a1489a6c` | `partially_covered` | 1 | Układ kierowniczy                                                    układu kierowniczego              układu kierowniczego |

## Authored finding

The candidate is the steering-type row. Only the attached electric-power-assistance signature belongs to this row. Turning-circle, brake, tyre, maximum-kerb-weight and payload signatures belong to other labelled rows on the same page and are rejected.
- `steering_type`: `Elektryczne wspomaganie układu kierowniczego` — The same value is printed for Hybrid-G 150 4x4, but the selected records cover only Hybrid 155 configurations.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- the turning-circle value belongs to the following row and is not selected;
- brake, tyre, mass and payload evidence is not substituted for the steering-type row;
- the Hybrid-G 150 4x4 column is not populated from Hybrid 155 configuration records.

## Next package

**Duster Mini Equipment Page 23 Ambiguity Review** — Review the 26 ambiguous equipment candidates from Duster mini-brochure page 23 against their 61 preserved evidence signatures without creating master-data rows or approved import specifications.
