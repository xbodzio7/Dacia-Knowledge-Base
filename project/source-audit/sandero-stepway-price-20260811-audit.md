# Sandero / Sandero Stepway price list 2026-08-11 — source audit

- Source code: src_pl_sandero_stepway_price_my26_20260811
- Title: DACIA SANDERO I SANDERO STEPWAY cennik MY26
- Publisher: Dacia
- Market: PL
- Effective/document date: 2026-08-11
- Pages: 7
- Supplied PDF SHA-256: c220ab0ff1df848b72121c6ebe0f05fb245bb9b70052a10dbd48068709b2034a
- Normalized extract: project/sources/sandero_stepway_price_my26_20260811_full_extract.json
- Audit status: fully_assimilated_with_deferrals

## Page inventory

| Page | Content | Result |
|---:|---|---|
| 1 | catalogue prices, model/grade columns, 2026 validity | imported/represented |
| 2 | model presentation and general equipment context | classified as context |
| 3 | exterior/interior/safety equipment matrix | fully extracted; Hybrid 155 applicability materialized |
| 4 | visibility/comfort/multimedia/packages | fully extracted; package and availability semantics preserved |
| 5 | technical data: engines, gearbox, power, torque, dimensions/cargo context | fully extracted; source-explicit values materialized where bounded |
| 6 | visual/model material | rendered visual checked |
| 7 | legal notes, validity, supersession and publication state | classified as provenance/context |

## Master-data result

The source is represented by the complete normalized extract. The four Hybrid 155 configurations have:

- 4 price records;
- 64 technical/configuration values;
- 258 equipment-availability records.

The extract retains the complete six-grade equipment matrix and the package definitions, even where individual cells were not imported as new observations because equivalent stronger configuration evidence already existed.

## Important boundary

This source is not a license to transfer an equipment cell from one grade, fuel, gearbox or model family to another. The six-column matrix remains source evidence; master-data rows are materialized only for exact configuration applicability.

## Result

The 2026-08-11 Sandero/Stepway price list itself is no longer an unreviewed source. Remaining portfolio gaps concern other documentary sources and/or current configurator states, not missing pages from this seven-page price list.
