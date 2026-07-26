# Duster Brochure Cargo Value Import Review

Date: 2026-07-26

## Source identity

The archived 25-page official Polish Duster mini brochure is verified against SHA-256 `84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8`.

## Reviewed evidence

The powertrain-specific technical tables on PDF pages 20 and 21 distinguish:

- Eco-G 120, 4x2, manual six-speed;
- mild hybrid 140, 4x2, manual six-speed;
- hybrid-G 150, 4x4, automatic;
- hybrid 155, 4x2, automatic multimode.

Cargo values distinguish VDA/ISO 3832 and ordinary litres, rear bench upright or folded, and repair-kit or spare-wheel state.

## Projection boundary

Only ten active configurations matching an exact source column are imported. The Eco-G 120 manual values are not inherited by the three automatic configurations. The hybrid-G 150 4x4 column remains unimported because no exact Duster configuration exists in master data.

The generic dimensions page is not used to assign values to a powertrain. Its 4x2/4x4 values are preserved as deferred evidence rather than used to overwrite the exact technical table.

## Reproducibility

The versioned specification generates value IDs 2055–2118, context IDs 224–287 and source-configuration IDs 207–216. The importer verifies the source hash and all 64 value/context pairs and is safe to run repeatedly.
