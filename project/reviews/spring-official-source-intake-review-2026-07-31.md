# Spring Official Source Intake Review

Date: 2026-07-31

## Context

The priority review selected Spring because it is a current canonical model with no registered source. This review evaluates the official Polish evidence without registering a source or importing data.

## Evidence classes

### Immutable brochure

The official Spring brochure is a 22-page PDF dated 2026-02-19. It covers essential, expression, extreme and cargo variants, electric 70 and electric 100, equipment matrices and technical data.

Its symbols and footnotes bind values to grades, cargo state, wheels and powertrains. No value may be flattened or copied between electric 70 and electric 100 solely because both appear in one table.

### Immutable price list

The official Spring price list is a six-page PDF effective from 2026-07-08. It explicitly describes a model-year-2025 stock offer and shows expression electric 70 and extreme electric 100.

Catalogue prices, campaign reductions and dealer-stock scope must remain distinct from current MY26 configurator states.

### Dynamic configurator

The configurator observed on 2026-07-31 proves one exact default state: essential electric 70 MY26.b. It exposes price and selected technical values. Visible grade selectors alone do not prove every grade/powertrain combination.

A separate normalized snapshot is required before this source can be registered or used for imports.

### Exact stock catalogue

The official stock catalogue contains exact MY26 cards, including extreme electric 100. Dealer prices, selected equipment and card availability are observations of individual cards only. They must not be generalized between cards or converted into catalogue-wide facts.

## Selected next package

**Spring Official PDF Source Registration**

The package will:

1. archive the exact brochure and price-list PDFs;
2. calculate and record SHA-256 for each file;
3. add two source rows to `data/master/sources.csv`;
4. add two Spring relationships to `data/master/source_models.csv`;
5. record a source-registration receipt;
6. update canonical project state.

## Preserved boundaries

The registration package will add no configuration, price, equipment, technical value, range, availability record, reporting scope, comparison pair, recommendation or inferred value.

Dynamic configurator and stock-card capture remain separate later packages.

## Decision

`SELECT_SPRING_OFFICIAL_PDF_SOURCE_REGISTRATION`
