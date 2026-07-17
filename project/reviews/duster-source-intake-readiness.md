# Duster Source Intake Readiness

## Decision

The repository is structurally ready for Duster III expansion, but source intake must remain blocked until the original source binary is available to the maintainer runtime.

This review is a justified review-only delivery because it records an external evidence boundary and the exact user action required to resume autonomous work.

## Repository readiness

The canonical model catalog already contains:

```text
duster_iii — Duster III — production from 2024 — current
```

No Duster III version, configuration or source relationship is currently registered. The active repository contains:

- five versions, all belonging to Sandero III or Sandero Stepway III;
- seven configurations, all belonging to those versions;
- seven source records, all Dacia Poland Sandero or Sandero Stepway configuration PDFs;
- seven source-model, source-version and source-configuration relationships, all scoped to Sandero or Sandero Stepway.

The existing schema supports the required Duster intake without migration:

- `sources.csv` records type, title, publisher, market, document date, external reference, local file path, SHA-256 and lifecycle status;
- `source_models.csv` links the source to `duster_iii`;
- `versions.csv` and `configurations.csv` can be extended only after source inspection;
- `source_versions.csv` and `source_configurations.csv` preserve provenance for every created catalog entity.

## Approved candidate source

The official Dacia Poland Duster campaign page currently links a price list labelled `MY26 PY25`:

```text
https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price-2025.pdf.asset.pdf/b281a995a9.pdf
```

Observed source properties:

- publisher: Dacia;
- market: PL;
- format: PDF;
- pages: 11;
- price-list validity date printed in the document: 2026-02-06;
- model scope: Duster III;
- versions shown: essential, expression, extreme, journey and journey+ where applicable;
- powertrains shown across the document include Eco-G 100, mild hybrid 130, hybrid 140, Eco-G 120, mild hybrid 140, hybrid 155 and hybrid-G 150;
- the document contains price, standard-equipment, option and technical tables.

This is sufficient to begin source registration and a bounded catalog bootstrap. It is not permission to import every visible value automatically: each version, powertrain, equipment and technical mapping must still be reviewed against canonical codes.

## Blocking condition

The GitHub connector can inspect repository text but cannot obtain the original PDF bytes from the external CDN. The source registry requires the exact local file path and a full SHA-256 digest. Reconstructing the PDF from parsed text or screenshots would produce a different binary and would violate provenance.

The package is therefore blocked by:

```text
missing_source_file_or_local_access
```

## Required source package

Provide the exact original PDF linked above by either:

1. uploading it directly to the current ChatGPT conversation; or
2. adding the unmodified PDF to an accessible repository branch and providing its path.

Do not print, re-save, optimize, merge or convert the PDF. The original downloaded bytes are required for a reproducible SHA-256.

Additional official Duster configuration PDFs may be supplied in the same way. They can improve configuration-level precision, but the approved price list is the minimum source needed to resume.

## Automatic resume sequence

After the source binary becomes available, the autonomous maintainer will:

1. calculate SHA-256 and verify the PDF header and page count;
2. store or reference the exact file under the repository source convention;
3. create one `sources.csv` record with conservative metadata;
4. link it to `duster_iii` in `source_models.csv`;
5. run validation, SQLite parity, source coverage and full Quality;
6. publish and merge the source-intake PR;
7. inspect the accepted source and create the bounded Duster Catalog Bootstrap package;
8. add only source-supported versions, configurations and provenance relationships;
9. defer prices, technical values and equipment records until their mappings pass a separate evidence review.

## Safety boundary

The intake must not:

- infer a document date from the download time;
- use dealer listings as the canonical source when an official Dacia document exists;
- create configurations from marketing names without checking the source table structure;
- assign canonical attributes by approximate text similarity;
- replace the original binary with screenshots or extracted text;
- import promotional discounts as catalog prices unless explicitly represented by the source schema and package scope.
