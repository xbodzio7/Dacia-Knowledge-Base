# Official Jogger Accessory Non-Configurator Reconciliation

Date: 2026-08-06

## Goal

Assimilate all rows from the official Polish Jogger accessory price list and reconcile them with the current official model accessory page and selected Dacia Shop product records, without using the configurator.

## Result

- 98 complete price-list rows from the document valid from 2022-10-03;
- 28 concepts explicitly promoted on the current Jogger accessory page;
- 18 current Dacia Shop corroboration records;
- historical prices and current availability kept as separate evidence layers;
- unresolved reference and compatibility questions preserved instead of inferred.

## Source limitation

The official accessory hub still links to the Jogger catalogue PDF, but the full catalogue matrix is not ingested in this package. This package therefore does not claim complete current grade-level accessory compatibility. It records the current official model-page concepts and current shop records separately from the historical price list.

## Important findings

- The current Jogger page promotes Aero Cargo Box, while the current shop card for reference `7717275154` lists only New Duster and Bigster.
- Current rubber mats for five- and seven-seat Jogger variants are promoted, but their references are not present in the 2022 price list.
- The current YouClip range is much broader than the 2022 document and must not be mapped to the older multifunction-system references.
- The Sleep box, mattress and blackout blinds remain separate official product references.
- Current shop prices matching selected 2022 prices do not justify treating all 2022 prices as current.

## Boundaries

- No configurator data.
- No inferred reference from a similar product name.
- No automatic transfer from Duster, Bigster, Sandero or another market.
- No absence from shop search treated as withdrawal.
- No historical price described as current unless the current shop card exposes the same price.

## Next step

Complete the official Jogger catalogue matrix ingestion, then continue with the remaining Spring accessory documents and build the cross-model missing-data queue.
