# Bigster MY26 2026-11-02 source binary recovery

## Objective
Recover the exact official Polish Bigster MY26 price-list PDF already supplied and SHA-256 verified by the project owner, but not yet archived in the repository.

## Source identity gate
- Source code: `src_pl_bigster_price_my26_20261102`
- URL: https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/2fe688def9.pdf
- Expected SHA-256: `592f28852118b57fe6bdef75864ea479d9e01bb9af9a166108014eff4ae85b5b`
- Expected size: 1,995,398 bytes
- Expected page count: 8
- Effective date: 2026-11-02
- Market/model year: Poland / MY26

## Why a capture workflow is used
The Library search can find and text-extract the owner-supplied PDF, but raw-byte materialization is not authorized for this Library item. The GitHub Contents text endpoint also does not return binary PDF bytes. The public official CDN URL is readable as an eight-page PDF, so the repository workflow downloads the original directly and compares its SHA-256, byte size, page count and all 13 first-page catalogue-price markers against the already registered source identity.

## Acceptance
1. All four identity gates match exactly: SHA-256, file size, 8 pages, and first-page date/year/price markers.
2. On success, archive the binary, capture manifest and SHA-256 sidecar on `data/bigster-my26-cennik-assimilation-20261115-001`.
3. Upload a diagnostic artifact with PDF, page text, rendered pages, pdfinfo and manifest even on failure.
4. On mismatch, retain diagnostic evidence only; do not commit the binary or alter canonical source records.
5. No master-data import is performed by this recovery package. The 13 catalogue prices were already imported and reconciled in prior packages.

## Workflow
`.github/workflows/source-assimilation-bigster-audit.yml` runs on a main push changing itself, and supports manual dispatch. Its first execution after merge captures the CDN binary and creates the dedicated source branch only when every identity gate passes.
