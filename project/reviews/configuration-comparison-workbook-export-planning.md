# Configuration Comparison Workbook Export Planning Review

## Decision status

`COMPLETE`

The next implementation package will add one deterministic XLSX workbook to each configuration comparison bundle. The workbook is a presentation surface over existing reports and does not create new comparisons, values, denominators or evidence classifications.

## Product boundary

- One bundle produces one `configuration-comparison-workbook.xlsx`.
- The workbook is written inside the existing transactional bundle directory.
- The bundle manifest records its relative path, byte size and SHA-256 after generation.
- Comparable scopes contribute their complete JSON comparison reports.
- Singleton scopes remain visible without artificial pair rows.
- Existing JSON, Markdown, CSV and HTML remain companion artifacts.
- No workbook may create a pair across independent scopes.

A bundle-level workbook is selected instead of one workbook per scope because it removes manual office-file assembly while preserving the 13-scope isolation contract.

## Fixed sheet contract

The workbook contains exactly six sheets in this order.

### `Overview`

Key/value metadata: workbook version, bundle version, selected configuration count, scope counts, comparable and singleton counts, total pairs and differences, report snapshot dates, manifest path and `cross_scope_pairs_generated = false`. It contains no runtime timestamp.

### `Scopes`

One row per scope, ordered by scope slug. Columns include status, source specification names, report date, configuration codes, pair and difference totals, domain summaries, evidence counts, report paths and report hashes. Singleton rows have zero pair counts and empty report-file fields.

### `Configurations`

One row per selected configuration, ordered by scope and configuration code. Columns include scope, group status, configuration code, model code and name, version code and name, powertrain, transmission and source code. Values are resolved from current master tables during the bundle transaction.

### `Comparisons`

One row per existing pair/domain/item result from every comparable scope. Rows are ordered by scope, pair code, domain order and current report item order. The sheet includes `equal`, `different` and `not_comparable` rows.

Columns preserve scope and report date; pair identifiers; domain, item, category, context, unit and range relation; both configuration identities; both states, data types, scalar values, range endpoints, inclusivity flags, source codes, observation dates, reason codes, reviewed pages and canonical evidence-basis JSON; and the existing price delta when present.

Integers and decimals use numeric cells, booleans use boolean cells, dates use date cells formatted `yyyy-mm-dd`, and text states remain text. Range endpoints remain separate and are never reduced to a midpoint.

### `Sources`

One row per referenced source code, ordered by code, reproducing registered source type, title, publisher, market, document date, external reference, repository path, registered SHA-256, status and notes.

### `Artifacts`

One row per companion bundle artifact, ordered by path, with owner scope, kind, relative path, byte size and SHA-256. The workbook's own final hash appears only in the external manifest to avoid self-reference.

## Spreadsheet behavior

- fixed sheet and row order;
- readable header rows;
- frozen header panes and auto-filters on tabular sheets;
- deterministic widths and wrapped long text;
- no formulas, charts, macros or hidden sheets;
- no value inference or spreadsheet-side recalculation.

## OOXML implementation decision

Quality currently installs no Python package dependency and validates Python 3.10, Python 3.13 and Windows. The fixed workbook feature set will use a small repository-owned OOXML writer based only on the Python standard library.

The writer will use deterministic XML, inline strings, fixed relationships and core properties, and fixed ZIP entry order, timestamps and permissions. Entries will use `ZIP_STORED` rather than deflate so the same input can produce identical bytes on Linux and Windows without depending on a zlib build. The writer is private to this workbook contract and is not a general spreadsheet library.

A third-party XLSX dependency is deferred unless a future approved package requires features outside this fixed contract.

## Validation contract

The implementation must verify:

1. required OOXML parts and six-sheet order;
2. readback through a repository-owned parser for the supported cell subset;
3. headers, filters, frozen panes and dimensions;
4. exact scope, configuration and comparison row counts;
5. preservation of equal, different, not-comparable, singleton and evidence states;
6. scalar types, ranges, inclusivity, dates and source codes;
7. source and companion-artifact parity;
8. absence of formulas and volatile timestamps;
9. byte-identical repeated generation;
10. identical SHA-256 on Linux and Windows for the same fixture bundle;
11. transactional cleanup on failure;
12. final workbook path, size and SHA-256 in the bundle manifest.

The dedicated workflow will generate at least two comparable scopes and one singleton, publish the XLSX with companion reports, and verify semantic counts and hashes.

## Rejected alternatives

- Per-scope workbooks: retain manual assembly and duplicate metadata.
- Differences-only workbook: hides equality and insufficient-evidence states.
- Formula-based summaries: add recalculation and application-version semantics.
- New third-party dependency: unnecessary for the fixed feature set and weaker for byte-level determinism.
- CSV with an XLSX extension: not a valid multi-sheet workbook.

## Next package

The next package is **Configuration Comparison Workbook Export**.

It will implement the fixed writer, renderer, bundle integration, manifest record, tests, workflow, documentation and state synchronization. It must not change data, comparison semantics, scope grouping, selection semantics, evidence classifications, ranking or recommendations.
