# Official Non-Configurator Catalog Source Inventory

Date: 2026-08-06

## Goal

Register official Polish Dacia sources outside the vehicle configurator for the complete collection of current exterior colours, wheels and wheel covers, upholstery and interior trim, standard equipment, standalone options, option packages and dealer accessories.

The configurator is a fallback source only. It may be used after document extraction to resolve remaining compatibility dependencies or genuinely missing fields.

## Current model scope

- Spring;
- Sandero;
- Sandero Stepway;
- Jogger;
- Duster;
- Bigster.

## Source order

1. current model price list;
2. current model brochure;
3. current accessory catalogue;
4. current accessory price list;
5. official model/version page;
6. official Dacia Shop product record;
7. official configurator fallback.

## First delivery

`data/reporting/official_nonconfigurator_catalog_source_inventory_20260806.json` registers:

- six current model brochures;
- official accessory source hubs;
- current accessory catalogues already resolved for Spring, Duster and Bigster;
- accessory price-list endpoints for all six model families;
- source-age warnings for Sandero, Sandero Stepway and Jogger price lists;
- unresolved direct catalogue links that require verification before extraction.

## Semantic boundaries

- No value is transferred between model families, grades, powertrains, transmissions or source dates.
- A historical accessory price list may establish that an item existed, but it may not establish current availability without corroboration.
- A brochure colour image is not used to infer a paint code or exact shade.
- An accessory catalogue description is not used to infer current price.
- Configurator data will be requested only for fields explicitly left unresolved by the document coverage matrix.

## Next steps within the milestone

1. register and date current model price lists;
2. verify unresolved accessory catalogue URLs;
3. extract document-backed colour, wheel, trim, equipment, package and accessory records;
4. produce a per-model coverage and contradiction matrix;
5. create a bounded configurator fallback queue containing only unresolved items.
