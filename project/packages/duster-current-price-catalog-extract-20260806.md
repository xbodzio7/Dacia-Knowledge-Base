# Duster Current Price Catalog Extract

Date: 2026-08-06

## Goal

Extract current Duster colours, wheels, upholstery, standalone options and option packages from the official Polish price list before using configurator fallback.

## Source

Official Dacia PDF `duster-price-2025.pdf`, valid from 2026-02-06, published as the MY26/PY25 price list.

## Result

The package records:

- five grade columns;
- five wheel configurations;
- paint pricing rules for metallic and non-metallic finishes;
- three upholstery families;
- selected standalone options;
- six option packages with prices, grade availability and exact component lists.

## Boundaries

- No configurator data is used.
- The printed `2700 / 2900` metallic-paint price remains unresolved until an official colour-level mapping is found.
- Records from separate powertrain tables are not merged.
- Dealer-only dependency statements are not inferred.

## Next package

Repeat the same extraction for the current Jogger price list, then continue with Sandero, Sandero Stepway, Spring and Bigster.
