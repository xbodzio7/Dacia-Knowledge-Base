# Bigster Official Accessory Catalogue Reconciliation

Date: 2026-08-06

## Goal

Assimilate the official Polish Bigster accessory price list and catalogue without using the vehicle configurator, then reconcile their part numbers, grade compatibility statements and selected current Dacia Shop records.

## Sources

- accessory price list valid from 2025-01-09: `https://akcesoria.dacia.pl/model/bigster`;
- accessory catalogue published in April 2025: `https://cdn.group.renault.com/dac/pl/pdf/akcesoria/axs-bigster.pdf`;
- current official shop: `https://sklep.dacia.pl/akcesoria`.

## Result

- 94 complete price-list rows;
- 89 catalogue compatibility rows;
- 68 shared part numbers;
- 26 references present only in the price list;
- 21 references present only in the later catalogue;
- 10 price-list rows marked as requiring installation;
- 17 selected current shop corroboration records.

Every price-list row preserves the product name, reference, VAT-inclusive price without installation and installation marker. Every catalogue row preserves compatibility with Essential, Expression, Extreme and Journey, including conditional footnotes.

## Important findings

The later catalogue does not merely repeat the January price list. It introduces package references and additional products, while the price list often exposes individual components. Important unresolved examples include:

- side steps: separate components in the price list versus one package reference in the catalogue;
- fixed and tool-free-removable towbars: component references versus complete package references;
- Sleep equipment: individual box, mattress and blind references versus powertrain-specific package references;
- different official references for Handpresso, portable fridge, YouClip headrest hanger, underbody protection and reversible boot mat;
- different descriptions for snow-chain reference `7711578474`;
- a second alarm reference present only in the price list.

These differences are preserved as source evidence and are not silently normalized.

## Current shop corroboration

The current Dacia Shop still lists multiple Bigster products from the documents, including Sleep components, steps, Bigster-specific mats, YouClip equipment, wheels, roof bars, seat covers and luggage accessories. A visible shop price is recorded only where the product page exposes one. Absence from retrieved search results is not treated as withdrawal.

## Semantic boundaries

- No configurator data was used.
- A document price is retained with its source date and is not automatically described as the current dealer price.
- A catalogue package is not assumed to be numerically equivalent to the sum of its price-list components.
- Similar product names with different references remain separate until an official relationship is established.
- Compatibility is not transferred between grades, powertrains or references.

## Data files

- `data/reporting/official_bigster_accessory_price_list_20260806.csv`;
- `data/reporting/official_bigster_accessory_catalog_compatibility_20260806.csv`;
- `data/reporting/official_bigster_accessory_catalog_reconciliation_20260806.json`.

## Next step

Complete current-shop corroboration for the remaining Bigster-specific references, then apply the same two-document reconciliation method to the new Duster accessory catalogue and price list.
