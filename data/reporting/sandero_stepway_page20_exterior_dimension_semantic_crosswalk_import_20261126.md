# Sandero Stepway — page 20 exterior-dimension crosswalk and import

- Report ID: `sandero_stepway_page20_exterior_dimension_semantic_crosswalk_import_20261126`
- Source: official Polish Sandero Stepway brochure, 2026-02-02, page 20
- Scope: five exact source-linked Eco-G 120 configurations
- Result: 15 new historical scalar observations across three attributes

## Imported observations

| Attribute | Value | Configurations | New rows |
|---|---:|---:|---:|
| Front track | 1520 mm | 5 | 5 |
| Rear track | 1509 mm | 5 | 5 |
| Ground clearance | 200 mm | 5 | 5 |

## Reused existing observations

- Overall length 4102 mm, wheelbase 2604 mm, front overhang 833 mm and rear overhang 665 mm were already present for all five configurations from exact configuration PDFs dated 2026-06-26.
- Roof height with rails 1586 mm and body height without rails 1535 mm were already present for all five configurations from saved configuration PDFs dated 2026-08-09.
- Overall width with mirrors 2012 mm was already present for all five configurations from exact configuration PDFs dated 2026-06-26.

## Deferred semantic conflict

The 1853 mm width label is not imported. Existing configuration PDFs record `overall_width=1784 mm`, while another source describes 1853/2012 mm as folded/unfolded exterior-mirror width. The diagram's mirror-state semantics require visual reconciliation before assigning 1853 mm to `overall_width`.

## Exclusions

Interior top-view values 1408, 1406 and 1026 mm and 14° seatback angles remain excluded.

Only the five exact Eco-G 120 configurations linked to this brochure are covered. No TCe 110 or Hybrid 155 applicability is inferred.

## Report metadata

- Report ID: sandero_stepway_page20_exterior_dimension_semantic_crosswalk_import_20261126
- Generated: 2026-11-26T22:05:00Z
- Analysed commit: c08d93156f3977cd4ba1ce0ad96cbc9e90bfcd57
- Status: current
- Scope: Page-20 exterior-dimension crosswalk and append-only import of three verified missing attributes for five exact source-related Eco-G 120 configurations.
