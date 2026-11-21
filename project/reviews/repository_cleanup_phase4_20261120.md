# Repository cleanup — phase 4

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`

## Removed duplicate intake payload

- `data/reporting/cross_model_configurator_pdf_intake.json`

The file is an exact Git-blob duplicate of the retained source record:
`project/sources/dacia-pl-configurator-cross-model-pdf-bundle-20260804.json`.

The dedicated regression test `tests/test_cross_model_configurator_pdf_intake_20260805.py` reads and validates the `project/sources/` record directly. That canonical source record remains unchanged. The human-readable companion report `data/reporting/cross_model_configurator_pdf_intake.md` also remains.

## Safety and validation boundary

- The source record and all 18 source-document hashes/metadata remain intact.
- No master data, PDF source, importer, test, or active workflow is changed.
- The GitHub code-search endpoint reported incomplete results, so this is not represented as a complete repository-wide reference scan. The removal is limited to an exact duplicate with a dedicated test that explicitly targets the retained canonical source path.
- No local tests are claimed; required GitHub Actions checks must validate the exact PR head.
