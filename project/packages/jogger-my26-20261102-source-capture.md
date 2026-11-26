# Jogger MY26 2026-11-02 — Official Price List Capture and Reconciliation

## Purpose

Capture, archive and register the official Polish Dacia Jogger MY26 price list effective 2026-11-02, compare all nine pages with the archived 2026-10-01 edition, and import only the new, source-supported commercial observation.

## Verified source identity

- Source code: `src_pl_jogger_price_my26_20261102`
- Official URL: https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/d0a86dff46.pdf
- Effective date: 2026-11-02
- Archive path: `PDF/Cenniki/DACIA JOGGER cennik MY26 20261102.pdf`
- SHA-256: `94324e97d00e825ed537b525052dacfc436b57984880585e087852411b65a5da`
- File size: 2,119,710 bytes
- Page count: 9
- Capture workflow: #44948446147
- Archive PR: #873, merged as `1b1ff883d713a5aab4d182b9f7d0172425e1ba3c`
- Source manifest: `data/source_intake/jogger_my26_20261102_capture.json`

## Page-by-page result

- Page 1: all 11 catalogue price cells are unchanged. The visible effective date is 02.11.2026. The text layer also retains an earlier 01.10.2026 string elsewhere on the page; this is recorded as a text-layer artifact.
- Pages 2, 4, 6, 7 and 8: extracted text is identical to the archived 2026-10-01 edition.
- Page 3: the 2026-11-02 source visibly lists special non-metallic paint at 2,800 PLN and metallic paint as a 2,800 / 3,000 PLN pair. Twelve special non-metallic mappings were added for the exact source-linked configurations. The metallic pair remains unmapped because no exact colour/configuration crosswalk is provided.
- Page 5: technical table content is unchanged; offer-status date is 02.11.2026.
- Page 9: legal/offer-status date is 02.11.2026.

No duplicate catalogue price rows were added because all 11 vehicle-price cells are unchanged. No technical or equipment rows were added.

## Historical paint-price delta — Do sprawdzenia

The archived 2026-10-01 PDF text extraction returns 0 / 2,700 PLN and 2,700 / 2,900 PLN on page 3. The earlier visual review and current master mapping record 0 / 2,800 PLN and 2,800 / 3,000 PLN. The old CDN URL is mutable and currently returns the newer 02.11.2026 document. The archived old page-3 image could not be retrieved through the Library reader in this session.

The 2026-10-01 historical mapping remains unchanged at 2,800 PLN. Do not overwrite it until the archived page-3 render is visually reverified. The new 2026-11-02 special non-metallic 2,800 PLN observation is registered independently.

## Striker boundary

Striker remains deferred until price-list reconciliation is complete for all model families already represented in the master data. No Striker source capture, model/configuration creation or data import is part of this package.
