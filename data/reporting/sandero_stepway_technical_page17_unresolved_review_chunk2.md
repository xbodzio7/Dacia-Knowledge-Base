# Sandero Stepway Technical Page 17 Unresolved Review — Chunk 2

Authored review of `residual_gap_023`. The remaining 9 candidates complete the 49-candidate Sandero Stepway page-17 technical group. They contain only mass-label fragments and the continuation of the WLTP explanatory footnote; the review does not approve imports.

## Summary

- candidates: 9 of 49 (chunk 2 of 2);
- visual groups: 4;
- `unresolved_signature_mismatch`: 0;
- `context_only_non_import`: 9;
- attached evidence signatures: 0;
- attached evidence records: 0.

## Source boundary

- source: `src_pl_sandero_stepway_brochure_20260202`;
- archived file: `PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf`;
- SHA-256: `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`;
- page: 17;
- mass columns: `TCe 110`, `120 Eco-G`, `120 Eco-G auto`.

No candidate in this chunk contains an aligned numeric mass value. The visible source-page values are retained only as review context and are not promoted to observations. The four WLTP continuation lines remain explanatory text.

## Candidate decisions

| # | Line | Candidate | Group | Decision | Exact text |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 86 | `db442cee20bca774f9f050ee825bc3a10600dfc6d28eb74eb2d8432de1368509` | `gross_combination_mass_label` | `context_only_non_import` | (DMC) zespołu pojazdów |
| 2 | 87 | `8d7d6482d14a5c864b665e78037751b578c6f18d06136b2d5fb991645ebf87a9` | `gross_vehicle_mass_label` | `context_only_non_import` | Dopuszczalna masa całkowita |
| 3 | 89 | `5e1c26d151720f1715ccccbca806e515ce08ddd64baffcb5e913e4cd8e75b323` | `gross_vehicle_mass_label` | `context_only_non_import` | (DMC) pojazdu |
| 4 | 90 | `12e7cf531cf25d1430da348c2cd6fd93733a27faf0a7f3d34dd91b4da13a4e9a` | `maximum_braked_trailer_mass_label` | `context_only_non_import` | Maksymalna masa całkowita |
| 5 | 92 | `9d77cafe7d4e5b1d4d728d3e47dd96a8301951800a364c664fce170f28b0da46` | `maximum_braked_trailer_mass_label` | `context_only_non_import` | przyczepy hamowanej |
| 6 | 99 | `a007994d7f70d85f6bc5e45d6e05b71373c72892d8ae2492adaff8586be2adef` | `wltp_method_footnote` | `context_only_non_import` | Procedures): nowy protokół, który w porównaniu z protokołem NEDC umożliwia uzyskanie wyników bardziej zbliżonych |
| 7 | 100 | `c423795dcd570b4afe1108733a879a865aa02708a98e61d25b520874a330aa56` | `wltp_method_footnote` | `context_only_non_import` | do wyników obserwowanych w rzeczywistych warunkach eksploatacji. Wartości emisji CO2 są homologowane zgodnie ze |
| 8 | 101 | `d06ff1b3887aa4dc6c80941455a11a2221582e4a0554c8b35d4cf15d19a06564` | `wltp_method_footnote` | `context_only_non_import` | standardową metodą pomiaru, określoną w obowiązujących przepisach. Metoda jest identyczna dla wszystkich producentów, co |
| 9 | 102 | `cf26bb2e12673b1a0e6952d976d2cc23cfc5cc0460ed99cf4acd696182c3673d` | `wltp_method_footnote` | `context_only_non_import` | umożliwia porównanie różnych modeli. |

## Review-only source context

The complete visual mass section prints one value per powertrain, rather than separate LPG and petrol subcolumns:

- minimum ready-to-drive mass: `1095`, `1194`, `1222` kg;
- maximum ready-to-drive mass: `1149`, `1225`, `1249` kg;
- gross combination mass: `2685`, `2760`, `2785` kg;
- gross vehicle mass: `1585`, `1660`, `1685` kg;
- maximum braked-trailer mass: `1100`, `1100`, `1100` kg.

These values clarify the visual row boundaries but do not create evidence-backed observations because the residual package contains no attached signature or record and its candidates are label fragments only.

## Milestone review

The five packages since the previous milestone covered both Duster technical pages 20 and 21 and the first Sandero Stepway page-17 chunk. They preserved the existing authored-review, zero-evidence and no-import boundaries. No new domain, schema or architecture decision is required, and a separate review-only Pull Request would add no value.

## Safety boundary

- no change under `data/master` or `data/imports`;
- no selected evidence and no automatic promotion;
- label fragments are not converted into mass observations;
- values visible elsewhere in the source row are review context only;
- WLTP explanatory text is not promoted to a specification or availability record;
- prior chunk decisions remain unchanged.

## Next package

**Jogger Technical Page 19 Unresolved Review — Chunk 1** (`residual_gap_024`), covering the first 40 of 43 candidates.
