# Brochure Equipment Inheritance and Colour Review

Date: 2026-07-31  
Status: **complete**

## Source audit

| Measure | Result |
| --- | ---: |
| Registered brochure and price-list PDFs | 20 |
| Repository files present | 20 |
| SHA-256 matches | 20 |
| Text extractions completed | 20 |
| Missing files | 0 |

The audit covers every registered `brochure_pdf` and `configuration_pdf`. Dynamic configurators, stock cards and other web snapshots remain separate dated evidence and are not merged into a PDF claim.

## Explicit grade inheritance

The review found **24 explicit inheritance statements in nine sources**. They cover Duster, Bigster, Jogger, Sandero, Sandero Stepway and Spring. Every statement is source-, model-, date/model-year- and grade-chain-bounded. A later or higher grade is never assumed to inherit a lower grade unless that exact source says so.

Direct matrix cells are preferred where available. Inheritance is not used to overwrite a direct dash, option marker or contradictory later observation.

## Colour evidence

Six brochures contain **40 named palette entries**. They identify metallic/non-metallic finish classes and, for some models, Essential restrictions or two-tone eligibility. They do not provide a complete price mapping from every name to every current configuration.

Seven exact Sandero/Sandero Stepway configuration PDFs already contribute the source-specific value `biel alpejska` at 0 PLN. The review preserves those observations and creates no duplicate.

Current price evidence separates into three classes:

- exact fixed amounts, such as Bigster metallic paint at 3000 PLN and two-tone body at 1400 PLN;
- exact fixed subsets, such as 2500 PLN for Sandero Essential/Expression/Journey and Stepway Essential;
- paired amounts such as `2500/2700`, `2700/2900` and `0/2700`, which are not flattened because the current commercial mapping stores one amount.

## Coverage findings

- Spring has three current source-backed configurations and **zero** equipment-availability records. Brochure pages 19-20 provide a direct three-column matrix.
- The Spring matrix maps conservatively to 42 existing attributes, producing **126 records: 106 standard, 7 optional and 13 not available**.
- The July Jogger matrix changes fog lights for Expression from the April source's standard state to not available. Six dated current observations can be added while retaining history.
- Duster Eco-G 120 automatic configurations have 26 same-grade attribute gaps relative to their manual counterparts. This is a review priority only; closure must use the current Duster matrix and its transmission/package conditions, never manual-value copying.

## Selected package

**Spring Version Equipment Matrix Availability Import**

Import exactly 126 direct matrix observations for:

- `spring_essential_electric70_automatic`;
- `spring_expression_electric70_automatic`;
- `spring_extreme_electric100_automatic`.

The package excludes commercial packages, the Type 2 cable choice, appearance strings, colours, technical data, Cargo and every unsupported attribute mapping.

## Ordered follow-up queue

1. Spring Commercial Packages and Charging Options — source-visible applicability and contents, with no invented prices.
2. Jogger MY26 Fog-Light Superseding Observations — six July `not_available` rows, preserving April history.
3. Bigster MY26 Exact Paint Options — two commercial items and 22 exact mappings.
4. Sandero and Stepway Fixed Paint Price Subset — one item and nine exact 2500 PLN mappings.
5. Duster Eco-G 120 Automatic Equipment Matrix Closure — row-level current-source contract before import.

## Deferred boundaries

- commercial price ranges require a source-faithful range model;
- all forty named colours require a model-level colour-choice/two-tone catalogue decision;
- the Spring 2300 PLN colour row remains MY25 stock-bounded;
- no fact crosses model year, campaign, model, powertrain or configuration without explicit source evidence.

Decision: `SELECT_SPRING_VERSION_EQUIPMENT_MATRIX_AVAILABILITY_IMPORT`.
