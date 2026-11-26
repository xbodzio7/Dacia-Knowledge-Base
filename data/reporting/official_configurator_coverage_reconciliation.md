# Official Configurator Coverage Reconciliation

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** one source registration only

## Active coverage

The official Dacia Polska catalogue exposes **6 active model families** and **7 primary configurator surfaces**: Spring, Sandero, Sandero Stepway, Jogger 5-seat, Jogger 7-seat, Duster and Bigster.

Striker is excluded because the catalogue exposes model discovery but no configurator action.

## Reconciliation

- Spring was missing from the broad 2026-07-23 configurator catalogue snapshot and is now included.
- Jogger is represented by separate 5-seat and 7-seat configurator surfaces.
- Current canonical configurator URLs are recorded for all six model families.
- Exact-state identity requires model, grade, powertrain, transmission, drive type, seat count, model phase and `conf` URL where applicable.
- No option, package, price, equipment item or technical value may be copied across a missing exact-state dimension.

## Spring deep-link finding

The user-provided Spring `conf` URL is registered. Static retrieval did not resolve its saved configuration and returned the default Essential state instead. Essential 70 remains directly confirmed, but the saved Expression cable state remains unresolved until the deep link is opened or exported as an exact state. The supplied-cable architecture decision remains deferred.

## Data impact

- source rows added: **1**;
- net master-row increase: **1**;
- configuration values, equipment availability and commercial mappings changed: **0**;
- canonical attributes added: **0**.

## Next package

`official_configurator_exact_state_capture_001` will capture exact saved states, starting with the supplied Spring link, before any new architecture or data mutation.
