# Sandero Stepway Equipment Page 18 Ambiguity Review

Authored review of `residual_gap_015`. The plain-roof-rail row is separated from the immediately following modular-roof-rail row; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 1 |
| Covered | 1 |
| Selected evidence signatures | 1 |
| Selected evidence records | 1 |
| Rejected attached signatures | 1 |
| Rejected attached records | 2 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Selected records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 42 | `ec4e48ba49e9e26f9b158c5427a8063c899061b5d2343499a5c4695767303f71` | `covered` | 1 | 1 | complete plain roof-rails row immediately above the distinct modular-roof-rails row |

## Rejected attached evidence

| Signature | Records | Rejection reason |
| --- | ---: | --- |
| `modular_roof_rails:standard` | 2 | The modular-roof-rail signature belongs to the immediately following, visually distinct row 'Modułowe relingi dachowe (szare Megalith)', which is unavailable in Essential and standard in Expression and Extreme. Its two Expression records must not be substituted into the plain-roof-rail row. |

The two rejected records remain embedded in the JSON report exactly as attached to the candidate.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- the candidate row remains Essential `•`, Expression `-`, Extreme `-`;
- the adjacent modular-roof-rail row remains Essential `-`, Expression `•`, Extreme `•`;
- `roof_rails` and `modular_roof_rails` remain distinct attributes;
- the rejected modular signature and both of its records are preserved with an explicit rejection reason;
- unavailable states are not inferred from missing configuration records;

## Next package

**Bigster Technical Page 20 Unresolved Review — Chunk 1** — Review chunk 1 of the 40 unresolved technical candidates from Bigster brochure page 20 without creating master-data rows or approved import specifications.
