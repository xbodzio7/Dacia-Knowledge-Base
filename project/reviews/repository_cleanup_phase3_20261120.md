# Repository cleanup — phase 3

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`

## Removed exact duplicate

- `.github/data-products-v1.8.1-public-audit.json`

Its Git blob is byte-for-byte identical to `data/reporting/data_products_v1_8_1_publication_audit.json`. The latter is retained as the canonical reporting artifact. The current data-product release and download workflows do not refer to the `.github/` copy.

## Safety

- The canonical audit JSON remains in `data/reporting/`.
- No release assets, source files, data, tests, or workflows are changed.
- No local test runtime is available in this session; required GitHub Actions checks must validate the exact PR head.
- This package intentionally removes only the duplicate copy. Other identical source/report artifacts remain deferred until all consumers can be checked with confidence.
