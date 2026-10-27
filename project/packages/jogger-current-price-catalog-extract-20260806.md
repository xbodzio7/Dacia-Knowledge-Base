# Jogger Current Price Catalog Extract

Date: 2026-08-06

## Goal

Extract current Polish Jogger catalogue evidence from the official model-year 2026 price list valid from 3 July 2026, without using the vehicle configurator.

## Source

`https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/51a64d2724.pdf`

## Delivered scope

`data/reporting/official_jogger_current_price_catalog_extract_20260806.json` records:

- four grades: essential, expression, extreme and journey;
- Eco-G 120, Eco-G 120 auto, TCe 110 and hybrid 155 catalogue prices;
- separate 5-seat and 7-seat price matrices;
- paint price classes;
- 16-inch Erelia and Tamia wheel evidence;
- upholstery evidence;
- standalone spare-wheel, heated-seat and Media Nav options;
- KOMFORT HEV, KOMFORT, ZIMOWY and DRIVE packages;
- selected equipment availability needed for later compatibility comparison.

## Semantic boundaries

- The exact named-colour assignment to the printed `0 / 2700` and `2700 / 2900` price pairs is not inferred.
- The two Tamia wheel variants are retained in their printed paired form where the PDF table does not provide a safe unambiguous semantic split.
- The internally inconsistent upholstery label is preserved and flagged rather than corrected from context.
- Dealer-only option requirements and mutual exclusions remain unresolved.
- No value is transferred between grades, powertrains, seat counts or source dates.
- No configurator data is used.

## Next package

Continue current-price-list extraction for the remaining model families, then reconcile brochures and price lists before any configurator fallback work.
