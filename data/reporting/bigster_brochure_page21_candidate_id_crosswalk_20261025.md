# Bigster brochure page 21 — candidate-ID crosswalk and closure gate

- Reviewed: 2026-10-25
- Source receipt: `src_pl_bigster_brochure_20251210`
- Source file: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- Source SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Printed page: 21; grade order: Essential / Expression / Journey / Extreme.
- Legend visually checked: `•` standard, `○` optional, `-` unavailable. Some extracted candidate text uses `¤` for the optional marker; the original candidate evidence is preserved unchanged.
- Status: visual row crosswalk; not an approved data import.

## Rows with visually confirmed grade applicability

| Row | Candidate ID | Essential | Expression | Journey | Extreme | Dictionary / decision |
|---|---|---|---|---|---|---|
| Rear tinted windows | `ae840ef24eb966f561f97265fdbf7a88256425dd1f9e722352cc408cae923381` | unavailable | unavailable | standard | standard | Existing candidate group `tinted_rear_windows`; use only if attribute scope matches rear glazing exactly. |
| Fixed roof rails | `919a22fcf13ca5f5b40fe96b28a731cceaad06559feb5eea379ba81921b7b53d` | standard | standard | standard | unavailable | Group `fixed_roof_rails`; keep distinct from modular rails. |
| Modular roof rails | `14d7a636eab9a3504352392d818d912c61c34ee3049679528163aed2821da8a6` | unavailable | unavailable | unavailable | standard | Group `modular_roof_rails`; not interchangeable with fixed rails. |
| Rear bench 1/3–2/3 split-fold | `41d1099bffd5ab0f2e916371ed7bad1947df6b90e7c4d1daa2070bd8716cd26e` | standard | unavailable | unavailable | unavailable | Group `rear_bench_1_3_2_3`; do not merge with the separate Easy Fold 40/20/40 row. |
| Rear bench Easy Fold 40/20/40 | `2cff5507638aed0bdbe57497ed19e1bbba3853f6038a8ee570b2f5e666e3651a` | unavailable | standard | standard | standard | Group `rear_bench_easy_fold`; exact fold geometry is material. |
| Driver seat height adjustment | `d173512d134f441a20a9e6d2f3cd57108c89da4fd7f32991c7ab692009e734de` | standard | standard | standard | standard | Group `driver_seat_height`; likely dictionary fit, but candidate signature still must be resolved. |
| Driver lumbar adjustment | `1fffd8b9b046c91dc987dc923fc9de0d8c7a780894e7558286f22dc0a8996b5d` | unavailable | standard | standard | standard | Group `driver_lumbar_adjustment`; do not infer passenger lumbar support from this row. |
| Passenger seat height adjustment | `2d2e916ea8403b95067f8f369f74c1fbc690d2e401e323de79ffbc388690fc8d` | unavailable | standard | standard | standard | Group `passenger_seat_height`; separate from driver seat. |
| Tyre-pressure monitoring | `0c3285c5a991dc6c1f5fdd4e634adbc49f9b4f089deb456bb51c4619a974885d` | standard | standard | standard | standard | Group `tyre_pressure_monitoring`; standard in all four grades in this brochure. |
| ISOFIX on outer rear seats | `baf6d2698208ca43d53c9a56abfd4725259b6e14832bbfb712157b09171df106` | standard | standard | standard | standard | Group `isofix_rear_outer`; preserve outer-rear-seat scope. |
| Cruise control and limiter operated from steering wheel | `142` line in chunk 3; candidate `3b98e962949c92710a3f8f0746900a85cc153421ece34992a08e1536cd02e1ea` is a different source group; do not use as a row ID | standard | standard | standard | standard | Candidate ID must be copied from the exact cruise-control row in chunk 3 before any mapping; no inference from line number. |
| Adaptive cruise control | See exact candidate in page-21 chunk 3 | unavailable | unavailable | unavailable | unavailable | This brochure matrix is source-specific. Preserve this historical brochure state even if a later price list differs. Exact candidate ID still needs extraction from the chunk. |
| Spare wheel option | Footnote candidate `51d53bd074a97dbd6479b2fdce7f528b530eb385deed469b3b1142c9df89fbc6` is not the wheel row; see page-21 chunk 3 | powertrain-qualified | powertrain-qualified | powertrain-qualified | powertrain-qualified | Keep the mild-hybrid-G 140 restriction and “replaces tyre repair kit” footnote attached to the option. Do not promote the footnote ID as a feature-row ID. |

## Fast closure rules

1. The 107 page-21 fragments are now visually grouped into rows, but the authored chunks report zero attached evidence signatures and zero attached evidence records. Therefore no new observations can be safely promoted into `data/imports` from these chunks alone.
2. Do not spend another cycle re-describing already aligned rows. For each row, either (a) resolve the exact configuration signature against the source receipt and current import contracts, or (b) close it as blocked by missing signature evidence / dictionary gap / source conflict.
3. Never use a candidate's line number as an ID. Never use a context-only fragment as the row-state record. Never reuse July 2026 price-list evidence to prove December 2025 grade applicability.
4. Do not modify `data/master` or approved import specs until exact configuration signature, source period, marker state and attribute scope all match.
5. Once the remaining page-21/page-22 candidate IDs are reconciled in one batch, run Quality and the reporting/release workflows; only then decide whether the brochure package is ready to close.

## Project-speed decision

This artifact intentionally consolidates verified row readings and explicit blockers instead of creating one file per row. Remaining work is narrowed to signature resolution and dictionary fit, not repeated source-text review. This crosswalk itself does not approve an import or claim the brochure is fully assimilated.
