# Jogger Eco-G 120 Automatic Reporting Selection

## Decision status

`SELECTED`

The review selects the four current Eco-G 120 automatic configurations as the first explicit Jogger reporting subset.

## Complete Jogger portfolio

| Powertrain group | Configurations | Technical slots | Scalar slots | Range slots | Technical observations | Equipment observations | Prices | Pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 34 | 25 | 9 | 204 | 318 | 6 | 15 |
| Eco-G 120 automatic | 4 | 34 | 25 | 9 | 136 | 212 | 4 | 6 |
| TCe 110 manual | 6 | 24 | 19 | 5 | 144 | 318 | 6 | 15 |
| Hybrid 155 automatic | 6 | 27 | 23 | 4 | 162 | 318 | 6 | 15 |

All four groups have identical technical slot sets within the group, 53 dated equipment observations and one dated catalogue price per configuration.

## Selection rationale

Eco-G 120 automatic is selected because it is the smallest complete group. It covers extreme and journey in both five- and seven-seat form, supports six deterministic comparisons and exercises dual-fuel scalar and range semantics without mixing gearboxes or powertrains.

The selected configurations are:

- `jogger_extreme_5seat_ecog120_automatic`;
- `jogger_extreme_7seat_ecog120_automatic`;
- `jogger_journey_5seat_ecog120_automatic`;
- `jogger_journey_7seat_ecog120_automatic`.

## Technical denominator

The 25 scalar slots are:

- LPG and petrol acceleration;
- braked trailer weight;
- VDA cargo volume to luggage-cover and seat-back height;
- cylinder count, emission standard and engine displacement;
- LPG and petrol engine power and torque;
- petrol fuel-tank capacity;
- gear count, gearbox type and gross vehicle weight;
- LPG and petrol injection type;
- LPG total-vessel and filling capacity;
- minimum kerb weight, number of seats, Start & Stop, top speed and total valve count.

The nine closed-range slots are:

- LPG and petrol CO2 emissions;
- LPG and petrol combined fuel consumption;
- LPG and petrol maximum-power speed;
- LPG and petrol maximum-torque speed;
- maximum payload.

## Implementation contract

The next package will:

1. select exactly the four configurations above;
2. declare the exact 34-slot mixed scalar/range denominator;
3. reuse the 53 source-backed Jogger equipment attributes;
4. require four dated catalogue prices and complete source evidence;
5. publish completeness, source coverage and six pairwise comparison artifacts under a `jogger-ecog120-automatic` prefix;
6. preserve scalar and closed-range observation kinds without choosing representative endpoints;
7. preserve all Sandero and Duster reporting scopes and artifacts.

Expected completeness is 136/136 technical observations, 212/212 equipment observations, 4/4 prices and six comparison pairs. Any missing mixed scalar/range reporting capability is a stop boundary for the implementation package rather than permission to change source semantics.

## Boundary

This decision does not combine automatic and manual Eco-G, does not mix five- and seven-seat values into one record and does not promote the remaining three Jogger groups. After implementation, the remaining Jogger reporting portfolio review resumes.
