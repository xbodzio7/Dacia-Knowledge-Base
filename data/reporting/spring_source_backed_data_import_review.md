# Spring Source-Backed Data Import Review

Date: 2026-07-31

Status: **complete**

## Reviewed evidence

The review combines three independently registered official sources:

- the Polish Spring brochure dated 2026-02-19;
- the model-year-2025 dealer-stock price list effective 2026-07-08;
- the dated official configurator snapshot observed 2026-07-31.

## Import-ready catalogue entities

The sources prove three current passenger grades and configurations:

- Essential — Electric 70 — automatic;
- Expression — Electric 70 — automatic;
- Extreme — Electric 100 — automatic.

Cargo remains outside the passenger catalogue because no exact current Cargo configurator state was captured.

## Selected first package

The next package is **Spring Electric 70 Catalogue Foundation**. It will add:

- versions `spring_essential` and `spring_expression`;
- configurations `spring_essential_electric70_automatic` and `spring_expression_electric70_automatic`;
- the exact current Essential price of 73,500 PLN dated 2026-07-31;
- the Expression catalogue price of 81,500 PLN dated 2026-07-08 and explicitly bounded to model-year-2025 dealer stock;
- source-to-version and source-to-configuration relationships;
- one comparable Electric 70 automatic reporting scope containing both configurations.

The expected master-data delta is 13 rows. The repository will then contain 80 active configurations, 21 reporting scopes and six model families, with 130 within-scope pairs.

## Preserved price boundaries

The combined version page repeats the Essential starting price of 73,500 PLN in other grade sections. That number is not accepted as an Expression price.

The stock price list headline discount of 17,000 PLN is not converted into calculated promotional prices. Only explicit catalogue values are eligible.

Extreme Electric 100 at 85,900 PLN is source-backed, but its import is deferred to a separate singleton catalogue package so that catalogue creation and reporting-contract activation do not become one mixed change.

## Deferred technical and equipment data

The brochure and later configurator snapshot contain exact but differently dated range and consumption observations. These values must remain source-specific dated records and cannot be flattened into the catalogue foundation.

The three-grade equipment matrix, individual options and packages are also deferred. Their standard, optional, unavailable and package-qualified states require a dedicated import package.

Decision: `SELECT_SPRING_ELECTRIC70_CATALOGUE_FOUNDATION`.
