# Spring MY26 2026-02-06 Price and Commercial Matrix Import

## Package identity

- Package ID: `spring_my26_price_and_commercial_matrix_import_20261115_001`
- Source: `src_pl_spring_price_my26_20260206`
- Source PDF: `PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf`
- SHA-256: `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`
- Branch: `data/spring-my26-price-commercial-matrix-import-20261116-001`

## Scope

Import three page-1 prices and ten explicit page-3/page-4 priced commercial mappings. Reuse the three exact active Spring configurations and existing commercial-item definitions. Add source-to-configuration and source-to-grade links. Do not import equipment availability, technical values, dimensions, accessories or financing/promotion claims.

## Source evidence

The seven-page source was fully reviewed in `data/reporting/spring_my26_price_list_source_assimilation_review_20261114.md` and its JSON companion. The detailed import reconciliation is in `data/reporting/spring_my26_price_commercial_matrix_reconciliation_20261116.md` and JSON.

## Preserved boundaries

- Page-1 catalogue-price heading/footer conflicts with row label “Cena promocyjna”; every imported price row carries the exact ambiguity note.
- Page-2 narrative versus page-5 technical table conflict remains unresolved; no technical observations are imported.
- The Extreme DC 40 kW cell marked “P” is not interpreted or imported.
- No historical MY25, July configurator or August exact-current observations are overwritten.
- No new Spring configuration or commercial-item definition is created.
- No inference is made from an omitted or ambiguous cell.

## Validation

The importer checks the registered source identity and archived PDF SHA-256, exact three-configuration/three-grade boundaries, all 3 price cells, all 10 priced commercial mappings, uniqueness and preservation of existing history. Focused tests cover source provenance, exact values, applicability, ambiguous-cell exclusion and historical non-overwrite. Final technical and independent source-fidelity gates are required before merge.


## Closure

- Status: complete
- Pull Request: #832
- Merge commit: `d48a22262d5127108bd139474a8905011a849343`
- Final PR HEAD: `01788e61bd104232e77001af901f938712ac00bc`
- Required exact-head CI: passed
- Independent rendered-PDF source-fidelity review: passed
- All three page-1 prices and ten page-3/page-4 priced mappings verified.
- Preserved the catalogue-price / “Cena promocyjna” wording ambiguity, the Extreme DC 40 kW “P” exclusion and the page-2/page-5 technical conflict.
