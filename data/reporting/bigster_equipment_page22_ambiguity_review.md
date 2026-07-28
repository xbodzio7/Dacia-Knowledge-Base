# Bigster Equipment Page 22 Ambiguity Review

Authored review of `residual_gap_009`. Climate, console and Winter-package row boundaries are preserved; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 7 |
| Covered | 3 |
| Partially covered | 4 |
| Selected evidence signatures | 18 |
| Selected evidence records | 126 |
| Rejected attached signatures | 0 |

## Candidate decisions

| Line | Candidate | Decision | Signatures | Records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 22 | `f8361f7eaf42bbf01040e78423f7190b9de86d9aff2ae02d12bae1666a3330ba` | `covered` | 2 | 14 | complete manual-air-conditioning row |
| 24 | `1aad4a730531585a37da9d3c73eb9115f9cca5a2eddd495d54e7a01e83f679a8` | `partially_covered` | 6 | 42 | first line of the dual-zone automatic-climate row with rear vents |
| 29 | `01f11f75e7390b17ccd40b4d46b23c55cb30ebfb71fdb6f292c07ae977b2f528` | `covered` | 2 | 14 | complete electrically folding mirrors row |
| 40 | `ad2df36a0dce4c4d725438894b52fd307695f3bd0cab142a509be8aa67859473` | `partially_covered` | 2 | 14 | first line of the centre-console-with-armrest-and-storage row |
| 48 | `4119069370e836ed8bf21cc28b8e9c5a9d889d4abbbfe789c1c9c229fb1d2d34` | `covered` | 2 | 14 | complete wireless-charging row |
| 97 | `e114af3d6918ae90c0ad19482028be640e718e50f989a1c282e0473f16759684` | `partially_covered` | 2 | 14 | final line of the Winter package row |
| 100 | `be9a3c17edaa4a791a8cbec07a987499acd8691f37c0712c06f5434d9f519437` | `partially_covered` | 2 | 14 | final line of the Winter Plus package row |

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- `•`, `¤` and `-` remain standard, optional and unavailable respectively;
- multi-line labels are reviewed as one visual row without inventing new attributes;
- Winter-package components do not inherit standard status from other trims or records;
- climate functions and centre-console variants remain separate attributes inside their visual rows;

## Next package

**Jogger Equipment Page 20 Ambiguity Review** — Review the 5 ambiguous equipment candidates from Jogger brochure page 20 against their 10 preserved evidence signatures without creating master-data rows or approved import specifications.
