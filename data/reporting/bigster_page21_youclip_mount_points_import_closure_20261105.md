# Bigster Page 21 — YouClip Mount Points Import Closure

**Status:** complete  
**Date:** 2026-11-05  
**Package:** `bigster_page21_youclip_mount_points_import_20261105_001`

## Source evidence

- Official source: `src_pl_bigster_brochure_20251210`
- File: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Printed page: 21
- Section: `PROWADZENIE I URZĄDZENIA KONTROLNE`
- Exact row: **Punkty mocowania YouClip — 4 / 5 / 5 / 5**

The rendered page shows four grade columns: Essential, Expression, Journey and Extreme. The values are 4, 5, 5 and 5 respectively. The source registry links this brochure to 14 active Bigster configurations: two Essential and four each for Expression, Journey and Extreme.

## Data model

Added one active canonical attribute:

- ID: `424`
- Code: `youclip_mount_points`
- Category: `Infotainment`
- Type: integer
- Unit: none

The existing `youclip_phone_holder` attribute describes a smartphone holder, not the number of mounting points. No existing attribute represented this count, so it was not reused or overloaded.

## Import

Added 14 scalar observations:

| Grade | Linked configurations | Value per configuration |
| --- | ---: | ---: |
| Essential | 2 | 4 |
| Expression | 4 | 5 |
| Journey | 4 | 5 |
| Extreme | 4 | 5 |

IDs: `8217–8230`  
Source date: `2025-12-10`  
No prior value slots existed for this attribute. No existing master observations were overwritten.

## Validation

- Source PDF SHA-256 matches the registered source.
- All 14 target configurations are active and linked to the brochure.
- The import test checks the exact 14-row manifest, attribute contract, source relationship, grade mapping and PDF page text.
- Three focused tests added.

## Files

- Import specification: `data/imports/configuration_values/bigster-page21-youclip-mount-points-20251210.json`
- Master values: `data/master/configuration_attribute_values.csv`
- Attribute dictionary: `data/master/attributes.csv`
- Test: `tests/test_bigster_page21_youclip_mount_points.py`
