# Duster Source Intake

## Decision

The original Dacia Poland Duster price-list PDF supplied by the project owner is accepted as the first registered Duster III source.

The binary is stored without modification and registered before any Duster version, configuration, price, technical-value or equipment import is attempted.

## Binary identity

```text
repository path: PDF/Cenniki/DACIA DUSTER cennik MY26 PY25.pdf
size: 2020286 bytes
SHA-256: f6126fd4546031c643248b0e19639aa5736e54f8088567460681c938be3932b7
PDF version: 1.7
pages: 11
encrypted: no
```

The PDF metadata records creation and modification on `2026-02-06T12:10:19+01:00`. Page 1 states that the price list applies from `2026-02-06`, so the conservative source `document_date` is `2026-02-06`.

## Registered source

```text
source_code: src_pl_duster_price_my26_py25_20260206
source_type: configuration_pdf
title: DACIA DUSTER cennik MY26 PY25
publisher: Dacia
market: PL
document_date: 2026-02-06
external_reference: b281a995a9
status: active
```

The external reference is the stable asset token from the official candidate URL approved by the readiness review. The full URL remains in `project/reviews/duster-source-intake-readiness.md`; it is not duplicated in master data.

## Model relationship

The source is linked to:

```text
duster_iii — configuration_for
```

No version or configuration relationship is created in this intake package because those entities do not exist yet. They belong to the separate `Duster Catalog Bootstrap` package.

## Source observations relevant to the next package

Page 1 contains a catalogue-price matrix for the named versions `essential`, `expression`, `extreme`, `journey` and `journey+` where applicable. It also names multiple powertrains, including the model-year-2025 rows for Eco-G 100, mild hybrid 130, hybrid 140, Eco-G 120, mild hybrid 140 and hybrid 155.

Pages 3 through 7 contain version and equipment descriptions. Pages 8 and 9 contain technical tables. These sections support bounded follow-up review but do not authorize bulk automatic import.

## Evidence boundary

This package intentionally does not:

- create Duster versions or configurations;
- import catalogue prices;
- import discounts, financing benefits or promotional claims;
- map technical labels to canonical attributes;
- import equipment availability;
- infer configurations from blank or unavailable cells;
- infer document facts from download time.

The visible promotional statements on pages 1 and 2 remain source content only. The later price package may import explicit catalogue prices, but it must exclude discount and financing amounts from `configuration_prices.csv`.

## Acceptance criteria

- the stored PDF bytes reproduce the declared SHA-256;
- `sources.csv` contains exactly one active Duster price-list record;
- `source_models.csv` links that record to `duster_iii`;
- repository validation and SQLite parity pass;
- source coverage and full Quality pass without weakening existing evidence rules;
- canonical state advances to `Duster Catalog Bootstrap`.
