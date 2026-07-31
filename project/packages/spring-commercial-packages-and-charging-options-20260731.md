# Spring Commercial Packages and Charging Options

Date: 2026-07-31

Status: **complete**

## Source contract

- Source: `src_pl_spring_brochure_20260219`.
- Registered file: `PDF/Broszury/DACIA SPRING broszura 20260219.pdf`.
- Locked SHA-256: `73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d`.
- Exact pages: 13-15.
- Exact existing configurations: Essential Electric 70 automatic, Expression Electric 70 automatic and Extreme Electric 100 automatic.

## Imported commercial catalogue

The package registers five direct commercial items:

- the Type 2 charging-cable option, directly listed for all three grades;
- Pakiet Techno, directly listed only for Expression;
- the standalone DC 40 kW CCS charging option, directly listed only for Expression;
- Pakiet Power, directly listed only for Extreme;
- Pakiet City, directly listed only for Extreme.

The five items contain 18 memberships to existing canonical attributes and seven exact item-to-configuration mappings. Every mapping is `optional`.

## Price boundary

The brochure states no amount for any of these items. Therefore `amount` and `price_date` remain blank. `currency_code` is `PLN` only because the commercial mapping schema requires a valid currency reference; it does not create a price. No zero price, estimated price, configurator price or price transferred from another document is introduced.

## Semantic boundaries

- Type 2, CCS, 40 kW, 10.1 inches and two USB ports remain in the item name or exact `source_text`; memberships to scalar attributes do not create unconditional scalar configuration values.
- Pakiet Power preserves the brochure statement that the package contains V2L even though the same brochure also lists V2L among Extreme standard equipment. The inconsistency is documented rather than silently resolved.
- The package does not alter the direct equipment matrix imported previously.
- No model, version, configuration, colour, technical observation, Cargo record or inherited fact is added.

## Integrity

`tools/import_spring_commercial_packages.py` verifies the source hash, exact active configuration boundary, registered source relationships, five-item specification, 18-membership distribution, seven page-bounded mappings, blank-price contract, idempotent output and contiguous ID suffixes for all three commercial tables.

The final pull-request diff contains exactly the sixteen paths declared by the canonical project state and no temporary workflow or extraction file. This human-authored commit triggers the final standard CI verification after materialization.
