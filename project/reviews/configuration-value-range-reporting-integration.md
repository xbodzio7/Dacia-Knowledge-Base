# Configuration Value Range Reporting Integration

## Status

`IMPLEMENTED`

This package integrates the approved separate range table with technical
completeness, source coverage and pairwise configuration comparison. It imports
no source data and does not change the scalar table.

## Latest-observation selection

For each configuration, attribute and fuel context, reporting selects the latest
observation across the scalar and range tables. A scalar and range row on the
same date is rejected as a semantic collision. Historical changes from one
shape to the other remain representable.

Legacy test fixtures without the range CSV are treated as having no ranges.
The canonical repository validator still requires the table.

## Completeness

A current range observation satisfies the same technical slot as a current
scalar observation. It remains incompatible with a `not_applicable` decision and
must use the source mapped to the configuration.

## Source coverage

Range observations:

- participate in as-of date resolution;
- count as present technical evidence;
- preserve source-to-configuration checks;
- appear in observation-date summaries;
- are included in out-of-scope source-record diagnostics.

## Pairwise comparison

Scalar-only comparisons retain their existing output. When either recorded side
is a range, the technical item adds `range_relation`:

- `identical` — same endpoints and endpoint inclusivity;
- `overlapping` — the intervals share at least one included value;
- `disjoint` — the intervals share no included value.

`identical` maps to the existing `comparison=equal`. `overlapping` and
`disjoint` map to `comparison=different`, preserving existing aggregate counters.
A scalar point is treated as a closed, zero-width interval when compared with a
range.

Range values render in Markdown and difference CSV using interval notation:
`[minimum,maximum]`, `(minimum,maximum]`, `[minimum,maximum)` or
`(minimum,maximum)`.

## Evidence boundary

This package does not:

- import any Jogger range;
- alter scalar values or existing range validation;
- average, midpoint or otherwise collapse endpoints;
- change the meaning of existing comparison counters.

## Expected baseline

After implementation:

- 520 tests;
- 37 master CSV files and 3,845 rows;
- 1,204 scalar configuration values;
- 0 range observations;
- 71 scalar import specifications;
- 1,811 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger WLTP Efficiency Range Import Selection** will define the first bounded
set of fuel-consumption and CO2 ranges, exact configuration/fuel context and
source-text denominator before materialization.

## Local validation

The package passed 520 tests, canonical-state verification and the complete
local Quality gate before removing its temporary workflow. The final branch
contains no temporary workflow or diagnostic artifact, and scalar-only generated
reports retain their established comparison counters and values.
