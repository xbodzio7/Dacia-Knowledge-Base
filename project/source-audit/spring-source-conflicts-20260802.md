# Spring documentary-source conflict register

Audit date: 2026-08-02

This register prevents dated documentary states from being flattened into one timeless configuration value.

## C-001 — domestic cable and Type 2 cable

| Source state | Domestic-socket cable | Type 2 cable |
| --- | --- | --- |
| Brochure, published 2026-02-19, pages 13 and 20 | standard for Essential, Expression and Extreme | optional for Essential, Expression and Extreme |
| MY2025 stock price list, effective 2026-07-08, page 4 | optional, 1500 PLN for Expression and Extreme | standard for Expression and Extreme |
| Exact saved MY2026 configurations, observed 2026-08-02 | no selected domestic cable shown | standard in Expression 70 and Extreme 100 |

Classification: **temporal/model-year commercial conflict**.

Rules:

1. Do not overwrite one source with another.
2. Do not infer unavailability from a saved configuration that omits an unselected option.
3. Preserve publication/effective date, model year and stock/current-configurator context.
4. Current master commercial mappings introduced from the July price list remain valid only with their source/date context; they do not invalidate the February brochure state.

## C-002 — internal price-list contradiction

The July price list page 2 prose describes the Type 2 cable as available in option. Page 4 exact matrix, read with its legend, marks Type 2 standard for both listed grades.

Classification: **internal source contradiction**.

Resolution boundary:

- for exact commercial availability in this price list, use page 4 matrix and legend;
- retain page 2 prose as a documented contradiction;
- do not silently edit or paraphrase the source into consistency.

## C-003 — brochure grade narrative versus exact matrix

The brochure grade pages use prose labels and may omit package dependencies. Pages 19–20 provide the exact three-column matrix and legend.

Classification: **precision hierarchy within one source**.

Resolution boundary: exact page-19/20 matrix cells govern availability classification for the brochure context; grade pages remain supporting descriptions.

## C-004 — brochure versus later MY2026 saved configurations

The February brochure describes the earlier grade structure, including Essential and charging-cable states that differ from the exact August MY2026 saved configurations.

Classification: **dated range evolution**.

Resolution boundary: facts may be imported only as dated observations or into configurations explicitly proven to share the relevant model-year/range state.

## Consequence for this package

This audit package changes no master value solely to reconcile these conflicts. Corrective migrations must be bounded by source, date, model year and exact configuration applicability. Where the current schema cannot preserve that context, the item remains deferred rather than guessed.
