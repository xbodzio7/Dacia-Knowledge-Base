# Spring MY26 Live Asset Identity Verification

Package: spring_my26_live_asset_identity_verification_20261114_001  
PR: #817  
Prior capture run: #43534970475

## Triggering observation

The first direct download through GitHub Actions retrieved a 1.35 MB PDF from the official CDN URL but the first-page text extracted by Poppler did not contain the expected ROCZNIK 2026 marker. The workflow stopped before hashing or committing the file. No binary was added to the repository.

This result conflicts with the web-extracted MY26 PDF text and must be resolved by inspecting the actual downloaded bytes, not by assuming that a URL identifies immutable content.

## Workflow repair

The existing Spring audit workflow now:
- downloads the original PDF and immediately records PDF metadata and SHA-256;
- extracts and prints first-page text for diagnostic review;
- records page count, size, expected markers, missing markers and whether the hash matches the registered MY25 SHA-256;
- uploads the full diagnostic bundle even when verification fails;
- commits the PDF to the dedicated source branch only when all MY26 identity checks pass;
- exits unsuccessfully after artifact upload if the downloaded source is not verified as MY26.

## Decision boundary

- If the downloaded bytes match the registered MY25 hash, treat the live URL response as MY25; do not register or import it as MY26.
- If the PDF is different but the page text shows another model year/date, preserve it as a separate candidate and investigate.
- If the PDF is MY26 but text extraction formatting differs, update the marker check only after the first-page text is inspected.
- If no distinct MY26 binary can be retrieved, request only the missing MY26 PDF; do not ask for the already available MY25 Library file.

No master source, configuration or price rows are changed by this package.
