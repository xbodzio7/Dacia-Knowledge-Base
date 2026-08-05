# Sandero Official Web Catalog Extract

Date: 2026-08-06

## Goal

Capture current Sandero and Sandero Stepway grade prices, selected engine prices and explicitly promoted equipment from official Polish Dacia model and versions-and-prices pages while continuing to search for a standalone current price-list PDF.

## Result

The package records three current Sandero grades and three current Sandero Stepway grades. It preserves the prices and equipment highlights published on the official static model pages. For Stepway Essential and Expression it also records the engine and transmission price rows explicitly exposed by the versions page.

The existing brochure extract remains the source for named colours, wheels and upholstery. This package does not duplicate or reinterpret those records.

## Source limitation

A standalone current Sandero/Sandero Stepway price-list PDF was not resolved during this package. Therefore the following remain explicitly incomplete:

- the complete engine-by-grade price matrix;
- named-colour prices;
- wheel upgrade prices;
- the complete standalone-option matrix;
- package prices, contents, requirements and exclusions.

The absence of a resolved PDF is not treated as evidence that no such document exists.

## Semantic boundaries

- No configurator data was used.
- No dealer listing was used as canonical evidence.
- No value was transferred between Sandero and Sandero Stepway, grades, engines or transmissions.
- No package dependency was inferred from marketing descriptions.
- Static page highlights establish promoted equipment, not a complete standard-equipment list.

## Next step

Continue with official accessory catalogues and accessory price lists while separately searching official Dacia document endpoints for the missing current vehicle price-list PDF. Only unresolved compatibility dependencies will later enter the bounded configurator fallback queue.
