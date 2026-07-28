# Duster Mini Equipment Page 22 Ambiguity Review

Authored review of `residual_gap_008`. Multi-line safety and control rows, trim columns and option markers are preserved; the review does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 11 |
| Covered | 3 |
| Partially covered | 8 |
| Selected evidence signatures | 23 |
| Selected evidence records | 524 |
| Rejected attached signatures | 4 |

## Candidate decisions

| Line | Candidate | Decision | Signatures | Records | Row context |
| ---: | --- | --- | ---: | ---: | --- |
| 15 | `d2cd87ae3c3eca07f3fe8d82719a57c12be9fa806e8f50b17630197a2181524e` | `partially_covered` | 1 | 24 | first line of the automatic dipped-headlights row |
| 117 | `3bc148f177d5790ba3cbca9a714aad74af045db4527e846796f014f9f0fa6811` | `partially_covered` | 2 | 54 | first line of the combined ESC and hill-start-assist row |
| 118 | `e504a831e8ebda129fbcbaa2a27bd82a916fd1c8f27a5f777ed19063b90d0a4c` | `partially_covered` | 2 | 54 | availability-bearing middle line of the combined ESC and hill-start-assist row |
| 120 | `8f90c98b7a9e1b6c384b2f156b2e5035648a177a0417e41aec1498b1f012885c` | `partially_covered` | 3 | 72 | first line of the front/rear pretensioner row without height adjustment |
| 121 | `e5957ec575751dfcf18e5a9e21f5e26a0112aa75a4483467f7bbedf0c5da15e4` | `partially_covered` | 3 | 81 | availability-bearing middle line of the front/rear pretensioner row without height adjustment |
| 122 | `4bafe8134f33bfb85a91020706ddcfd101195d36c14e6101f8d1c140defd073c` | `partially_covered` | 3 | 81 | final line of the front/rear pretensioner row without height adjustment |
| 153 | `5962f79da4da74d4680112782476829ed627ddd91cca737527725f094aef95fa` | `partially_covered` | 2 | 27 | middle line of the 7-inch digital instrument-cluster row |
| 164 | `e8e19aa4e1de55306aff83b6261e273c67386748f1c8a0c37aa0534783f09734` | `covered` | 2 | 48 | complete speed-limiter and cruise-control row |
| 170 | `e8e92c334cfdb2f2476fc2ad204eb75925f5235325abcf7edd4762c868858980` | `covered` | 1 | 27 | complete rear-parking-sensor row |
| 173 | `25175fba71d23d4587ebeb4365f188e9ec7e0ba7ed1cd1d818962e42350713f6` | `partially_covered` | 2 | 29 | front-and-side parking-sensor row with option markers split across adjacent lines |
| 176 | `01325df6ea284632046d8257e9f1994fd542d4626c697d47d962916a74a78968` | `covered` | 2 | 27 | complete rear-view-camera row |

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- `•`, `¤` and `-` remain standard, optional and unavailable respectively;
- multi-line labels are reviewed as one visual row without inventing new attributes;
- option and package markers do not inherit standard status from later configuration records;
- rain-sensor, front-sensor and other adjacent-attribute evidence is rejected rather than substituted;

## Next package

**Bigster Equipment Page 22 Ambiguity Review** — Review the 7 ambiguous equipment candidates from Bigster brochure page 22 against their 18 preserved evidence signatures without creating master-data rows or approved import specifications.
