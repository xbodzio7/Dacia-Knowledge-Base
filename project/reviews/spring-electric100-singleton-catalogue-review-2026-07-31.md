# Spring Electric 100 singleton catalogue review

Date: 2026-07-31

## Decision

Implement the source-backed Spring Extreme Electric 100 automatic configuration as a dedicated singleton catalogue scope.

## Evidence

The registered official configurator snapshot observed on 2026-07-31 contains the exact Extreme Electric 100 automatic state and an exact catalogue price of 85,900 PLN. No price inference or grade transfer is required.

## Product boundary

The configuration must not be added to `spring_electric70_automatic`. Electric 70 and Electric 100 remain separate reporting scopes.

The new singleton scope:

- contains one configuration;
- produces zero pairs and zero differences;
- is navigable in consumer products;
- preserves all cross-scope, ranking, recommendation and inference prohibitions.

Existing bundle and selection-export examples already exercise singleton behavior. The implementation only updates their expected counts after adding one more automatic configuration under 100,000 PLN.

## Data boundary

The package adds catalogue identity and price only. Technical observations, the brochure equipment matrix, packages, dealer-stock cards and Cargo remain independent follow-ups.

## Expected totals

- active configurations: 81;
- reporting scopes: 22;
- model families: 6;
- within-scope pairs: 130;
- recorded catalogue prices: 81.
