# Jogger MY26 2026-11-02 — Source Registration and Paint Reconciliation

Report ID: jogger_my26_20261102_source_registration_and_paint_reconciliation_20261121_001
Generated: 2026-11-21
Status: complete with explicit deferrals
Scope: Official Polish Jogger MY26 cennik, all nine pages; 12 exact source-linked configurations; no configurator or brochure evidence.

## Source identity

- Official URL: https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/d0a86dff46.pdf
- Effective date: 2026-11-02
- Archived path: `PDF/Cenniki/DACIA JOGGER cennik MY26 20261102.pdf`
- SHA-256: `94324e97d00e825ed537b525052dacfc436b57984880585e087852411b65a5da`
- Size: 2,119,710 bytes
- Pages: 9
- Archive PR: #873, merged as `1b1ff883d713a5aab4d182b9f7d0172425e1ba3c`
- Capture workflow: run #44948446147

The verified manifest is `data/source_intake/jogger_my26_20261102_capture.json`. The source register contains row 130, 12 configuration links and 3 grade links.

## Page comparison

| Pages | Result |
|---|---|
| 1 | 11 catalogue prices unchanged; visible effective date 02.11.2026. PDF text layer also retains 01.10.2026 elsewhere; recorded as an extraction artifact. |
| 2, 4, 6, 7, 8 | Extracted text identical to archived 2026-10-01 edition. |
| 3 | New source shows special non-metallic paint at 2,800 PLN and metallic pair 2,800 / 3,000 PLN. |
| 5 | Technical table unchanged; offer status date 02.11.2026. |
| 9 | Legal/offer status date 02.11.2026. |

All 11 catalogue price cells are already represented and unchanged. No duplicate catalogue price rows were added.

## Page 3 — commercial paint

The 2026-11-02 source explicitly shows:

- Special non-metallic paint: 0 / 2,800 PLN for Essential, Expression and Extreme.
- Metallic paint: 2,800 / 3,000 PLN for all three grades.

The existing item `jogger_special_nonmetallic_paint_option` was reused. Twelve dated 2026-11-02 mappings at 2,800 PLN were added across the exact 12 source-linked configurations. No new commercial item was created.

The metallic pair remains deferred: the cennik does not provide a named-colour or exact configuration crosswalk. No metallic-paint item or mapping was inferred.

## Historical 2026-10-01 paint amount — Do sprawdzenia

The archived 2026-10-01 PDF text extraction returns 0 / 2,700 PLN for special non-metallic paint and 2,700 / 2,900 PLN for metallic paint. However, the earlier visual review and current master mapping record 2,800 PLN and 2,800 / 3,000 PLN.

The original 2026-10-01 PDF is archived at `owner_supplied/2026-10-01/f5cdbd7878.pdf` with SHA-256 `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`. Its Library copy is 2,119,272 bytes, matching the repository blob size. The page-3 image could not be retrieved through the Library reader in this session. Therefore:

- the 2026-10-01 mapping remains unchanged at 2,800 PLN;
- no historical amount is overwritten;
- the delta is marked **Do sprawdzenia** until the archived page-3 render is visually reverified.

## Mutable source URL safeguard

The old CDN URL ending in `f5cdbd7878.pdf` currently returns a document titled `RI1 11.2026` with the 02.11.2026 effective date. The URL is mutable. The archived binary and SHA-256—not the current response from that URL—remain authoritative for the 2026-10-01 source.

## Outcome

- 1 new source registry row
- 12 source-configuration links
- 3 source-grade links
- 12 new dated special non-metallic paint mappings
- 0 new commercial items
- 0 duplicate catalogue price rows
- 0 technical or equipment rows added
- 0 historical paint mappings overwritten

The Jogger 2026-11-02 source is registered and assimilated with two explicit deferrals: historical paint-price delta pending old-page visual verification, and metallic-paint applicability pending an exact source crosswalk.
