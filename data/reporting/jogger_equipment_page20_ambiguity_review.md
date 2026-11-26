# Jogger Equipment Page 20 Ambiguity Review

Authored review of `residual_gap_010`. ESC/HSA, front-airbag row boundaries and the brochure-versus-price-list camera conflict are preserved; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 5 |
| Covered | 0 |
| Partially covered | 3 |
| Selected evidence signatures | 8 |
| Selected evidence records | 154 |
| Rejected attached signatures | 2 |

## Candidate decisions

| Line | Candidate | Decision | Signatures | Records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 104 | `9d57df671f89142af2044fbdd10fbd54d161263845b3844d261e084c992b5229` | `partially_covered` | 2 | 44 | first line of the combined ESC and hill-start-assist row |
| 125 | `193d1c166bdaa5b2dc4de8e6e10baa5acc2b636af093d320cdc580f53944e46e` | `partially_covered` | 2 | 44 | first line of the driver/passenger front-airbag row |
| 126 | `9ee402355ae79cfac77ff578143243621c2b9eb00eb32ea03698fce8a4321114` | `partially_covered` | 2 | 44 | availability-bearing middle line of the driver/passenger front-airbag row |
| 127 | `9487bcbf484f556f17b25bc13b8dc2cc9b76d4617bc31048806dfc176e244359` | `context_only_non_import` | 0 | 0 | final passenger-airbag deactivation clause of the three-line front-airbag row |
| 138 | `1316f560401dec9a13d2a771fbd535448cf85f650d0f938239baf73f56452b59` | `deferred_source_conflict` | 2 | 22 | complete rear-view-camera row with a brochure versus later price-list trim conflict |

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- `•`, `¤` and `-` remain standard, optional and unavailable respectively;
- multi-line labels are reviewed as one visual row without inventing new attributes;
- the passenger-airbag deactivation clause does not inherit airbag-presence evidence;
- the 2025-12 brochure and 2026-04 price-list camera states remain an explicit unresolved conflict;

## Next package

**Bigster Equipment Page 21 Ambiguity Review** — Review the 1 ambiguous equipment candidate from Bigster brochure page 21 against its 3 preserved evidence signatures without creating master-data rows or approved import specifications.
