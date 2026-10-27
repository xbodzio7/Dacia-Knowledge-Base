# Interactive Selection Export Planning Review

## Decision status

`SELECTED — PERSISTENT BROWSER SELECTION WITH BUNDLE-COMPATIBLE EXPORT`

The next package will extend the interactive configuration shortlist with explicit selection controls. Selected configurations will remain independent of the current filter view and can be exported as deterministic shortlist JSON or a plain code list. The existing comparison bundle remains the only component that creates comparison reports.

## Selection model

The browser will maintain a set of selected configuration codes:

- each visible result card has an explicit checkbox;
- filtering never selects or deselects a configuration automatically;
- changing filters does not discard hidden selections;
- `Select visible` adds the current result set to the selection;
- `Clear selection` removes every selected code;
- selected codes are displayed in a persistent summary area with individual remove controls;
- the selected count distinguishes all selected configurations from the currently visible subset;
- ordering follows the deterministic catalog order used by the shortlist engine.

This model avoids silently replacing an intentional selection when the user adjusts price, equipment or metadata criteria.

## Export formats

The browser will provide two offline downloads.

### Bundle-compatible shortlist JSON

The JSON document will contain:

- `version: 1`;
- `export_type: interactive_configuration_selection`;
- the source snapshot `as_of` date;
- a selection summary;
- `results[]` ordered by the catalog order;
- one result object per selected configuration containing at least `configuration_code`, model, version, powertrain, transmission and current price metadata.

The existing comparison bundle already consumes `results[].configuration_code` and ignores compatible additional fields. No bundle parser change is required.

### Plain configuration code list

The text export will contain one exact configuration code per line in the same deterministic order. It is intended for review, shell scripts and repeated `--configuration-code` inputs.

Neither export contains a runtime timestamp. The same snapshot and selected set therefore produce byte-identical content.

## Browser behavior

- export actions are disabled when the selection is empty;
- filenames include the snapshot date and selected count;
- downloads use browser-native Blob and object URL APIs and require no network connection;
- the selected tray remains visible while browsing and filtering;
- reset of search criteria does not reset the selection;
- clearing the selection does not change active filters;
- selection changes do not alter evidence, unknown-state or exclusion summaries.

## Testing contract

The implementation will expose pure JavaScript helpers for:

- normalizing selected codes against the embedded catalog;
- ordering selections by catalog order;
- building the JSON export payload;
- rendering the plain code list;
- producing deterministic filenames.

CI will execute these helpers in Node.js and verify:

- deterministic output;
- duplicate and unknown-code handling;
- persistence across filter changes;
- visible-selection union behavior;
- exact compatibility with the Python bundle parser;
- empty-selection behavior;
- safety of exported metadata strings.

## Scope boundary

The package will not:

- generate comparison reports in the browser;
- upload files or call network services;
- persist selections between browser sessions;
- encode selections in URLs;
- rank, score or recommend configurations;
- infer missing values;
- automatically select all matches after every filter change.

## Implementation target

The next package is **Interactive Configuration Selection Export**, with browser card selection, persistent selected-summary controls, deterministic JSON and text downloads, Node.js regression coverage, workflow artifacts, documentation and canonical project-state synchronization.
