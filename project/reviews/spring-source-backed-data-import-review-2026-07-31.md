# Spring source-backed data import review

Date: 2026-07-31

## Decision

Select **Spring Electric 70 Catalogue Foundation** as the first master-data import after registering the Spring PDF and web sources.

## Why this boundary

Essential and Expression form a natural two-configuration comparison scope because both are explicitly observed with the Electric 70 automatic powertrain. They can be introduced without creating a singleton scope or mixing differently powered configurations.

Extreme Electric 100 is also source-backed, but it would be the only member of its reporting scope. Its catalogue import and the resulting singleton product-contract change will be reviewed separately.

## Selected data

The package will add two versions, two configurations and two explicit catalogue-price observations:

- Essential Electric 70 automatic — 73,500 PLN, exact current configurator state dated 2026-07-31;
- Expression Electric 70 automatic — 81,500 PLN, official catalogue price dated 2026-07-08 and limited to model-year-2025 dealer stock.

It will also add explicit source relationships and one Electric 70 automatic completeness scope.

## Rejected shortcuts

- do not assign the repeated 73,500 PLN starting price to Expression;
- do not calculate promotional prices from the 17,000 PLN headline discount;
- do not merge brochure and configurator technical observations into one undated value;
- do not import the equipment matrix or packages in the entity-foundation package;
- do not create a Cargo configuration from brochure-only evidence;
- do not activate the Electric 100 singleton in the same package.

## Planned sequence

1. Spring Electric 70 Catalogue Foundation;
2. Spring Electric 100 Singleton Catalogue Review;
3. Spring Dated Technical Observation Review;
4. Spring Version Equipment Matrix Import;
5. Spring Exact Stock Card Snapshot.
