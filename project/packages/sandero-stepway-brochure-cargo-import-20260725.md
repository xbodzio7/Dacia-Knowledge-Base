# Sandero and Stepway Brochure Cargo Import

Date: 2026-07-25

## Scope

Import the model-wide cargo table on page 20 of the official Polish Sandero and
Sandero Stepway brochures dated 2 February 2026 into every active Eco-G 120
configuration represented by those brochures.

The package creates 45 canonical `boot_capacity` observations, 45 one-to-one cargo
context rows and nine source-to-configuration relationships. It does not import TCe
100 configurations because they are not present in master data.

## Imported observations per configuration

- 328 dm3 according to ISO 3832, second row upright, main luggage compartment;
- 410 ordinary litres, second row upright, main luggage compartment;
- 1108 dm3 according to ISO 3832, second row folded, source-stated total;
- 1455 ordinary litres, second row folded, source-stated total;
- 78 dm3 according to ISO 3832, underfloor compartment, seat state not stated.

The source does not qualify these values by spare wheel, repair kit or double floor.
Those three fields remain empty and mean **not stated**, never `absent`.

## Historical conflict policy

Seven configuration documents dated 26 June 2026 already record 410 L and a separate
legacy `cargo_volume_vda` value of 372 dm3. The brochure observation of 328 dm3 is older
and uses the new canonical context model. Both histories are retained. No legacy row is
rewritten, deleted or assigned a context retroactively.

## Evidence boundary

The page presents one model-wide table and no trim-dependent or powertrain-dependent
cargo columns. The import is therefore projected only to active Sandero and Stepway
Eco-G 120 configurations belonging to the corresponding model. Five-seat layout is
verified where configuration-level evidence exists and otherwise follows the unambiguous
five-seat body represented by the brochure.

## Follow-up

The next package imports Jogger cargo values with explicit five- and seven-seat layouts
and second-/third-row state combinations.
