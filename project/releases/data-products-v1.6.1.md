# Data Products v1.6.1 Publication

Date: 2026-07-24

## Published identity

- GitHub Release: `data-products-v1.6.1`
- Release ID: `359532111`
- Published at: `2026-07-24T20:30:34Z`
- Exact tag target and source commit: `4b77571c788b862a6543161b9343a35f464bd7c6`
- Source Pull Request: `#236`
- Verified Pull Request head: `8dce2a3f6ccbeb563fb9532c7b86c36d294735bf`
- Quality workflow: `#1275`

The tag resolves exactly to the squash-merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Asset ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `SHA256SUMS` | `488795807` | 213 bytes | `f8a402f879ab3410af5c2d1840ced4ab6abec517b7d344b6e248c27d6725821a` |
| `dacia-knowledge-base-data-products-v1.6.1.zip` | `488795809` | 46,477,840 bytes | `0dd8da53b5ccdb7030040c669d4f32ac80e6fa34ec6b1910d81af5c77d13359a` |
| `data-product-release-manifest.json` | `488795810` | 19,154 bytes | `6f40676d3f8771f63b9240accc3bb73975b5f7d3da8f3cb233c737e0aa777d7f` |

GitHub's recorded API digests match the independently calculated SHA-256 values for all three downloaded assets.

## Release contents

- 69 active configurations;
- 18 independent comparison scopes;
- 79 deterministic archive members;
- 88 source-backed technical comparison facets;
- 109 equipment facets;
- five official Dacia Polska model-media entries with offline SVG fallbacks;
- equipment-list search that visibly hides non-matching entries;
- selected equipment preserved until explicit user removal;
- only source-complete compatible additions exposed after each selection;
- mutually exclusive alternatives hidden while the active choice remains selected;
- incomplete cross-model option data preserved as unknown rather than unavailable.

## Consumer verification focus

The user-visible regression scenarios for this patch are: searching the equipment list for `ABS`; selecting the 10.1-inch colour instrument cluster and confirming the incompatible 3.5-inch TFT alternative disappears; and selecting LED cabin lighting without allowing a later lighting choice to clear it automatically. Duster options with incomplete evidence must remain hidden or unknown rather than being labelled unavailable.

## Published-browser audit

The exact `shortlist/configuration-shortlist.html` member extracted from the public release archive was audited after re-downloading the asset from GitHub Release. The embedded catalogue still contains 69 configurations, 88 technical comparison facets, 109 equipment facets and five official model-media entries.

The audit confirmed the `hidden` CSS override used by equipment search, the `selection_conflict` and `addable_equipment` contracts, and the user-facing statement that the system does not deselect filters automatically. It also proved that the previous automatic-selection removal calls are absent from the published HTML.

## Verification

All 15 source Pull Request workflows passed on the final source head, including 719 tests, Windows, HTML, workbook, comparison, selection-export and versioned-release verification.

The public assets were then downloaded again from the published GitHub Release and accepted by `data-product-release --verify`. Exact sizes, SHA-256 values, GitHub API digests, tag target, release status, archive membership and published browser payload were independently audited. Publication audit result: `PASS`.

## Data boundary

This patch changes browser interaction only. It does not add, infer or reclassify Duster, Jogger, Sandero, Sandero Stepway or Bigster options. Missing cross-model option records remain unknown until a separate official-configurator source import proves their status.

## Immutability

The release assets and tag are immutable. Later corrections or source-backed data extensions must use a new semantic version and must not replace or rewrite `data-products-v1.6.1`.
