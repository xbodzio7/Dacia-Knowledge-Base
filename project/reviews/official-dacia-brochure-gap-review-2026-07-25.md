# Official Dacia Brochure Gap Review

Date: 2026-07-25

## Scope

This review compares the five newly archived official Polish brochures with the current master data and registered price-list or exact-card evidence. It identifies source-backed candidates but does not import technical observations.

Machine-readable result: `data/reporting/official_dacia_brochure_gap_review.json`.

## Cross-source conclusion

Most ordinary scalar technical tables repeat evidence already available from current price lists or exact configuration cards. The brochures are most valuable where they expose measurement context that the current scalar observation relation cannot preserve.

A second official source is not by itself a reason to duplicate a master-data observation. A brochure becomes an import source only when the exact fact, target scope and complete measurement context are represented.

## Sandero

The brochure contains Eco-G 120 manual and automatic technical tables. Most engine, mass, towing and dimension fields overlap existing Sandero evidence.

New candidates:

- 80–120 km/h elasticity separated by fourth or fifth gear and by petrol or LPG;
- minimum and maximum luggage capacity expressed in VDA and ordinary litres;
- a separately identified underfloor compartment.

Current boundary:

- the existing `elasticity_80_120` scalar cannot distinguish the gear;
- one luggage-volume field cannot safely collapse VDA, ordinary litres, seat state and compartment type;
- country-adjustment placeholder wording must not become a numeric CO2 or fuel-consumption record.

## Sandero Stepway

The brochure repeats the principal Eco-G technical data already represented from configuration documents and the July 2026 price list.

New candidates:

- 80–120 km/h elasticity separated by fourth, fifth or sixth gear and by fuel;
- 328 dm3 VDA / 410 litres minimum luggage capacity;
- 1108 dm3 VDA / 1455 litres maximum luggage capacity;
- 78 litres of underfloor storage.

These values require explicit measurement-basis, seat-state and compartment context. They are not imported as interchangeable litres.

## Jogger

The technical and dimension tables distinguish five-seat and seven-seat states and multiple rear-seat arrangements.

New candidates include:

- performance or elasticity values dependent on passenger layout, powertrain and gear;
- minimum luggage capacity of 708/829 for five seats and 160/212 for seven seats on the brochure's VDA/litre bases;
- maximum capacities of 1819/2094 and 1807/2085;
- intermediate states such as second row raised with third row folded or removed.

A safe import needs passenger-layout and seat-state dimensions in addition to measurement basis. Treating these numbers as one generic Jogger luggage capacity would lose source meaning.

## Bigster

The ordinary engine, performance, WLTP, mass and dimension values substantially overlap the current July 2026 catalogue import.

The brochure adds useful luggage variants depending on:

- repair kit or spare wheel,
- double floor presence,
- rear bench state,
- VDA or ordinary-litre measurement basis.

The dimension illustration also gives values for a named equipment state. Those values must not be generalized to every Bigster configuration without preserving that state.

## Duster

The mini brochure contains equipment and technical material for the model range, including luggage values that vary by:

- 4x2 or 4x4,
- repair kit or spare wheel,
- rear-seat state,
- VDA or ordinary-litre basis.

The Eco-G 120 technical table in this brochure describes the manual powertrain. It is therefore an explicit non-source for the exact Eco-G 120 automatic configurations introduced in later Polish and Romanian evidence packages.

## Required model before value import

The next architecture package should determine the smallest reusable representation for cargo observations. At minimum it must decide how to preserve:

- measurement basis: VDA/ISO 3832 or ordinary litres;
- seat state and affected row;
- passenger layout such as five or seven seats;
- drive type where the source distinguishes 4x2 and 4x4;
- spare wheel or repair kit;
- double-floor state;
- main luggage space versus a separate underfloor compartment.

Gear-specific elasticity should remain a separate later modeling question unless the cargo-context package can introduce a general measurement-context mechanism without over-expanding the accepted scope.

## Decision

Register all five brochures as immutable model-level sources. Import no technical values in this package. Proceed next with `Brochure Cargo Measurement Context Modeling`; retain gear-specific elasticity as a documented candidate for a subsequent context package.
