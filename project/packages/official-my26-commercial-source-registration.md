# Official MY26 Commercial Source Registration

Date: 2026-07-21

## Purpose

Register and archive four current official Polish Dacia price lists supplied by the project owner. All documents state that their catalogue prices apply from 3 July 2026.

## Registered sources

| Model range | Pages | SHA-256 | Commercial scope |
| --- | ---: | --- | --- |
| Sandero and Sandero Stepway | 7 | `5af2dbaf268480ec1e7e6d6e35fd2037b6fba3fb79972026e4f68c08055ba783` | Prices, equipment, options and COMFORT, THERMO, ZIMOWY, MEDIA NAV LIVE and EASY packages |
| Duster | 8 | `40bb4f3db9019c500fcb4c759f5ad395aa3b35a68bb22aa74f031fefe09727f2` | Prices, equipment, options and ZIMOWY, ZIMOWY PLUS, PARKING and TECHNO 1 packages |
| Jogger | 7 | `92606411c4d8c10dd830b0d1c387fe663c4c9618422c5db639c13a23138f4a87` | Five- and seven-seat prices, equipment, options and KOMFORT HEV, KOMFORT, ZIMOWY and DRIVE packages |
| Bigster | 8 | `9528654fb3daf3767a2defbbc80e8a85abceecb11e04bb176aa0b76443be178a` | Prices, equipment, options and EASY, PARKING, ZIMOWY and ZIMOWY PLUS packages |

The exact original URLs are retained in `sources.csv`, and the downloaded bytes are archived under `PDF/Cenniki/`.

The archived PDFs are registration inputs for later controlled imports; registering a document does not by itself make every value shown in it an active master-data observation.

Commercial package names in this record preserve the wording used by the Polish source documents; normalized interface labels may be introduced separately without changing source provenance.

## Relationships

- Sandero and Sandero Stepway are related to both current model records, five existing trims and seven currently modeled Eco-G 120 configurations.
- Duster is related to the current model, four trims present in the new price matrix and ten currently modeled configurations that match the new Eco-G 120, mild hybrid 140 and hybrid 155 rows.
- Jogger is related to the current model, all four existing trims and all 22 currently modeled five- and seven-seat configurations.
- Bigster is related to the existing model record only. Bigster versions and configurations are not created by this source-registration package.

Source-to-configuration relationships are additive: an earlier configuration-specific PDF remains registered when a newer general commercial price list also documents that configuration.

## Evidence boundary

Registration and relationships do not import or supersede observations. Existing dated prices, technical values and equipment records remain unchanged. New configurations visible only in the July price lists, such as automatic Eco-G variants or hybrid-G variants, are not inferred into the catalogue.

The next package may model named commercial options and packages with their version-specific prices and use them in the interactive interface and filterable workbook.

## Validation

- archived bytes match the recorded SHA-256 values;
- all four PDFs are readable and contain the stated page counts;
- source, model, version and configuration relationships pass repository validation;
- one regression contract verifies the complete registration set;
- documentation counters and canonical project state are regenerated;
- the full repository quality gate is required before merge.
