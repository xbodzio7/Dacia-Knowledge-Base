# Sandero and Stepway Brochure Cargo Import Review

Date: 2026-07-25

## Source verification

Both archived PDFs are checked against their registered SHA-256 identities:

- Sandero: `adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97`;
- Sandero Stepway: `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`.

The reviewed page-20 tables contain the same five cargo facts: `328/410`, `1108/1455`
and underfloor capacity `78`.

## Mapping

The source is model-wide. Four active Sandero and five active Stepway Eco-G 120
configurations are linked using `brochure_technical_data_for`. The importer checks model
prefix, active status, Eco-G 120 powertrain and manual/automatic transmission.

## Context mapping

VDA/ISO 3832 and ordinary-litre values are separate observations. Minimum values use
`upright` plus `main_luggage_compartment`; maximum values use `folded` plus
`source_stated_total`; underfloor capacity uses `underfloor_compartment` with seat state
left unstated. Spare-wheel, tyre-repair-kit and double-floor states remain blank because
the brochure does not state them.

## Non-inference

- no tyre-repair-kit state is copied from configuration PDFs;
- no spare-wheel or double-floor state is inferred;
- no legacy value is migrated to the new relation;
- no TCe 100 configuration is invented;
- the later 372 dm3 legacy observation is not replaced by the older 328 dm3 brochure row.

## Reproducibility

One versioned JSON specification generates exact IDs 1832-1876 and context IDs 1-45.
The importer is idempotent, validates every semantic row and preserves all unrelated
master data.
