# Cross-model Configurator PDF Intake

## Package

- Package ID: `cross_model_configurator_pdf_intake_001`
- Kind: `source_intake`
- Status: complete
- Source date: 2026-08-04

## Scope

Register the 18 user-supplied official Dacia configurator PDF exports for Bigster, Duster, new Jogger, new Sandero F.2 and new Sandero Stepway F.2 as exact saved-state evidence.

## Result

- 18 documents;
- five model families;
- exact SHA-256, byte size, page count and configuration code for every document;
- exact grade, powertrain, fuel, transmission and displayed total price;
- no master-data mutation;
- no propagation between phases or configurations.

## Next package

`cross_model_configurator_data_reconciliation_001` will parse all pages, compare the captured equipment, options, prices and technical values with canonical records, and produce bounded migration candidates and explicit conflicts.
