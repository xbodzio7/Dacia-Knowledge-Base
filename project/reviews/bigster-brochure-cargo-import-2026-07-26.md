# Bigster Brochure Cargo Value Import Review

Date: 2026-07-26

## Source identity

The archived 24-page official Polish Bigster brochure is verified against SHA-256
`76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`.

## Technical table

Page 20 distinguishes four powertrains and provides VDA/ISO 3832 and ordinary-litre
values under the luggage shelf and with the rear bench folded. The mild hybrid 140
and hybrid 155 columns separately state repair-kit and spare-wheel values. The
mild hybrid-G 140 footnote states that a spare wheel is unavailable.

## Configuration projection

Only exact active configurations whose canonical powertrain labels match the
source column are included. The import covers eleven 4x2 configurations and creates
`brochure_technical_data_for` relationships for those targets only.

The three hybrid-G 150 4x4 configurations remain outside the import because the
brochure contradicts itself on tyre-repair-kit presence. No source relationship is
created for an observation that remains deferred.

## Context rules

- VDA/ISO 3832 and ordinary litres remain separate rows;
- rear bench upright uses `main_luggage_compartment`;
- rear bench folded uses `source_stated_total`;
- repair kit and spare wheel are mutually exclusive only where the brochure
  explicitly says the spare option replaces the kit;
- double-floor and third-row states remain empty because page 20 does not qualify
  them;
- no value from the generic dimensions page is assigned to a powertrain by matching
  its number.

## Reproducibility

The versioned JSON specification generates exact value IDs 1987-2054 and context
IDs 156-223. The importer is idempotent, verifies the archived PDF hash, exact
configuration labels and all 68 value/context pairs, and preserves unrelated master
data.
