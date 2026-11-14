# Jogger MY26 2026-10-01 Commercial Matrix Completion

**Package:** `jogger_price_list_20261001_commercial_matrix_import_20261114_001`  
**Source:** `src_pl_jogger_price_my26_20261001`  
**Official PDF:** https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/f5cdbd7878.pdf  
**Archived binary:** `owner_supplied/2026-10-01/f5cdbd7878.pdf`  
**SHA-256:** `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`

## Imported result

One item and 54 dated configuration mappings were added from printed pages 3–4 across the 12 source-linked configurations: 38 `optional`, 16 `not_available`.

| Commercial item | Page | Optional | Not available | Price |
|---|---:|---:|---:|---:|
| Special non-metallic paint | 3 | 12 | 0 | 2,800 PLN |
| Media Nav | 4 | 10 | 2 | 1,600 PLN |
| Heated front seats | 4 | 4 | 2 | 700 PLN |
| ZIMOWY package | 4 | 6 | 6 | 1,200 PLN |
| DRIVE package | 4 | 6 | 6 | 1,400 PLN |
| **Total** | | **38** | **16** | |

Existing item codes were reused for Media Nav, heated front seats, ZIMOWY and DRIVE.

## Evidence boundaries

- Page 3 prints non-metallic / special non-metallic paint as 0 / 2,800 PLN. The paid special non-metallic finish is mapped for all 12 configurations; no named colour is inferred.
- Metallic paint 2,800 / 3,000 PLN remains deferred because no exact grade/colour mapping is established.
- Page 4 marks Extreme heated front seats as `P` (part of a package). No standalone Extreme heated-seat mapping was added; ZIMOWY is represented separately.
- Media Nav is optional for Expression and Extreme and explicitly unavailable for Essential.
- ZIMOWY and DRIVE are optional for Extreme and explicitly unavailable for Essential and Expression.
- Removed KOMFORT packages and separate accessory lists are not inferred.

## Preservation

- Existing April/July price observations and 48 July Jogger commercial mappings remain unchanged.
- The 7-seat Eco-G 120 manual matrix remains Essential dash, Expression 86,550 PLN and Extreme 94,400 PLN; catalogue price rows were not changed.
- Source register now uses the direct official PDF URL.
- No commercial-item attributes were added because the source does not support named-colour mapping.

## Reproducible artifacts

- `data/imports/jogger_commercial_items_20261001.csv`
- `data/imports/jogger_commercial_item_configurations_20261001.csv`
- `tools/import_jogger_price_list_commercial_matrix_20261001.py`
- `tests/test_jogger_price_list_commercial_matrix_20261001.py`

## Acceptance

The importer checks source SHA-256, 12 configuration links, three grade links, 11 price cells, exact natural keys, row counts, status distribution and historical preservation. Focused tests, package preflight, canonical state/documentation checks, independent source-fidelity review and final-head Quality are mandatory.
