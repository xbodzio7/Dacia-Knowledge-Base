# Spring Exterior Colour Options

Date: 2026-07-31

Status: **complete**

## Source contract

- Source: `src_pl_spring_brochure_20260219`.
- Registered file: `PDF/Broszury/DACIA SPRING broszura 20260219.pdf`.
- Locked SHA-256: `73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d`.
- Exact page: 12.
- Exact existing configurations: Essential Electric 70 automatic, Expression Electric 70 automatic and Extreme Electric 100 automatic.

## Imported palette

The package registers six selectable exterior-colour options:

- Czerwony Brick — non-metallic;
- Seafoam — non-metallic;
- Szary Diamond — metallic;
- Lichen Khaki — non-metallic;
- Niebieski Stonewash — non-metallic;
- Biel Alpejska — non-metallic.

Each item is linked to the existing `exterior_color` attribute and mapped as `optional` to all three exact Spring configurations because page 12 states no grade restriction.

## Price and value boundary

The source page states no individual colour price and does not identify a standard or no-surcharge colour. Therefore all 18 configuration mappings preserve a blank amount and blank price date. `currency_code=PLN` is only the required schema reference and does not create a price.

The package does not create a single scalar `exterior_color` configuration value because the source presents a palette of alternatives, not one selected vehicle colour.

## Exclusions

- No MY25 stock price is transferred to current configurations.
- No colour is marked free, standard or default.
- No grade restriction is invented.
- No two-tone semantics are introduced.
- No model, version or configuration is added.

## Integrity

`tools/import_spring_exterior_colour_options.py` verifies the source hash, exact active Spring configuration boundary, six names and finish classifications, uniform three-grade applicability, blank-price contract, idempotent output and contiguous ID suffixes in all three commercial tables.

The final pull-request diff contains exactly fourteen declared package paths and no temporary workflow or extraction file. This human-authored commit triggers the final standard CI verification after materialization.
