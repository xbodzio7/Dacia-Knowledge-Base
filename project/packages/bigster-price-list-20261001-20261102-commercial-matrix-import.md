# Bigster MY26 commercial option and package price matrix — 2026-10-01 / 2026-11-02

## Scope

Reconcile printed pages 4–5 of the official Polish Bigster MY26 price lists effective 2026-10-01 and 2026-11-02. Import dated prices for existing options/packages, add the two explicitly priced paint options, and preserve powertrain qualifiers without projecting prices to unmatched configurations.

## Sources

- October source: `src_pl_bigster_price_my26_20261001`, archived at `owner_supplied/2026-10-01/d477c604e8.pdf`, SHA-256 `0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97`.
- November source: `src_pl_bigster_price_my26_20261102`, official URL `https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/2fe688def9.pdf`. Raw bytes remain in the user's Library; no SHA-256 is asserted.

Both price matrices cover the same 13 exact configurations already represented by dated catalogue-price records. The October source has 13 existing `source_configurations` links; the November source remains a price-only source with zero such links.

## Result

- 2 new commercial items: `bigster_metallic_paint_option` and `bigster_two_tone_body_option`.
- 172 new dated `commercial_item_configurations` rows: 86 per source date.
- No existing commercial item or mapping row was overwritten; July history remains intact.
- No new `commercial_item_attributes` rows were required; both paint items are represented as priced commercial options.

## Dated price comparison

| Option / package | 2026-10-01 | 2026-11-02 | Scope |
|---|---:|---:|---|
| Metallic paint | 3000 PLN | 3100 PLN | All 13 source-listed configurations |
| Two-tone body | 1400 PLN | 1500 PLN | Extreme and Journey; not with black paint |
| 19-inch RASAN wheels | 1200 PLN | 1200 PLN | Journey |
| Panoramic roof | 4300 PLN | 4300 PLN | Journey; standard in Extreme |
| Powered tailgate | 1300 PLN | 1300 PLN | Extreme; standard in Journey |
| Media Nav Live | 2400 PLN | 2400 PLN | Expression |
| EASY (P1) | 2700 PLN | 2700 PLN | Expression |
| PARKING (P2) | 2200 PLN | 2200 PLN | Extreme and Journey |
| WINTER (P3) | 1200 PLN | 1200 PLN | Expression, Extreme, Journey |
| WINTER PLUS (P4) | 2300 PLN | 2300 PLN | Expression, Extreme, Journey |
| Space-saver spare wheel | 800 PLN | 900 PLN | Hybrid 155 only |

## Spare-wheel evidence boundary

The October page-4 table contains two separate spare-wheel rows. The 215/70 R16 row is qualified to “mild hybrid 130 4x4”; no canonical Bigster configuration matches that exact powertrain label, so it is not mapped to tribrid 150 4x4. The 135/80 R17 space-saver row is qualified to “mild hybrid 140 4x2 and hybrid 155”. The October source's 13 configurations include Hybrid 155, mild hybrid-G 140 and tribrid 150, but no non-G mild hybrid 140. Only the three Hybrid 155 configurations receive the 800 PLN price.

The November page-4 row qualifies the space-saver to Hybrid 155 only and prices it at 900 PLN. For the ten other configurations inside each dated 13-configuration matrix, the import records `unknown` with the source date and no amount. This is deliberately not `not_available`: the source does not establish a negative availability state. The commercial-offer loader now lets a later `unknown` or `not_available` mapping suppress an older optional price, preventing the July 800 PLN amount from being shown as current for those configurations.

## Deferred

- No colour-by-colour surcharge is inferred from the metallic-paint surcharge. The brochure's page-14 colour palette and two-tone asterisk remain separate evidence.
- No equipment availability observations were added from pages 4–5 in this commercial-price package; those rows require their own exact attribute reconciliation.
- The 2026-11-02 page-6 technical table remains outside this package.

## Validation

The importer `tools/import_bigster_price_list_commercial_matrix_20261001_20261102.py` verifies the October source hash, both 13-configuration price scopes, the Library-only November receipt boundary, all 172 mapping rows, unique natural keys, and preservation of July history. Focused tests verify that the current commercial-offer view suppresses stale optional prices when a later source records `unknown`.
