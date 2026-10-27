# Sandero Equipment Page 19 Ambiguity Review

Authored review of `residual_gap_014`. The complete combined cruise-control and speed-limiter row is mapped to two distinct standard signatures; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 1 |
| Covered | 1 |
| Selected evidence signatures | 2 |
| Selected evidence records | 4 |
| Rejected attached signatures | 0 |

## Candidate decisions

| Line | Candidate | Decision | Signatures | Records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 20 | `95fc01e2757ac30f1c2f3a5f43cc0b52f65e6097240d2179401eac2b2a17b32c` | `covered` | 2 | 4 | complete combined speed-limiter and cruise-control row |

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- the three `•` markers remain standard for Essential, Expression and Journey;
- the complete combined row is read against all three trim columns;
- `cruise_control` and `speed_limiter` remain two distinct attributes;
- the four attached records are preserved exactly and are not projected to Essential;

## Next package

**Sandero Stepway Equipment Page 18 Ambiguity Review** — Review the 1 ambiguous equipment candidate from Sandero Stepway brochure page 18 against its 2 preserved evidence signatures without creating master-data rows or approved import specifications.
