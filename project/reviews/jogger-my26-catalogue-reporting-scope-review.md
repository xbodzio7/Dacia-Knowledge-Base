# Jogger MY26 Catalogue Reporting Scope Review

## Decision status

`SELECTED`

The first Jogger catalogue foundation will cover **all 22 non-empty catalogue
price cells** in the accepted Polish MY26 source dated 2026-04-01.

A smaller initial subset would omit equally explicit source-backed combinations
without reducing a real evidence or modelling risk. Technical values, equipment
availability and reporting promotion remain separate later packages.

## Selected catalogue

| Powertrain / transmission | Essential | Expression | Extreme | Journey | Configurations per seat count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | yes | yes | yes | no | 3 |
| Eco-G 120 automatic | no | no | yes | yes | 2 |
| TCe 110 manual | no | yes | yes | yes | 3 |
| Hybrid 155 automatic | no | yes | yes | yes | 3 |

The same availability matrix is stated for five and seven seats, producing
11 five-seat and 11 seven-seat configurations.

## Entity boundary

The existing current model `jogger` is reused. Four active versions will be
created:

- `jogger_essential`;
- `jogger_expression`;
- `jogger_extreme`;
- `jogger_journey`.

Configuration codes use this order:

`jogger_<trim>_<seat-count>_<powertrain>_<transmission>`

Examples:

- `jogger_essential_5seat_ecog120_manual`;
- `jogger_extreme_7seat_ecog120_automatic`;
- `jogger_expression_5seat_tce110_manual`;
- `jogger_journey_7seat_hybrid155_automatic`.

The code carries identity, while `number_of_seats` stores the explicit integer
value `5` or `7`. The `powertrain_label` remains only `Eco-G 120`, `TCe 110` or
`hybrid 155`; seat count must not be hidden in that field.

All configurations are front-wheel-drive candidates, but no drive observation
is imported merely from the absence of another drive option in the price matrix.

## Price boundary

The catalogue prices on page 1 are imported as dated gross catalogue prices in
PLN for market `PL` on `2026-04-01`.

| Seats | Powertrain | Essential | Expression | Extreme | Journey |
| ---: | --- | ---: | ---: | ---: | ---: |
| 5 | Eco-G 120 manual | 77,900 | 82,050 | 89,900 | — |
| 5 | Eco-G 120 automatic | — | — | 96,800 | 98,950 |
| 5 | TCe 110 manual | — | 84,050 | 91,900 | 94,050 |
| 5 | Hybrid 155 automatic | — | 103,550 | 111,400 | 113,550 |
| 7 | Eco-G 120 manual | 82,400 | 86,550 | 94,400 | — |
| 7 | Eco-G 120 automatic | — | — | 101,300 | 103,450 |
| 7 | TCe 110 manual | — | 88,550 | 96,400 | 98,550 |
| 7 | Hybrid 155 automatic | — | 108,050 | 115,900 | 118,050 |

Financing instalments, insurance percentages, service packages and promotional
claims are excluded from `configuration_prices.csv`.

## Source-registration boundary

The entity-foundation package will atomically add:

- one `sources.csv` row using `src_pl_jogger_price_my26_20260401`;
- one source-to-model relation;
- four source-to-version relations;
- 22 source-to-configuration relations;
- four active versions;
- 22 active configurations;
- 22 dated catalogue prices;
- 22 `number_of_seats` observations;
- one declarative seating-capacity import specification.

The source row will retain the verified original PDF SHA-256 and the reserved
archive path. Its notes will state that the connected writer could not archive
the binary in the intake PR, avoiding a false repository-presence claim.

## Deferred technical boundary

Page 6 combines exact values, seat-specific pairs and ranges. The entity package
must not flatten these into trim-specific scalar facts.

A later technical review will distinguish:

- exact powertrain-wide values such as displacement, cylinders, top speed, fuel
  tank capacity and braked trailer mass;
- exact five-/seven-seat pairs such as Eco-G and TCe acceleration, minimum kerb
  weight and gross vehicle weight;
- source ranges for consumption, emissions and payload, which require either
  explicit range modelling or exclusion from scalar observations;
- Hybrid 155 values whose printed ranges are not safely attributable to one seat
  count or trim without an explicit source rule.

## Deferred equipment boundary

Pages 4-5 primarily describe trim-level equipment, but include conditions for
Hybrid 155, seven seats and packages. Equipment import therefore follows after
entities and prices and must preserve each condition rather than treating the
matrix as universally trim-only.

## Acceptance contract

The selected entity foundation must keep the existing Sandero and Duster
reporting scopes unchanged, retain the 446-test baseline unless tests are
explicitly generalized, and update all generated documentation counters in the
same PR as the master-data rows.
