# Sandero Stepway Technical Page 17 Ambiguity Review

Authored review of `residual_gap_005`. Decisions preserve row, attribute and candidate boundaries and do not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 4 |
| Partially covered | 3 |
| Unresolved signature mismatch | 1 |
| Selected evidence signatures | 5 |
| Selected evidence records | 15 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 42 | `7174bea551651d0ef41e920ec1836f014de7a5a6f6cf4374ee9741c818b20423` | `partially_covered` | 1 | Układ kierowniczy – |
| 80 | `142dcad00906e420e554f558092509354e221a4a255e777e1a3394f8923b4968` | `unresolved_signature_mismatch` | 0 | gotowego do jazdy |
| 81 | `42122e7844285bbea37c05cd6bbd36f3e3e8c24f8ee740d6c8b53cf0a9767f3c` | `partially_covered` | 2 | Maksymalna masa pojazdu |
| 83 | `a53c392d018f9e1f8538c42625fa5f6a91c6f66bb144966f5c1f68e492d9292f` | `partially_covered` | 2 | gotowego do jazdy |

## Authored findings

### Line 42 — `7174bea551651d0ef41e920ec1836f014de7a5a6f6cf4374ee9741c818b20423`

The fragment starts the steering-system turning-circle label. Only the attached 10.64 m turning-circle signature belongs to this row; suspension, tyre and kerb-mass signatures belong to other labelled rows on the same page.
- `turning_circle_between_kerbs`: `10.64` — The value is printed on the following continuation line, so this label fragment is only partially covered by the selected evidence.

### Line 80 — `142dcad00906e420e554f558092509354e221a4a255e777e1a3394f8923b4968`

This continuation belongs to the minimum kerb-mass row (1095/1194/1222 kg), but both attached signatures are maximum kerb masses 1225 and 1249 kg from the following row. Cross-row substitution is rejected.
- `minimum_kerb_weight`: `1095`, `1194`, `1222` — The visual row has no matching evidence signature attached to this candidate.

### Line 81 — `42122e7844285bbea37c05cd6bbd36f3e3e8c24f8ee740d6c8b53cf0a9767f3c`

Both attached signatures belong to the maximum kerb-mass row and cover the manual and automatic Eco-G columns. The visible 1149 kg TCe 110 value has no attached record and is not inferred.
- `maximum_kerb_weight`: `1149` — The TCe 110 value is visible in the row but is outside the attached evidence set.

### Line 83 — `a53c392d018f9e1f8538c42625fa5f6a91c6f66bb144966f5c1f68e492d9292f`

This continuation completes the maximum kerb-mass label, so the attached 1225 and 1249 kg signatures remain valid for the manual and automatic Eco-G columns. The TCe 110 value remains unattached.
- `maximum_kerb_weight`: `1149` — The TCe 110 maximum kerb mass has no attached evidence for this fragment.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- values without attached evidence are retained only as source facts;
- minimum and maximum kerb-mass evidence is not exchanged between adjacent row fragments;
- suspension, tyre and mass signatures are not substituted for the steering label;
- selected Eco-G evidence is not projected onto the TCe 110 configuration.

## Next package

**Duster Mini Technical Page 21 Ambiguity Review** — Review the 1 ambiguous technical candidate from the Duster mini-brochure page 21 against its 7 preserved evidence signatures without creating master-data rows or approved import specifications.
