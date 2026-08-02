# Official Configurator Coverage Reconciliation

Package ID: `official_configurator_coverage_reconciliation_001`

Status: complete

## Goal

Register every active Dacia Polska configurator surface and define the exact-state evidence boundary before using configurator data to fill gaps or make a supplied-cable architecture decision.

## Delivered

- one dated consolidated official-web snapshot;
- one registered source row with SHA-256 provenance;
- six active model families and seven primary configurator surfaces;
- separate Jogger 5-seat and 7-seat surfaces;
- the user-provided Spring `conf` link preserved as an opaque saved-state source;
- an explicit non-propagation rule across grade, powertrain, gearbox, drive, seat count, phase and saved-state URL;
- no configuration, availability, commercial or attribute mutation.

## Decision boundary

The Spring supplied-cable architecture remains undecided. Static retrieval of the saved `conf` link falls back to Essential and cannot prove Expression. The next package must capture exact saved states before architecture is reconsidered.
