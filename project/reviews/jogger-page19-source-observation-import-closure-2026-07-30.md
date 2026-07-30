# Review — Jogger Page 19 Source Observation Import Closure

Date: 2026-07-30  
Package: `post_residual_jogger_page19_source_observation_import_closure_001`

## Decision

The review package is complete, but the page 19 import queue is not closed.

The acceleration, minimum-kerb-weight and fuel/LPG-capacity follow-ups are complete and collectively preserve 90 new brochure-source observations. Repository evidence also shows that the torque-speed ranges and the matching subset of maximum-power-speed ranges were already imported by earlier packages.

Two safe exact import areas remain:

1. `gross_vehicle_weight` for all 22 current Jogger configurations;
2. `braked_trailer_weight` for the 16 non-Hybrid configurations only.

The gross-vehicle-weight package is selected next because its source row is unambiguous, its values match the later official source for every current configuration, and it does not depend on interpretation of the two adjacent mislabeled blocks.

## Required safety boundaries

The following evidence remains deferred and must not be normalized by inference:

- maximum-kerb-like values printed under a gross-train heading;
- gross-train-like values printed under a gross-vehicle heading;
- Hybrid 155 braked trailer weight of 1200 kg versus the later 1000 kg observation;
- Hybrid 155 system power of 105 kW versus the later 116 kW observation;
- Eco-G petrol maximum-power-speed upper endpoint of 5000 rpm versus the later 5750 rpm endpoint.

The source energy row and WLTP protocol footnote remain context-model questions rather than scalar import candidates.

## Scope confirmation

This package is review-only. It changes no master CSV, creates no approved import specification, and does not promote or overwrite any observation.

## Handoff

Next package: `post_residual_jogger_page19_gross_vehicle_weight_source_observation_import_001`.

Expected result: 22 source-specific `gross_vehicle_weight` observations with exact configuration targets, kilogram units, page 19 provenance and coexistence with later official observations.
