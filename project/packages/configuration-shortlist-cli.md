# Configuration Shortlist CLI

## Goal

Provide a transparent user-facing way to find current Dacia configurations that satisfy explicit budget, drivetrain, transmission, seating and equipment requirements without adding scoring or inferred data.

## Command

```bash
python tools/dkb.py configuration-shortlist \
  --transmission automatic \
  --max-price 100000 \
  --require-equipment rear_view_camera \
  --json ../shortlist.json \
  --markdown ../shortlist.md \
  --csv ../shortlist.csv
```

## Supported criteria

- exact model codes through repeatable `--model`;
- exact version codes through repeatable `--version`;
- manual or automatic transmission through repeatable `--transmission`;
- case-insensitive powertrain-label fragments through repeatable `--powertrain`;
- minimum and maximum current Polish catalogue gross price in PLN;
- an exact recorded seat count;
- equipment available as standard or optional through repeatable `--require-equipment`;
- equipment required specifically as standard through repeatable `--require-standard-equipment`;
- a historical snapshot through `--as-of YYYY-MM-DD`.

Repeated values within model, version, transmission and powertrain criteria are ORed. Different criterion dimensions and equipment requirements are ANDed.

## Evidence semantics

A missing source statement never satisfies a criterion:

- missing prices are separate from prices outside the requested range;
- missing seat counts are separate from recorded non-matching values;
- missing equipment statements are separate from `not_available`;
- optional equipment satisfies a general availability requirement but not a standard-only requirement.

The JSON report contains non-exclusive exclusion-reason counts and data-unknown totals. Every matched price, seat count and required equipment state preserves its source code and observation date.

## Outputs

- JSON contains the complete filters, audit summary, unknown counts and matched records;
- Markdown provides a readable shortlist and exclusion summary;
- CSV contains one row per match with flattened price, seat and equipment provenance.

All formats are deterministic and sort matches by catalogue price, model, version and configuration code.

## Delivery

The `Configuration Shortlist` workflow publishes:

- the unfiltered 53-configuration portfolio;
- an example shortlist of automatic configurations priced at no more than 100,000 PLN;
- JSON, Markdown and CSV for both scenarios;
- a SHA-256 artifact manifest.

## Scope boundary

The package does not add preference scoring, financing calculations, total-cost estimates, fuzzy equipment synonyms, inferred values, market conversion or recommendations. It is an auditable filter over existing source-backed records.
