# Brochure Equipment Inheritance and Colour Review

Date: 2026-07-31

## Decision

Select **Spring Version Equipment Matrix Availability Import** as the first implementation package after this review.

## Evidence examined

All twenty registered brochure and price-list PDFs were read from the repository. Every file was present and matched the SHA-256 recorded in `data/master/sources.csv`. The review treated dynamic configurators, exact stock cards, promotional stock lists and immutable brochures as separate evidence classes.

## Inheritance contract

Twenty-four source statements explicitly define a higher grade as a lower grade plus additional equipment. They occur in nine Duster, Bigster, Jogger, Sandero, Sandero Stepway and Spring sources.

These statements authorize only the chain written in that exact source. They do not authorize:

- moving equipment between MY25 and MY26;
- moving a brochure state into a later configurator or price list;
- copying a manual-powertrain observation into an automatic configuration;
- treating an omitted row as unavailable;
- overriding a direct matrix cell with reconstructed inheritance.

## Why Spring is first

Spring Essential Electric 70, Expression Electric 70 and Extreme Electric 100 are already active, source-backed configurations, but they have no equipment-availability records. The registered brochure has a direct three-grade matrix on pages 19-20 and an explicit Essential → Expression → Extreme chain on pages 14-15.

The matrix can be mapped without architecture changes to 42 existing attributes. Applying every direct cell yields 126 observations with a deterministic distribution of 106 standard, seven optional and thirteen not available. Direct cells avoid having to reconstruct inherited states.

The package remains deliberately smaller than the broader earlier label “Spring Version Equipment Matrix Import”. Commercial packages, charging-cable choices and package membership will follow in a separate PR because the brochure states applicability and contents but no prices.

## Colour review decision

The six brochure palettes contain forty named colours. Their finish footnotes and grade restrictions are preserved in the review artifact, but the repository currently has only a configuration-level string observation for `exterior_color` and no model-level colour-choice or two-tone catalogue.

Fixed generic price rows can be imported separately. Paired values such as `2700/2900` cannot be assigned to a single commercial item amount, and named palette entries cannot be joined to later price tiers unless the source performs that mapping.

## Small package queue

1. **Spring Version Equipment Matrix Availability Import** — 126 direct availability rows.
2. **Spring Commercial Packages and Charging Options** — Techno, Power, City and Type 2 cable applicability, no invented amount.
3. **Jogger MY26 Fog-Light Superseding Observations** — six dated July corrections, historical April rows retained.
4. **Bigster MY26 Exact Paint Options** — metallic and two-tone generic options with exact fixed amounts.
5. **Sandero and Stepway Fixed Paint Price Subset** — only the nine configurations with an unambiguous 2500 PLN cell.
6. **Duster Eco-G 120 Automatic Equipment Matrix Closure** — direct current-source review of 26 priority gaps.

## Explicit deferrals

- commercial price-range representation;
- model-level named-colour and two-tone semantics;
- Duster `0/2700` named non-metallic choices until zero-surcharge optionality is contracted;
- Spring MY25 stock colour price in current MY26 configurations;
- any propagation based only on grade ordering or sibling similarity.

## Result

The review changes no master data. It records exact import packages and leaves unresolved modelling boundaries visible rather than converting them into values.
