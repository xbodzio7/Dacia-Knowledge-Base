# Brochure Gear-Specific Performance Context Model Review

Date: 2026-07-26

## Source review

The official brochure performance tables supply one neutral fact, 80–120 km/h elasticity in seconds, with additional qualifiers:

- Sandero: fourth and fifth gear, with LPG/petrol alternatives for Eco-G;
- Sandero Stepway: fourth, fifth and sixth gear where stated, with LPG/petrol alternatives;
- Jogger: fourth gear, exact five- or seven-seat variant, and LPG/petrol alternatives where stated.

## Existing model coverage

The repository already contains:

- active decimal attribute `elasticity_80_120` with unit `s`;
- optional observation-level `fuel_type_code`;
- exact configuration identity, including powertrain and transmission;
- exact Jogger five- and seven-seat configurations backed by `number_of_seats`.

Only selected gear is missing from observation identity.

## Decision review

An optional `gear_number` column on `configuration_attribute_values.csv` is smaller and clearer than a separate context relation. It follows the established observation-level fuel pattern and allows the reporting key to distinguish otherwise identical fourth-, fifth- and sixth-gear observations.

The field is not derived from `gear_count`. Automatic-transmission observations may use it only when the source explicitly names the gear. Missing gear context is never interpreted as a default gear.

## Compatibility

Existing observations remain valid with an empty future `gear_number`. Existing cargo context architecture remains separate because cargo requires several controlled dimensions and a dedicated relation; this decision does not create a general measurement-context mechanism.
