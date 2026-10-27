# Duster Catalog Bootstrap

## Scope

This package creates only source-backed catalogue entities from the official Dacia Poland price list `DACIA DUSTER cennik MY26 PY25`.

It adds:

- 5 active Duster III versions,
- 24 active version and powertrain configurations,
- 5 source-to-version relationships,
- 24 source-to-configuration relationships.

It does not import catalogue prices, discounts, financing claims, equipment availability or detailed technical observations.

## Source

- source code: `src_pl_duster_price_my26_py25_20260206`
- document date: `2026-02-06`
- file: `PDF/Cenniki/DACIA DUSTER cennik MY26 PY25.pdf`
- SHA-256: `f6126fd4546031c643248b0e19639aa5736e54f8088567460681c938be3932b7`

The version and powertrain availability matrix is stated on page 1. Transmission types are confirmed in the technical tables on pages 8 and 9.

## Versions

| Code | Source name |
| --- | --- |
| `duster_iii_essential` | essential |
| `duster_iii_expression` | expression |
| `duster_iii_extreme` | extreme |
| `duster_iii_journey` | journey |
| `duster_iii_journey_plus` | journey+ |

## Powertrain matrix

| Source powertrain | Drive | Transmission | Version count |
| --- | --- | --- | ---: |
| Eco-G 100 | 4x2 | manual, 6-speed | 4 |
| mild hybrid 130 | 4x2 | manual, 6-speed | 3 |
| hybrid 140 | 4x2 | automatic Multi-mode | 4 |
| mild hybrid 130 | 4x4 | manual, 6-speed | 3 |
| Eco-G 120 | 4x2 | manual, 6-speed | 4 |
| mild hybrid 140 | 4x2 | manual, 6-speed | 3 |
| hybrid 155 | 4x2 | automatic Multi-mode | 3 |

The matrix contains exactly 24 combinations. Codes include `4x2` or `4x4` explicitly because the same source contains both drive layouts.

## Reporting boundary

All new catalogue entities use the existing `active` status. Under the explicit reporting-subset contract, they are visible in master data but are not automatically enrolled in the current Sandero completeness and comparison denominators.

After the bootstrap:

- repository-wide active configurations: 31,
- current reporting configurations: 7,
- explicitly excluded Duster configurations: 24,
- comparison pairs: 21,
- comparison difference rows: 305.

## Evidence boundary

The package does not infer unavailable combinations from general model knowledge. A configuration exists only where the page-1 matrix contains a catalogue price. A dash is treated as absence from this source matrix.

Transmission values use the controlled repository enum:

- `manual` for the source rows described as `manualna 6-biegowa`,
- `automatic` for `automatyczna Multi-mode`.

No separate gearbox, engine, drive-type observation or price record is created in this package.

## Validation

Acceptance requires:

- exact five-version and 24-configuration sets,
- exact source relationship coverage,
- no Duster price, technical-value or equipment-availability rows,
- repository validation and SQLite parity at 34 tables and 1,440 rows,
- unchanged Sandero reporting output,
- full Quality and Windows checks.
