# Configuration Comparison Workbook Export

## Status

`ACTIVE`

## Goal

Add one deterministic, source-aware XLSX workbook to every transactional configuration comparison bundle without changing comparison semantics or reporting-scope isolation.

## Delivered contract

- one `configuration-comparison-workbook.xlsx` per bundle;
- six fixed sheets: `Overview`, `Scopes`, `Configurations`, `Comparisons`, `Sources`, `Artifacts`;
- complete `equal`, `different` and `not_comparable` comparison rows;
- typed integer, decimal, boolean and ISO-date cells;
- separate range endpoints and inclusivity flags;
- configuration, source, evidence and companion-artifact provenance;
- singleton scopes without artificial comparison rows;
- final workbook path, byte size and SHA-256 in the external bundle manifest;
- no formulas, macros, charts, hidden sheets, external links, ranking, recommendations or inferred values.

## Implementation

The workbook uses a repository-owned OOXML writer built from the Python standard library. It writes inline strings, fixed relationships, fixed core properties and `ZIP_STORED` entries with deterministic order, timestamps and permissions. This keeps the existing dependency-free toolchain and allows byte-identical output across Linux and Windows.

A matching readback parser validates the supported cell subset in regression tests. The writer is private to this fixed workbook contract and is not intended as a general spreadsheet library.

## Verified fixture

The dedicated workflow uses five selected configurations across three independent scopes:

- two Sandero Stepway Eco-G 120 automatic configurations;
- two Jogger Eco-G 120 automatic configurations;
- one Duster Eco-G 100 singleton.

The resulting workbook contains:

- 3 scope rows;
- 5 configuration rows;
- 203 comparison rows;
- 4 referenced source rows;
- 8 companion-artifact rows;
- 170 equal, 19 different and 14 not-comparable comparison states.

Both Linux and Windows generate byte-identical workbook files, and a separate verification job compares their bytes, SHA-256 values and six-sheet order.

## Validation

- 12 dedicated workbook regression tests;
- updated bundle regression contract including XLSX publication;
- independent opening with the repository readback parser and external `openpyxl` inspection during development;
- fixed ZIP metadata and absence of volatile workbook timestamps;
- manifest parity for path, size and SHA-256;
- transactional cleanup when workbook generation fails;
- dedicated Ubuntu/Windows cross-platform workflow.

## Boundary

This package does not change source data, active configurations, completeness specifications, evidence decisions, pair generation, comparison states, shortlist semantics or scope grouping.
