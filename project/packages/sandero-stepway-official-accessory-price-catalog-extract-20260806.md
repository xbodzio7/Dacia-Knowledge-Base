# Sandero and Sandero Stepway Official Accessory Price Catalog Extract

Date: 2026-08-06

## Goal

Preserve every accessory row exposed by the official Polish Dacia accessory price lists linked from the current accessory hub for Sandero and Sandero Stepway, while keeping historical price evidence separate from current shop corroboration.

The vehicle configurator was not used.

## Sources

- official accessory hub: `https://akcesoria.dacia.pl/`;
- shared accessory catalogue: `https://cdn.group.renault.com/dac/pl/pdf/akcesoria/axs-sandero.pdf`;
- Sandero accessory price list: `https://akcesoria.dacia.pl/model/sandero_nowe`;
- Sandero Stepway accessory price list: `https://akcesoria.dacia.pl/model/sandero_stepway_nowe`;
- official Dacia Shop product records: `https://sklep.dacia.pl/akcesoria`.

## Result

`data/reporting/official_sandero_stepway_accessory_price_catalog_extract_20260806.json` records:

- 104 Sandero price-list rows;
- 99 Sandero Stepway price-list rows;
- product name, reference number, printed price, category and installation requirement;
- 83 shared reference numbers with no price or installation-marker conflict between the two documents;
- 21 Sandero-only and 16 Stepway-only reference numbers;
- ten separately retrieved current Dacia Shop corroboration records.

## Evidence status

The official hub still links to both price lists, but each document is explicitly dated 3 October 2022. Therefore:

- the printed price is retained as a historical official price;
- an uncorroborated row is not promoted to current availability;
- a current shop product record may corroborate the product reference, model assignment and displayed shop price;
- absence from the retrieved shop search does not prove that an accessory has been withdrawn.

## Semantic boundaries

- No accessory is transferred between Sandero and Stepway unless the same reference is present in both source documents or the current official shop record names both models.
- No price is updated by inference.
- No installation cost is added.
- No compatibility is inferred for MY2026 grades, Eco-G 120, automatic transmission or option packages.
- Dealer-only dependencies remain unresolved.
- The shared descriptive catalogue remains registered for a later complete description and image-association extract.

## Next package

Continue the same source-first method for the remaining current accessory catalogues and price lists, then generate a portfolio coverage matrix and a bounded configurator fallback queue.
