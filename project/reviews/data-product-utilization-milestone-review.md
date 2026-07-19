# Data Product Utilization Milestone Review

## Decision status

`COMPLETE`

The first data-utilization milestone is complete. Five user-facing products now form one source-backed offline workflow from configuration discovery to explicit selection and homogeneous comparison reporting.

## Product inventory

| Product | Delivery | User outcome | Stable contract |
| --- | --- | --- | --- |
| Interactive Configuration Comparison HTML | PR #143 | Open and filter a complete comparison report without a server | Existing comparison states, source provenance and offline HTML |
| Configuration Shortlist CLI | PR #145 | Filter all active configurations by model, version, powertrain, transmission, price, seats and equipment | JSON, Markdown and CSV with explicit unknown and exclusion reporting |
| Interactive Configuration Shortlist HTML | PR #147 | Browse the complete 53-configuration snapshot in a browser | JavaScript/Python filter parity and no external resources |
| Configuration Comparison Bundle CLI | PR #149 | Turn explicit selections into reports inside independent reporting scopes | Transactional JSON, Markdown, CSV and HTML outputs with SHA-256 manifest |
| Interactive Configuration Selection Export | PR #151 | Persist selections independently from filters and download bundle-compatible inputs | Deterministic JSON and TXT export with no runtime timestamp |

## End-to-end workflow

The verified user workflow is:

1. generate a complete shortlist browser with `configuration-shortlist --html`;
2. filter the 53 active configurations without changing source semantics;
3. explicitly select visible or individual configurations;
4. download deterministic shortlist JSON or exact configuration codes;
5. pass the JSON to `configuration-comparison-bundle`;
6. receive separate reports only for homogeneous groups with at least two configurations;
7. review singleton groups and the bundle manifest without cross-scope comparisons.

The current catalog maps all 53 active configurations exactly once to 13 independent reporting scopes. The workflow never generates cross-scope pairs, rankings, recommendations, inferred values or network requests.

## Verified quality baseline

The milestone closes with:

- 628 automated tests;
- Python 3.10, Python 3.13 and Windows package-state validation;
- dedicated workflows for shortlist, shortlist HTML, selection export, comparison HTML and comparison bundle;
- regression workflows for both Sandero scopes and all four Jogger scopes;
- deterministic offline artifacts with source provenance and SHA-256 manifests.

## Remaining user friction

The workflow is complete but its outputs are distributed across JSON, Markdown, CSV, HTML and manifest files. Users who work primarily in office software must open several artifacts or manually assemble tables before sorting, annotating and sharing a review.

The repository backlog already identifies Excel export as the next stable external format. It can reuse existing shortlist rows, flat comparison differences, scope summaries and provenance without changing data or comparison semantics.

## Options considered

| Option | Value | Boundary assessment | Decision |
| --- | --- | --- | --- |
| Configuration comparison workbook | High: one portable review surface for summary, configurations, differences and provenance | Reuses existing reports; requires an explicit sheet and dependency contract | **Select for planning** |
| Persist browser selection between sessions | Medium | Requires browser storage and lifecycle semantics not needed for the completed offline handoff | Defer |
| Encode selection in URLs | Medium | Adds URL-size, privacy and compatibility contracts | Defer |
| Cross-model or cross-powertrain comparison | Unclear | Would merge currently independent denominators | Reject for this milestone |
| Ranking or recommendations | Unclear | Requires scoring and preference semantics absent from source data | Reject for this milestone |

## Next package

The next package is **Configuration Comparison Workbook Export Planning Review**.

It must decide, before implementation:

- whether the workbook is generated per comparable scope, per bundle or both;
- the minimum sheet set and column contracts;
- how summary, configurations, differences, singleton groups and source provenance are represented;
- how deterministic ordering, dates, decimals, ranges and unknown states are preserved;
- whether XLSX generation uses an explicit dependency or a repository-owned minimal writer;
- how workbook contents and checksums are tested across Python and Windows.

The planning review must not introduce new source data, cross-scope comparisons, scoring, recommendations or inferred values.
