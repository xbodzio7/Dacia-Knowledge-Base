# Striker MY26 Matrix Marker Semantics Correction

**Package:** `striker_my26_matrix_marker_semantics_correction_20261124_001`  
**Source:** `src_pl_striker_price_my26_20261102`  
**Archived PDF:** `PDF/Cenniki/striker-price.pdf`  
**SHA-256:** `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`  
**Evidence:** printed page 5; Project Owner interpretation recorded as D-035.

## Owner-defined symbol interpretation

| Symbol | Meaning | Stored status |
|---|---|---|
| `●` | Present / standard | `standard` |
| `-` | Absent / unavailable | `not_available` |
| `o` | Paid selectable option | `optional` |
| `P` | Available as part of a package | `package` |

This is an explicit Project Owner interpretation. The cennik itself does not print a legend defining `P`; the correction is not presented as a source-defined legend.

## Corrected result

The 11 commercial items and 121 mappings are retained. The status distribution is:

| Status | Count |
|---|---:|
| `optional` | 60 |
| `standard` | 3 |
| `not_available` | 51 |
| `package` | 7 |
| `unknown` | 0 |
| **Total** | **121** |

For **Podgrzewane dysze spryskiwaczy i szyba przednia**, Essential remains `not_available`; Expression and Extreme are `package`; Journey remains `optional` at 1,000 PLN. The seven package mappings carry no amount.

## Boundary retained

The `package` status says that the item is available only as part of a package. It does not identify which named package contains the item. No specific package-component relationship or equipment-attribute row has been inferred.

## Reproducible controls

- Updated the shared `equipment_availability_statuses.csv` dictionary with `package`.
- Updated the Striker import specification, master mappings, importer contract and regression tests.
- Preserved the raw `P` marker and source page in mapping notes.
- Added D-035 and updated the project data-schema/glossary documentation.

Report ID: striker_my26_matrix_marker_semantics_correction_20261124_001
Generated: 2026-11-24T16:00:00+01:00
Analysed commit: 5695c54ba971e710ac381e3a52b9f5f27d8d18c5
Status: current
Scope: Owner-directed correction of the official Polish Striker MY26 2026-11-02 page-5 priced option/package matrix; 11 exact source-linked configurations and 121 mappings. The symbol interpretation is supplied by the Project Owner, not inferred from a cennik legend.
