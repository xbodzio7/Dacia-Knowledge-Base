# Duster Official Accessory Catalogue Reconciliation

Date: 2026-08-06

## Goal

Assimilate the official Polish accessory price list for the new Duster and the compatibility matrix from the official accessory catalogue, then preserve every cross-source difference before any configurator fallback is considered.

## Sources

- accessory price list valid from 2024-03-26: `https://akcesoria.dacia.pl/model/nowy_duster`;
- accessory catalogue published in June 2024: `https://cdn.group.renault.com/dac/pl/pdf/akcesoria/axs-new-duster.pdf`;
- current official shop: `https://sklep.dacia.pl/akcesoria`.

## Result

- 95 complete price-list rows;
- 103 unique catalogue compatibility rows;
- 82 shared part numbers;
- 13 references present only in the price list;
- 21 references present only in the catalogue;
- seven price-list rows explicitly marked as requiring installation;
- seven selected current Dacia Shop corroboration records.

The price-list file preserves name, part number, VAT-inclusive price without installation and the printed installation marker. The catalogue file preserves compatibility with Essential, Expression, Extreme and Journey, including conditional standard-equipment and double-floor notes.

## Important findings

The two official documents contain several differences that must not be silently normalized:

- roof-box references `7711574056` and `7711574057` are described as 330/390 l in the price list and 400/480 l in the catalogue;
- snow-chain references `7711578473` and `7711578474` have different size and wheel descriptions;
- reference `7711940856` is described once as Polaire Steel Grip and once as Premium Grip;
- rubber mats `749M62782R` and `749M67996R` are described as incompatible with Extreme in the price list, while the catalogue identifies them as standard equipment in Extreme;
- boot-floor references `849P70348R` and `849P77880R` are described by drivetrain in the price list but by double-floor configuration and grade in the catalogue;
- the portable fridge and Handpresso use different references in the two documents;
- package references for side steps, spare-wheel tools, towbars, the roof rack and Sleep equipment exist only in the catalogue, while the price list mainly exposes their components;
- the Aero cargo box and electric tailgate lift appear in the price list but not in the catalogue matrix.

## Current shop corroboration

The current Dacia Shop still exposes selected new-Duster products, including Sleep components, steps, Tergan wheels, Dacia Link centre caps and powertrain-specific rubber mats. Shop presence and visible lead time are recorded separately from document prices.

## Semantic boundaries

- No configurator data was used.
- A 2024 printed price is not automatically described as the current dealer price.
- Similar names with different references remain separate.
- A package reference is not collapsed into its components.
- Absence from one official source is not interpreted as withdrawal.
- The configurator will be used only for unresolved dynamic dependencies remaining after all document-backed comparisons.

## Data files

- `data/reporting/official_duster_accessory_price_list_20260806.csv`;
- `data/reporting/official_duster_accessory_catalog_compatibility_20260806.csv`;
- `data/reporting/official_duster_accessory_catalog_reconciliation_20260806.json`.

## Next step

Run repository validation, merge this bounded package after green CI, and continue with the Jogger accessory catalogue and price list using the same source-preserving method.
