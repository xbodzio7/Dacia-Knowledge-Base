# New Spring official accessory price-list extract

Date: 2026-08-06  
Source commit: `90a1a77caed9f73b6a5020a014a225b44a19a75c`

## Goal

Extract every row from the official Polish `NOWY SPRING` accessory price list before using configurator or dealer-only evidence for accessory completeness.

## Official source

- title: `NOWY SPRING - Cennik akcesoriów`;
- official endpoint: `https://akcesoria.dacia.pl/model/nowy_spring`;
- printed valid-from date: `2024-04-17`;
- retrieved: `2026-08-06`;
- price basis: gross price with VAT, excluding installation.

The document is still served from the official current-model endpoint, but its printed date is older than the capture date. Document prices are therefore preserved as published prices, not automatically labelled as live shop prices.

## Extract result

- 56 accessory rows;
- 5 main categories;
- 13 subcategories;
- 5 rows with a positive marker in the `Wymaga montażu` column;
- minimum published price: 56 PLN;
- maximum published price: 3219 PLN.

Category counts:

| Category | Rows |
|---|---:|
| BEZPIECZEŃSTWO | 5 |
| DESIGN | 18 |
| KOMFORT I OCHRONA | 27 |
| MULTIMEDIA | 4 |
| TRANSPORT | 2 |

All source product names, reference numbers, prices and page locations are preserved. The split description for part `7717278287` is joined into one normalized row without changing its meaning.

## Current official shop corroboration

Four part numbers were checked against current official Dacia Shop product pages:

| Part number | Document price | Shop price | Result |
|---|---:|---:|---|
| 7717301274 | 111 PLN | 111 PLN | exact price and label match |
| 684344266R | 56 PLN | 56 PLN | exact price and label match |
| 7711945469 | 125 PLN | 125 PLN | exact part and price match; current shop label differs |
| 7711940885 | 318 PLN | 318 PLN | exact price and label match |

All four shop pages list compatibility with `NOWY SPRING` and currently report temporary unavailability. Availability is treated as volatile. The four exact price matches do not validate the other 52 document prices.

The commercial-label drift for part `7711945469` is retained explicitly:

- price-list label: `Wkładka do uchwytu na kubek`;
- current shop label: `Wielofunkcyjny uchwyt na kubek Dacia`.

The part number remains the stable identity.

## Files

- `data/reporting/official_new_spring_accessory_price_list_extract_20260806.json`
- `data/reporting/official_new_spring_accessory_price_list_extract_20260806.csv`
- `data/reporting/official_new_spring_accessory_shop_corroboration_20260806.json`

## Boundaries

- no master-data mutation;
- no compatibility transfer to legacy Spring or another model;
- no installation-price estimate;
- no shop availability inferred from the PDF;
- no current-price claim for the 52 unreviewed shop items;
- no permanent-withdrawal inference from temporary unavailability;
- no dealer-local price inferred from the national catalogue price.

## Next step

Reconcile the remaining 52 New Spring part numbers against the official shop where product pages exist, then repeat the same bounded extraction for New Duster and Bigster accessory price lists. Older Sandero, Stepway and Jogger accessory lists remain historical references until current shop or newer official evidence corroborates each item.
