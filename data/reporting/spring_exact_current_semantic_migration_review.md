# Spring Exact Current Semantic Migration Review

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** 0

## Classification

| Class | Count |
|---|---:|
| Safe in-place update | 1 |
| Verified current — no change | 2 |
| Semantic migration required | 3 |
| Unresolved — no change | 19 |
| New representation required | 2 |

## Safe in-place update

`spring_colour_lichen_khaki__spring_essential_electric70_automatic` can be updated from an optional item with an unknown amount to an exact current **2300 PLN** optional paint price. The item, configuration and option semantics already match the current Essential configurator state.

## Verified current records

- Extreme CITY: **1800 PLN** — already correct.
- Extreme POWER: **3000 PLN** — already correct.

## Semantic migrations — not a price import

- Type 2 cable for Essential: exact current standard equipment, but modeled as a commercial option.
- Type 2 cable for Extreme: exact current standard equipment, but modeled as a commercial option.
- Biel Alpejska for Essential: exact current standard paint at zero surcharge, but modeled as an optional commercial item with an unknown price.

These records require an explicit standard/default representation before the stale option mapping can be retired or converted.

## New representation required

The home charging cable is an exact current **1500 PLN option** for Essential and Extreme, but the repository has neither a compatible commercial item nor a dedicated cable attribute. `charging_connector_type` describes the vehicle connector standard and must not be reused for a supplied cable.

## Unresolved mappings

Nineteen mappings remain unchanged:

- 9 Expression mappings: current price, charging states and full palette are not exposed by exact current grade pages;
- 6 Extreme paint mappings: no complete current priced palette was captured;
- 4 residual Essential paint mappings: absence from the captured palette is not treated as proof of unavailability.

## Next package

`spring_essential_khaki_price_apply_001` will apply only the exact current Essential Lichen Khaki price and leave every semantic or unresolved case untouched.
