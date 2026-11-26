# Interactive Configuration Selection Export

## Goal

Allow users of the offline configuration shortlist to build an explicit, persistent set of configurations and export it directly into the existing comparison bundle workflow without changing filter, evidence or comparison semantics.

## Selection behavior

Every rendered configuration card receives a `Wybierz do porównania` checkbox. The browser stores selected configuration codes independently from the active shortlist filters.

- changing filters never selects or deselects automatically;
- hidden selections remain selected;
- `Wybierz widoczne` adds the current result set to the existing selection;
- each selected item can be removed individually;
- `Wyczyść wybór` removes all selections without changing filters;
- selected items remain ordered by the deterministic catalog order.

The selected-summary panel is persistent while browsing and displays both the selected count and each selected configuration.

## Bundle-compatible JSON

`Pobierz JSON` creates a deterministic document containing:

- `version: 1`;
- `export_type: interactive_configuration_selection`;
- the embedded snapshot `as_of` date;
- selected and catalog configuration counts;
- ordered `results[]` entries;
- configuration, model, version, powertrain and transmission metadata;
- the current price and seat states with provenance.

The document has no runtime timestamp. The same snapshot and selected set therefore produce byte-identical output. The existing comparison bundle consumes `results[].configuration_code` directly and safely ignores the additional display metadata.

## Plain code export

`Pobierz kody TXT` writes one exact configuration code per line in the same deterministic order. It is suitable for review, scripts and repeated `--configuration-code` arguments.

Both download actions are disabled for an empty selection. Filenames include the snapshot date and selected count.

## Offline delivery

The selection module is embedded in the existing self-contained shortlist HTML. It uses browser-native Blob and object URL APIs and requires no server, upload, external dependency or network connection.

All metadata is written using DOM text nodes or JSON serialization. Data-derived strings are never inserted as executable markup.

## Testing contract

Eight regression tests verify:

- deterministic catalog ordering;
- duplicate and unknown-code normalization;
- persistent union with visible results;
- individual removal;
- deterministic JSON and text content;
- empty-selection output;
- direct consumption by the Python comparison bundle parser;
- presence of all offline selection controls in the generated HTML.

The `Configuration Selection Export` workflow executes the complete path:

1. generate a full shortlist browser;
2. generate the automatic-under-100000 PLN shortlist;
3. use the JavaScript selection module to export four selected configurations;
4. consume that JSON with `configuration-comparison-bundle`;
5. verify two comparable scopes, no singleton and no cross-scope pair;
6. publish the browser, JSON, text, comparison bundle and SHA-256 manifests.

## Scope boundary

The package does not generate comparisons in the browser, persist selections between sessions, encode selections in URLs, upload data, call network services, rank configurations, score preferences, recommend vehicles or infer missing values.
