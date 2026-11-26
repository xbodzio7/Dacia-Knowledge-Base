# Jogger Brochure Cargo Value Import Review

Date: 2026-07-26

## Source verification

The archived 23-page official Polish Jogger brochure is checked against SHA-256
`eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6`.

Page 22 contains separate columns for the five- and seven-seat variants and gives
VDA/ISO 3832 values alongside ordinary litres.

## Mapping

Eleven active five-seat and eleven active seven-seat configurations are linked with
`brochure_technical_data_for`. The importer checks active status, Jogger identity,
powertrain, transmission and the exact `number_of_seats` value for every
configuration.

## Context mapping

- five-seat minimum: second row `upright`, third row not applicable/not stated;
- five-seat maximum: second row `folded`, `source_stated_total`;
- seven-seat minimum: second and third rows `upright`;
- seven-seat intermediate: second row `upright`, third row `folded`;
- seven-seat removed-row state: second row `upright`, third row `removed`;
- VDA/ISO 3832 and ordinary litres remain separate observations.

## Non-inference

- `1807/2085` is excluded because its third-row state is not stated;
- no five-seat value is reused for a seven-seat configuration;
- no spare-wheel, repair-kit or double-floor state is inferred;
- no configuration outside the explicit 22-row scope receives a value;
- no source value is converted between VDA/ISO 3832 and ordinary litres.

## Reproducibility

The versioned JSON specification generates exact value IDs 1877-1986 and context
IDs 46-155. The importer is idempotent, validates the archived PDF hash, reproduces
all 110 values and contexts, and preserves unrelated master data.
