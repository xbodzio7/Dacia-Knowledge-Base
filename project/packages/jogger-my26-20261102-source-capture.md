# Jogger MY26 2026-11-02 — Official Price List Source Capture

## Purpose

Capture and verify the official Polish Dacia Jogger MY26 price list effective 2026-11-02. This is a source-intake package only; it does not alter master prices, equipment, commercial items, or technical observations.

## Source

- Official Dacia / Renault Group CDN: https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/d0a86dff46.pdf
- Effective date printed on page 1: 2026-11-02
- Expected document length: 9 pages
- Previous registered edition: `src_pl_jogger_price_my26_20261001`
- Previous archived binary: `owner_supplied/2026-10-01/f5cdbd7878.pdf`
- Previous binary SHA-256: `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`

## Initial source review

The new official page-1 matrix contains 11 catalogue-price cells. All 11 amounts match the registered 2026-10-01 edition:

- 5 seats: 77,900; 82,050; 89,900; 96,800; 103,550; 111,400 PLN
- 7 seats: 86,550; 94,400; 101,300; 108,050; 115,900 PLN

The document's technical section also states an offer status date of 2026-11-02 and repeats the explicit Eco-G 120 injection and LPG tank-capacity wording already captured in the 2026-10-01 edition. No master price rows are to be duplicated solely to attach unchanged values to a later document.

## Capture and acceptance

The dedicated workflow:

1. Downloads the PDF from the official CDN.
2. Checks the exact 2026-11-02 date, all 11 price values, technical markers, and nine-page structure.
3. Verifies the archived comparison PDF against its registered SHA-256.
4. Extracts and compares all nine pages against the 2026-10-01 PDF, recording changed page numbers and text hashes.
5. Computes the new binary SHA-256 and file size.
6. Archives only the PDF and SHA-256 sidecar on a dedicated source branch if the source markers and document structure pass. The full capture manifest, extracted page text, page diffs and rendered page images remain in the workflow diagnostic artifact. The manifest is promoted to `data/source_intake` only in the follow-up registration package, together with its matching `data/master/sources.csv` row, so the package preflight cannot encounter an orphaned verified manifest.

The follow-up data package must inspect the page-by-page comparison before deciding whether any master data changed. Do not re-import unchanged catalogue prices, options, equipment or technical values. Do not use the configurator for this source review.

## Scope boundary

This package does not include Dacia Striker. The Project Owner has deferred Striker until price-list reconciliation is complete for all model families already represented in the master data. Do not begin Striker source capture, model/configuration creation or data import before that milestone is complete.
