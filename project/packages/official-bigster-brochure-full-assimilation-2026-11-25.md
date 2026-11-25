# Official Bigster Brochure Full Assimilation

- Package ID: `official_bigster_brochure_full_assimilation_20261014_001`
- Review date: 2026-11-25
- Source: official Polish Dacia Bigster brochure dated 2025-12-10
- Archived PDF: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Coverage: `fully_assimilated_with_deferrals`
- Report: `data/reporting/official_bigster_brochure_full_assimilation_20261125.json`

## Review and existing coverage

All 24 pages were reviewed as text and rendered images. The brochure is linked to 14 active configurations. Reconciled source coverage includes 458 scalar observations, 557 equipment-availability observations (157 page 21; 400 page 22), 34 value ranges, 68 cargo-context values, 56 grade-detail observations and 126 page-23 exterior-dimension observations.

## Exact additions

1. Six standalone colour palette items and six `exterior_color` item attributes from page 14. Finish and the printed two-tone marker are retained. No grade/configuration mappings or prices are inferred.
2. The page-19 incompatibility note for accessory part `7717277154` and the panoramic glass roof.
3. Updated source registry, page-20 technical reconciliation, page-by-page inventory report and deferral ledger.

## Non-import decisions and preserved conflicts

- Ten page-20 payload values match the 2026-07-03 cennik and are not duplicated. Four 2025 mild hybrid-G 140 values remain as historical observations because they differ (452/521 kg vs 451/540 kg).
- The 1813 mm brochure body-width value remains separate from the later 1812 mm value.
- The brochure's 280 V Hybrid 155 battery statement remains separate from the later 200 V observation.
- Hybrid-G 150 4x4 cargo values remain deferred because the same brochure's technical and equipment tables disagree about repair-kit state.
- YouClip count, front 12 V socket, USB-C distribution, multimedia semantics, colour grade applicability, accessory capacities, interior geometry and 2025 package identities remain explicitly deferred.

No configurator evidence was used. No existing observations were overwritten; no cross-powertrain projection or unsupported grade mapping was made.

## Validation

One focused contract test checks the archived PDF SHA-256, colour item records, absence of unsupported grade mappings, roof-rack note, exact payload reconciliation, source coverage and canonical baseline counters. Full Quality and Repository Baselines checks are required on the exact PR head before merge.
