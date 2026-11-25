# Official Bigster Brochure Full Assimilation

- Package ID: `official_bigster_brochure_full_assimilation_20261014_001`
- Review date: 2026-11-25
- Source: official Polish Dacia Bigster brochure dated 2025-12-10
- Archived PDF: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Coverage state: `fully_assimilated_with_deferrals`
- Full page inventory: `data/reporting/official_bigster_brochure_full_assimilation_20261125.json`

## Scope and source review

All 24 pages were reviewed through text extraction and rendered page images, including the colour palette, equipment matrix symbols/footnotes, technical table and dimension diagram. The source is linked to 14 active Bigster configurations. The official 2026-10-01 Polish price list was used as the current MY26 comparator; the 2026-07-03 source was also checked where it already contained exact payload ranges.

## Existing source coverage reconciled

- 458 scalar configuration observations from the 2025 brochure.
- 557 equipment-availability observations: 157 from printed page 21 and 400 from printed page 22.
- 34 source-specific configuration value ranges, including four 2025 maximum-payload ranges.
- 68 cargo-context values across 11 configurations.
- 56 grade-detail scalar observations from printed pages 14–17.
- 126 exterior-dimension observations from printed page 23.
- 14 exact source-configuration relationships.

## Exact additions in this package

1. Six standalone commercial palette items for Biel Alpejska, Czarna Perła, Szary Shiste, Niebieski Indigo, Zielony Cedar and Brązowy Terracotta, with six `exterior_color` item attributes. Finish and the printed two-tone marker are preserved. No grade/configuration mappings or prices are inferred because page 14 does not provide that scope.
2. The page-19 incompatibility note for accessory part `7717277154` (roof rack) and the panoramic glass roof.
3. Updated source registry and technical reconciliation records, plus the page-by-page full assimilation report and deferral ledger.

## Deliberate non-imports and preserved evidence

- Ten page-20 maximum-payload values exactly match the 2026-07-03 cennik and are not duplicated. Four 2025 brochure values for mild hybrid-G 140 remain preserved because they differ from the later 451/540 kg range (brochure: 452/521 kg).
- The 1813 mm brochure body-width observation remains separate from the 1812 mm later price-list observation.
- The brochure's 280 V Hybrid 155 battery statement remains separate from the later 200 V observation.
- Hybrid-G 150 4x4 cargo values remain deferred because the same brochure's technical and equipment tables disagree about the repair-kit state.
- YouClip count, front 12 V socket, USB-C port distribution, multimedia composite/screen-size semantics, colour grade applicability, accessory capacities and interior seat geometry remain explicitly deferred.
- The 2025 package markers are not assumed identical to the later 2026 commercial package identities.

No configurator evidence was used. No existing master observations were overwritten, no cross-powertrain projection was made, and unresolved facts were not entered as master values.

## Validation

The focused package contract test verifies the archived PDF SHA-256, exact colour item records, absence of unsupported grade mappings, roof-rack incompatibility note, source-specific payload reconciliation, current source coverage counts and canonical state counters. Full Quality and Repository Baselines checks are required on the exact Pull Request head before merge.
