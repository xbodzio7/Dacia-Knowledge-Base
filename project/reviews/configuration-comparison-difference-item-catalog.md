# Configuration Comparison Difference Item Catalog

Date: 2026-07-17

## Purpose

The configuration comparison difference CSV accepts one exact `--difference-item-code`, but the active report currently contains 109 valid codes and previously offered no deterministic discovery mechanism.

This package adds a dedicated catalog command:

```bash
python tools/dkb.py configuration-comparison-item-catalog \
  --csv ../configuration-comparison-item-catalog.csv
```

A dedicated command was selected instead of another output flag on `configuration-comparison` so discovery remains explicit, always uses the full active report and cannot accidentally inherit pair, domain or item filters.

## Contract

The CSV contains one deterministic row per `(domain, item_code)` with these columns:

- `domain`,
- `item_code`,
- `item_name`,
- `category`,
- `context_count`,
- `comparison_count`,
- `equal_count`,
- `different_count`,
- `not_comparable_count`.

Rows are ordered by the controlled domain order `prices`, `technical`, `equipment`, then by `item_code`.

Technical fuel contexts are aggregated into `context_count`. Price contexts retain the market and currency boundary. Equipment uses one empty context because availability comparisons are configuration-level states.

## Safety boundaries

- the command always builds the full active comparison report,
- it does not accept pair, domain or item filters,
- it does not change JSON, Markdown or difference-CSV output,
- it does not change master data or evidence classifications,
- unsupported comparison states are rejected,
- inconsistent name or category metadata for one domain/code is rejected,
- item codes appearing in more than one domain are rejected explicitly.

The collision rule turns the current collision-free snapshot into an executable contract. If domain-qualified item selection is introduced later, that rule may be reviewed separately.

## Validation performed before publication

The new module was compiled with Python and exercised against a synthetic two-pair report covering:

- deterministic domain and code ordering,
- aggregation of two fuel contexts,
- counts for `equal`, `different` and `not_comparable`,
- CSV round-trip parsing,
- rejection of a cross-domain item-code collision,
- registration and help visibility in the unified `dkb.py` CLI.

Repository-wide behavior is delegated to the pull-request Quality workflow because the execution environment used for this package did not have a network-accessible local checkout.

## Scope

Changed behavior is limited to the new catalog command and unified CLI registration. Existing comparison outputs, master data, evidence specifications, quality steps and workflow structure remain unchanged.
