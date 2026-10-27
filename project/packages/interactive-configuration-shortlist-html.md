# Interactive Configuration Shortlist HTML

## Goal

Make the complete source-backed configuration portfolio usable in a browser without requiring Python, a local server or knowledge of the repository schema, while preserving the transparent shortlist semantics already provided by the CLI.

## Command

```bash
python tools/dkb.py configuration-shortlist \
  --transmission automatic \
  --max-price 100000 \
  --html ../configuration-shortlist.html
```

The generated HTML contains the complete active configuration snapshot for the selected `--as-of` date. Criteria supplied on the command line become the initial browser state. Clearing the form restores the complete embedded snapshot.

JSON, Markdown and CSV remain server-side filtered outputs. They can be generated together with HTML in one command.

## Embedded catalog

The browser file contains:

- every active configuration with model, version, powertrain and transmission metadata;
- the current Polish catalogue gross price, date and source or an explicit missing state;
- the recorded seat count, date and source or an explicit missing state;
- every current equipment availability record with state, date and source;
- deterministic facets for models, versions, transmissions, powertrains, seat counts and equipment attributes;
- the normalized CLI criteria as the initial form state.

The catalog is escaped before embedding and is not added to the default JSON shortlist schema.

## Browser filters

The interface provides:

- free-text search over configuration, model, version and powertrain labels;
- multi-select model, version and transmission filters;
- case-insensitive powertrain fragments;
- minimum and maximum price filters;
- an exact seat-count filter;
- equipment required as standard or optional;
- equipment required specifically as standard;
- a full reset action;
- deterministic ordering by price, model, version and configuration code.

## Evidence semantics

Browser filtering preserves the CLI rules:

- missing prices, seat counts and equipment statements never satisfy constrained criteria;
- missing equipment statements remain distinct from `not_available`;
- optional equipment satisfies a general requirement but not a standard-only requirement;
- the interface reports non-exclusive exclusion reasons and missing-statement counts;
- every displayed price, seat value and selected equipment state retains provenance.

## Drift prevention

The browser filter is a separate testable JavaScript module embedded verbatim into the HTML. CI executes representative metadata, price, seat, equipment, standard-only and missing-statement scenarios in Node.js and compares result codes and audit summaries with the Python engine over the same fixture.

## Delivery

The `Configuration Shortlist HTML` workflow publishes:

- a full interactive 53-configuration browser;
- an interactive browser initialized to automatic configurations priced at no more than 100,000 PLN;
- a SHA-256 artifact manifest.

Both files are deterministic, responsive, printable and contain no external scripts, stylesheets, fonts, analytics or network dependencies.

## Scope boundary

The package does not add ranking, weighted preferences, financing, total-cost calculations, fuzzy synonyms, market conversion, persistence, URL sharing or direct comparison of selected configurations.
