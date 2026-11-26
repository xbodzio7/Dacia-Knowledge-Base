# Sandero Stepway Equipment Page 18 Ambiguity Review

## Scope

Reviewed the single ambiguous roof-rails candidate from page 18 of the archived Sandero Stepway brochure.

## Decision

The complete `Relingi dachowe` row is `covered`. Visual inspection shows plain roof rails as standard for Essential and unavailable for Expression and Extreme. The immediately following `Modułowe relingi dachowe (szare Megalith)` row has the inverse layout: unavailable for Essential and standard for Expression and Extreme.

The attached `roof_rails:standard` signature and its exact Essential record are selected. The attached `modular_roof_rails:standard` signature and both exact Expression records are preserved in the report and explicitly rejected because they belong to the adjacent modular-roof-rail row.

## Boundaries

- no `data/master` changes;
- no approved import specifications;
- no projection between trims, engines or gearboxes;
- plain and modular roof rails remain distinct attributes;
- the candidate row remains Essential standard, Expression unavailable and Extreme unavailable;
- the adjacent modular row remains Essential unavailable, Expression standard and Extreme standard;
- rejected evidence remains visible with its exact records and rejection reason.

## Next

Bigster Technical Page 20 Unresolved Review — Chunk 1.
