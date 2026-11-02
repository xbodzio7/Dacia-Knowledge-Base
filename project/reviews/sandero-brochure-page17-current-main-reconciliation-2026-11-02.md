# Sandero Brochure Page 17 — Current Main Reconciliation

Date: 2026-11-02  
Package: `sandero_brochure_page17_current_main_reconciliation_20261102_001`  
Source: `src_pl_sandero_brochure_20260202`, page 17

## Result

**No new import.** The prior ambiguity review selected 8 exact evidence signatures representing 16 records. Current `data/master/configuration_attribute_values.csv` already contains all 16 with the exact brochure source code.

| Attribute | Existing exact records |
|---|---:|
| `engine_power` | 4 |
| `engine_torque` | 4 |
| `maximum_kerb_weight` | 4 |
| `gross_vehicle_weight` | 2 |
| `gross_train_weight` | 2 |
| **Total** | **16** |

The 41 unresolved candidates remain split into 27 `context_only_non_import` and 14 `unresolved_signature_mismatch`; they have zero selected evidence signatures. They are not import-ready.

## Scope closure

- Candidates reconciled against current main: 46
- Exact selected observations missing from master: 0
- Master values overwritten: 0
- New import specifications: 0
- New master-data rows: 0

The page-17 residual review is closed as already covered or not importable from retained evidence. The next package must select the next stable residual boundary; it must not repeat this page or the Bigster PR #754 crosswalk.
