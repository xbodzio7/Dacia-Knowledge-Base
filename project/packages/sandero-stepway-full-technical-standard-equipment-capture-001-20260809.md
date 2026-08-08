# Sandero Stepway Full Technical and Standard Equipment Capture

Date: 2026-08-09

## Goal

Capture the complete standard-equipment and technical-specification accordions from every exact current Sandero and Sandero Stepway configurator state.

## Result

- captured all 15 exact grade and engine/transmission states;
- preserved 1,029 configuration-bounded standard-equipment rows;
- preserved 679 configuration-bounded technical label/value rows;
- retained the exact post-navigation URL for every state;
- removed accessories, prices, financing and optional-equipment controls from this evidence artifact.

## Boundaries

- this is a literal source snapshot, not a canonical import;
- model-qualified shared strings remain literal and are not reduced to configuration-specific scalar claims;
- no equipment inheritance is inferred across grades, engines or transmissions;
- no missing source statement is interpreted as `not_available`;
- the next normalization package must reconcile rows against existing dated observations before adding master data.

## Next package

Reconcile the 1,708 captured rows against canonical technical values and equipment availability, map only exact safe matches, and preserve unmatched or ambiguous literal evidence without guessing.
