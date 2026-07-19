# Interactive Configuration Shortlist HTML Planning Review

## Decision status

`SELECTED — SELF-CONTAINED INTERACTIVE SHORTLIST HTML`

The next package will extend the existing `configuration-shortlist` command with `--html FILE`. The generated file will embed the complete active configuration snapshot and provide browser-side filters that mirror the transparent CLI criteria without adding preference scoring or inferred values.

## Delivery model

The HTML output will be:

- one deterministic UTF-8 file with embedded CSS, JavaScript and data;
- usable directly from the filesystem without a server or network connection;
- generated from the same source-backed snapshot loader as JSON, Markdown and CSV;
- responsive, keyboard-usable and printable;
- free of external scripts, stylesheets, fonts, analytics and runtime dependencies.

## Relationship to CLI filtering

JSON, Markdown and CSV remain server-side shortlist results for the criteria passed on the command line. HTML embeds all active configurations from the selected `--as-of` snapshot so users can widen or change criteria after opening the file.

Any CLI criteria supplied together with `--html` become the initial browser filter state. Clearing the form restores the complete embedded snapshot rather than only the server-side matches.

## Browser catalog

The Python engine will expose a dedicated browser catalog containing:

- configuration, model and version codes and names;
- powertrain label and transmission type;
- current Polish catalogue gross price, date and source;
- recorded seat count, date and source or an explicit missing state;
- all current equipment availability states, dates and sources;
- deterministic facet catalogs for models, versions, powertrains, transmissions, seat counts and equipment attributes.

The catalog is an HTML delivery payload and will not be added to the existing shortlist JSON schema by default.

## Browser controls

The first implementation will provide:

- model and version selectors;
- transmission selector;
- powertrain text filter;
- minimum and maximum price inputs;
- exact seat-count selector with missing-state visibility;
- repeatable equipment requirements accepting standard or optional;
- repeatable standard-only equipment requirements;
- free-text search over configuration, model, version and powertrain labels;
- deterministic result ordering identical to the CLI;
- visible counts for matches, exclusions and missing price, seat or equipment statements;
- a reset action returning to the complete snapshot.

## Semantic contract

Browser filtering must preserve the CLI rules:

- repeated model, version, transmission and powertrain values are ORed within a dimension;
- different dimensions and equipment requirements are ANDed;
- general equipment requirements accept `standard` or `optional`;
- standard-only requirements accept only `standard`;
- missing statements never satisfy a requirement and remain distinct from `not_available`;
- no value is inferred and no unknown is silently converted to a negative result.

## Drift prevention

The implementation will separate the normalized browser catalog from presentation code. Representative browser-filter scenarios will be executed in JavaScript during CI and compared with the Python shortlist engine over the same fixture. This contract must cover metadata, price, seats, equipment availability, standard-only equipment and missing statements.

## Scope boundary

The package will not add ranking, weighted preferences, financing, total-cost calculations, fuzzy synonym matching, currency conversion, URL sharing, browser persistence or direct comparison of selected results. Those capabilities remain separate product decisions.

## Implementation target

The next package is **Interactive Configuration Shortlist HTML**, with `--html` CLI integration, a source-backed browser catalog, semantic parity tests, a publishing workflow, documentation and canonical state synchronization.
