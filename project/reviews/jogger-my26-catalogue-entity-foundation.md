# Jogger MY26 Catalogue Entity Foundation

## Delivery status

`IMPLEMENTED`

The accepted Polish Jogger MY26 price list dated 2026-04-01 now has a complete
catalogue entity foundation covering every non-empty page-1 price cell.

## Materialized scope

- one active source registration retaining the verified original PDF SHA-256 and reserved archive path;
- one source-to-model relationship;
- four active Jogger versions: Essential, Expression, Extreme and Journey;
- 22 active configurations: 11 five-seat and 11 seven-seat;
- four source-to-version and 22 source-to-configuration relationships;
- 22 dated PL gross catalogue prices;
- 22 dated `number_of_seats` observations.

The original PDF SHA-256 is
`a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b`. The
repository path `PDF/Cenniki/DACIA JOGGER cennik MY26 20260401.pdf` is reserved,
but the connected GitHub writer cannot transfer the supplied binary. Archival and
the shared declarative import contract remain a controlled follow-up boundary.

## Identity boundary

Configuration identity is the combination of trim, seat count, powertrain and
transmission. Seat count appears in the stable code and is also stored as the
integer attribute `number_of_seats`. It is not folded into `powertrain_label`.

The foundation contains:

- six Eco-G 120 manual configurations per both seat groups combined;
- four Eco-G 120 automatic configurations;
- six TCe 110 manual configurations;
- six Hybrid 155 automatic configurations.

## Price boundary

All prices are `catalog_gross`, market `PL`, currency `PLN`, dated 2026-04-01.
Financing instalments, insurance percentages, service packages and promotional
claims are not represented as vehicle catalogue prices.

## Binary archive boundary

The 22 seating observations are materialized directly and covered by regression
tests. A declarative import specification is intentionally not added while its
registered source file cannot pass the repository hash-verification contract.

## Deferred evidence

No page-6 technical value and no page-4/5 equipment state is imported here.
Technical ranges, seat-specific pairs and conditional equipment require separate
reviews so the entity package does not manufacture trim-specific scalar facts.

## Regression boundary

The package preserves the existing Sandero default reporting scope and all seven
Duster powertrain reporting scopes. The new Jogger entities are not silently
added to any existing completeness denominator.

Legacy Duster tests now distinguish their fixed 24-configuration subset from the
repository-wide totals of 53 active configurations and 724 configuration values.

The synchronized repository baseline is 451 automated tests, 3,346 master rows
and 724 configuration values.
